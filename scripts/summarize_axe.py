#!/usr/bin/env python3
"""
summarize_axe.py - Ringkasan hasil axe-core untuk Tahap 1.

Input : results/automated/axe-YYYYMMDD/*.json + inventory/heuristics.csv + standards/sc-mapping.csv
Output: results/automated/axe-YYYYMMDD/tahap1-summary.md
        results/automated/axe-YYYYMMDD/violations-by-url.csv
        results/automated/axe-YYYYMMDD/violations-by-rule.csv

Usage:
    python scripts/summarize_axe.py
    python scripts/summarize_axe.py --dir results/automated/axe-20261011
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
HEURISTICS = PROJECT_ROOT / "inventory" / "heuristics.csv"
SC_MAPPING = PROJECT_ROOT / "standards" / "sc-mapping.csv"
URLS_ALL = PROJECT_ROOT / "inventory" / "urls-all.txt"

RULE_SC = {
    "image-alt": "1.1.1",
    "input-image-alt": "1.1.1",
    "area-alt": "1.1.1",
    "object-alt": "1.1.1",
    "role-img-alt": "1.1.1",
    "video-caption": "1.2.2",
    "audio-caption": "1.2.2",
    "link-name": "2.4.4",
    "button-name": "4.1.2",
    "frame-title": "4.1.2",
    "frame-title-unique": "4.1.2",
    "aria-allowed-attr": "4.1.2",
    "aria-prohibited-attr": "4.1.2",
    "aria-allowed-role": "4.1.2",
    "aria-required-attr": "4.1.2",
    "aria-valid-attr-value": "4.1.2",
    "aria-roles": "4.1.2",
    "aria-command-name": "4.1.2",
    "aria-toggle-field-name": "4.1.2",
    "aria-dialog-name": "4.1.2",
    "aria-meter-name": "4.1.2",
    "aria-progressbar-name": "4.1.2",
    "aria-input-field-name": "4.1.2",
    "aria-required-children": "1.3.1",
    "aria-required-parent": "1.3.1",
    "aria-hidden-focus": "4.1.2",
    "aria-hidden-body": "1.3.1",
    "duplicate-id-aria": "4.1.1",
    "duplicate-id-active": "4.1.1",
    "heading-order": "1.3.1",
    "page-has-heading-one": "1.3.1",
    "landmark-unique": "1.3.1",
    "landmark-no-duplicate-banner": "1.3.1",
    "landmark-complementary-is-top-level": "1.3.1",
    "landmark-one-main": "1.3.1",
    "list": "1.3.1",
    "listitem": "1.3.1",
    "definition-list": "1.3.1",
    "dlitem": "1.3.1",
    "label": "3.3.2",
    "form-field-multiple-labels": "3.3.2",
    "select-name": "3.3.2",
    "color-contrast": "1.4.3",
    "link-in-text-block": "1.4.1",
    "meta-viewport": "1.4.4",
    "html-has-lang": "3.1.1",
    "html-lang-valid": "3.1.1",
    "document-title": "2.4.2",
    "tabindex": "2.4.3",
    "bypass": "2.4.1",
    "skip-link": "2.4.1",
    "accesskeys": "2.1.1",
    "meta-refresh": "2.2.1",
    "frame-tested": "4.1.2",
    "target-size": "2.5.8",
    "focus-order-semantics": "2.4.3",
    "focus-visible": "2.4.7",
    "scrollable-region-focusable": "2.1.1",
    "avoid-inline-spacing": "1.4.12",
    "link-in-text-block": "1.4.1",
}

IMPACT_ORDER = ["critical", "serious", "moderate", "minor"]


def load_known_urls():
    if not URLS_ALL.exists():
        return None
    return {line.strip().rstrip("/") for line in URLS_ALL.read_text(encoding="utf-8").splitlines() if line.strip()}


def load_post_types():
    mapping = {}
    if not HEURISTICS.exists():
        return mapping
    for row in csv.DictReader(open(HEURISTICS, encoding="utf-8")):
        mapping[row["url"].rstrip("/")] = row.get("post_type", "")
    return mapping


def load_sc_meta():
    meta = {}
    if not SC_MAPPING.exists():
        return meta
    for row in csv.DictReader(open(SC_MAPPING, encoding="utf-8")):
        meta[row["SC"]] = (row.get("Nama", ""), row.get("Level", ""), row.get("Versi", ""))
    return meta


def main():
    ap = argparse.ArgumentParser(description="Ringkasan hasil axe-core (Tahap 1)")
    ap.add_argument("--dir", default="")
    args = ap.parse_args()

    if args.dir:
        scan_dir = Path(args.dir)
    else:
        dated = sorted((PROJECT_ROOT / "results" / "automated").glob("axe-*"))
        if not dated:
            print("[ERROR] tidak ada folder results/automated/axe-*", file=sys.stderr)
            sys.exit(1)
        scan_dir = dated[-1]

    files = [f for f in sorted(scan_dir.glob("*.json"))
             if f.name != "summary.json" and not f.name.endswith(".error.json")]
    if not files:
        print(f"[ERROR] tidak ada hasil axe di {scan_dir}", file=sys.stderr)
        sys.exit(1)

    known = load_known_urls()
    post_types = load_post_types()
    sc_meta = load_sc_meta()

    by_rule = defaultdict(lambda: {"urls": 0, "impact": {}, "nodes": 0, "samples": []})
    by_template = defaultdict(lambda: {"urls": 0, "urls_with_violation": 0, "violations": 0,
                                        "rules": defaultdict(int)})
    by_url_rows = []
    per_url_rules = {}
    seen_urls = set()
    skipped = 0
    dupes = 0
    total_violations = 0

    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        url = (data.get("url") or "").rstrip("/")
        if known and url not in known:
            skipped += 1
            continue
        if url in seen_urls:
            dupes += 1
            continue
        seen_urls.add(url)

        tpl = post_types.get(url, "unknown")
        by_template[tpl]["urls"] += 1

        rules_here = defaultdict(int)
        url_violations = 0
        for v in data.get("violations", []):
            rid = v.get("id", "unknown")
            impact = v.get("impact", "unknown")
            nodes = len(v.get("nodes", []))
            total_violations += 1
            url_violations += 1

            rec = by_rule[rid]
            rec["urls"] += 1
            rec["nodes"] += nodes
            rec["impact"][impact] = rec["impact"].get(impact, 0) + 1
            if len(rec["samples"]) < 2:
                node = (v.get("nodes") or [{}])[0]
                rec["samples"].append((node.get("target") or [""])[0])

            rules_here[rid] += 1
            by_template[tpl]["violations"] += 1
            by_template[tpl]["rules"][rid] += 1

        if url_violations:
            by_template[tpl]["urls_with_violation"] += 1
        per_url_rules[url] = dict(rules_here)
        by_url_rows.append({
            "url": url,
            "template": tpl,
            "violations": url_violations,
            "rules": "; ".join(f"{k}:{v}" for k, v in sorted(rules_here.items(),
                                                               key=lambda x: -x[1])),
        })

    impact_total = defaultdict(int)
    for rid, rec in by_rule.items():
        for imp, c in rec["impact"].items():
            impact_total[imp] += c

    lines = [
        "# Tahap 1 - Ringkasan Scan Otomatis (axe-core)",
        "",
        f"Folder hasil: `{scan_dir.name}`  ",
        f"Dihasilkan: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Cakupan",
        "",
        "| Metrik | Nilai |",
        "|--------|-------|",
        f"| File hasil diproses | {len(files)} |",
        f"| URL unik tercakup | {len(seen_urls)} |",
        f"| File duplikat (dilewati) | {dupes} |",
        f"| URL di luar `urls-all.txt` (diabaikan) | {skipped} |",
        f"| URL dengan violation | {sum(1 for r in by_url_rows if r['violations'])} |",
        f"| Total violation | {total_violations} |",
        f"| Rule aktif | {len(by_rule)} |",
        "",
        "## Violasi per impact",
        "",
        "| Impact | Jumlah |",
        "|--------|--------|",
    ]
    for imp in IMPACT_ORDER:
        if impact_total.get(imp):
            lines.append(f"| {imp} | {impact_total[imp]} |")
    for imp in sorted(set(impact_total) - set(IMPACT_ORDER)):
        lines.append(f"| {imp} | {impact_total[imp]} |")

    lines += ["", "## Per rule (urut URL terdampak) - dengan pemetaan SC", "",
              "| Rule | SC | Nama SC | Level | URL terdampak | Node | Impact tertinggi | Contoh target |",
              "|------|----|----------|-------|---------------|------|-----------------|--------------|"]
    for rid, rec in sorted(by_rule.items(), key=lambda x: -x[1]["urls"]):
        sc = RULE_SC.get(rid, "")
        nama, level, _ = sc_meta.get(sc, ("", "", ""))
        top_impact = max(rec["impact"].items(), key=lambda x: x[1])[0] if rec["impact"] else ""
        sample = rec["samples"][0][:60] if rec["samples"] else ""
        lines.append(f"| `{rid}` | {sc or '-'} | {nama} | {level or '-'} | {rec['urls']} | "
                     f"{rec['nodes']} | {top_impact} | `{sample}` |")

    lines += ["", "## Per template", "",
              "| Template | URL discan | URL bermasalah | Violation | Top 3 rule |",
              "|----------|------------|----------------|-----------|------------|"]
    for tpl, rec in sorted(by_template.items(), key=lambda x: -x[1]["violations"]):
        top3 = ", ".join(f"`{r}` ({c})" for r, c in
                         sorted(rec["rules"].items(), key=lambda x: -x[1])[:3])
        lines.append(f"| {tpl} | {rec['urls']} | {rec['urls_with_violation']} | "
                     f"{rec['violations']} | {top3} |")

    lines += ["", "## Catatan interpretasi", "",
              "- Angka di atas adalah instance violation per URL, bukan jumlah isu unik. "
              "Satu isu template (mis. `landmark-unique`) yang muncul di 738 URL tetap dihitung 1 fix.",
              "- `incomplete` (needs review) tidak dihitung sebagai violation; itu masuk Tahap 3 (manual).",
              "- Scan ini hanya mencakup sebagian SC WCAG 2.2 AA. Evaluasi keyboard, focus order, "
              "reflow, error message, caption video, dan struktur PDF tetap wajib manual.",
              "- Severity final (Critical/Serious/Moderate/Minor) ditentukan di Tahap 2, bukan dari impact axe.",
              ""]

    (scan_dir / "tahap1-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    with open(scan_dir / "violations-by-url.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "template", "violations", "rules"])
        w.writeheader()
        for r in sorted(by_url_rows, key=lambda x: -x["violations"]):
            w.writerow(r)

    with open(scan_dir / "violations-by-rule.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rule", "sc", "nama_sc", "level", "url_terdampak", "node", "critical",
                    "serious", "moderate", "minor", "contoh_target"])
        for rid, rec in sorted(by_rule.items(), key=lambda x: -x[1]["urls"]):
            sc = RULE_SC.get(rid, "")
            nama, level, _ = sc_meta.get(sc, ("", "", ""))
            imp = rec["impact"]
            w.writerow([rid, sc, nama, level, rec["urls"], rec["nodes"],
                        imp.get("critical", 0), imp.get("serious", 0),
                        imp.get("moderate", 0), imp.get("minor", 0),
                        rec["samples"][0][:120] if rec["samples"] else ""])

    print(f"[OK] {scan_dir / 'tahap1-summary.md'}")
    print(f"[OK] {scan_dir / 'violations-by-url.csv'}")
    print(f"[OK] {scan_dir / 'violations-by-rule.csv'}")
    print(f"\nURL discan: {len(by_url_rows)} | violation: {total_violations} | rule: {len(by_rule)}")
    print(f"Per impact: {dict(impact_total)}")


if __name__ == "__main__":
    main()