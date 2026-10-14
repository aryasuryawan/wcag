#!/usr/bin/env python3
"""
check_pdfs.py - Cek dasar aksesibilitas PDF: tagged, bahasa, judul metadata, layer teks.

Input : inventory/pdfs.csv (kolom `status` dipakai untuk skip PDF yang 403)
Output: results/automated/pdf-check-YYYYMMDD/
  - pdf-check-results.json   (hasil lengkap per PDF)
  - pdf-check-summary.csv    (tabel ringkas)
  - summary.md               (agregat + daftar PDF gagal)

Catatan batasan: script ini mendeteksi struktur dasar (tagged, bahasa, judul,
layer teks, bookmark). Pemeriksaan lengkap PDF/UA (alt text gambar, heading
hierarchy, reading order, tab order) perlu tools seperti veraPDF atau PAC 2024
yang tidak dipasang di repo ini.

Idempotent: hasil per URL di-cache di inventory/.cache/pdfcheck-*.json sehingga
run ulang tidak mengunduh PDF yang sama lagi.

Usage:
    python scripts/check_pdfs.py
    python scripts/check_pdfs.py --pdfs-file inventory/pdfs.csv --no-cache
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

import requests
import pymupdf

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_PDFS_FILE = PROJECT_ROOT / "inventory" / "pdfs.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "automated"
CACHE_DIR = PROJECT_ROOT / "inventory" / ".cache"

REQUEST_DELAY = 1.5
USER_AGENT = "WebQA-AccessibilityBot/1.0 (+audit aksesibilitas; hanya GET/HEAD)"
TIMEOUT = 90
MAX_PDF_SIZE = 60 * 1024 * 1024
TEXT_PAGES_TO_SAMPLE = 3
STRUCT_PAGES_TO_SAMPLE = 10


def cache_path(url):
    return CACHE_DIR / f"pdfcheck-{hashlib.sha1(url.encode('utf-8')).hexdigest()}.json"


def load_cache(url):
    p = cache_path(url)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            return None
    return None


def save_cache(url, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path(url).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def detect_tagged(doc):
    """PyMuPDF 1.28 tidak punya doc.is_tagged; baca MarkInfo + StructTreeRoot dari catalog."""
    evidence = []
    try:
        catalog = doc.pdf_catalog()
        kind, value = doc.xref_get_key(catalog, "MarkInfo")
        if kind != "null" and value and "/Marked true" in value.replace(" ", " "):
            evidence.append(f"MarkInfo {value.strip()}")
        elif kind != "null" and value and "true" in value.lower():
            evidence.append(f"MarkInfo {value.strip()}")
        skind, sval = doc.xref_get_key(catalog, "StructTreeRoot")
        if skind != "null" and sval:
            evidence.append(f"StructTreeRoot {sval.strip()}")
    except Exception:
        pass
    try:
        xmp = doc.get_xml_metadata() or ""
        if "pdfuaid:part" in xmp:
            m = re.search(r"pdfuaid:part[^>]*>([^<]+)<", xmp)
            evidence.append(f"XMP pdfuaid:part={m.group(1) if m else 'ada'}")
    except Exception:
        pass
    return (len(evidence) > 0), "; ".join(evidence)


def detect_language(doc):
    try:
        cat = doc.pdf_catalog()
        kind, value = doc.xref_get_key(cat, "Lang")
        if kind != "null" and value:
            lang = value.strip().strip("()")
            if lang:
                return lang, "catalog /Lang"
    except Exception:
        pass
    try:
        if doc.language:
            return doc.language, "document info"
    except Exception:
        pass
    try:
        xmp = doc.get_xml_metadata() or ""
        m = re.search(r"dc:language[^>]*>\s*<rdf:li[^>]*>([^<]+)<", xmp)
        if m:
            return m.group(1).strip(), "XMP dc:language"
    except Exception:
        pass
    return None, None


def analyze_pdf(path):
    result = {
        "pages": None, "is_tagged": False, "tag_evidence": "", "language": None,
        "language_source": None, "title_metadata": None, "author": None,
        "creator": None, "producer": None, "has_bookmarks": False, "bookmarks_count": 0,
        "images_count": 0, "text_chars_sampled": 0, "text_layer": "unknown",
        "has_forms": False, "errors": [],
    }

    try:
        doc = pymupdf.open(path)
    except Exception as e:
        result["errors"].append(f"gagal dibuka: {e}")
        return result

    try:
        result["pages"] = doc.page_count

        tagged, evidence = detect_tagged(doc)
        result["is_tagged"] = tagged
        result["tag_evidence"] = evidence

        lang, lang_src = detect_language(doc)
        result["language"] = lang
        result["language_source"] = lang_src

        meta = doc.metadata or {}
        result["title_metadata"] = (meta.get("title") or "").strip() or None
        result["author"] = (meta.get("author") or "").strip() or None
        result["creator"] = (meta.get("creator") or "").strip() or None
        result["producer"] = (meta.get("producer") or "").strip() or None

        toc = doc.get_toc()
        result["has_bookmarks"] = bool(toc)
        result["bookmarks_count"] = len(toc)

        result["has_forms"] = bool(doc.is_form_pdf)

        pages_to_sample = min(doc.page_count, TEXT_PAGES_TO_SAMPLE)
        chars = 0
        for i in range(pages_to_sample):
            chars += len((doc[i].get_text() or "").strip())
        result["text_chars_sampled"] = chars

        for i in range(min(doc.page_count, STRUCT_PAGES_TO_SAMPLE)):
            result["images_count"] += len(doc[i].get_images())

        if pages_to_sample == 0:
            result["text_layer"] = "no-pages"
        elif chars == 0:
            result["text_layer"] = "image-only"
        elif chars < 100 * pages_to_sample:
            result["text_layer"] = "sparse"
        else:
            result["text_layer"] = "ok"

    except Exception as e:
        result["errors"].append(f"analisis gagal: {e}")
    finally:
        doc.close()

    return result


def download(session, url, temp_dir, index):
    time.sleep(REQUEST_DELAY)
    try:
        resp = session.get(url, timeout=TIMEOUT, stream=True, allow_redirects=True)
    except requests.RequestException as e:
        return None, f"request gagal: {e}"
    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code}"
    ctype = (resp.headers.get("Content-Type") or "").lower()
    if "pdf" not in ctype:
        return None, f"bukan PDF (Content-Type: {ctype or 'kosong'})"
    path = temp_dir / f"dl_{index:04d}.pdf"
    size = 0
    with open(path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=16384):
            size += len(chunk)
            if size > MAX_PDF_SIZE:
                f.close()
                path.unlink(missing_ok=True)
                return None, f"ukuran melebihi {MAX_PDF_SIZE // (1024*1024)} MB"
            f.write(chunk)
    return path, None


def main():
    ap = argparse.ArgumentParser(description="Cek dasar aksesibilitas PDF")
    ap.add_argument("--pdfs-file", default=str(DEFAULT_PDFS_FILE))
    ap.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="batasi jumlah PDF (0 = semua)")
    args = ap.parse_args()

    pdfs_file = Path(args.pdfs_file)
    if not pdfs_file.exists():
        print("[ERROR] pdfs.csv tidak ada. Jalankan crawl_inventory.py dulu.", file=sys.stderr)
        return 1

    date_str = datetime.now().strftime("%Y%m%d")
    scan_dir = Path(args.output_dir) / f"pdf-check-{date_str}"
    scan_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = scan_dir / "temp"
    temp_dir.mkdir(exist_ok=True)

    rows = list(csv.DictReader(open(pdfs_file, encoding="utf-8")))
    if args.limit:
        rows = rows[:args.limit]

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    print(f"[PDF] {len(rows)} PDF dari {pdfs_file.name}")
    print(f"[PDF] output: {scan_dir}")

    results = []
    stats = {"diperiksa": 0, "cache": 0, "tidak_bisa_diakses": 0, "gagal_unduh": 0,
             "tagged": 0, "punya_bahasa": 0, "punya_judul": 0, "image_only": 0}
    start = time.time()

    for i, row in enumerate(rows, 1):
        url = (row.get("url") or "").strip()
        if not url:
            continue
        status_known = (row.get("status") or "").strip()
        title = (row.get("title") or "").strip()

        cached = None if args.no_cache else load_cache(url)
        if cached:
            stats["cache"] += 1
            cached.update({"url": url, "title": title})
            results.append(cached)
            continue

        if status_known and status_known != "200":
            rec = {"url": url, "title": title, "error": f"HTTP {status_known} (diblokir server)",
                   "checked_at": datetime.now().isoformat(timespec="seconds")}
            save_cache(url, rec)
            stats["tidak_bisa_diakses"] += 1
            results.append(rec)
            print(f"[{i}/{len(rows)}] SKIP {status_known} {url.rsplit('/', 1)[-1][:60]}")
            continue

        path, err = download(session, url, temp_dir, i)
        if path is None:
            rec = {"url": url, "title": title, "error": err,
                   "checked_at": datetime.now().isoformat(timespec="seconds")}
            save_cache(url, rec)
            stats["gagal_unduh"] += 1
            results.append(rec)
            print(f"[{i}/{len(rows)}] GAGAL {err} {url.rsplit('/', 1)[-1][:50]}")
            continue

        size_bytes = path.stat().st_size
        res = analyze_pdf(path)
        res.update({"url": url, "title": title, "size_bytes": size_bytes,
                    "source_page": row.get("source_page", ""),
                    "checked_at": datetime.now().isoformat(timespec="seconds")})
        path.unlink(missing_ok=True)

        save_cache(url, res)
        results.append(res)
        stats["diperiksa"] += 1
        if res.get("is_tagged"):
            stats["tagged"] += 1
        if res.get("language"):
            stats["punya_bahasa"] += 1
        if res.get("title_metadata"):
            stats["punya_judul"] += 1
        if res.get("text_layer") == "image-only":
            stats["image_only"] += 1

        print(f"[{i}/{len(rows)}] {res.get('pages')}p | tagged={res.get('is_tagged')} "
              f"| lang={res.get('language') or '-'} | title={'ada' if res.get('title_metadata') else 'TIDAK'} "
              f"| teks={res.get('text_layer')}")

    (scan_dir / "pdf-check-results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    fields = ["url", "title", "pages", "is_tagged", "tag_evidence", "language", "language_source",
              "title_metadata", "author", "creator", "producer", "has_bookmarks",
              "bookmarks_count", "images_count", "text_layer", "text_chars_sampled",
              "has_forms", "size_bytes", "source_page", "error", "checked_at"]
    with open(scan_dir / "pdf-check-summary.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in results:
            w.writerow({k: r.get(k, "") for k in fields})

    checked = [r for r in results if r.get("pages")]
    n = len(checked) or 1

    lines = [
        "# Cek Aksesibilitas Dasar PDF",
        "",
        f"Dihasilkan: {datetime.now().isoformat(timespec='seconds')}  ",
        f"Durasi: {(time.time() - start) / 60:.1f} menit",
        "",
        "## Ringkasan",
        "",
        "| Aspek | Hasil |",
        "|-------|-------|",
        f"| PDF terdaftar | {len(rows)} |",
        f"| Tidak bisa diakses (403) | {stats['tidak_bisa_diakses']} |",
        f"| Gagal diunduh | {stats['gagal_unduh']} |",
        f"| Berhasil diperiksa | {stats['diperiksa']} (dari cache: {stats['cache']}) |",
        f"| Tagged (ada MarkInfo/StructTreeRoot) | {stats['tagged']}/{len(checked)} |",
        f"| Punya bahasa (/Lang atau dc:language) | {stats['punya_bahasa']}/{len(checked)} |",
        f"| Punya judul metadata | {stats['punya_judul']}/{len(checked)} |",
        f"| Tanpa layer teks (hasil scan) | {stats['image_only']}/{len(checked)} |",
        "",
        "## Yang Dipakai sebagai Patokan",
        "",
        "- Tagged: `/MarkInfo <</Marked true>>` atau `/StructTreeRoot` ada di catalog PDF. "
        "Ini prasyarat PDF/UA; tanpa itu, screen reader hanya membaca urutan visual.",
        "- Bahasa: entri `/Lang` di catalog, fallback ke metadata dokumen, lalu XMP `dc:language`.",
        "- Judul: metadata `/Title`. Layar baca file sering membacakan nama file kalau judul kosong.",
        "- Layer teks: 3 halaman pertama. PDF hasil scan tanpa OCR punya 0 karakter - "
        "tidak bisa dibaca screen reader sama sekali (SC 1.1.1).",
        "",
        "## Yang BELUM Diperiksa",
        "",
        "- Alt text gambar di dalam PDF (butuh parser struktur tag, mis. veraPDF/PAC).",
        "- Heading hierarchy dan reading order (butuh tools PDF/UA penuh).",
        "- Tab order form, kontras teks, dan ukuran font.",
        "- Isi bahasa dokumen (apakah teksnya Bahasa Indonesia yang benar).",
        f"- {stats['tidak_bisa_diakses']} PDF yang membalas 403 tidak bisa diperiksa tanpa "
        "akses ke direktori `securepdfs`.",
        "",
    ]
    (scan_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    try:
        temp_dir.rmdir()
    except OSError:
        pass

    print(f"\n[PDF] diperiksa {stats['diperiksa']} | 403 {stats['tidak_bisa_diakses']} | "
          f"gagal {stats['gagal_unduh']} | cache {stats['cache']}")
    if checked:
        print(f"[PDF] tagged {stats['tagged']}/{len(checked)} | "
              f"bahasa {stats['punya_bahasa']}/{len(checked)} | "
              f"judul {stats['punya_judul']}/{len(checked)} | "
              f"tanpa layer teks {stats['image_only']}/{len(checked)}")
    print(f"[PDF] output: {scan_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())