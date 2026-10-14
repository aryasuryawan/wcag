#!/usr/bin/env python3
"""
run_axe.py - Jalankan scan axe-core batch pada URL dari file urls.

Runner Node (scripts/axe_runner.js) memakai satu instance Chrome untuk seluruh URL
dengan beberapa tab paralel, plus resume (JSON yang sudah ada dilewati).
Output: results/automated/axe-YYYYMMDD/

Usage:
    python scripts/run_axe.py
    python scripts/run_axe.py --urls-file inventory/urls-utama.txt --concurrency 3
    python scripts/run_axe.py --urls-file inventory/urls-all.txt --concurrency 4
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_URLS_FILE = PROJECT_ROOT / "inventory" / "urls.txt"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "automated"
RUNNER = PROJECT_ROOT / "scripts" / "axe_runner.js"
REQUIRED_PACKAGES = ["@axe-core/puppeteer", "puppeteer-core"]


def check_deps():
    missing = [p for p in REQUIRED_PACKAGES
               if not (PROJECT_ROOT / "node_modules" / p.replace("/", os.sep)).exists()]
    if missing:
        return False, f"Dependency Node belum ada: {', '.join(missing)}. Jalankan 'npm install'."
    return True, "OK"


def main():
    ap = argparse.ArgumentParser(description="Scan axe-core batch")
    ap.add_argument("--urls-file", default=str(DEFAULT_URLS_FILE))
    ap.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    ap.add_argument("--concurrency", type=int, default=3)
    ap.add_argument("--chrome-path", default="")
    args = ap.parse_args()

    urls_file = Path(args.urls_file)
    if not urls_file.exists():
        print(f"[ERROR] {urls_file} tidak ada. Jalankan crawl_inventory.py dulu.", file=sys.stderr)
        sys.exit(1)

    ok, msg = check_deps()
    if not ok:
        print(f"[ERROR] {msg}", file=sys.stderr)
        sys.exit(1)

    date_str = datetime.now().strftime("%Y%m%d")
    scan_dir = Path(args.output_dir) / f"axe-{date_str}"
    scan_dir.mkdir(parents=True, exist_ok=True)

    n_urls = sum(1 for line in urls_file.read_text(encoding="utf-8").splitlines()
                 if line.strip() and not line.startswith("#"))
    est_min = n_urls * 20 / max(args.concurrency, 1) / 60

    print(f"[AXE] urls-file   : {urls_file} ({n_urls} URL)")
    print(f"[AXE] output      : {scan_dir}")
    print(f"[AXE] concurrency : {args.concurrency}")
    print(f"[AXE] estimasi    : ~{est_min:.0f} menit")
    print(f"[AXE] log         : {scan_dir / 'run.log'}\n")

    cmd = ["node", str(RUNNER), str(urls_file), str(scan_dir), str(args.concurrency)]
    if args.chrome_path:
        cmd.append(args.chrome_path)

    start = time.time()
    with open(scan_dir / "run.log", "w", encoding="utf-8") as log:
        proc = subprocess.Popen(cmd, cwd=PROJECT_ROOT, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                errors="replace", bufsize=1)
        for line in proc.stdout:
            sys.stdout.write(line)
            log.write(line)
        code = proc.wait()

    elapsed = (time.time() - start) / 60
    summary_file = scan_dir / "summary.json"
    if code != 0:
        print(f"\n[AXE ERROR] exit code {code}, durasi {elapsed:.1f} mnt", file=sys.stderr)
        print(f"[AXE] log: {scan_dir / 'run.log'}", file=sys.stderr)
        sys.exit(code)

    if summary_file.exists():
        summary = json.loads(summary_file.read_text(encoding="utf-8"))
        print(f"\n[AXE] URL discan   : {summary['scanned']}/{summary['totalUrls']}")
        print(f"[AXE] error       : {summary['failed']}")
        print(f"[AXE] violations  : {summary['totalViolations']}")
        print(f"[AXE] by impact   : {summary['violationsByImpact']}")
        print(f"[AXE] durasi      : {elapsed:.1f} mnt")
        print(f"[AXE] top rules   :")
        for rule, count in summary["violationsByRule"][:12]:
            print(f"   {rule}: {count}")
    else:
        print(f"[AXE] selesai tanpa summary.json, cek {scan_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()