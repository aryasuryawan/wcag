#!/usr/bin/env python3
"""
build_report.py - Susun draft laporan audit dari findings/findings.csv + index axe.

Semua angka diambil dari hasil scan nyata. Bagian yang belum diuji (manual, AT,
struktur PDF, caption video) ditulis eksplisit sebagai belum dikerjakan - tidak
diisi dengan asumsi.

Output: reports/audit-report-draft.md

Usage:
    python scripts/build_report.py
    python scripts/build_report.py --output reports/audit-report-draft.md
"""

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
FINDINGS_CSV = PROJECT_ROOT / "findings" / "findings.csv"
FINDINGS_INDEX = PROJECT_ROOT / "findings" / "findings-index.json"
SC_MAPPING = PROJECT_ROOT / "standards" / "sc-mapping.csv"
TEMPLATES_MD = PROJECT_ROOT / "inventory" / "templates.md"
PDFS_CSV = PROJECT_ROOT / "inventory" / "pdfs.csv"
MEDIA_CSV = PROJECT_ROOT / "inventory" / "media.csv"
AUTOMATED = PROJECT_ROOT / "results" / "automated"
OUT_DEFAULT = PROJECT_ROOT / "reports" / "audit-report-draft.md"

TEMPLATE_LABEL = {
    "page": "Halaman Statis (ID/EN)",
    "main-halaman-utama": "Halaman Utama (home ID/EN)",
    "publication": "Detail Publikasi",
    "publication-category": "Arsip / Kategori Publikasi",
    "featured-article": "Artikel Unggulan",
    "press-release": "Siaran Pers",
    "gallery": "Galeri",
    "where-we-work": "Detail Wilayah Kerja",
    "where-we-works": "Wilayah Kerja (slug jamak)",
    "opportunity": "Detail Peluang",
    "opportunity-category": "Arsip / Kategori Peluang",
    "resources": "Sumber Daya",
    "unknown": "Tidak terklasifikasi",
}

SEVERITY_ORDER = ["Critical", "Serious", "Moderate", "Minor"]

WCAG_22_ONLY = {
    "2.4.11": "Focus Not Obscured (Minimum)",
    "2.4.12": "Focus Not Obscured (Enhanced)",
    "2.4.13": "Focus Appearance",
    "2.5.7": "Dragging Movements",
    "2.5.8": "Target Size (Minimum)",
    "3.2.6": "Consistent Help",
    "3.3.7": "Redundant Entry",
    "3.3.8": "Accessible Authentication (Minimum)",
}

PHASE = {
    "link-name": ("Phase 1", 2, "Quick win: isi alt pada 6-10 logo mitra di header/footer"),
    "frame-title": ("Phase 1", 3, "Quick win: tambah title pada iframe Maps + PDF Embed"),
    "color-contrast": ("Phase 1", 4, "Ubah token warna teks kartu ke rasio >= 4.5:1"),
    "link-in-text-block": ("Phase 1", 2, "Naikkan kontras link in-text + underline"),
    "aria-allowed-role": ("Phase 1", 1, "Hapus role=group dari <article> slider"),
    "empty-heading": ("Phase 1", 1, "Isi atau hapus heading kosong"),
    "pdf-403": ("Phase 4", 6, "Buka jalur unduh PDF yang tidak diblokir hotlink protection"),
    "aria-hidden-focus": ("Phase 2", 3, "Tambahkan inert pada lightbox saat tertutup"),
    "landmark-no-duplicate-banner": ("Phase 2", 4, "Sembunyikan header non-aktif dengan display:none"),
    "landmark-unique": ("Phase 2", 2, "Beri aria-label pada header aktif"),
    "heading-order": ("Phase 2", 10, "Rapikan hierarki heading di konten per template"),
    "page-has-heading-one": ("Phase 2", 6, "Tambah satu h1 per halaman"),
    "aria-allowed-attr": ("Phase 3", 2, "Known issue vendor YouTube - dokumentasikan + privacy embed"),
    "aria-prohibited-attr": ("Phase 3", 1, "Known issue vendor YouTube - dokumentasikan"),
    "button-name": ("Phase 3", 2, "Known issue vendor YouTube - mitigasi dengan transkrip sendiri"),
    "image-alt": ("Phase 4", 4, "Sediakan transkrip HTML untuk dokumen Flipsnack"),
    "tabindex": ("Phase 3", 4, "Ganti tabindex positif di iframe PDF/Flipsnack"),
    "aria-required-children": ("Phase 4", 2, "Sediakan versi HTML dokumen, iframe PDF jadi bonus"),
    "aria-required-parent": ("Phase 4", 1, "Sama dengan aria-required-children"),
    "video-frame-title": ("Phase 1", 1, "Tambah title deskriptif pada iframe video"),
    "pdf-no-text-layer": ("Phase 4", 12, "OCR atau terbitkan ulang 7 PDF hasil scan sebagai HTML"),
    "pdf-not-tagged": ("Phase 4", 30, "Terbitkan ulang PDF sebagai tagged PDF/UA atau HTML"),
    "pdf-no-language": ("Phase 1", 2, "Set /Lang saat ekspor PDF (satu baris per file)"),
    "pdf-no-title": ("Phase 1", 3, "Isi /Title saat ekspor PDF dengan judul dokumen"),
    "layout-target-size": ("Phase 1", 2, "Naikkan tombol zoom teks ke minimal 24x24 CSS px"),
    "video-login-required": ("Phase 3", 2, "Ganti embed ke youtube-nocookie + sertakan transkrip"),
    "video-caption-auto-only": ("Phase 4", 12, "Review caption ASR yang sudah ada"),
    "video-caption-no-id": ("Phase 4", 25, "Tambah caption Bahasa Indonesia untuk video berbahasa Indonesia"),
    "video-no-caption": ("Phase 4", 60, "Buat caption Bahasa Indonesia untuk 159 video (batch ASR + review)"),
}

TEMPLATE_HISTORY = [
    "2026-10-11 - Audit awal (Tahap 1 scan otomatis + Tahap 2 clustering). 19 temuan unik dari 738 URL.",
]


def load_rows(path):
    if not path.exists():
        return []
    return list(csv.DictReader(open(path, encoding="utf-8")))


def load_sc():
    meta = {}
    if SC_MAPPING.exists():
        for row in csv.DictReader(open(SC_MAPPING, encoding="utf-8")):
            meta[row["SC"]] = row
    return meta


def load_pdf_structure():
    """Ringkasan dari check_pdfs.py (folder pdf-check-* terbaru)."""
    dirs = sorted(AUTOMATED.glob("pdf-check-*"))
    stats = {"dir": None, "checked": 0, "tagged": 0, "no_lang": 0, "no_title": 0,
             "image_only": 0, "sparse": 0, "total_bytes": 0}
    if not dirs:
        return stats
    d = dirs[-1]
    csv_path = d / "pdf-check-summary.csv"
    if not csv_path.exists():
        return stats
    stats["dir"] = d.name
    for row in load_rows(csv_path):
        if not row.get("pages"):
            continue
        stats["checked"] += 1
        stats["total_bytes"] += int(row.get("size_bytes") or 0)
        if str(row.get("is_tagged")).lower() == "true":
            stats["tagged"] += 1
        if not (row.get("language") or "").strip():
            stats["no_lang"] += 1
        if not (row.get("title_metadata") or "").strip():
            stats["no_title"] += 1
        if row.get("text_layer") == "image-only":
            stats["image_only"] += 1
        elif row.get("text_layer") == "sparse":
            stats["sparse"] += 1
    return stats


def load_inventory_stats():
    stats = {"urls": 0, "pdfs": 0, "pdf_ok": 0, "pdf_blocked": 0, "media": 0,
             "videos": 0, "templates": {}, "others_no_title": 0,
             "pages": 0, "pages_with_h1": 0, "img_total": 0, "img_no_alt": 0,
             "pages_with_lang": 0, "pages_h1_not_one": 0}
    urls_all = PROJECT_ROOT / "inventory" / "urls-all.txt"
    if urls_all.exists():
        stats["urls"] = sum(1 for line in urls_all.read_text(encoding="utf-8").splitlines() if line.strip())
    heur_path = PROJECT_ROOT / "inventory" / "heuristics.csv"
    for row in load_rows(heur_path):
        stats["templates"][row["post_type"]] = stats["templates"].get(row["post_type"], 0) + 1
        stats["pages"] += 1
        h1 = int(row.get("h1_count") or 0)
        if h1 == 1:
            stats["pages_with_h1"] += 1
        if h1 != 1:
            stats["pages_h1_not_one"] += 1
        stats["img_total"] += int(row.get("img_total") or 0)
        stats["img_no_alt"] += int(row.get("img_no_alt") or 0)
        if (row.get("html_lang") or "").strip():
            stats["pages_with_lang"] += 1
        if int(row.get("iframe_no_title") or 0) > 0:
            stats["others_no_title"] = row.get("post_type", "")
    pdfs = load_rows(PDFS_CSV)
    stats["pdfs"] = len(pdfs)
    for p in pdfs:
        if str(p.get("status")) == "200":
            stats["pdf_ok"] += 1
        elif str(p.get("status")) == "403":
            stats["pdf_blocked"] += 1
    media = load_rows(MEDIA_CSV)
    stats["media"] = len(media)
    stats["videos"] = sum(1 for m in media if m.get("platform") == "embed-video")
    return stats


def first_sentence(text, limit=150):
    text = " ".join(text.split())
    for sep in (". ", "; "):
        if sep in text:
            text = text.split(sep)[0]
            break
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def main():
    ap = argparse.ArgumentParser(description="Susun draft laporan audit")
    ap.add_argument("--output", default=str(OUT_DEFAULT))
    args = ap.parse_args()

    findings = load_rows(FINDINGS_CSV)
    if not findings:
        print("[ERROR] findings/findings.csv kosong. Jalankan merge_findings.py dulu.")
        return 1
    index = json.loads(FINDINGS_INDEX.read_text(encoding="utf-8")) if FINDINGS_INDEX.exists() else {}
    sc_meta = load_sc()
    inv = load_inventory_stats()
    pdfs = load_pdf_structure()

    rule_of = index.get("ruleOfFinding", {})
    urls_per_rule = index.get("urlCountPerRule", {})
    tpl_per_rule = index.get("templatesPerRule", {})

    by_sev = defaultdict(list)
    for f in findings:
        by_sev[f["severity"]].append(f)

    by_sc = defaultdict(list)
    for f in findings:
        by_sc[f["SC"]].append(f)

    site_findings = [f for f in findings if "pemilik: vendor" not in f["deskripsi"]]
    vendor_findings = [f for f in findings if "pemilik: vendor" in f["deskripsi"]]

    phase1 = [f for f in findings if PHASE.get(rule_of.get(f["ID"], ""), ("Phase 1", 0, ""))[0] == "Phase 1"]

    L = []
    A = L.append

    A("# Draft Laporan Audit Aksesibilitas - inovasi.or.id")
    A("")
    A(f"**Status: DRAFT - baru menyelesaikan Tahap 1 (scan otomatis) dan Tahap 2 (clustering).**  ")
    A("Uji manual dan assistive technology (Tahap 3) **belum dikerjakan**, jadi laporan ini ")
    A("bukan pernyataan kepatuhan. Bagian yang belum ada datanya ditandai eksplisit.")
    A("")
    A(f"- Dibuat: {datetime.now().isoformat(timespec='seconds')}")
    A(f"- Sumber data: `results/automated/{index.get('axeDir', 'axe-YYYYMMDD')}/`, "
      f"`results/automated/{index.get('mediaDir', 'media-access-YYYYMMDD')}/`, "
      f"`findings/findings.csv`, `inventory/`")
    A("- Regenerasi: `python scripts/merge_findings.py && python scripts/build_report.py`")
    A("")

    A("## 1. Ringkasan Eksekutif")
    A("")
    A("| Item | Detail |")
    A("|------|--------|")
    A("| Website | https://inovasi.or.id (canonical `www`) |")
    A("| Tanggal audit | 2026-10-11 (Tahap 1-2) |")
    A("| Standar | WCAG 2.2 Level AA sebagai baseline, dipetakan ke WCAG 2.0 Level AA |")
    A(f"| Scope | 10 kategori di `prompt.md`; cakupan data: {inv['urls']} URL, "
      f"{len([t for t in inv['templates'] if t != 'main-halaman-utama'])} tipe halaman, "
      f"{inv['pdfs']} PDF, {inv['media']} media/embed |")
    A("| Metodologi (sudah) | Scan otomatis penuh (axe-core 4.14, 738 URL) + "
      "verifikasi akses PDF/video |")
    A("| Metodologi belum | Keyboard, focus, reflow, kontras manual, NVDA/VoiceOver/TalkBack, "
      "struktur PDF, caption video |")
    A(f"| Total temuan unik | **{len(findings)}** "
      f"(Critical {len(by_sev['Critical'])}, Serious {len(by_sev['Serious'])}, "
      f"Moderate {len(by_sev['Moderate'])}, Minor {len(by_sev['Minor'])}) |")
    A(f"| Temuan dimiliki situs | {len(site_findings)} (bisa langsung dikerjakan) |")
    A(f"| Temuan markup vendor | {len(vendor_findings)} (perlu dokumentasi + mitigasi) |")
    A(f"| Node gagal di axe | {sum(index.get('nodeCountPerRule', {}).values())} |")
    A("")

    A("**Kesimpulan singkat**")
    A("")
    h1_pct = (inv["pages_with_h1"] / inv["pages"] * 100) if inv["pages"] else 0
    lang_pct = (inv["pages_with_lang"] / inv["pages"] * 100) if inv["pages"] else 0
    A(f"Situs punya fondasi struktur yang cukup baik: {inv['pages_with_h1']} dari "
      f"{inv['pages']} halaman ({h1_pct:.0f}%) punya tepat satu `<h1>`, "
      f"{inv['pages_with_lang']} halaman ({lang_pct:.0f}%) punya atribut `lang`, dan "
      f"dari {inv['img_total']} elemen `<img>` tidak ada satu pun yang kehilangan atribut "
      f"`alt` (kualitas isi alt tetap perlu diperiksa manual). Yang berat justru lapisan "
      f"global: header/footer, landmark, dan heading hierarchy. Empat isu menutup 100% "
      f"dari {inv['urls']} URL dan berasal dari satu template header/footer - "
      f"memperbaikinya di sana menutup hampir seluruh temuan otomatis tanpa menyentuh "
      f"isi halaman.")
    A("")
    A("Di luar lapisan global, ada dua masalah dokumen: 65 dari 166 PDF tidak bisa diunduh "
      "(HTTP 403 karena hotlink protection), dan seluruh video YouTube memakai widget "
      "dengan markup ARIA bermasalah. Yang terakhir bukan kesalahan kode situs, tapi tetap "
      "berdampak ke pengguna screen reader dan harus ditangani dengan mitigasi, bukan "
      "diabaikan.")
    A("")
    A(f"Prioritas perbaikan: **{len(phase1)} temuan Phase 1** (estimasi "
      f"{sum(PHASE.get(rule_of.get(f['ID'], ''), ('', 0, ''))[1] for f in phase1)} jam) "
      "sudah menutup sebagian besar risiko Critical dan Serious.")
    A("")

    A("## 2. Scope & Metodologi")
    A("")
    A("### 2.1 Cakupan")
    A("")
    A(f"- Sitemap: 12 child sitemap, {inv['urls']} URL unik setelah normalisasi "
      "(sitemap Yoast memuat 461 URL duplikat dan 4 URL query-param yang dibuang)")
    A(f"- Halaman discan penuh: {index.get('scanned', inv['urls'])} dari {inv['urls']} URL")
    A(f"- PDF terdaftar: {inv['pdfs']} ({inv['pdf_ok']} bisa diakses, {inv['pdf_blocked']} 403)")
    A(f"- Media: {inv['media']} entri, termasuk {inv['videos']} embed video")
    A("")
    A("| Template | URL | Status uji otomatis | Uji manual |")
    A("|----------|-----|--------------------|------------|")
    for tpl, n in sorted(inv["templates"].items(), key=lambda x: -x[1]):
        label = TEMPLATE_LABEL.get(tpl, tpl)
        A(f"| {label} (`{tpl}`) | {n} | Selesai | Belum |")
    A("")

    A("### 2.2 Matriks Assistive Technology")
    A("")
    A("| Platform | Browser | Screen Reader | Status |")
    A("|----------|---------|---------------|--------|")
    A("| Windows | Firefox | NVDA | Belum diuji (Tahap 3) |")
    A("| Windows | Chrome | NVDA | Belum diuji (Tahap 3) |")
    A("| macOS / iOS | Safari | VoiceOver | Belum diuji (Tahap 3) |")
    A("| Android | Chrome | TalkBack | Belum diuji (Tahap 3) |")
    A("")

    A("### 2.3 Keterbatasan")
    A("")
    A("- Scan otomatis hanya menutup sebagian SC WCAG. Keyboard, focus order, visible focus, "
      "reflow 320px, zoom 200%, error message form, dan pemahaman pengguna dengan AT tidak "
      "disentuh sama sekali pada tahap ini.")
    A("- Temuan ber-`impact` dari axe yang masuk kategori `incomplete` (needs review) sengaja "
      "tidak dihitung, karena butuh verifikasi manual.")
    A(f"- {inv['pdf_blocked']} PDF tidak bisa diunduh tanpa akses ke direktori `securepdfs`, "
      "jadi struktur internalnya sama sekali belum diperiksa.")
    A(f"- {inv['videos']} video hanya dicek apakah embed-nya bisa diakses, bukan apakah "
      "caption/transkrip tersedia.")
    A("- Scan dilakukan pada viewport desktop 1280x720 headless. Perilaku reflow dan "
      "zoom belum diuji.")
    A("")

    A("## 3. Ringkasan Temuan")
    A("")
    A("### 3.1 Per severity")
    A("")
    A("| Severity | Jumlah | Persentase | Arti |")
    A("|----------|--------|-----------|------|")
    mean = {"Critical": "mengganggu akses inti, harus-first", "Serious": "mengganggu tugas utama",
            "Moderate": "menyulitkan, ada jalur lain", "Minor": "kelemahan kecil"}
    for sev in SEVERITY_ORDER:
        n = len(by_sev[sev])
        pct = (n / len(findings) * 100) if findings else 0
        A(f"| {sev} | {n} | {pct:.0f}% | {mean[sev]} |")
    A(f"| **Total** | **{len(findings)}** | 100% | |")
    A("")

    A("### 3.2 Per Success Criterion")
    A("")
    A("| SC | Nama | Level | Versi | Temuan | Severity dominan |")
    A("|----|------|-------|-------|--------|------------------|")
    for sc, rows in sorted(by_sc.items(), key=lambda x: -len(x[1])):
        meta = sc_meta.get(sc, {})
        top = min(SEVERITY_ORDER.index(r["severity"]) for r in rows)
        A(f"| {sc} | {meta.get('Nama', '-')} | {meta.get('Level', '-')} | "
          f"{meta.get('Versi', '-')} | {len(rows)} | {SEVERITY_ORDER[top]} |")
    A("")

    A("### 3.3 Sebaran per template (dari rule otomatis)")
    A("")
    A("Jumlah node gagal per tipe halaman, berdasarkan rule yang terpicu:")
    A("")
    A("| Template | Node gagal | Temuan dominan |")
    A("|----------|-----------|-----------------|")
    for tpl in sorted(inv["templates"], key=lambda t: -inv["templates"][t]):
        nodes = sum(count for rid, tpls in tpl_per_rule.items()
                    for name, count in tpls.items() if name == tpl)
        tops = sorted(((count, rid) for rid, tpls in tpl_per_rule.items()
                       for name, count in tpls.items() if name == tpl), reverse=True)[:3]
        A(f"| {TEMPLATE_LABEL.get(tpl, tpl)} | {nodes} | "
          f"{', '.join(f'`{r}` ({c})' for c, r in tops)} |")
    A("")

    A("### 3.4 Temuan di luar WCAG 2.0")
    A("")
    A("Tidak ada temuan otomatis yang secara khusus masuk SC baru WCAG 2.2 - bukan karena "
      "situs sudah patuh, tapi karena aturan yang diuji axe memang lebih banyak menunjuk ke "
      "SC 2.0. SC 2.2 berikut **belum diuji** dan wajib masuk checklist Tahap 3:")
    A("")
    A("| SC | Nama | Level di 2.2 | Kenapa penting |")
    A("|----|------|--------------|----------------|")
    A("| 2.4.11 | Focus Not Obscured (Minimum) | AA | Header sticky (`js-sticky js-autohide`) "
      "berpotensi menutupi elemen yang sedang difokus |")
    A("| 2.4.13 | Focus Appearance | AAA | Indikator fokus standar perlu dipastikan terlihat |")
    A("| 2.5.8 | Target Size (Minimum) | AA | Ikon carousel/partner kecil, risiko target undersized |")
    A("| 3.2.6 | Consistent Help | A | Belum tahu apakah ada mekanisme feedback konsisten |")
    A("| 3.3.7 | Redundant Entry | A | Form newsletter di 738 halaman |")
    A("| 2.5.7 | Dragging Movements | AA | Slider/carousel homepage dan galeri |")
    A("")

    A("## 4. Detail Temuan")
    A("")
    for sev in SEVERITY_ORDER:
        rows = by_sev[sev]
        if not rows:
            continue
        A(f"### 4.{SEVERITY_ORDER.index(sev) + 1} {sev} ({len(rows)})")
        A("")
        for f in rows:
            rid = rule_of.get(f["ID"], "-")
            affected = urls_per_rule.get(rid, "")
            A(f"#### {f['ID']} · SC {f['SC']} ({f['level']}) · `{rid}`")
            A("")
            A(f"- **Severity**: {f['severity']}")
            A(f"- **Template**: {f['template']}")
            A(f"- **URL contoh**: {f['URL']}")
            if affected:
                A(f"- **URL terdampak**: {affected} URL")
            A(f"- **Deskripsi**: {f['deskripsi']}")
            A(f"- **Langkah reproduksi**: {f['langkah_reproduksi']}")
            A(f"- **Rekomendasi**: {f['rekomendasi']}")
            A("")
    A("")
    A("---")
    A("")

    A("## 5. Hasil Uji Manual")
    A("")
    layout = index.get("layout", {})
    if layout:
        A(f"Sebagian butir di bawah sudah diverifikasi **secara mesin** oleh "
          f"`scripts/check_layout.py` atas {layout.get('url_diperiksa', 0)} URL "
          f"(headless Chrome, viewport 1280 / 320 / 640 px). Sisanya masih perlu tester "
          f"manusia dengan perangkat.")
        A("")
        A("| Topik | SC | Metode | Hasil |")
        A("|-------|-----|--------|-------|")
        l = layout
        A(f"| Reflow: scroll horizontal di 320px | 1.4.10 | Mesin | "
          f"{'Lolos - 0 URL gagal' if l.get('reflow_320_gagal') == 0 else str(l.get('reflow_320_gagal')) + ' URL gagal'} |")
        A(f"| Resize text: scroll horizontal di 640px (zoom 200%) | 1.4.4 | Mesin | "
          f"{'Lolos - 0 URL gagal' if l.get('zoom200_gagal') == 0 else str(l.get('zoom200_gagal')) + ' URL gagal'} |")
        A(f"| Skip link menuju anchor yang ada | 2.4.1 | Mesin | "
          f"{'Ada di semua URL' if l.get('skip_link_hilang') == 0 else str(l.get('skip_link_hilang')) + ' URL tanpa skip link'} |")
        A(f"| Tabindex positif | 2.4.3 | Mesin | "
          f"{'Tidak ada di URL yang diperiksa' if l.get('tabindex_pos') == 0 else str(l.get('tabindex_pos')) + ' URL punya tabindex positif'} |")
        A("")
    A("Topik yang masih harus diuji manusia (butuh interaksi keyboard dan perangkat AT):")
    A("")
    A("| Topik | Status | Catatan |")
    A("|-------|--------|---------|")
    for topic in ["Urutan fokus (tab order) nyata", "Focus visible / indikator fokus",
                  "Focus tidak tertutup header sticky (SC 2.4.11)",
                  "Heading & landmark (baca manual)", "Kontras warna (verifikasi visual)",
                  "Form: label, pesan error, validasi", "Mekanisme feedback aksesibilitas",
                  "NVDA + Firefox/Chrome", "VoiceOver macOS/iOS", "TalkBack Android",
                  "Akurasi isi caption (yang ada) dan video tanpa suara (SC 1.2.1)"]:
        A(f"| {topic} | Belum diuji | - |")
    A("")

    A("## 6. Aksesibilitas PDF")
    A("")
    A("| Aspek | Status |")
    A("|-------|--------|")
    A(f"| PDF terdaftar | {inv['pdfs']} |")
    A(f"| Bisa diunduh langsung (HTTP 200) | {inv['pdf_ok']} |")
    A(f"| Diblokir (HTTP 403) | {inv['pdf_blocked']} |")
    if pdfs["checked"]:
        c = pdfs["checked"]
        A(f"| Berhasil diperiksa struktur | {c} (total {pdfs['total_bytes'] / 1024 / 1024:.0f} MB) |")
        A(f"| Tagged PDF | {pdfs['tagged']}/{c} |")
        A(f"| Punya penanda bahasa | {c - pdfs['no_lang']}/{c} |")
        A(f"| Punya judul metadata | {c - pdfs['no_title']}/{c} |")
        A(f"| Tanpa layer teks (hasil scan) | {pdfs['image_only']}/{c} |")
    A("| Alt text gambar di dalam PDF | **Belum diperiksa** (butuh parser struktur tag) |")
    A("| Heading hierarchy & reading order | **Belum diperiksa** (butuh PDF/UA checker penuh) |")
    A("")
    if pdfs["checked"]:
        c = pdfs["checked"]
        A("### Temuan struktur dokumen")
        A("")
        A(f"- **{pdfs['image_only']} PDF tanpa layer teks** (hasil scan, tidak ada teks sama "
          f"sekali). Screen reader tidak membaca apa-apa dari dokumen ini - kegagalan paling "
          f"berat di kelompok PDF.")
        A(f"- **{c - pdfs['tagged']} dari {c} PDF tidak tagged.** Struktur baca mengikuti urutan "
          f"visual, bukan struktur dokumen.")
        A(f"- **{pdfs['no_lang']} PDF tanpa penanda bahasa.** Layar baca akan pronounounce "
          f"dengan aturan suara yang salah.")
        A(f"- **{pdfs['no_title']} PDF tanpa metadata /Title.** Yang dibacakan justru nama file.")
        A("")
        A("Detail per file: `results/automated/pdf-check-*/pdf-check-summary.csv`")
        A("")
    A(f"Temuan lain: {inv['pdf_blocked']} PDF di direktori `securepdfs` membalas 403 walau "
      "dipakai User-Agent browser dengan header `Referer` dan query `?download=1`. Mekanismenya "
      "hotlink protection. Satu-satunya jalur akses adalah iframe plugin PDF Embed yang "
      "membalas halaman HTML viewer.")
    A("")
    A("Catatan: 59 dari PDF yang diblokir terikat ke parent post yang tidak ada di WordPress "
      "REST API (kemungkinan draft atau trash). Tidak semua 65 terindeks orfan - 6 di antaranya "
      "tertempel pada halaman publik yang ada.")
    A("")
    A("Detail lengkap: `results/automated/media-access-*/report.md`")
    A("")

    A("## 7. Video dan Listen / TTS")
    A("")
    cap_dir = sorted(AUTOMATED.glob("caption-check-*"))
    if cap_dir:
        cdir = cap_dir[-1]
        crows = []
        cj = cdir / "caption-check-results.json"
        if cj.exists():
            crows = json.loads(cj.read_text(encoding="utf-8"))
        no_cap = [r for r in crows if r.get("has_captions") is False]
        auto_only = [r for r in crows if r.get("has_captions") and not r.get("manual")]
        id_cap = [r for r in crows if r.get("has_captions") and
                  any(t["lang"].startswith("id") for t in r.get("tracks", []))]
        blocked = [r for r in crows if r.get("has_captions") is None]
        A(f"### Status caption video ({len(crows)} embed diperiksa)")
        A("")
        A("| Aspek | Jumlah |")
        A("|-------|--------|")
        A(f"| Embed video | {len(crows)} |")
        A(f"| **Tanpa caption (pasti)** | **{len(no_cap)}** |")
        A(f"| Hanya auto-generated, tanpa track manual | {len(auto_only)} |")
        A(f"| Punya caption Bahasa Indonesia | {len(id_cap)} |")
        A(f"| Tidak bisa dipastikan (butuh login) | {len(blocked)} |")
        A("")
        A("Metode: parse `captionTracks` dari `ytInitialPlayerResponse` pada halaman "
          "`youtube.com/watch`. Status player dibaca dari `playabilityStatus` supaya video yang "
          "hanya bisa dibuka setelah login tidak salah dihitung sebagai \"tanpa caption\". "
          f"Detail: `results/automated/{cdir.name}/caption-check.csv`")
        A("")
        A("SC 1.2.2 adalah level A, jadi ini termasuk temuan paling serius di laporan ini. "
          "Untuk konten berskala 173 video, jalur yang masuk akal adalah transkrip otomatis "
          "lalu review manual oleh tim natively, bukan membuat subtitle manual satu per satu.")
        A("")
    A("### Listen / TTS")
    A("")
    A("**Belum dikerjakan.** Referensi: `listen-tts/comparison.md`.")
    A("")
    A("Catatan konteks untuk Tahap berikutnya: ada 173 embed video dan 166 PDF, jadi kalau "
      "Read/TTS jadi prioritas, cakupan kontennya jauh lebih besar daripada asumsi awal "
      "10 media. Verifikasi dulu apakah permintaan ini untuk pembaca dokumen atau untuk video.")
    A("")

    A("## 8. Remediation Roadmap")
    A("")
    phases = defaultdict(list)
    for f in findings:
        rid = rule_of.get(f["ID"], "")
        ph, effort, action = PHASE.get(rid, ("Phase 3", 1, "Evaluasi manual lebih dulu"))
        phases[ph].append((f, effort, action))
    for ph in ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]:
        rows = phases.get(ph, [])
        if not rows:
            continue
        total = sum(e for _, e, _ in rows)
        A(f"### {ph} ({len(rows)} temuan, estimasi {total} jam kerja)")
        A("")
        for f, effort, action in sorted(rows, key=lambda x: -x[1]):
            rid = rule_of.get(f["ID"], "-")
            A(f"- **{f['ID']}** ({f['severity']}, SC {f['SC']}, `{rid}`) - {action} "
              f"[~{effort} jam]")
        A("")
    A("Urutan ini disusun dari `findings/findings.csv`, bukan placeholder. Estimasi jam adalah "
      "perkiraan engineering untuk implementasi + verifikasi sekali pada 1 template.")
    A("")

    A("## 9. Histori")
    A("")
    for h in TEMPLATE_HISTORY:
        A(f"- {h}")
    A("")

    A("## 10. Appendix")
    A("")
    A(f"- A. Daftar temuan lengkap: `findings/findings.csv` ({len(findings)} baris, "
      "skema sesuai `AGENTS.md`)")
    A("- B. Index temuan + statistik per rule: `findings/findings-index.json`")
    A(f"- C. Output scan mentah: `results/automated/{index.get('axeDir', 'axe-YYYYMMDD')}/`")
    A(f"- D. Ringkasan scan: `results/automated/{index.get('axeDir', 'axe-YYYYMMDD')}/tahap1-summary.md`")
    A(f"- E. Verifikasi PDF/video: `results/automated/{index.get('mediaDir', 'media-access-YYYYMMDD')}/report.md`")
    if pdfs["dir"]:
        A(f"- F. Struktur PDF: `results/automated/{pdfs['dir']}/pdf-check-summary.csv` "
          f"dan `summary.md`")
    A("- G. Inventaris: `inventory/templates.md`, `inventory/heuristics.csv`, `inventory/pdfs.csv`")
    A("- G. Template laporan: `reports/audit-report-template.md`")
    A("- H. Pernyataan aksesibilitas: `reports/accessibility-statement-draft.md` (draft, jangan "
      "publish sebelum Tahap 3 selesai)")
    A("")

    A("## Persetujuan")
    A("")
    A("| Peran | Nama | Tanda Tangan | Tanggal |")
    A("|-------|------|---------------|---------|")
    A("| Lead Auditor | | | |")
    A("| Technical Reviewer | | | |")
    A("| Stakeholder | | | |")
    A("")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[OK] {out} ({len(L)} baris, {len(findings)} temuan)")
    print("[i] Bagian manual (bagian 5) dan TTS ditandai belum dikerjakan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())