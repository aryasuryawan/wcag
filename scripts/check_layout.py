#!/usr/bin/env python3
"""
check_layout.py - Ukur reflow 320px, zoom 200%, skip link, dan target size.

Bagian Tahap 3 yang bisa dikerjakan mesin (tidak butuh NVDA/VoiceOver).
Runner Node scripts/layout_check.js memakai satu Chrome untuk semua URL.

Output: results/automated/layout-check-YYYYMMDD/
  - layout.json per URL (mentah)
  - layout-summary.csv
  - summary.md

SC yang diperiksa:
  1.4.10 Reflow          -> scrollWidth > viewport di 320px
  1.4.4  Resize Text     -> scrollWidth > viewport di 640px (setara zoom 200% dari 1280px)
  2.4.1  Bypass Blocks   -> link skip ke anchor yang benar-benar ada
  2.5.8  Target Size     -> elemen interaktif < 24x24 CSS px (khusus WCAG 2.2)
  2.4.3  Focus Order     -> hitungan tabindex positif

Usage:
    python scripts/check_layout.py
    python scripts/check_layout.py --urls-file inventory/urls-utama.txt --concurrency 3
"""

import argparse
import csv
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
AUTOMATED = PROJECT_ROOT / "results" / "automated"
RUNNER = PROJECT_ROOT / "scripts" / "layout_check.js"
DEFAULT_URLS = PROJECT_ROOT / "inventory" / "urls-utama.txt"


def main():
    ap = argparse.ArgumentParser(description="Cek reflow, zoom, skip link, target size")
    ap.add_argument("--urls-file", default=str(DEFAULT_URLS))
    ap.add_argument("--output-dir", default=str(AUTOMATED))
    ap.add_argument("--concurrency", type=int, default=3)
    args = ap.parse_args()

    urls_file = Path(args.urls_file)
    if not urls_file.exists():
        print(f"[ERROR] {urls_file} tidak ada. Jalankan crawl_inventory.py dulu.", file=sys.stderr)
        return 1
    if not RUNNER.exists():
        print("[ERROR] scripts/layout_check.js hilang", file=sys.stderr)
        return 1

    date_str = datetime.now().strftime("%Y%m%d")
    out_dir = Path(args.output_dir) / f"layout-check-{date_str}"
    out_dir.mkdir(parents=True, exist_ok=True)

    n_urls = sum(1 for line in urls_file.read_text(encoding="utf-8").splitlines()
                 if line.strip() and not line.startswith("#"))
    print(f"[LAYOUT] {n_urls} URL | concurrency {args.concurrency}")
    print(f"[LAYOUT] output: {out_dir}\n")

    proc = subprocess.run(
        ["node", str(RUNNER), str(urls_file), str(out_dir), str(args.concurrency)],
        cwd=PROJECT_ROOT, text=True, encoding="utf-8", errors="replace",
        capture_output=True)
    sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        print(f"[ERROR] runner exit {proc.returncode}", file=sys.stderr)
        return proc.returncode

    known = set()
    urls_all = PROJECT_ROOT / "inventory" / "urls-all.txt"
    if urls_all.exists():
        known = {line.strip().rstrip("/") for line in
                 urls_all.read_text(encoding="utf-8").splitlines() if line.strip()}

    rows = []
    seen = set()
    for f in sorted(out_dir.glob("*.json")):
        if f.name.endswith(".error.json"):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        url = (d.get("url") or "").rstrip("/")
        if url in seen or (known and url not in known):
            continue
        seen.add(url)
        d1280 = d.get("desktop1280", {})
        d320 = d.get("narrow320", {})
        d640 = d.get("zoom200_640", {})
        rows.append({
            "url": url,
            "scrollWidth_1280": d1280.get("scrollWidth"),
            "scrollWidth_320": d320.get("scrollWidth"),
            "scrollWidth_640": d640.get("scrollWidth"),
            "reflow_320_gagal": "Y" if d320.get("horizontalScroll") else "N",
            "zoom200_gagal": "Y" if d640.get("horizontalScroll") else "N",
            "scroll_horizontal_1280": "Y" if d1280.get("horizontalScroll") else "N",
            "skip_link": (d1280.get("skipLink") or {}).get("text", ""),
            "skip_link_ada": "Y" if d1280.get("skipLink") else "N",
            "focusable": d1280.get("focusableCount"),
            "tabindex_positif": d1280.get("positiveTabindexCount"),
            "target_kecil": d1280.get("smallTargetCount"),
            "target_inline_kecualian": d1280.get("smallTargetInlineExempt"),
            "target_spacing_kecualian": d1280.get("smallTargetSpacingExempt"),
            "contoh_target_kecil": "; ".join(
                f"{t['tag']}.{t['cls']}({t['w']}x{t['h']})" for t in (d1280.get("smallTargets") or [])[:3]),
            "contoh_offender_reflow": "; ".join(
                f"{o['tag']}.{o['cls']}" for o in (d320.get("offenders") or [])[:3]),
            "landmark_banner": (d1280.get("landmarks") or {}).get("banner"),
            "landmark_main": (d1280.get("landmarks") or {}).get("main"),
            "landmark_nav": (d1280.get("landmarks") or {}).get("nav"),
        })

    fields = list(rows[0].keys()) if rows else ["url"]
    with open(out_dir / "layout-summary.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    n = len(rows) or 1
    counts = {
        "reflow_320": sum(1 for r in rows if r["reflow_320_gagal"] == "Y"),
        "zoom200": sum(1 for r in rows if r["zoom200_gagal"] == "Y"),
        "no_skiplink": sum(1 for r in rows if r["skip_link_ada"] == "N"),
        "small_target": sum(1 for r in rows if (r["target_kecil"] or 0) > 0),
        "tabindex_pos": sum(1 for r in rows if (r["tabindex_positif"] or 0) > 0),
        "scroll_1280": sum(1 for r in rows if r["scroll_horizontal_1280"] == "Y"),
    }

    worst_reflow = sorted((r for r in rows if r["reflow_320_gagal"] == "Y"),
                          key=lambda r: -(r["scrollWidth_320"] or 0))[:10]
    worst_small = sorted((r for r in rows if (r["target_kecil"] or 0) > 0),
                         key=lambda r: -(r["target_kecil"] or 0))[:10]

    lines = [
        "# Cek Layout: Reflow, Zoom, Skip Link, Target Size",
        "",
        f"Dihasilkan: {datetime.now().isoformat(timespec='seconds')}  ",
        f"URL diperiksa: {len(rows)} (dari {n_urls} di file urls)",
        "",
        "Metode: viewport 1280px (desktop), 320px (SC 1.4.10 Reflow), 640px "
        "(setara zoom 200% pada 1280px, SC 1.4.4). Headless Chrome, tanpa interaksi keyboard.",
        "",
        "## Ringkasan",
        "",
        "| Pemeriksaan | SC | URL gagal | Persentase |",
        "|-------------|----|-----------|------------|",
        f"| Scroll horizontal di 320px | 1.4.10 | {counts['reflow_320']} | {counts['reflow_320']/n*100:.0f}% |",
        f"| Scroll horizontal di 640px (zoom 200%) | 1.4.4 | {counts['zoom200']} | {counts['zoom200']/n*100:.0f}% |",
        f"| Tidak ada skip link yang berfungsi | 2.4.1 | {counts['no_skiplink']} | {counts['no_skiplink']/n*100:.0f}% |",
        f"| Ada target interaktif < 24x24 px | 2.5.8 | {counts['small_target']} | {counts['small_target']/n*100:.0f}% |",
        f"| Ada tabindex positif | 2.4.3 | {counts['tabindex_pos']} | {counts['tabindex_pos']/n*100:.0f}% |",
        f"| Scroll horizontal bahkan di 1280px | - | {counts['scroll_1280']} | {counts['scroll_1280']/n*100:.0f}% |",
        "",
        "## 10 URL terburuk untuk reflow 320px",
        "",
        "| URL | scrollWidth @320 | Contoh elemen melebar |",
        "|-----|------------------|------------------------|",
    ]
    for r in worst_reflow:
        lines.append(f"| {r['url']} | {r['scrollWidth_320']} | `{r['contoh_offender_reflow']}` |")
    lines += ["", "## 10 URL dengan target terkecil", "",
              "| URL | jumlah target < 24px | Contoh |",
              "|-----|----------------------|--------|"]
    for r in worst_small:
        lines.append(f"| {r['url']} | {r['target_kecil']} | `{r['contoh_target_kecil']}` |")

    lines += ["", "## Catatan interpretasi", "",
              "- Ukuran target diukur pada viewport 1280px. Pada 320px banyak target justru lebih "
              "besar karena layout berubah, jadi angka ini konservatif untuk SC 2.5.8.",
              "- Dua pengecualian SC 2.5.8 sudah diterapkan: link inline di dalam blok teks, dan "
              "spacing (lingkaran 24px tidak beririsan dengan lingkaran target lain). Target "
              "24x24 dianggap memenuhi batas minimum.",
              "- Kehadiran skip link di sini hanya berarti ada link anchor yang menunjuk ke element "
              "yang ada. Apakah link itu terlihat saat fokus dan apakah pengguna bisa menemukannya "
              "lewat keyboard tetap perlu uji manual.",
              "- Scroll horizontal di 320px bisa menyebabkan dua arah baca pada mobile dan "
              "termasuk kegagalan SC 1.4.10 kalau tidak ada cara scroll dua arah yang disengaja.",
              "- Pemeriksaan ini tidak menggantikan uji keyboard sungguhan: urutan fokus, "
              "focus trap, dan perilaku reader layar belum diperiksa.",
              ""]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[OK] {out_dir / 'layout-summary.csv'} ({len(rows)} URL)")
    print(f"[OK] {out_dir / 'summary.md'}")
    print(f"\n[LAYOUT] reflow320 {counts['reflow_320']} | zoom200 {counts['zoom200']} | "
          f"no-skiplink {counts['no_skiplink']} | target<24px {counts['small_target']} | "
          f"tabindex+ {counts['tabindex_pos']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())