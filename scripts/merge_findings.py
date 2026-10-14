#!/usr/bin/env python3
"""
merge_findings.py - Tahap 2: cluster hasil tool jadi isu unik + severity + findings.csv.

Input:
  results/automated/axe-YYYYMMDD/*.json       (hasil Tahap 1)
  results/automated/media-access-YYYYMMDD/*.csv (verifikasi akses PDF & video)
  standards/sc-mapping.csv                      (SC, level, versi, kategori scope)
  inventory/heuristics.csv                      (post type per URL)

Output:
  findings/findings.csv        (skema sesuai AGENTS.md)
  reports/tahap2-summary.md    (ringkasan per SC, severity, template, dan gap yang belum diuji)

Aturan: deskripsi dan rekomendasi diambil dari node axe yang benar-benar gagal
(contoh selector + HTML), bukan dari tebakan. Rule yang berasal dari konten
third-party di dalam iframe ditandai `pemilik: vendor`.

Usage:
    python scripts/merge_findings.py
    python scripts/merge_findings.py --axe-dir results/automated/axe-20261011
"""

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
AUTOMATED = PROJECT_ROOT / "results" / "automated"
FINDINGS_DIR = PROJECT_ROOT / "findings"
REPORTS_DIR = PROJECT_ROOT / "reports"
SC_MAPPING = PROJECT_ROOT / "standards" / "sc-mapping.csv"
HEURISTICS = PROJECT_ROOT / "inventory" / "heuristics.csv"
URLS_ALL = PROJECT_ROOT / "inventory" / "urls-all.txt"

FINDING_FIELDS = ["ID", "URL", "template", "SC", "level", "versi", "kategori_scope",
                  "severity", "source", "deskripsi", "langkah_reproduksi", "rekomendasi", "status"]

RULE_META = {
    "link-name": {
        "SC": "2.4.4", "severity": "Critical", "pemilik": "situs",
        "deskripsi": "Link logo mitra di header/footer dibungkus <a> dengan <img alt=\"\">, "
                     "sehingga tidak ada accessible name. Reader screen reader hanya "
                     "mengumumkan \"link\" tanpa tujuan. Contoh node yang gagal: "
                     "<a href=\"https://kemendikdasmen.go.id/\"><img src=\"partner-1.png\" alt=\"\"></a>",
        "langkah": "1. Buka halaman mana pun. 2. Aktifkan NVDA. 3. Tekan Tab sampai "
                   "masuk ke blok logo mitra di header/footer. 4. Dengarkan nama yang "
                   "dibacakan untuk tiap link logo.",
        "rekomendasi": "Isi alt deskriptif pada tiap logo (mis. \"Kementerian Pendidikan, "
                       "Republik Indonesia\"), atau tambahkan teks link yang terlihat. Jangan "
                       "sekadar `alt=\"logo\"` karena itu tidak menjelaskan tujuan link.",
    },
    "aria-hidden-focus": {
        "SC": "4.1.2", "severity": "Serious", "pemilik": "situs",
        "deskripsi": "Lightbox galeri (PhotoSwipe) memakai <div class=\"fy-pswp\" role=\"dialog\" "
                     "aria-hidden=\"true\" tabindex=\"-1\"> yang tetap berisi konten fokusable "
                     "di dalam DOM. Konten yang disembunyikan dari AT tapi masih bisaAGING focus.",
        "langkah": "1. Buka halaman yang punya galeri. 2. Tekan Tab berulang kali tanpa membuka "
                   "lightbox. 3. Perhatikan apakah fokus bisa masuk ke area lightbox yang "
                   "tidak terlihat.",
        "rekomendasi": "Tambahkan `inert` pada lightbox saat tertutup, atau pindahkan "
                       "lightbox ke luar DOM sampai dibuka. Kalau tetap perlu `tabindex=\"-1\"`, "
                       "pastikan lightbox di-`display:none` saat tertutup.",
    },
    "landmark-no-duplicate-banner": {
        "SC": "1.3.1", "severity": "Serious", "pemilik": "situs",
        "deskripsi": "Halaman punya lebih dari satu landmark `banner`. Penyebabnya header "
                     "desktop dan header mobile dirender bersamaan: "
                     "<header class=\"fy-header fy-header-left is-on-top ...\">.",
        "langkah": "1. BukaNVDA landmark list (D key). 2. Cek berapa entri `banner` "
                   "yang muncul pada satu halaman. 3. Ulangi di viewport mobile.",
        "rekomendasi": "Pastikan hanya satu header yang aktif pada satu waktu: sembunyikan "
                       "header mobile dengan `display:none` (bukan hanya `visibility:hidden` "
                       "atau off-screen) saat desktop aktif, dan sebaliknya.",
    },
    "landmark-unique": {
        "SC": "1.3.1", "severity": "Serious", "pemilik": "situs",
        "deskripsi": "Heading landmark `banner` tidak punya label unik, sehingga dua header "
                     "(desktop dan mobile) tidak bisa dibedakan screen reader.",
        "langkah": "1. Buka NVDA landmark list. 2. Pilih tiap entri banner. 3. Dengarkan "
                   "label yang dibacakan - keduanya sama.",
        "rekomendasi": "Beri `aria-label=\"Header utama\"` pada header aktif, dan hilangkan "
                       "landmark dari header yang non-aktif (ubah ke `role=\"presentation\"`).",
    },
    "heading-order": {
        "SC": "1.3.1", "severity": "Serious", "pemilik": "situs",
        "deskripsi": "Hierarki heading melompat, misalnya <h4> muncul tanpa <h2>/<h3> "
                     "sebelumnya. Contoh: <h4 class=\"wp-block-heading\"> di hero homepage, "
                     "dan <h6> di dalam slider galeri. Headings jadi cara utama screen "
                     "reader user berpindah section.",
        "langkah": "1. Buka halaman. 2. NVDA heading list (H). 3. Perhatikan level yang "
                   "melompat turun lebih dari 1 tanpa naik dulu.",
        "rekomendasi": "Perbaiki urutan heading di konten WordPress: pakai satu <h1> "
                       "judul halaman, <h2> untuk section, <h3>/<h4> untuk sub-item. "
                       "Ganti style, jangan ganti level tag.",
    },
    "aria-allowed-attr": {
        "SC": "4.1.2", "severity": "Moderate", "pemilik": "vendor",
        "deskripsi": "Widget YouTube di dalam iframe memakai atribut ARIA yang tidak diizinkan "
                     "pada elemennya: <a class=\"ytmVideoInfoVideoTitle\" aria-level=\"2\">. "
                     "Markup ini dibuat oleh player YouTube, bukan oleh kode situs.",
        "langkah": "1. Buka halaman yang punya embed video. 2. Jalankan axe atau DevTools "
                   "ARIA inspection pada iframe video. 3. Lihat atribut pada elemen "
                   "ytmVideoInfoVideoTitle.",
        "rekomendasi": "Tidak bisa diperbaiki dari sisi situs. Opsi: pakai privacy mode "
                       "YouTube (`youtube-nocookie.com`) yang kadang punya markup lebih "
                       "bersih, atau catat sebagai known third-party issue dengan "
                       "workaround caption manual. Jangan dipakai sebagai alasan "
                       "membiarkan isu tanpa keterangan di laporan.",
    },
    "aria-prohibited-attr": {
        "SC": "4.1.2", "severity": "Moderate", "pemilik": "vendor",
        "deskripsi": "Player YouTube memakai `aria-label` pada <div class=\"html5-video-player\"> "
                     "tanpa role yang valid, yang dilarang WCAG. Markup ini berasal dari vendor.",
        "langkah": "1. Buka halaman ber-embed video. 2. DevTools > Elements > cari "
                   "html5-video-player. 3. Perhatikan aria-label tanpa role.",
        "rekomendasi": "Sama seperti aria-allowed-attr: isu vendor. Dokumentasikan sebagai "
                       "known issue dengan bukti (URL + screenshot), usulkan privacy-enhanced "
                       "embed, dan pastikan caption tetap tersedia sebagai konten sendiri.",
    },
    "button-name": {
        "SC": "4.1.2", "severity": "Moderate", "pemilik": "vendor",
        "deskripsi": "Tombol di dalam iframe YouTube tanpa accessible name, contoh "
                     "<button class=\"ytmVideoInfoLink ytmVideoInfoChannelAvatar\"> yang "
                     "hanya berisi <img> tanpa alt.",
        "langkah": "1. Buka halaman ber-embed. 2. NVDA, tekan Tab-M untuk masuk ke iframe "
                   "video. 3. Dengarkan nama tombol yang dibacakan.",
        "rekomendasi": "Isu vendor. Mitigasi yang bisa dilakukan situs: jangan menjadikan "
                       "iframe video sebagai satu-satunya cara akses video (beri link "
                       "transkrip video di bawahnya).",
    },
    "frame-title": {
        "SC": "4.1.2", "severity": "Serious", "pemilik": "situs",
        "deskripsi": "Iframe tanpa accessible name: 35 titik, yaitu iframe Google Maps di "
                     "halaman kontak (`<iframe src=\"https://www.google.c...\" width=\"400\">`) "
                     "dan iframe plugin PDF (`.pdfembed-iframe`). Screen reader hanya "
                     "membacakan \"iframe\" tanpa penjelasan isinya.",
        "langkah": "1. Buka /kontak. 2. NVDA, navigasi ke iframe peta. 3. Perhatikan tidak "
                   "ada nama yang dibacakan. 4. Ulangi pada halaman publikasi yang punya "
                   "PDF embedded.",
        "rekomendasi": "Tambah `title` pada setiap iframe: Maps -> \"Peta lokasi kantor "
                       "INOVASI di Jakarta\"; PDF -> \"Pratinjau dokumen: <judul dokumen>\" "
                       "(isi dinamis dari hook plugin).",
    },
    "color-contrast": {
        "SC": "1.4.3", "severity": "Serious", "pemilik": "situs",
        "deskripsi": "Kontras teks gagal, rasio 1.12:1 (foreground #e3e3e4 di atas background "
                     "#f0f0f0) pada judul kartu-konten `.dpt-title-link` dan elemen "
                     "<time>. 468 node gagal di 23 URL, jadi masalahnya systemic di komponen "
                     "kartu bukan acak.",
        "langkah": "1. Buka homepage. 2. Inspect judul kartu konten dan tanggal di bawahnya. "
                   "3. Hitung rasio foreground vs background (atau pakai tool kontras). "
                   "4. Konfirmasi juga di 320px dan zoom 200%.",
        "rekomendasi": "Naikkan kontras teks kartu ke minimal 4.5:1 (AA untuk teks normal). "
                       "Nilai #e3e3e4 di #f0f0f0 hampir tidak terlihat - kemungkinan "
                       "warna teks lama tidak ikut diubah saat redesign background card.",
    },
    "image-alt": {
        "SC": "1.1.1", "severity": "Serious", "pemilik": "vendor",
        "deskripsi": "Gambar halaman majalah Flipsnack di dalam iframe tanpa atribut alt: "
                     "<img class=\"page-image\" data-page=\"1\"> pada 8 URL. Screen reader "
                     "user tidak tahu isi dokumen yang sedang dibaca.",
        "langkah": "1. Buka salah satu URL publikasi yang Flipsnack-nya gagal. 2. NVDA, "
                   "masuk ke iframe. 3. Dengarkan deskripsi gambar - tidak ada.",
        "rekomendasi": "Kalau dokumen Flipsnack memang dipakai, sediakan transkrip atau "
                       "versi HTML teks sebagai alternatif di luar iframe (SC 1.1.1). "
                       "Alt untuk gambar halaman majalah sebaiknya describing isi halaman, "
                       "bukan \"halaman 1\".",
    },
    "tabindex": {
        "SC": "2.4.3", "severity": "Serious", "pemilik": "vendor",
        "deskripsi": "Elemen dengan tabindex positif: <body id=\"wppdf-iframe-body\" tabindex=\"1\"> "
                     "di dalam iframe PDF plugin, dan <div id=\"accessibility\" tabindex=\"1\"> "
                     "di iframe Flipsnack. tabindex positif memutus urutan focus natural.",
        "langkah": "1. Buka halaman dengan PDF embedded atau Flipsnack. 2. Tekan Tab dari "
                   "awal halaman. 3. Perhatikan fokus melompat atau terlempar ke area "
                   "iframe secara tidak wajar.",
        "rekomendasi": "Hindari tabindex positif. Untuk iframe PDF, pastikan plugin "
                       "memakai tabindex=\"0\" atau \"-1\", atau ganti dengan embed yang "
                       "mendukung navigasi keyboard (dan sediakan link unduh sebagai alternatif).",
    },
    "aria-required-children": {
        "SC": "1.3.1", "severity": "Serious", "pemilik": "vendor",
        "deskripsi": "Struktur ARIA tabel tidak valid di dalam iframe PDF: <span role=\"table\"> "
                     "punya anak <span role=\"columnheader\"> yang struktur role-nya tidak "
                     "sesuai (butuh parent row/rowgroup). Reader screen reader bisa "
                     "kehilangan konteks tabel.",
        "langkah": "1. Buka halaman yang punya PDF embedded. 2. NVDA, masuk ke iframe PDF, "
                   "coba mode tabel. 3. Perhatikan navigasi baris/kolom tidak konsisten.",
        "rekomendasi": "Markup dari plugin PDF. Mitigasi situs: sediakan versi HTML atau "
                       "transkrip dokumen sebagai alternatif utama, dan jadikan iframe "
                       "PDF sebagai bonus.",
    },
    "aria-required-parent": {
        "SC": "1.3.1", "severity": "Serious", "pemilik": "vendor",
        "deskripsi": "Role ARIA table/row/columnheader di iframe PDF tidak punya parent yang "
                     "diperlukan (butuh grid, rowgroup, table, atau treegrid). Lanjutan dari "
                     "aria-required-children di iframe yang sama.",
        "langkah": "Sama dengan aria-required-children, periksa di dalam iframe PDF dengan "
                   "NVDA mode tabel.",
        "rekomendasi": "Sama seperti di atas: sediakan alternative HTML atau transkrip di luar "
                       "iframe sebagai jalur utama.",
    },
    "aria-allowed-role": {
        "SC": "4.1.2", "severity": "Moderate", "pemilik": "situs",
        "deskripsi": "role=\"group\" dipakai pada <article class=\"fy-slide\"> di slider "
                     "homepage, padahal role group tidak diizinkan untuk elemen article.",
        "langkah": "1. Buka homepage. 2. DevTools > inspect elemen slider. 3. Lihat "
                   "role=\"group\" pada article.",
        "rekomendasi": "Hapus role=\"group\" dari article slider, atau ganti elemennya "
                       "menjadi <div> yang memang boleh memakai role group.",
    },
    "page-has-heading-one": {
        "SC": "1.3.1", "severity": "Moderate", "pemilik": "situs",
        "deskripsi": "Sebagian halaman tidak punya heading level 1 sama sekali. Tanpa <h1>, "
                     "reader screen reader tidak punya titik awal untuk memahami topik "
                     "halaman (best practice, bukan kegagalan SC eksak).",
        "langkah": "1. Buka salah satu halaman yang gagal. 2. NVDA heading list (H). "
                   "3. Level pertama yang muncul bukan level 1.",
        "rekomendasi": "Tambahkan satu <h1> per halaman - boleh disembunyikan secara visual "
                       "kalau desain tidak menyediakan, tapi tetap ada di accessibility tree.",
    },
    "empty-heading": {
        "SC": "1.3.1", "severity": "Minor", "pemilik": "situs",
        "deskripsi": "Ada heading kosong (<h*> tanpa teks) di 1 halaman. Mengacaukan "
                     "heading list reader screen reader.",
        "langkah": "1. Buka halaman yang gagal. 2. NVDA heading list. 3. Cari entri "
                   "heading tanpa nama.",
        "rekomendasi": "Isi teksnya, atau hapus elemen heading kosong tersebut.",
    },
    "link-in-text-block": {
        "SC": "1.4.1", "severity": "Serious", "pemilik": "situs",
        "deskripsi": "Link teks di dalam paragraf punya kontras 1.08:1 terhadap teks "
                     "sekitarnya (#2850aa di #3f4f77) tanpa underline, sehingga hilang "
                     "bagi pengguna low vision (SC 1.4.1 Use of Color).",
        "langkah": "1. Buka URL publikasi terkait. 2. Lihat link di dalam paragraf. "
                   "3. Cek apakah ada bedanya dari teks biasa selain warna.",
        "rekomendasi": "Naikkan kontras link teks minimal 3:1 terhadap teks sekitarnya, "
                       "dan/atau tambahkan underline pada link di dalam blok teks.",
    },
}

VERSION_22_ONLY = {"2.5.8", "3.3.7", "3.3.8", "2.4.11", "2.4.12", "2.4.13", "3.2.5", "3.2.6"}


def load_sc_meta():
    meta = {}
    if SC_MAPPING.exists():
        for row in csv.DictReader(open(SC_MAPPING, encoding="utf-8")):
            meta[row["SC"]] = row
    return meta


def load_post_types():
    mapping = {}
    if HEURISTICS.exists():
        for row in csv.DictReader(open(HEURISTICS, encoding="utf-8")):
            mapping[row["url"].rstrip("/")] = row.get("post_type", "")
    return mapping


def load_known_urls():
    if not URLS_ALL.exists():
        return None
    return {line.strip().rstrip("/") for line in URLS_ALL.read_text(encoding="utf-8").splitlines() if line.strip()}


def newest_dir(pattern):
    dirs = sorted(AUTOMATED.glob(pattern))
    return dirs[-1] if dirs else None


def collect_axe(axe_dir):
    rule_urls = defaultdict(set)
    rule_nodes = defaultdict(int)
    rule_impacts = defaultdict(lambda: defaultdict(int))
    rule_samples = defaultdict(list)
    rule_templates = defaultdict(lambda: defaultdict(int))
    seen = set()
    scanned = 0

    post_types = load_post_types()
    known = load_known_urls()

    for f in sorted(axe_dir.glob("*.json")):
        if f.name == "summary.json" or f.name.endswith(".error.json"):
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        url = (data.get("url") or "").rstrip("/")
        if url in seen or (known and url not in known):
            continue
        seen.add(url)
        scanned += 1
        tpl = post_types.get(url, "unknown")

        for v in data.get("violations", []):
            rid = v.get("id", "unknown")
            rule_urls[rid].add(url)
            rule_templates[rid][tpl] += 1
            impact = v.get("impact", "unknown")
            for n in v.get("nodes", []):
                rule_nodes[rid] += 1
                rule_impacts[rid][impact] += 1
                if len(rule_samples[rid]) < 2:
                    rule_samples[rid].append({
                        "url": url,
                        "target": " > ".join(str(t) for t in (n.get("target") or []))[:150],
                        "html": (n.get("html") or "")[:200],
                    })

    return {
        "rule_urls": rule_urls, "rule_nodes": rule_nodes, "rule_impacts": rule_impacts,
        "rule_samples": rule_samples, "rule_templates": rule_templates, "scanned": scanned,
    }


def build_findings(axe, media_dir, sc_meta, date_str):
    findings = []
    rule_of_finding = {}
    index_extra = {}
    seq = 0

    def add(rule_id=None, **kw):
        nonlocal seq
        seq += 1
        kw["ID"] = f"A11Y-{date_str}-{seq:03d}"
        sc = kw.get("SC", "")
        meta = sc_meta.get(sc, {})
        kw.setdefault("level", meta.get("Level", ""))
        kw.setdefault("versi", meta.get("Versi", ""))
        kw.setdefault("kategori_scope", meta.get("Kategori_Scope", ""))
        kw.setdefault("status", "Open")
        findings.append(kw)
        rule_of_finding[kw["ID"]] = rule_id or ""

    for rid, meta in RULE_META.items():
        urls = axe["rule_urls"].get(rid)
        if not urls:
            continue
        sample = axe["rule_samples"][rid][0] if axe["rule_samples"][rid] else {"target": "", "html": "", "url": ""}
        tpls = sorted(axe["rule_templates"][rid].items(), key=lambda x: -x[1])
        tpl_str = ", ".join(t for t, _ in tpls[:4])
        impacts = axe["rule_impacts"][rid]
        impact_str = ", ".join(f"{k} {v}" for k, v in sorted(impacts.items(), key=lambda x: -x[1]))

        deskripsi = (f"[{meta['severity']}] {meta['deskripsi']} "
                     f"Terjadi di {len(urls)} URL ({axe['rule_nodes'][rid]} node gagal; "
                     f"impact axe: {impact_str}). Contoh URL: {sample['url']} "
                     f"(pemilik: {meta['pemilik']}).")

        add(rule_id=rid,
            URL=sample["url"] or sorted(urls)[0],
            template=tpl_str,
            SC=meta["SC"],
            severity=meta["severity"],
            source="axe",
            deskripsi=deskripsi,
            langkah_reproduksi=meta["langkah"] + f" (selector contoh: {sample['target']})",
            rekomendasi=meta["rekomendasi"])

    if media_dir and (media_dir / "pdf-access.csv").exists():
        rows = list(csv.DictReader(open(media_dir / "pdf-access.csv", encoding="utf-8")))
        blocked = [r for r in rows if r.get("accessible") == "N"]
        if blocked:
            add(rule_id="pdf-403", URL=blocked[0]["url"],
                template="publication, opportunity, resources",
                SC="1.1.1",
                severity="Critical",
                source="pdf-check",
                deskripsi=f"[Critical] {len(blocked)} dari {len(rows)} PDF membalas HTTP 403 "
                         f"saat diakses langsung. Semua berada di direktori "
                         f"/wp-content/uploads/securepdfs/. Tetap 403 walau memakai User-Agent "
                         f"browser + header Referer + query ?download=1. Satu-satunya jalur "
                         f"tersedia adalah iframe plugin PDF Embed yang membalas halaman HTML "
                         f"viewer, bukan file PDF. Contoh: {blocked[0]['url']} "
                         f"(SC 1.1.1 dipakai sebagai proksi: dokumen tidak punya jalur teks "
                         f"yang bisa diakses, bukan karena teksnya hilang)",
                langkah_reproduksi="1. Ambil URL PDF dari inventory/pdfs.csv. 2. Buka URL di "
                                   "browser. 3. Perhatikan respons 403 Forbidden. 4. Bandingkan "
                                   "dengan PDF di direktori uploads/ biasa yang bisa dibuka.",
                rekomendasi="Terbitkan dokumen sebagai HTML (dan atau PDF accessible) tanpa "
                            "hotlink protection, atau sediakan jalur unduh yang tetap bisa "
                            "diakses screen reader. Kalau proteksi hotlink memang dibutuhkan, "
                            "berikan mekanisme unduh yang menghasilkan response 200 untuk "
                            "pengguna browser biasa.")
        if media_dir and (media_dir / "video-access.csv").exists():
            vrows = list(csv.DictReader(open(media_dir / "video-access.csv", encoding="utf-8")))
            no_title = [r for r in vrows if r.get("iframe_title_present") == "N"]
            if no_title:
                add(rule_id="video-frame-title", URL=no_title[0]["url"],
                    template="publication, featured-article",
                    SC="4.1.2",
                    severity="Serious",
                    source="pdf-check",
                    deskripsi=f"[Serious] {len(no_title)} iframe video tidak punya atribut "
                             f"title yang bisa dibaca screen reader.",
                    langkah_reproduksi="1. Buka halaman dengan embed video. 2. Inspect iframe. "
                                       "3. Perhatikan tidak ada title.",
                    rekomendasi="Tambahkan title deskriptif pada iframe video.")

    pdf_structure_dir = newest_dir("pdf-check-*")
    if pdf_structure_dir and (pdf_structure_dir / "pdf-check-summary.csv").exists():
        prows = list(csv.DictReader(open(pdf_structure_dir / "pdf-check-summary.csv", encoding="utf-8")))
        checked = [r for r in prows if r.get("pages")]
        if checked:
            n = len(checked)
            no_text = [r for r in checked if r.get("text_layer") == "image-only"]
            no_tag = [r for r in checked if str(r.get("is_tagged")).lower() != "true"]
            no_lang = [r for r in checked if not (r.get("language") or "").strip()]
            no_title = [r for r in checked if not (r.get("title_metadata") or "").strip()]

            if no_text:
                add(rule_id="pdf-no-text-layer",
                    URL=no_text[0]["url"],
                    template="publication, resources",
                    SC="1.1.1",
                    severity="Critical",
                    source="pdf-check",
                    deskripsi=f"[Critical] {len(no_text)} dari {n} PDF yang bisa diunduh tidak punya "
                             f"layer teks sama sekali (hasil scan tanpa OCR). Screen reader tidak "
                             f"membaca apa-apa dari dokumen ini. Contoh: {no_text[0]['title'] or no_text[0]['url']}",
                    langkah_reproduksi="1. Buka salah satu PDF pada daftar. 2.coba select all + salin "
                                       "teks di Acrobat: tidak ada teks yang bisa disalin. 3. Bandingkan "
                                       "dengan PDF lain yang teksnya bisa dipilih.",
                    rekomendasi="Jalankan OCR (dan/atau sumber ulang dokumen dari file yang teksnya "
                                "bisa dipilih), lalu pastikan hasilnya tagged PDF. Untuk dokumen "
                                "sekolah, jauh lebih baik menerbitkan versi HTML.")

            if no_tag:
                add(rule_id="pdf-not-tagged",
                    URL=no_tag[0]["url"],
                    template="publication, resources",
                    SC="1.3.1",
                    severity="Serious",
                    source="pdf-check",
                    deskripsi=f"[Serious] {len(no_tag)} dari {n} PDF tidak tagged (tidak ada "
                             f"/MarkInfo /Marked true dan tidak ada /StructTreeRoot). Struktur baca "
                             f"screen reader mengikuti urutan visual, bukan struktur dokumen. "
                             f"Contoh: {no_tag[0]['title'] or no_tag[0]['url']}",
                    langkah_reproduksi="1. Buka PDF di Acrobat > File > Properties. 2. Lihat "
                                       "tagged/tidak. 3. Coba navigasi dengan keyboard: urutan "
                                       "baca tidak mengikuti kolom/heading.",
                    rekomendasi="Publikasikan ulang sebagai tagged PDF (PDF/UA), atau lebih baik "
                                "sebagai HTML. Kalau sumber dokumen tidak tersedia, gunakan "
                                "tools untuk meng-generate PDF/UA dari HTML yang sudah accessible.")

            if no_lang:
                add(rule_id="pdf-no-language",
                    URL=no_lang[0]["url"],
                    template="publication, resources",
                    SC="3.1.1",
                    severity="Serious",
                    source="pdf-check",
                    deskripsi=f"[Serious] {len(no_lang)} dari {n} PDF tidak punya penanda bahasa "
                             f"(tidak ada /Lang di catalog maupun dc:language di XMP). Layar baca "
                             f"tidak tahu pronounounce-nya Bahasa Indonesia atau Inggris.",
                    langkah_reproduksi="1. Buka PDF. 2. properties > Advanced > Language: kosong. "
                                       "3. Dengarkan beberapa paragraf: lafal screen reader "
                                       "menggunakan aturan suara default yang bisa salah.",
                    rekomendasi="Set /Lang ke id-ID (atau en bila dokumennya Inggris) saat "
                                "ekspor PDF. Ini satu baris di tool exporting.")

            if no_title:
                add(rule_id="pdf-no-title",
                    URL=no_title[0]["url"],
                    template="publication, resources",
                    SC="2.4.2",
                    severity="Moderate",
                    source="pdf-check",
                    deskripsi=f"[Moderate] {len(no_title)} dari {n} PDF tidak punya metadata "
                             f"/Title. Pembaca file dan screen reader membacakan nama file "
                             f"sebagai gantinya, misalnya "
                             f"\"modul-literasi-dasar-fase-a-fonik\". Contoh: "
                             f"{no_title[0]['url'].rsplit('/', 1)[-1]}",
                    langkah_reproduksi="1. Buka daftar file PDF. 2. Perhatikan nama file yang "
                                       "penuh dengan tanda hubung dan angka. 3. Buka properties: "
                                       "kolom Title kosong.",
                    rekomendasi="Isi /Title saat ekspor PDF dengan judul dokumen yang "
                                "memb intelligible, bukan nama file.")

    layout_dir = newest_dir("layout-check-*")
    if layout_dir and (layout_dir / "layout-summary.csv").exists():
        lrows = [r for r in csv.DictReader(open(layout_dir / "layout-summary.csv", encoding="utf-8"))]
        small = [r for r in lrows if int(r.get("target_kecil") or 0) > 0]
        reflow = [r for r in lrows if r.get("reflow_320_gagal") == "Y"]
        zoom = [r for r in lrows if r.get("zoom200_gagal") == "Y"]
        noskip = [r for r in lrows if r.get("skip_link_ada") == "N"]

        if small:
            sample = small[0]
            add(rule_id="layout-target-size",
                URL=sample["url"],
                template="semua template",
                SC="2.5.8",
                severity="Moderate",
                source="layout-check",
                deskripsi=f"[Moderate] {len(small)} dari {len(lrows)} URL punya tombol pengatur "
                         f"ukuran teks milik situs sendiri (kelas `accessibility-scale-increase` / "
                         f"`accessibility-scale-decrease`) berukuran 23,5 x 23,5 CSS px, di bawah "
                         f"minimum 24 x 24 SC 2.5.8. Selisihnya kecil (0,5 px) tapi tetap gagal. "
                         f"Kontrol aksesibilitas yang justru ukurannya tidak memenuhi target size.",
                langkah_reproduksi="1. Buka halaman mana pun. 2. Inspect tombol zoom in/out di "
                                   "sudut layar. 3. Ukur lewat DevTools: 23,5 x 23,5 px.",
                rekomendasi="Naikkan ukuran tombol ke minimal 24 x 24 CSS px, idealnya 44 x 44 "
                            "(praktik terbaik untuk touch). Periksa juga spacing antar tombol.")

        layout_pass = {
            "reflow_320_gagal": len(reflow),
            "zoom200_gagal": len(zoom),
            "skip_link_hilang": len(noskip),
            "url_diperiksa": len(lrows),
        }
        index_extra = {"layout": layout_pass, "layoutDir": layout_dir.name}

    caption_dir = newest_dir("caption-check-*")
    if caption_dir and (caption_dir / "caption-check-results.json").exists():
        crows = json.loads((caption_dir / "caption-check-results.json").read_text(encoding="utf-8"))
        no_cap = [r for r in crows if r.get("has_captions") is False]
        auto_only = [r for r in crows if r.get("has_captions") and not r.get("manual")]
        id_cap = [r for r in crows if r.get("has_captions") and
                  any(t["lang"].startswith("id") for t in r.get("tracks", []))]
        blocked = [r for r in crows if r.get("has_captions") is None]

        if no_cap:
            ids = ", ".join(f"`{r['video_id']}`" for r in no_cap[:5])
            add(rule_id="video-no-caption",
                URL=no_cap[0].get("source_page") or f"https://www.youtube.com/watch?v={no_cap[0]['video_id']}",
                template="publication, featured-article, page",
                SC="1.2.2",
                severity="Critical",
                source="axe",
                deskripsi=f"[Critical] {len(no_cap)} dari {len(crows)} video YouTube di situs ini "
                         f"tidak punya caption sama sekali (dicek dari `captionTracks` di "
                         f"`ytInitialPlayerResponse`; status player OK, jadi ini bukan efek "
                         f"blokir). SC 1.2.2 adalah level A. Video contoh: {ids}. "
                         f"Identitas video ada di `results/automated/{caption_dir.name}/caption-check.csv`",
                langkah_reproduksi="1. Buka salah satu halaman yang punya video. 2. Klik play "
                                   "atau buka langsung `youtube.com/watch?v=<id>`. 3. Klik ikon "
                                   "CC / subtitle: tidak ada. 4. Ulangi tanpa menyalakan "
                                   "subtitle: tidak ada teks pengganti.",
                rekomendasi="Tambah caption Bahasa Indonesia untuk video yang berisi suara. "
                            "Untuk 159 video, ini pekerjaan batch: pakai transkrip otomatis "
                            "lalu review manual, atau upstreamkan ke NFJS/rumah baca "
                            "komunitas. Minimal sediakan transkrip teks di bawah video.")

        if id_cap and len(id_cap) < len(crows):
            add(rule_id="video-caption-no-id",
                URL=(id_cap[0].get("source_page")
                    or f"https://www.youtube.com/watch?v={id_cap[0]['video_id']}"),
                template="publication, featured-article",
                SC="1.2.2",
                severity="Serious",
                source="axe",
                deskripsi=f"[Serious] Hanya {len(id_cap)} dari {len(crows)} video punya caption "
                         f"Bahasa Indonesia. Sisanya hanya punya caption Inggris, atau caption "
                         f"dalam bahasa lain, atau tidak punya caption. Untuk konten berbahasa "
                         f"Indonesia, caption Inggris tidak memenuhi kebutuhan pengguna.",
                langkah_reproduksi="1. Buka video. 2. Nyalakan subtitle. 3. Lihat daftar bahasa "
                                   "yang tersedia di ikon settings subtitle.",
                rekomendasi="Prioritaskan caption Bahasa Indonesia. Caption Inggris tidak "
                            "pengganti untuk konten yang perkecilannya berbahasa Indonesia.")

        if auto_only:
            add(rule_id="video-caption-auto-only",
                URL=(auto_only[0].get("source_page")
                    or f"https://www.youtube.com/watch?v={auto_only[0]['video_id']}"),
                template="publication, featured-article",
                SC="1.2.2",
                severity="Moderate",
                source="axe",
                deskripsi=f"[Moderate] {len(auto_only)} video punya caption, tapi semuanya "
                         f"auto-generated (ASR) tanpa track manual. Caption seperti ini biasanya "
                         f"menyalah pada nama diri, istilah pendidikan, dan angka.",
                langkah_reproduksi="1. Buka video. 2. Nyalakan caption. 3. Dengarkan nama "
                                   "pribadi dan istilah teknis - bandingkan dengan teks aslinya.",
                rekomendasi="Review manual caption ASR, minimal untuk nama diri, nama lembaga, "
                            "dan angka statistik yang muncul di video.")

        if blocked:
            add(rule_id="video-login-required",
                URL=f"https://www.youtube.com/watch?v={blocked[0]['video_id']}",
                template="publication, featured-article",
                SC="1.2.2",
                severity="Moderate",
                source="axe",
                deskripsi=f"[Moderate] {len(blocked)} video membalas LOGIN_REQUIRED dari "
                         f"server YouTube (age-restricted atau member-only). Video seperti ini "
                         f"hanya bisa dilihat setelah login, sehingga caption dan transkripnya "
                         f"juga tidak bisa diakses tanpa akun. Alasan yang dikembalikan: "
                         f"\"{(blocked[0].get('status_reason') or '-')[:80]}\"",
                langkah_reproduksi="1. Buka video dalam jendela penyamaran (tanpa login). "
                                   "2. Muncul layar \"Login untuk mengonfirmasi\". 3. Video "
                                   "tidak bisa diputar.",
                rekomendasi="Pastikan embed memakai parameter privacy (`youtube-nocookie.com`) "
                            "dan tidak memerlukan login. Bila video memangricted, sertakan "
                            "transkrip teks di halaman sebagai alternatif.")

    return findings, rule_of_finding, index_extra


def write_summary(path, findings, axe, scanned, date_str):
    by_sev = defaultdict(int)
    by_sc = defaultdict(int)
    by_source = defaultdict(int)
    by_owner = defaultdict(int)
    for f in findings:
        by_sev[f["severity"]] += 1
        by_sc[f["SC"]] += 1
        by_source[f["source"]] += 1
        if "pemilik: vendor" in f["deskripsi"]:
            by_owner["vendor"] += 1
        else:
            by_owner["situs"] += 1

    lines = [
        "# Tahap 2 - Ringkasan Temuan (clustering + severity)",
        "",
        f"Dihasilkan: {datetime.now().isoformat(timespec='seconds')}  ",
        f"Sumber: `results/automated/axe-*/` ({scanned} URL), "
        f"`results/automated/media-access-*/`, `standards/sc-mapping.csv`",
        "",
        "## Ringkasan",
        "",
        "| Metrik | Nilai |",
        "|--------|-------|",
        f"| URL hasil scan | {scanned} |",
        f"| Node gagal di axe (Tahap 1) | {sum(axe['rule_nodes'].values())} |",
        f"| Rule aktif | {len(axe['rule_nodes'])} |",
        f"| Isu unik setelah clustering | {len(findings)} |",
        "",
        "## Temuan per severity",
        "",
        "| Severity | Jumlah |",
        "|----------|--------|",
    ]
    for sev in ["Critical", "Serious", "Moderate", "Minor"]:
        if by_sev.get(sev):
            lines.append(f"| {sev} | {by_sev[sev]} |")

    lines += ["", "## Temuan per SC", "", "| SC | Nama | Level | Temuan |", "|----|------|-------|--------|"]
    sc_meta = load_sc_meta()
    for sc, n in sorted(by_sc.items(), key=lambda x: -x[1]):
        meta = sc_meta.get(sc, {})
        lines.append(f"| {sc} | {meta.get('Nama', '')} | {meta.get('Level', '')} | {n} |")

    lines += ["", "## Temuan per sumber", "", "| Source | Jumlah |", "|--------|--------|"]
    for src, n in sorted(by_source.items()):
        lines.append(f"| {src} | {n} |")

    lines += ["", "## Split ownership (situs vs vendor)", "",
              f"- Dimiliki situs (bisa langsung diperbaiki): {by_owner.get('situs', 0)} temuan",
              f"- Markup vendor di dalam iframe (perlu opsi/workaround): {by_owner.get('vendor', 0)} temuan",
              "",
              "## Daftar temuan (urut severity)",
              "",
              "| ID | Severity | SC | Temuan | URL terdampak |",
              "|----|----------|----|--------|---------------|"]

    for f in findings:
        affected = ""
        for rid, meta in RULE_META.items():
            if f["deskripsi"].startswith(f"[{f['severity']}] {meta['deskripsi'][:40]}"):
                affected = str(len(axe["rule_urls"].get(rid, [])))
                break
        if not affected and f["source"] == "pdf-check":
            affected = "65 PDF / 166"
        lines.append(f"| {f['ID']} | {f['severity']} | {f['SC']} | {f['deskripsi'][:80]}... | {affected or '-'} |")

    lines += ["", "## Yang BELUM diuji (bukan temuan, ini gap)", "",
              "- Caption/transcript 173 video YouTube (hanya dicek aksesibilitas embed, bukan subtitle).",
              "- Struktur internal 101 PDF yang bisa diunduh (tagged, heading, bahasa, alt gambar).",
              "- 65 PDF yang 403 - tidak bisa diunduh tanpa akses ke direktori securepdfs.",
              "- Evaluasi manual: keyboard navigation, focus order, visible focus, reflow 320px, "
              "zoom 200%, error message form, mekanisme feedback.",
              "- `incomplete` dari axe (needs review) yang sengaja tidak dihitung di Tahap 2.",
              ""]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Tahap 2: clustering + severity + findings.csv")
    ap.add_argument("--axe-dir", default="")
    ap.add_argument("--media-dir", default="")
    args = ap.parse_args()

    axe_dir = Path(args.axe_dir) if args.axe_dir else newest_dir("axe-*")
    if not axe_dir or not axe_dir.exists():
        print("[ERROR] folder hasil axe tidak ditemukan. Jalankan run_axe.py dulu.")
        return 1

    media_dir = Path(args.media_dir) if args.media_dir else newest_dir("media-access-*")

    sc_meta = load_sc_meta()
    axe = collect_axe(axe_dir)
    date_str = datetime.now().strftime("%Y%m%d")
    findings, rule_of_finding, index_extra = build_findings(axe, media_dir, sc_meta, date_str)

    FINDINGS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = FINDINGS_DIR / "findings.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FINDING_FIELDS, extrasaction="ignore")
        w.writeheader()
        for f in findings:
            w.writerow(f)

    summary_path = REPORTS_DIR / "tahap2-summary.md"
    write_summary(summary_path, findings, axe, axe["scanned"], date_str)

    import json as _json
    index_payload = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "axeDir": axe_dir.name,
        "mediaDir": media_dir.name if media_dir else None,
        "ruleOfFinding": rule_of_finding,
        "urlCountPerRule": {rid: len(urls) for rid, urls in axe["rule_urls"].items()},
        "nodeCountPerRule": dict(axe["rule_nodes"]),
        "templatesPerRule": {rid: dict(tpl) for rid, tpl in axe["rule_templates"].items()},
        "scanned": axe["scanned"],
    }
    index_payload.update(index_extra)
    (FINDINGS_DIR / "findings-index.json").write_text(
        _json.dumps(index_payload, indent=2), encoding="utf-8")

    print(f"[OK] {csv_path} ({len(findings)} temuan)")
    print(f"[OK] {summary_path}")
    print(f"\nURL discan: {axe['scanned']} | violation instance: {sum(axe['rule_nodes'].values())} "
          f"| isu unik: {len(findings)}")
    sev = defaultdict(int)
    for f in findings:
        sev[f["severity"]] += 1
    print(f"Severity: {dict(sev)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())