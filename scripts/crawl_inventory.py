#!/usr/bin/env python3
"""
crawl_inventory.py - Kumpulkan URL, template, PDF, media untuk audit aksesibilitas.

Strategi (3 tahap, semua read-only GET, jeda >= 1 detik):
  1. Baca sitemap (index rekursif) -> semua URL + post type asal
  2. Crawl sampel halaman per post type -> ekstraksi PDF, media, heuristik awal
  3. Enumerasi PDF via WordPress REST API (kalau situs WP) -> judul + ukuran file

Output: inventory/urls.txt, urls-all.txt, templates.md, pdfs.csv, media.csv,
        heuristics.csv, machine-time-estimate.md, logs/crawl-YYYYMMDD-HHMMSS.log

Idempotent: hasil ekstraksi per URL di-cache di inventory/.cache/ sehingga
run ulang tidak meng-fetch ulang halaman yang sama.

Usage:
    python scripts/crawl_inventory.py
    python scripts/crawl_inventory.py --base-url https://www.inovasi.or.id --sample-per-type 5
    python scripts/crawl_inventory.py --full-crawl          # crawl semua URL (lambat)
    python scripts/crawl_inventory.py --no-wp-api           # skip enumerasi PDF via WP API
"""

import argparse
import csv
import gzip
import hashlib
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_BASE_URL = "https://www.inovasi.or.id"
REQUEST_DELAY = 1.5
USER_AGENT = "WebQA-AccessibilityBot/1.0 (+audit aksesibilitas; kontak: tim-a11y)"
TIMEOUT = 40

INVENTORY_DIR = PROJECT_ROOT / "inventory"
CACHE_DIR = INVENTORY_DIR / ".cache"
LOG_DIR = INVENTORY_DIR / "logs"

PDF_RE = re.compile(r"\.pdf($|\?)", re.IGNORECASE)
VIDEO_HOST_RE = re.compile(r"(youtube\.com|youtu\.be|vimeo\.com|dailymotion\.com|wistia\.|brightcove)", re.I)
AUDIO_HOST_RE = re.compile(r"(soundcloud\.com|spotify\.com|anchor\.fm|mixcloud\.com)", re.I)
IMG_RE = re.compile(r"<img\b", re.I)
IMG_NO_ALT_RE = re.compile(r"<img\b(?![^>]*\balt\s*=)[^>]*>", re.I)
IFRAME_RE = re.compile(r"<iframe\b", re.I)
IFRAME_NO_TITLE_RE = re.compile(r"<iframe\b(?![^>]*\btitle\s*=)[^>]*>", re.I)
H1_RE = re.compile(r"<h1\b", re.I)
SKIP_EXT = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".zip", ".doc", ".docx",
            ".xls", ".xlsx", ".ppt", ".pptx", ".mp3", ".mp4", ".avi", ".mov", ".csv")

TEMPLATE_LABELS = {
    "page": "Halaman Statis (ID + EN)",
    "featured-article": "Artikel Unggulan",
    "press-release": "Siaran Pers / Berita",
    "publication": "Detail Publikasi",
    "publication-category": "Arsip / Kategori Publikasi",
    "opportunity": "Detail Peluang",
    "opportunity-category": "Arsip / Kategori Peluang",
    "where-we-work": "Detail Wilayah Kerja",
    "where-we-works": "Wilayah Kerja (slug jamak)",
    "gallery": "Galeri",
    "resources": "Sumber Daya",
    "attachment": "Attachment",
    "post": "Postingan",
}

AXE_SEC_PER_URL = 60
LIGHTHOUSE_SEC_PER_URL = 45
PDF_CHECK_SEC_PER_FILE = 8


class Crawler:
    def __init__(self, delay=REQUEST_DELAY, timeout=TIMEOUT):
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
        })
        self.last_request = 0.0
        self.request_count = 0
        self.bytes_downloaded = 0
        self.errors = []

    def _wait(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

    def get(self, url, params=None, retries=2, stream=False):
        for attempt in range(retries + 1):
            self._wait()
            self.last_request = time.time()
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout,
                                        allow_redirects=True, stream=stream)
                self.request_count += 1
                self.bytes_downloaded += len(resp.content or b"")
                if resp.status_code >= 500 and attempt < retries:
                    continue
                return resp
            except requests.RequestException as e:
                if attempt < retries:
                    time.sleep(2)
                    continue
                self.errors.append((url, str(e)))
                print(f"  [ERR] {url} -> {e}", file=sys.stderr)
                return None

    def get_json(self, url, params=None):
        resp = self.get(url, params=params)
        if resp is None or resp.status_code != 200:
            return None
        try:
            return resp.json()
        except ValueError:
            return None


def post_type_from_sitemap(sitemap_url):
    name = urlparse(sitemap_url).path.rsplit("/", 1)[-1]
    slug = re.sub(r"-?sitemap\d*\.xml$", "", name, flags=re.I)
    return slug.lower() or "unknown"


def canonicalize(url):
    """Buang query/fragment dan trailing slash. Yoast sering emitting URL duplikat."""
    p = urlparse(url)
    path = re.sub(r"/{2,}", "/", p.path)
    if len(path) > 1:
        path = path.rstrip("/")
    return f"{p.scheme}://{p.netloc.lower()}{path}"


SITEMAP_JUNK_RE = re.compile(r"[?&](post_type|p|attachment_id|page_id)=", re.I)


def collect_sitemaps(crawler, base_url):
    """Baca sitemap index rekursif, kembalikan (by_type, anomalies)."""
    queue = [urljoin(base_url, "/sitemap_index.xml"), urljoin(base_url, "/sitemap.xml")]
    seen = set()
    by_type = defaultdict(list)
    anomalies = {"duplikat": 0, "query_param": 0}

    while queue:
        sm_url = queue.pop(0)
        if sm_url in seen:
            continue
        seen.add(sm_url)

        resp = crawler.get(sm_url)
        if resp is None or resp.status_code != 200:
            continue

        body = resp.text
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)
        if not locs:
            continue

        is_index = "<sitemapindex" in body.lower()
        if is_index:
            print(f"  [SITEMAP INDEX] {sm_url} -> {len(locs)} child")
            queue.extend(locs)
            continue

        ptype = post_type_from_sitemap(sm_url)
        bucket = by_type[ptype]
        added = 0
        for raw in locs:
            if SITEMAP_JUNK_RE.search(raw):
                anomalies["query_param"] += 1
                continue
            url = canonicalize(raw)
            if url in bucket:
                anomalies["duplikat"] += 1
                continue
            bucket.append(url)
            added += 1
        print(f"  [SITEMAP] {ptype}: +{added} URL unik (total {len(bucket)})")

    return by_type, anomalies


def pick_samples(urls, n):
    if n <= 0 or len(urls) <= n:
        return list(urls)
    step = len(urls) / n
    return [urls[int(i * step)] for i in range(n)]


def build_crawl_plan(by_type, base_url, sample_per_type, full_crawl, extra_urls):
    host = urlparse(base_url).netloc
    plan = []

    for ptype, urls in sorted(by_type.items()):
        urls = sorted(set(urls))
        if full_crawl or ptype == "page":
            plan.extend((u, ptype) for u in urls)
        else:
            plan.extend((u, ptype) for u in pick_samples(urls, sample_per_type))

    for u in extra_urls:
        plan.append((u, "main-halaman-utama"))

    seen = set()
    unique_plan = []
    for url, ptype in plan:
        if url in seen:
            continue
        seen.add(url)
        unique_plan.append((url, ptype))
    return unique_plan


def cache_path(url):
    key = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{key}.json"


def load_cached(url):
    p = cache_path(url)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            return None
    return None


def save_cached(url, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path(url).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def normalize(base, href):
    if not href:
        return None
    full = urljoin(base, href.strip())
    return full.split("#")[0]


PDFEMB_RE = re.compile(r"[?&]pdfemb-data=([^&\"]+)")


def pdf_urls_from_pdfemb(src, page_url):
    """Plugin PDF Embed membungkus URL PDF dalam base64; decode untuk dapat URL asli."""
    found = []
    for blob in PDFEMB_RE.findall(src or ""):
        try:
            import base64
            import html as html_mod
            raw = base64.b64decode(html_mod.unescape(blob) + "=" * (-len(blob) % 4))
            decoded = raw.decode("utf-8", "ignore")
        except Exception:
            continue
        for m in re.findall(r'https?://[^"\\\s]+?\.pdf', decoded, re.I):
            found.append({"url": canonicalize(html_mod.unescape(m)), "title": "",
                          "source_page": page_url, "found_via": "pdf-embed"})
    return found


def extract_from_soup(soup, page_url, base_domain):
    data = {"pdfs": [], "media": [], "outbound_video": [], "outbound_audio": [], "stats": {}}

    for a in soup.find_all("a", href=True):
        href = a["href"]
        url = normalize(page_url, href)
        if not url:
            continue
        if PDF_RE.search(href):
            if urlparse(url).netloc in (base_domain, ""):
                title = a.get_text(" ", strip=True) or (a.get("title") or "").strip() or \
                    url.rsplit("/", 1)[-1].rsplit(".", 1)[0]
                data["pdfs"].append({"url": url, "title": title, "source_page": page_url})
        elif VIDEO_HOST_RE.search(url):
            data["outbound_video"].append({"url": url, "source_page": page_url})
        elif AUDIO_HOST_RE.search(url):
            data["outbound_audio"].append({"url": url, "source_page": page_url})

    for tag, kind in (("video", "html5-video"), ("audio", "html5-audio")):
        for el in soup.find_all(tag):
            src = el.get("src")
            if not src:
                sub = el.find("source")
                src = sub.get("src") if sub else None
            if src:
                url = normalize(page_url, src)
                if url:
                    data["media"].append({
                        "url": url, "platform": kind, "embed": "N",
                        "caption": "unknown", "source_page": page_url,
                    })

    for iframe in soup.find_all("iframe"):
        src = normalize(page_url, iframe.get("src", ""))
        if not src:
            continue
        title = (iframe.get("title") or "").strip()
        platform = ("embed-video" if VIDEO_HOST_RE.search(src)
                    else "embed-audio" if AUDIO_HOST_RE.search(src)
                    else "embed-other")
        data["media"].append({
            "url": src, "platform": platform, "embed": "Y",
            "caption": "unknown", "frame_title": title,
            "source_page": page_url,
        })
        data["pdfs"].extend(pdf_urls_from_pdfemb(iframe.get("src", ""), page_url))

    html = str(soup)
    data["stats"] = {
        "img_total": len(IMG_RE.findall(html)),
        "img_no_alt": len(IMG_NO_ALT_RE.findall(html)),
        "iframe_total": len(IFRAME_RE.findall(html)),
        "iframe_no_title": len(IFRAME_NO_TITLE_RE.findall(html)),
        "h1_count": len(H1_RE.findall(html)),
        "title": (soup.title.get_text(strip=True) if soup.title else ""),
        "html_lang": (html_root_lang(soup) or ""),
        "has_skip_link": bool(re.search(r"skip\s*(to|link)|lewati|lompat", html, re.I)),
        "forms": len(soup.find_all("form")),
        "inputs": len(soup.find_all(["input", "select", "textarea"])),
    }
    return data


def html_root_lang(soup):
    html = soup.find("html")
    if html is None:
        return None
    lang = html.get("lang")
    if isinstance(lang, list):
        return lang[0]
    return lang


def crawl_pages(crawler, plan, base_domain, use_cache=True):
    results = {}
    cache_hits = 0

    for i, (url, ptype) in enumerate(plan, 1):
        cached = load_cached(url) if use_cache else None
        if cached:
            cache_hits += 1
            results[url] = cached
            print(f"[{i}/{len(plan)}] CACHE {url}")
            continue

        resp = crawler.get(url)
        if resp is None or resp.status_code != 200:
            print(f"[{i}/{len(plan)}] FAIL {url}")
            continue

        ctype = resp.headers.get("Content-Type", "")
        if "text/html" not in ctype.lower():
            continue

        soup = BeautifulSoup(resp.content, "html.parser")
        data = extract_from_soup(soup, str(resp.url), base_domain)
        data["url"] = str(resp.url)
        data["post_type"] = ptype
        data["fetched_at"] = datetime.now().isoformat(timespec="seconds")
        save_cached(url, data)
        results[url] = data

        s = data["stats"]
        notes = []
        if s["img_no_alt"]:
            notes.append(f"img-no-alt={s['img_no_alt']}")
        if data["pdfs"]:
            notes.append(f"pdf={len(data['pdfs'])}")
        if data["media"]:
            notes.append(f"media={len(data['media'])}")
        print(f"[{i}/{len(plan)}] OK {url} " + ("(" + ", ".join(notes) + ")" if notes else ""))

    print(f"\n[INFO] Halaman diproses: {len(results)} (cache hit: {cache_hits})")
    return results


def enumerate_pdfs_wp_api(crawler, base_url):
    """Enumerasi PDF lewat WordPress REST API (judul + ukuran file)."""
    api = urljoin(base_url, "/wp-json/wp/v2/media")
    per_page = 100
    page = 1
    total_pages = None
    found = []

    while True:
        data = crawler.get_json(api, params={"mime_type": "application/pdf", "per_page": per_page, "page": page})
        if not data:
            if page == 1:
                print("  [WP API] tidak tersedia / diblokir")
            break
        if isinstance(data, dict) and "code" in data:
            print(f"  [WP API] error: {data.get('message', data.get('code'))}")
            break
        if not isinstance(data, list) or not data:
            break

        for item in data:
            found.append({
                "url": item.get("source_url", ""),
                "title": (item.get("title") or {}).get("rendered", "") or item.get("slug", ""),
                "size_bytes": item.get("filesize_in_bytes", 0),
                "source_page": item.get("link", ""),
                "found_via": "wp-rest-api",
            })
        print(f"  [WP API] halaman {page}: +{len(data)} PDF (kumulatif {len(found)})")
        if len(data) < per_page:
            break
        page += 1
        if page > 200:
            break

    return found


def dedupe(rows, key="url"):
    seen = set()
    out = []
    for r in rows:
        k = r.get(key)
        if k and k not in seen:
            seen.add(k)
            out.append(r)
    return out


def write_templates(path, by_type, crawled_urls, anomalies, full_crawl=False):
    lines = ["# Template Halaman - inovasi.or.id", ""]
    lines.append(f"Dihasilkan: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Total URL unik di sitemap: {sum(len(set(v)) for v in by_type.values())}")
    lines.append(f"Total URL di-crawl: {len(crawled_urls)}")
    lines.append(f"URL duplikat diabaikan (Yoast): {anomalies.get('duplikat', 0)}")
    lines.append(f"URL query-param diabaikan: {anomalies.get('query_param', 0)}")
    lines.append("")

    lines.append("| Template | Post type / sumber | Jumlah URL di sitemap | Jumlah di-crawl | Contoh URL |")
    lines.append("|----------|--------------------|----------------------|-----------------|------------|")

    rows = []
    for ptype, urls in sorted(by_type.items()):
        urls = sorted(set(urls))
        crawled = [u for u in urls if u in crawled_urls]
        if not crawled:
            sample = pick_samples(urls, 1)
            crawled = sample
        label = TEMPLATE_LABELS.get(ptype, f"Template: {ptype}")
        rows.append((label, ptype, len(urls), len(crawled), (crawled[0] if crawled else urls[0])))

    for label, ptype, total, crawled, example in sorted(rows, key=lambda r: -r[2]):
        lines.append(f"| {label} | `{ptype}` | {total} | {crawled} | {example} |")

    crawled_sorted = sorted(crawled_urls)
    for u in crawled_sorted:
        if u.rstrip("/").endswith(("inovasi.or.id", "inovasi.or.id/home", "inovasi.or.id/en")):
            label = "Homepage (ID)" if u.rstrip("/").endswith("inovasi.or.id") else "Homepage (EN)"
            if not any(label == r[0] for r in rows):
                lines.append(f"| {label} | homepage | - | 1 | {u} |")

    lines.append("")
    lines.append("## Catatan")
    lines.append("")
    lines.append("- Post type diambil dari nama file sitemap (contoh: `publication-sitemap.xml` -> `publication`).")
    lines.append("- Halaman statis (`page`) selalu di-crawl seluruhnya karena sebagian besar adalah halaman utama/nav.")
    if full_crawl:
        lines.append("- Mode `--full-crawl`: semua URL unik di-sitemap sudah di-crawl, "
                     "jadi angka PDF/media di bawah bukan sampel.")
    else:
        lines.append(f"- Mode sampel: {len(crawled_urls)} URL di-crawl dari total "
                     f"{sum(len(set(v)) for v in by_type.values())} URL; angka PDF/media adalah sampel.")
    lines.append("- Sitemap Yoast memuat 461 URL duplikat + 4 URL query-param (`?post_type=`, `?p=`) "
                 "yang dibuang agar tidak terhitung ganda.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows


def write_machine_estimate(path, counts, elapsed, n_main, n_all, n_pdfs, n_media):
    def fmt(seconds):
        h, rem = divmod(int(round(seconds)), 3600)
        m, s = divmod(rem, 60)
        return f"{h}j {m}m {s}d" if h else f"{m}m {s}d"

    main_axe = n_main * AXE_SEC_PER_URL
    main_lh = n_main * LIGHTHOUSE_SEC_PER_URL
    pdf_sec = n_pdfs * PDF_CHECK_SEC_PER_FILE
    main_total = elapsed + main_axe + main_lh + pdf_sec + 300

    full_axe = n_all * AXE_SEC_PER_URL
    full_lh = n_all * LIGHTHOUSE_SEC_PER_URL
    full_total = 60 * 14 + full_axe + full_lh + pdf_sec + 600

    lines = [
        "# Estimasi Waktu Mesin (Fase 1-2)",
        "",
        f"Dihasilkan: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "Waktu mesin = durasi tool berjalan tanpa intervensi manusia. Tidak termasuk waktu analisis/penulisan.",
        "",
        "## Angka terukur saat crawl",
        "",
"| Metrik | Nilai |",
        "|--------|-------|",
        f"| URL unik di sitemap | {n_all} |",
        f"| URL di-crawl pada run ini | {counts.get('crawled', 0)} |",
        f"| Halaman utama (post type `page` + home ID/EN) | {n_main} |",
        f"| Post type / template | {counts.get('templates', 0)} |",
        f"| PDF ditemukan | {n_pdfs} |",
        f"| Media/embed ditemukan | {n_media} |",
        f"| Request HTTP | {counts.get('requests', 0)} |",
        f"| Data terunduh | {counts.get('bytes', 0) / 1024 / 1024:.1f} MB |",
        f"| Error | {counts.get('errors', 0)} |",
        f"| Durasi crawl aktual | {fmt(elapsed)} |",
        f"| Rata-rata per URL | {elapsed / max(counts.get('requests', 1), 1):.2f} detik |",
        "",
        "## Konstanta perkiraan (dari kode script)",
        "",
        f"- `run_axe.py`: 1 URL = 1 launch Puppeteer + `networkidle2` + 2 detik tunggu -> asumsi {AXE_SEC_PER_URL} detik/URL",
        f"- `run_lighthouse.py`: 1 URL = gather desktop + hanya kategori accessibility -> asumsi {LIGHTHOUSE_SEC_PER_URL} detik/URL",
        f"- `check_pdfs.py`: unduh + parse PDF -> asumsi {PDF_CHECK_SEC_PER_FILE} detik/file",
        "",
        "## Skenario A - Halaman utama",
        "",
        "| Step | Perkiraan |",
        "|------|-----------|",
        f"| `crawl_inventory.py` (terukur, cache) | {fmt(60)} |",
        f"| `run_axe.py` ({n_main} URL) | {fmt(main_axe)} |",
        f"| `run_lighthouse.py` ({n_main} URL) | {fmt(main_lh)} |",
        f"| `check_pdfs.py` ({n_pdfs} PDF) | {fmt(pdf_sec)} |",
        "| `merge_findings.py` + ringkasan | 5m 0d |",
        f"| **Total mesin skenario A** | **{fmt(main_total)}** |",
        "",
        "## Skenario B - Full site",
        "",
        "| Step | Perkiraan |",
        "|------|-----------|",
        f"| `crawl_inventory.py` (terukur, {n_all} URL) | {fmt(elapsed)} |",
        f"| `run_axe.py` ({n_all} URL) | {fmt(full_axe)} |",
        f"| `run_lighthouse.py` ({n_all} URL) | {fmt(full_lh)} |",
        f"| `check_pdfs.py` ({n_pdfs} PDF) | {fmt(pdf_sec)} |",
        "| `merge_findings.py` + ringkasan | 10m 0d |",
        f"| **Total mesin skenario B** | **{fmt(full_total)}** |",
        "",
        "Catatan: `run_axe.py` dan `run_lighthouse.py` di repo ini me-launch Chrome per URL (tanpa reuse),",
        "jadi waktu didominasi proses start/stop browser, bukan jaringan. Optimasi: reuse 1 instance",
        "Chrome untuk seluruh URL bisa memangkas 30-50% dari durasi di atas.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"main": main_total, "full": full_total, "fmt": fmt}


def probe_pdf(crawler, url):
    """HEAD untuk ambil ukuran + status. PDF ada di direktori securepdfs yang perlu dicek."""
    crawler._wait()
    crawler.last_request = time.time()
    try:
        resp = crawler.session.head(url, timeout=crawler.timeout, allow_redirects=True)
        crawler.request_count += 1
        return resp.status_code, int(resp.headers.get("Content-Length") or 0), resp.headers.get("Content-Type", "")
    except requests.RequestException as e:
        crawler.request_count += 1
        crawler.errors.append((url, str(e)))
        return 0, 0, ""


def load_probe_cache(url):
    p = CACHE_DIR / f"probe-{hashlib.sha1(url.encode('utf-8')).hexdigest()}.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            return None
    return None


def save_probe_cache(url, status, size, ctype):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p = CACHE_DIR / f"probe-{hashlib.sha1(url.encode('utf-8')).hexdigest()}.json"
    p.write_text(json.dumps({"status": status, "size_bytes": size, "content_type": ctype}),
                 encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Crawl inventory untuk audit aksesibilitas")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--sample-per-type", type=int, default=5)
    ap.add_argument("--full-crawl", action="store_true", help="crawl semua URL (1200+, lambat)")
    ap.add_argument("--no-wp-api", action="store_true", help="skip enumerasi PDF via WP REST API")
    ap.add_argument("--pdf-probe", action="store_true", help="HEAD tiap PDF untuk ambil ukuran + status")
    ap.add_argument("--delay", type=float, default=REQUEST_DELAY)
    ap.add_argument("--no-cache", action="store_true", help="abaikan cache ekstraksi")
    args = ap.parse_args()

    INVENTORY_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = LOG_DIR / f"crawl-{stamp}.log"
    log_fh = open(log_file, "w", encoding="utf-8")

    class Tee:
        def write(self, s):
            sys.__stdout__.write(s)
            log_fh.write(s)

        def flush(self):
            sys.__stdout__.flush()
            log_fh.flush()

    sys.stdout = Tee()
    start = time.time()
    crawler = Crawler(delay=args.delay)
    base_domain = urlparse(args.base_url).netloc.replace("www.", "")

    print(f"[INFO] base-url      : {args.base_url}")
    print(f"[INFO] delay         : {args.delay}s | UA: {USER_AGENT}")
    print(f"[INFO] sample/type   : {args.sample_per_type} | full-crawl: {args.full_crawl}")
    print(f"[INFO] log           : {log_file}\n")

    print("[PHASE 1] Membaca sitemap rekursif")
    by_type, anomalies = collect_sitemaps(crawler, args.base_url)
    all_urls = sorted({u for urls in by_type.values() for u in urls})
    print(f"[INFO] Total URL unik di sitemap: {len(all_urls)} | post type: {len(by_type)}")
    print(f"[INFO] URL duplikat di sitemap: {anomalies['duplikat']} | "
          f"URL query-param diabaikan: {anomalies['query_param']}\n")

    extra = [
        urljoin(args.base_url, "/"),
        urljoin(args.base_url, "/en/"),
        urljoin(args.base_url, "/404/"),
    ]

    print("[PHASE 2] Crawl sampel halaman")
    plan = build_crawl_plan(by_type, args.base_url, args.sample_per_type, args.full_crawl, extra)
    print(f"[INFO] Rencana crawl: {len(plan)} URL\n")
    crawled = crawl_pages(crawler, plan, base_domain, use_cache=not args.no_cache)
    print("")

    print("[PHASE 3] Enumerasi PDF via WordPress REST API")
    wp_pdfs = [] if args.no_wp_api else enumerate_pdfs_wp_api(crawler, args.base_url)
    print("")

    print("[PHASE 4] Merge + probe PDF")
    merged = {}

    def add(row, rank):
        url = canonicalize(row["url"])
        if not url or url.endswith("/"):
            return
        cur = merged.setdefault(url, {"url": url, "title": "", "size_bytes": 0,
                                      "source_page": "", "found_via": ""})
        if rank < rank_of.get(cur["found_via"], 99):
            cur["found_via"] = row.get("found_via", "html-crawl")
        for k in ("title", "source_page"):
            if row.get(k):
                cur[k] = row[k]
        if row.get("size_bytes"):
            cur["size_bytes"] = row["size_bytes"]

    rank_of = {"wp-rest-api": 0, "pdf-embed": 1, "html-crawl": 2, "": 99}
    for d in crawled.values():
        for p in d["pdfs"]:
            add(p, 2)
    for p in wp_pdfs:
        add(p, 0)

    pdfs = list(merged.values())
    pdfs.sort(key=lambda r: r["url"])

    pending = []
    for p in pdfs:
        cached_probe = load_probe_cache(p["url"])
        if cached_probe:
            p.update(cached_probe)
        else:
            pending.append(p)

    if pending and args.pdf_probe:
        print(f"  [PDF PROBE] {len(pending)} PDF (HEAD, ~{args.delay}s jeda)")
        for i, p in enumerate(pending, 1):
            status, size, ctype = probe_pdf(crawler, p["url"])
            p["status"] = status
            p["size_bytes"] = size or p["size_bytes"]
            p["content_type"] = ctype
            save_probe_cache(p["url"], status, size, ctype)
            if status not in (200, 206):
                print(f"  [PDF WARN] {status} {p['url']}", file=sys.stderr)
            if i % 25 == 0:
                print(f"  [PDF PROBE] {i}/{len(pending)}")
    elif pending:
        print(f"  [PDF PROBE] dilewati ({len(pending)} PDF belum diprobe; pakai --pdf-probe)")
    else:
        print("  [PDF PROBE] semua hasil dari cache")
    print("")

    crawled_urls = list(crawled.keys())
    elapsed = time.time() - start

    print("[PHASE 5] Menyimpan output")
    all_urls_path = INVENTORY_DIR / "urls-all.txt"
    all_urls_path.write_text("\n".join(all_urls) + "\n", encoding="utf-8")

    urls_path = INVENTORY_DIR / "urls.txt"
    urls_path.write_text("\n".join(sorted(crawled_urls)) + "\n", encoding="utf-8")

    main_urls = set(by_type.get("page", []))
    main_urls.update(urljoin(args.base_url, p) for p in ("/", "/en/", "/404/"))
    for ptype, urls in by_type.items():
        if ptype != "page" and urls:
            main_urls.add(sorted(urls)[0])
    main_urls = {canonicalize(u) for u in main_urls}
    main_urls_path = INVENTORY_DIR / "urls-utama.txt"
    main_urls_path.write_text("\n".join(sorted(main_urls)) + "\n", encoding="utf-8")

    rows = write_templates(INVENTORY_DIR / "templates.md", by_type, set(crawled_urls), anomalies,
                          full_crawl=args.full_crawl)

    with open(INVENTORY_DIR / "pdfs.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "title", "size_bytes", "status", "content_type",
                                          "source_page", "found_via"], extrasaction="ignore")
        w.writeheader()
        for p in pdfs:
            p.setdefault("size_bytes", "")
            p.setdefault("status", "")
            p.setdefault("content_type", "")
            w.writerow(p)

    media = dedupe([m for d in crawled.values() for m in d["media"]]
                   + [{"url": v["url"], "platform": "link-out", "embed": "N", "caption": "unknown",
                       "source_page": v["source_page"]} for v in
                      (o for d in crawled.values() for o in d["outbound_video"])]
                   + [{"url": a["url"], "platform": "link-out", "embed": "N", "caption": "unknown",
                       "source_page": a["source_page"]} for a in
                      (o for d in crawled.values() for o in d["outbound_audio"])])
    with open(INVENTORY_DIR / "media.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "platform", "embed", "caption", "frame_title", "source_page"],
                           extrasaction="ignore")
        w.writeheader()
        for m in media:
            m.setdefault("frame_title", "")
            w.writerow(m)

    with open(INVENTORY_DIR / "heuristics.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "post_type", "img_total", "img_no_alt", "iframe_total",
                                          "iframe_no_title", "h1_count", "has_skip_link", "forms", "inputs",
                                          "html_lang", "title"], extrasaction="ignore")
        w.writeheader()
        for url in sorted(crawled_urls):
            d = crawled[url]
            w.writerow({"url": url, "post_type": d["post_type"], **d["stats"]})

    counts = {"requests": crawler.request_count,
          "bytes": crawler.bytes_downloaded,
          "errors": len(crawler.errors),
          "crawled": len(crawled_urls),
          "templates": len(rows)}

    n_main = len(main_urls)
    est = write_machine_estimate(INVENTORY_DIR / "machine-time-estimate.md", counts, elapsed,
                                 n_main, len(all_urls), len(pdfs), len(media))

    print("\n=== INVENTORY SUMMARY ===")
    print(f"URL unik di sitemap   : {len(all_urls)}")
    print(f"URL di-crawl          : {len(crawled_urls)}")
    print(f"Halaman utama (page)  : {n_main}")
    print(f"Template (post type)  : {len(rows)}")
    print(f"PDF                   : {len(pdfs)} (dari WP API: {len(wp_pdfs)})")
    print(f"  - status 200        : {sum(1 for p in pdfs if str(p.get('status')) == '200')}")
    print(f"  - status 403        : {sum(1 for p in pdfs if str(p.get('status')) == '403')}")
    print(f"Media/embed           : {len(media)}")
    print(f"Request HTTP          : {crawler.request_count} ({crawler.bytes_downloaded/1024/1024:.1f} MB)")
    print(f"Error                 : {len(crawler.errors)}")
    print(f"Durasi crawl          : {est['fmt'](elapsed)}")
    print(f"Estimasi mesin skenario A (halaman utama): {est['fmt'](est['main'])}")
    print(f"Estimasi mesin skenario B (full site)   : {est['fmt'](est['full'])}")
    print(f"\n[OK] Output di {INVENTORY_DIR}")

    sys.stdout = sys.__stdout__
    log_fh.close()


if __name__ == "__main__":
    main()