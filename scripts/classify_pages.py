#!/usr/bin/env python3
"""
classify_pages.py - Klasifikasikan isi halaman publication (artikel asli vs wrapper).

Untuk menjawab pertanyaan "apakah 689 halaman selain 49 halaman utama itu lampiran/iframe?":
mengukur panjang teks, jumlah paragraf, dan jumlah embed di tiap halaman.

Output: results/automated/page-classification-YYYYMMDD/
  - pages.csv        (url, kata, paragraf, iframe, pdfemb, video, kelas)
  - summary.md       (agregat + distribusi + contoh per kelas)

Read-only GET, jeda >= 1 detik. Idempotent: cache per URL di
inventory/.cache/classify-<sha1>.json.

Usage:
    python scripts/classify_pages.py
    python scripts/classify_pages.py --urls-file inventory/urls-all.txt --delay 1.5
"""

import argparse
import csv
import hashlib
import json
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).parent.parent
CACHE_DIR = PROJECT_ROOT / "inventory" / ".cache"
OUTPUT_ROOT = PROJECT_ROOT / "results" / "automated"
DEFAULT_URLS = PROJECT_ROOT / "inventory" / "urls-all.txt"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

ARTICLE_MIN_WORDS = 250
THIN_MAX_WORDS = 150


def cache_path(url):
    return CACHE_DIR / f"classify-{hashlib.sha1(url.encode('utf-8')).hexdigest()}.json"


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


def measure(soup):
    """Panjang teks isi, paragraf, embed. Header/footer/nav dibuang."""
    clone_soup = BeautifulSoup(str(soup), "html.parser")
    for tag in clone_soup(["script", "style", "nav", "header", "footer", "noscript",
                           "form", "svg"]):
        tag.decompose()

    text = " ".join(clone_soup.get_text(" ", strip=True).split())
    words = len(text.split())
    paragraphs = len([p for p in clone_soup.find_all("p") if len(p.get_text(strip=True)) > 40])
    headings = len(clone_soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]))

    iframes = soup.find_all("iframe")
    pdfemb = len([i for i in iframes if "pdfemb" in (i.get("src") or "")])
    video = len([i for i in iframes
                 if re.search(r"youtube|youtu\.be|vimeo", i.get("src") or "", re.I)])
    flipsnack = len([i for i in iframes if "flipsnack" in (i.get("src") or "")])
    maps = len([i for i in iframes if "google" in (i.get("src") or "") and "map" in (i.get("src") or "")])
    other_iframe = len(iframes) - pdfemb - video - flipsnack - maps

    pdf_links = len([a for a in soup.find_all("a", href=True)
                     if ".pdf" in (a["href"] or "").lower()])
    outbound = len([a for a in soup.find_all("a", href=True)
                    if urlparse_host(a["href"]) not in (None, "www.inovasi.or.id", "inovasi.or.id")])

    return {
        "words": words, "paragraphs": paragraphs, "headings": headings,
        "iframes": len(iframes), "pdfemb": pdfemb, "video": video,
        "flipsnack": flipsnack, "maps": maps, "other_iframe": other_iframe,
        "pdf_links": pdf_links, "outbound_links": outbound,
    }


def urlparse_host(href):
    if not href:
        return None
    if href.startswith("//"):
        return href[2:].split("/")[0]
    if not href.startswith("http"):
        return None
    return href.split("//", 1)[1].split("/")[0]


def classify(m):
    has_embed = (m["iframes"] > 0) or (m["pdf_links"] > 0)
    if m["words"] >= ARTICLE_MIN_WORDS:
        return "artikel-asli"
    if m["words"] <= THIN_MAX_WORDS and has_embed:
        return "wrapper-embed"
    if m["words"] <= THIN_MAX_WORDS:
        return "tipis-teks"
    return "menengah"


def main():
    ap = argparse.ArgumentParser(description="Klasifikasi isi halaman publication")
    ap.add_argument("--urls-file", default=str(DEFAULT_URLS))
    ap.add_argument("--delay", type=float, default=1.5)
    ap.add_argument("--filter", default="/publication/",
                    help="hanya URL yang mengandung pola ini (kosongkan untuk semua)")
    args = ap.parse_args()

    urls = [line.strip() for line in Path(args.urls_file).read_text(encoding="utf-8").splitlines()
            if line.strip()]
    if args.filter:
        urls = [u for u in urls if args.filter in u]

    date_str = datetime.now().strftime("%Y%m%d")
    out_dir = OUTPUT_ROOT / f"page-classification-{date_str}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[CLASSIFY] {len(urls)} URL dengan pola '{args.filter}'")
    print(f"[CLASSIFY] output: {out_dir}\n")

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept-Language": "id-ID,id;q=0.9"})

    rows = []
    cache_hits = 0
    failed = 0
    start = time.time()

    for i, url in enumerate(urls, 1):
        cached = load_cached(url)
        if cached:
            cache_hits += 1
        else:
            time.sleep(args.delay)
            try:
                resp = session.get(url, timeout=40)
                if resp.status_code != 200:
                    failed += 1
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")
                m = measure(soup)
                m["url"] = url
                m["slug"] = url.rstrip("/").rsplit("/", 1)[-1]
                m["kelas"] = classify(m)
                m["fetched_at"] = datetime.now().isoformat(timespec="seconds")
                save_cached(url, m)
                cached = m
            except requests.RequestException as e:
                failed += 1
                print(f"  [ERR] {url} {e}", file=sys.stderr)
                continue

        rows.append(cached)
        if i % 25 == 0 or i == len(urls):
            mins = (time.time() - start) / 60
            rate = (time.time() - start) / max(i, 1)
            eta = (len(urls) - i) * rate / 60
            print(f"[CLASSIFY] {i}/{len(urls)} | {mins:.1f} mnt | ETA {eta:.1f} mnt | "
                  f"cache {cache_hits} | gagal {failed}")

    rows.sort(key=lambda r: r["words"])

    fields = ["url", "slug", "kelas", "words", "paragraphs", "headings", "iframes",
              "pdfemb", "video", "flipsnack", "maps", "other_iframe",
              "pdf_links", "outbound_links", "fetched_at"]
    with open(out_dir / "pages.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    counts = Counter(r["kelas"] for r in rows)
    total = len(rows) or 1
    by_class = defaultdict(list)
    for r in rows:
        by_class[r["kelas"]].append(r)

    lines = [
        "# Klasifikasi Isi Halaman Publication",
        "",
        f"Dihasilkan: {datetime.now().isoformat(timespec='seconds')}  ",
        f"URL diperiksa: {len(rows)} (dari {len(urls)} pola `{args.filter}`)  ",
        f"Durasi: {(time.time() - start) / 60:.1f} menit | cache hit: {cache_hits} | gagal: {failed}",
        "",
        "## Metode",
        "",
        "Header, footer, nav, script, style, dan form dibuang sebelum menghitung teks. "
        f"ambang: artikel asli >= {ARTICLE_MIN_WORDS} kata; tipis <= {THIN_MAX_WORDS} kata.",
        "",
        "## Ringkasan",
        "",
        "| Kelas | Halaman | % | Rata-rata kata | Median kata |",
    ]
    for klass in ("artikel-asli", "menengah", "tipis-teks", "wrapper-embed"):
        sub = by_class.get(klass, [])
        if not sub:
            continue
        words = [r["words"] for r in sub]
        lines.append(f"| {klass} | {len(sub)} | {len(sub) / total * 100:.0f}% | "
                     f"{statistics.mean(words):.0f} | {statistics.median(words):.0f} |")

    lines += ["", "## Rincian per kelas", ""]
    for klass in ("artikel-asli", "menengah", "tipis-teks", "wrapper-embed"):
        sub = by_class.get(klass, [])
        if not sub:
            continue
        words = [r["words"] for r in sub]
        lines += [
            f"### {klass} ({len(sub)} halaman)",
            "",
            f"- Kata: min {min(words)}, median {statistics.median(words):.0f}, "
            f"rata-rata {statistics.mean(words):.0f}, max {max(words)}",
            f"- Punya iframe: {sum(1 for r in sub if r['iframes'] > 0)}"
            f" | punya link PDF: {sum(1 for r in sub if r['pdf_links'] > 0)}",
            f"- Embed video: {sum(1 for r in sub if r['video'] > 0)}"
            f" | Flipsnack: {sum(1 for r in sub if r['flipsnack'] > 0)}"
            f" | PDF Embed: {sum(1 for r in sub if r['pdfemb'] > 0)}",
            "",
            "| Kata | Paragraf | Embed | Slug |",
            "|------|-----------|-------|------|",
        ]
        for r in (sub[:8] if klass == "artikel-asli" else sub[:12]):
            embed = []
            if r["video"]:
                embed.append(f"video {r['video']}")
            if r["flipsnack"]:
                embed.append(f"flipsnack {r['flipsnack']}")
            if r["pdfemb"]:
                embed.append(f"pdfemb {r['pdfemb']}")
            if r["maps"]:
                embed.append("maps")
            if r["pdf_links"]:
                embed.append(f"pdf-link {r['pdf_links']}")
            lines.append(f"| {r['words']} | {r['paragraphs']} | {', '.join(embed) or '-'} "
                         f"| `{r['slug'][:58]}` |")
        lines.append("")

    wrapper = by_class.get("wrapper-embed", [])
    if wrapper:
        lines += ["## Implikasi sampling audit", "",
                  f"{len(wrapper)} halaman publication tidak punya teks artikel - isinya hanya embed. "
                  "Untuk halaman seperti ini, temuan yang muncul berasal dari media (caption, "
                  "iframe title, PDF), bukan dari template halaman. Sampling audit sebaiknya "
                  "stratifik:", "",
                  "| Kelompok | Sampel yang disarankan | Alasan |",
                  "|----------|------------------------|--------|",
                  f"| artikel-asli | 10 | Butuh cek heading, link text, tabel |",
                  f"| wrapper-embed | 5 | Semua temuan datang dari media yang di-embed |",
                  f"| tipis-teks | 3 | Kombinasi: teks pendek + mungkin media |",
                  ""]

    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n[CLASSIFY] total {len(rows)}")
    for klass, n in counts.most_common():
        print(f"  {klass}: {n} ({n / total * 100:.0f}%)")
    print(f"[CLASSIFY] output: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())