#!/usr/bin/env python3
"""
run_lighthouse.py - Run Lighthouse CLI accessibility audit on URLs
Output: results/automated/lighthouse-YYYYMMDD/

Usage:
    python scripts/run_lighthouse.py
    python scripts/run_lighthouse.py --urls-file inventory/urls.txt --output-dir results/automated
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_URLS_FILE = PROJECT_ROOT / "inventory" / "urls.txt"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "automated"

# Lighthouse config - accessibility only
LIGHTHOUSE_CONFIG = {
    "extends": "lighthouse:default",
    "settings": {
        "onlyCategories": ["accessibility"],
        "onlyAudits": [
            # Core accessibility audits
            "accesskeys",
            "aria-allowed-attr",
            "aria-allowed-role",
            "aria-command-name",
            "aria-dialog-name",
            "aria-hidden-body",
            "aria-hidden-focus",
            "aria-input-field-name",
            "aria-meter-name",
            "aria-progressbar-name",
            "aria-required-attr",
            "aria-required-children",
            "aria-required-parent",
            "aria-roles",
            "aria-toggle-field-name",
            "aria-valid-attr-value",
            "aria-valid-attr",
            "audio-caption",
            "button-name",
            "bypass",
            "checkbox-name",
            "color-contrast",
            "definition-list",
            "dlitem",
            "document-title",
            "duplicate-id-active",
            "duplicate-id-aria",
            "form-field-multiple-labels",
            "frame-title",
            "heading-order",
            "html-has-lang",
            "html-lang-valid",
            "image-alt",
            "input-image-alt",
            "label",
            "landmark-one-main",
            "landmark-unique",
            "link-name",
            "list",
            "listitem",
            "meta-refresh",
            "meta-viewport",
            "object-alt",
            "tabindex",
            "td-headers-attr",
            "th-has-data-cells",
            "valid-lang",
            "video-caption",
            "video-description"
        ],
        "formFactor": "desktop",
        "screenEmulation": {
            "mobile": False,
            "width": 1350,
            "height": 940,
            "deviceScaleFactor": 1,
            "disabled": False
        },
        "throttling": {
            "rttMs": 40,
            "throughputKbps": 10240,
            "cpuSlowdownMultiplier": 1
        }
    }
}


def check_lighthouse():
    """Check if Lighthouse CLI is available."""
    try:
        result = subprocess.run(["lighthouse", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
    except FileNotFoundError:
        pass

    # Try npx
    try:
        result = subprocess.run(["npx", "lighthouse", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
    except FileNotFoundError:
        pass

    return False, "Lighthouse CLI not found. Install: npm install -g lighthouse"


def run_lighthouse_scan(urls_file, output_dir):
    """Run Lighthouse accessibility scan on each URL."""
    date_str = datetime.now().strftime("%Y%m%d")
    scan_dir = Path(output_dir) / f"lighthouse-{date_str}"
    scan_dir.mkdir(parents=True, exist_ok=True)

    # Write Lighthouse config
    config_file = scan_dir / "lighthouse-config.json"
    with open(config_file, "w") as f:
        json.dump(LIGHTHOUSE_CONFIG, f, indent=2)

    # Read URLs
    with open(urls_file, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"[LIGHTHOUSE] Starting accessibility scan for {len(urls)} URLs")
    print(f"[LIGHTHOUSE] Output: {scan_dir}")
    print(f"[LIGHTHOUSE] Config: {config_file}")

    results_summary = {
        "scan_date": datetime.now().isoformat(),
        "tool": "lighthouse",
        "category": "accessibility",
        "total_urls": len(urls),
        "urls": []
    }

    for i, url in enumerate(urls, 1):
        print(f"[LIGHTHOUSE] {i}/{len(urls)} {url}")

        # Output filename
        safe_name = url.replace("://", "_").replace("/", "_").replace("?", "_")[:100]
        output_file = scan_dir / f"{safe_name}.json"
        html_file = scan_dir / f"{safe_name}.html"

        try:
            # Run Lighthouse
            cmd = [
                "lighthouse", url,
                "--config-path", str(config_file),
                "--output", "json",
                "--output", "html",
                "--output-path", str(output_file),
                "--chrome-flags=--headless --no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage",
                "--quiet"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Parse JSON result
                try:
                    with open(output_file, "r") as f:
                        lh_data = json.load(f)

                    accessibility_score = lh_data.get("categories", {}).get("accessibility", {}).get("score", 0)
                    audits = lh_data.get("audits", {})

                    failed_audits = []
                    for audit_id, audit in audits.items():
                        if audit.get("score") is not None and audit.get("score") < 1:
                            failed_audits.append({
                                "id": audit_id,
                                "title": audit.get("title", ""),
                                "score": audit.get("score"),
                                "description": audit.get("description", "")
                            })

                    results_summary["urls"].append({
                        "url": url,
                        "score": accessibility_score,
                        "failed_audits_count": len(failed_audits),
                        "failed_audits": failed_audits[:10]  # Top 10
                    })

                    print(f"  Score: {accessibility_score*100:.0f}/100 | Failed: {len(failed_audits)}")

                except Exception as e:
                    print(f"  [WARN] Failed to parse result: {e}")
                    results_summary["urls"].append({"url": url, "error": str(e)})
            else:
                print(f"  [ERROR] Lighthouse failed: {result.stderr[:200]}")
                results_summary["urls"].append({"url": url, "error": result.stderr[:500]})

        except subprocess.TimeoutExpired:
            print(f"  [ERROR] Timeout after 5 minutes")
            results_summary["urls"].append({"url": url, "error": "Timeout"})
        except Exception as e:
            print(f"  [ERROR] {e}")
            results_summary["urls"].append({"url": url, "error": str(e)})

        # Delay between scans
        if i < len(urls):
            time.sleep(3)

    # Save summary
    summary_file = scan_dir / "summary.json"
    with open(summary_file, "w") as f:
        json.dump(results_summary, f, indent=2)

    print(f"\n[LIGHTHOUSE] Done. Summary: {summary_file}")

    # Print summary stats
    scores = [u.get("score", 0) for u in results_summary["urls"] if "score" in u]
    if scores:
        avg_score = sum(scores) / len(scores)
        print(f"[LIGHTHOUSE] Average accessibility score: {avg_score*100:.1f}/100")
        print(f"[LIGHTHOUSE] Min: {min(scores)*100:.0f} | Max: {max(scores)*100:.0f}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Run Lighthouse accessibility audit")
    parser.add_argument("--urls-file", default=str(DEFAULT_URLS_FILE), help="Path to urls.txt")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    args = parser.parse_args()

    urls_file = Path(args.urls_file)
    output_dir = Path(args.output_dir)

    if not urls_file.exists():
        print(f"[ERROR] URLs file not found: {urls_file}", file=sys.stderr)
        print("Run 'python scripts/crawl_inventory.py' first.", file=sys.stderr)
        sys.exit(1)

    # Check Lighthouse
    ok, msg = check_lighthouse()
    if not ok:
        print(f"[ERROR] {msg}", file=sys.stderr)
        print("Install: npm install -g lighthouse", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"[LIGHTHOUSE] Found: {msg}")

    success = run_lighthouse_scan(urls_file, output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()