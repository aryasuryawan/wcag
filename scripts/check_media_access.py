#!/usr/bin/env python3
"""
check_media_access.py - Verifikasi apakah PDF dan video bisa diakses / diunduh / dibuka.

Read-only GET/HEAD, jeda >= 1 detik. Tidakjudgment soal isi, caption, atau struktur dokumen.

Output: results/automated/media-access-YYYYMMDD/
  - pdf-access.csv   (url, status, content_type, size, accessible, metode, catatan)
  - video-access.csv (url, video_id, oembed_status, accessible, judul, iframe_title)
  - summary.json

Usage:
    python scripts/check_media_access.py
    python scripts/check_media_access.py --delay 2
    python scripts/check_media_access.py --no-cache
"""

import argparse
import csv
import hashlib
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

PROJECT_ROOT = Path(__file__).parent.parent
INVENTORY_DIR = PROJECT_ROOT / "inventory"
CACHE_DIR = INVENTORY_DIR / ".cache"
OUTPUT_ROOT = PROJECT_ROOT / "results" / "automated"
USER_AGENT = "WebQA-AccessibilityBot/1.0 (+audit aksesibilitas; hanya GET/HEAD)"
REQUEST_DELAY = 1.5
TIMEOUT = 30

PDFS_CSV = INVENTORY_DIR / "pdfs.csv"
MEDIA_CSV = INVENTORY_DIR / "media.csv"

YT_ID_RE = re.compile(r"(?:embed/|v=|youtu\.be/|/shorts/)([A-Za-z0-9_-]{11})")


def cache_get(key, url):
    p = CACHE_DIR / f"access-{key}-{hashlib.sha1(url.encode('utf-8')).hexdigest()}.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            return None
    return None


def cache_put(key, url, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p = CACHE_DIR / f"access-{key}-{hashlib.sha1(url.encode('utf-8')).hexdigest()}.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class Fetcher:
    def __init__(self, delay):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.last = 0.0
        self.requests = 0
        self.errors = []

    def _wait(self):
        gap = time.time() - self.last
        if gap < self.delay:
            time.sleep(self.delay - gap)

    def head(self, url):
        self._wait()
        self.last = time.time()
        self.requests += 1
        try:
            r = self.session.head(url, timeout=TIMEOUT, allow_redirects=True)
            return {"status": r.status_code, "content_type": r.headers.get("Content-Type", ""),
                    "size_bytes": int(r.headers.get("Content-Length") or 0)}
        except requests.RequestException as e:
            self.errors.append((url, str(e)))
            return {"status": 0, "content_type": "", "size_bytes": 0, "error": str(e)}

    def get_json(self, url):
        self._wait()
        self.last = time.time()
        self.requests += 1
        try:
            r = self.session.get(url, timeout=TIMEOUT, allow_redirects=True)
            body = None
            if r.status_code == 200:
                try:
                    body = r.json()
                except ValueError:
                    body = None
            return {"status": r.status_code, "json": body}
        except requests.RequestException as e:
            self.errors.append((url, str(e)))
            return {"status": 0, "json": None, "error": str(e)}


def check_pdf(fetcher, url, use_cache):
    cached = cache_get("pdf", url) if use_cache else None
    if cached:
        cached["method"] = "HEAD"
        return cached

    res = fetcher.head(url)
    res["method"] = "HEAD"
    if res["status"] not in (200, 206) or "pdf" not in res["content_type"].lower():
        res["fallback_status"] = res["status"]
        fb = fetcher.head(url + ("&" if "?" in url else "?") + "download=1")
        res["status_fallback"] = fb["status"]
        res["content_type_fallback"] = fb["content_type"]
    cache_put("pdf", url, res)
    return res


def video_id_from(url):
    m = YT_ID_RE.search(url)
    if m:
        return m.group(1)
    qs = parse_qs(urlparse(url).query)
    if "v" in qs and qs["v"]:
        return qs["v"][0]
    return None


def probe_video(fetcher, vid, use_cache):
    key_url = f"https://www.youtube.com/watch?v={vid}"
    cached = cache_get("yt", key_url) if use_cache else None
    if cached:
        return cached
    res = fetcher.get_json(f"https://www.youtube.com/oembed?url={key_url}&format=json")
    out = {
        "oembed_status": res["status"],
        "accessible": res["status"] == 200 and bool(res.get("json")),
        "title": (res.get("json") or {}).get("title", ""),
    }
    if not out["accessible"]:
        out["error"] = {401: "private / butuh login", 403: "diblokir /_age-restricted",
                        404: "tidak ada / sudah dihapus"}.get(res["status"], f"status {res['status']}")
    cache_put("yt", key_url, out)
    return out


def main():
    ap = argparse.ArgumentParser(description="Verifikasi akses PDF dan video")
    ap.add_argument("--delay", type=float, default=REQUEST_DELAY)
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args()

    if not PDFS_CSV.exists() or not MEDIA_CSV.exists():
        print("[ERROR] Jalankan crawl_inventory.py lebih dulu.", file=sys.stderr)
        sys.exit(1)

    date_str = datetime.now().strftime("%Y%m%d")
    out_dir = OUTPUT_ROOT / f"media-access-{date_str}"
    out_dir.mkdir(parents=True, exist_ok=True)

    fetcher = Fetcher(args.delay)
    start = time.time()

    pdf_rows = list(csv.DictReader(open(PDFS_CSV, encoding="utf-8")))
    media_rows = list(csv.DictReader(open(MEDIA_CSV, encoding="utf-8")))
    video_rows = [m for m in media_rows if m["platform"] == "embed-video"]
    other_rows = [m for m in media_rows if m["platform"] not in ("embed-video", "link-out")]
    linkout_rows = [m for m in media_rows if m["platform"] == "link-out"]

    print(f"[INFO] PDF: {len(pdf_rows)} | embed video: {len(video_rows)} | "
          f"iframe lain: {len(other_rows)} | link-out: {len(linkout_rows)}")
    print(f"[INFO] Output: {out_dir}\n")

    pdf_out = []
    for i, row in enumerate(pdf_rows, 1):
        res = check_pdf(fetcher, row["url"], use_cache=not args.no_cache)
        status = res.get("status")
        fb = res.get("status_fallback")
        accessible = status in (200, 206)
        note = ""
        if not accessible:
            if res.get("fallback_status") == 403:
                note = "403 + query download=1 juga 403 (hotlink protection)"
            elif fb and fb != 403:
                note = f"fallback ?download=1 -> {fb}"
            else:
                note = f"status {status}"
        pdf_out.append({
            "url": row["url"],
            "title": row.get("title", ""),
            "status": status,
            "content_type": res.get("content_type", ""),
            "size_bytes": res.get("size_bytes", 0) or row.get("size_bytes", ""),
            "fallback_status": fb if fb is not None else "",
            "accessible": "Y" if accessible else "N",
            "source_page": row.get("source_page", ""),
            "note": note,
        })
        flag = "OK " if accessible else "FAIL"
        print(f"[{i}/{len(pdf_rows)}] {flag} {status} {row['url'].rsplit('/', 1)[-1][:70]}")

    with open(out_dir / "pdf-access.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "title", "status", "content_type", "size_bytes",
                                          "fallback_status", "accessible", "source_page", "note"])
        w.writeheader()
        w.writerows(pdf_out)

    video_out = []
    for i, row in enumerate(video_rows, 1):
        vid = video_id_from(row["url"])
        res = probe_video(fetcher, vid, use_cache=not args.no_cache) if vid else {
            "oembed_status": 0, "accessible": False, "title": "", "error": "ID tidak terbaca"}
        video_out.append({
            "url": row["url"],
            "video_id": vid or "",
            "oembed_status": res["oembed_status"],
            "accessible": "Y" if res["accessible"] else "N",
            "title": res.get("title", ""),
            "iframe_title": row.get("frame_title", ""),
            "iframe_title_present": "Y" if (row.get("frame_title") or "").strip() else "N",
            "source_page": row.get("source_page", ""),
            "note": res.get("error", ""),
        })
        flag = "OK " if res["accessible"] else "FAIL"
        print(f"[{i}/{len(video_rows)}] {flag} {res['oembed_status']} "
              f"{row.get('frame_title') or row['url'][:60]}")

    with open(out_dir / "video-access.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "video_id", "oembed_status", "accessible", "title",
                                          "iframe_title", "iframe_title_present", "source_page", "note"])
        w.writeheader()
        w.writerows(video_out)

    pdf_ok = sum(1 for r in pdf_out if r["accessible"] == "Y")
    vid_ok = sum(1 for r in video_out if r["accessible"] == "Y")
    vid_no_title = sum(1 for r in video_out if r["iframe_title_present"] == "N")

    summary = {
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "scope": "verifikasi akses saja (bukan caption/strultur/tag)",
        "pdf_total": len(pdf_out),
        "pdf_accessible": pdf_ok,
        "pdf_blocked": len(pdf_out) - pdf_ok,
        "pdf_blocked_status": {},
        "video_total": len(video_out),
        "video_accessible": vid_ok,
        "video_blocked": len(video_out) - vid_ok,
        "video_iframe_no_title": vid_no_title,
        "iframe_lain_total": len(other_rows),
        "iframe_lain_tanpa_title": sum(1 for r in other_rows if not (r.get("frame_title") or "").strip()),
        "link_out_bukan_embed": len(linkout_rows),
        "http_requests": fetcher.requests,
        "errors": len(fetcher.errors),
        "elapsed_sec": round(time.time() - start, 1),
    }
    for r in pdf_out:
        if r["accessible"] == "N":
            key = str(r["status"])
            summary["pdf_blocked_status"][key] = summary["pdf_blocked_status"].get(key, 0) + 1

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                                           encoding="utf-8")

    print("\n=== RINGKASAN AKSES MEDIA ===")
    print(f"PDF  : {pdf_ok}/{len(pdf_out)} bisa diakses | "
          f"{len(pdf_out) - pdf_ok} diblokir {summary['pdf_blocked_status']}")
    print(f"Video: {vid_ok}/{len(video_out)} embed bisa diakses | "
          f"{len(video_out) - vid_ok} diblokir | iframe video tanpa title: {vid_no_title}")
    print(f"Iframe lain (Maps/PDF Embed): {summary['iframe_lain_total']} | "
          f"tanpa title: {summary['iframe_lain_tanpa_title']}")
    print(f"Link ke kanal YouTube (bukan embed): {len(linkout_rows)} - di luar scope embed")
    print(f"Request: {fetcher.requests} | error: {len(fetcher.errors)} | "
          f"durasi: {summary['elapsed_sec'] / 60:.1f} mnt")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()