# Accessibility QA Workspace - inovasi.or.id

Workspace untuk audit aksesibilitas website https://inovasi.or.id berdasarkan WCAG 2.2 Level AA (dipetakan ke WCAG 2.0 Level AA).

## Struktur Direktori

```
.
├── README.md
├── AGENTS.md
├── planning/
│   └── tasklist.md             # tasklist & estimasi effort (jam/manday)
├── standards/
│   ├── wcag-2.0-vs-2.2.md
│   └── sc-mapping.csv
├── inventory/
│   ├── urls.txt               # URL hasil crawl (dipakai run_axe / run_lighthouse)
│   ├── urls-all.txt           # semua URL unik dari sitemap
│   ├── templates.md           # template halaman + jumlah URL + 1 contoh tiap template
│   ├── pdfs.csv               # PDF (URL, judul, ukuran, status HTTP, sumber penemuan)
│   ├── media.csv              # video/audio/iframe (URL, platform, embed, caption)
│   ├── heuristics.csv         # hitung cepat img/alt/h1/iframe/form per URL
│   ├── machine-time-estimate.md  # estimasi durasi mesin Fase 1-2
│   ├── logs/                  # log crawl bertanggal
│   └── .cache/                # cache ekstraksi (idempoten, run ulang tidak re-fetch)
├── scripts/
│   ├── crawl_inventory.py
│   ├── run_axe.py
│   ├── run_lighthouse.py
│   ├── check_pdfs.py
│   └── merge_findings.py
├── results/
│   ├── automated/
│   └── manual/
├── findings/
│   ├── findings.csv
│   └── findings-template.md
├── testing/
│   ├── test-plan.md
│   ├── manual-checklist.md
│   └── screen-reader-script.md
├── listen-tts/
│   ├── comparison.md
│   └── poc/
└── reports/
    ├── audit-report-template.md
    └── accessibility-statement-draft.md
```

## Instalasi Dependensi

### Python
```bash
pip install -r requirements.txt
```

### Node.js (untuk axe-core, Pa11y, Lighthouse CLI)
```bash
npm install
```

## Menjalankan Audit

### 1. Inventory (Kumpulkan URL, PDF, Media)
```bash
python scripts/crawl_inventory.py                          # sampel: 5 URL per post type + semua halaman statis
python scripts/crawl_inventory.py --sample-per-type 10     # sampel lebih lebar
python scripts/crawl_inventory.py --full-crawl --pdf-probe  # census semua URL + HEAD tiap PDF (±35 menit)
```
Output: `inventory/urls.txt`, `inventory/urls-all.txt`, `inventory/templates.md`, `inventory/pdfs.csv`,
`inventory/media.csv`, `inventory/heuristics.csv`, `inventory/machine-time-estimate.md`

Scan otomatis hanya perlu halaman utama. `urls-utama.txt` sudah dibuat otomatis
(halaman statis + home ID/EN + 1 URL contoh tiap post type = 1 URL per template):
```bash
python scripts/run_axe.py        --urls-file inventory/urls-utama.txt
python scripts/run_lighthouse.py --urls-file inventory/urls-utama.txt
```

### 2. Scan Otomatis - axe-core
```bash
python scripts/run_axe.py
```
Output: `results/automated/axe-YYYYMMDD/`

### 3. Scan Otomatis - Lighthouse (aksesibilitas saja)
```bash
python scripts/run_lighthouse.py
```
Output: `results/automated/lighthouse-YYYYMMDD/`

### 4. Cek Akses PDF & Video (ringkas, tanpa caption/tag)
```bash
python scripts/check_media_access.py
```
Output: `results/automated/media-access-YYYYMMDD/` (`pdf-access.csv`, `video-access.csv`, `summary.json`)
Hanya jawab "bisa diakses / diunduh / dibuka atau tidak". Tidak memeriksa caption atau struktur PDF.

### 5. Cek Caption Video (SC 1.2.2)
```bash
python scripts/check_captions.py
```
Output: `results/automated/caption-check-YYYYMMDD/`
Parse `captionTracks` dari `ytInitialPlayerResponse`, tanpa API key. Video yang hanya bisa
dibuka setelah login dibaca statusnya dari `playabilityStatus` supaya tidak salah dihitung.

### 6. Cek Layout (reflow, zoom, skip link, target size)
```bash
python scripts/check_layout.py --urls-file inventory/urls-utama.txt
python scripts/check_layout.py --urls-file inventory/urls-all.txt --concurrency 3
```
Output: `results/automated/layout-check-YYYYMMDD/` (`layout-summary.csv`, `summary.md`)

### 7. Cek Aksesibilitas PDF (struktur dasar)
```bash
python scripts/check_pdfs.py
```
Output: `results/automated/pdf-check-YYYYMMDD/`

### 8. Gabungkan Temuan (Tahap 2)
```bash
python scripts/merge_findings.py
```
Output: `findings/findings.csv` (19 temuan unik), `findings/findings-index.json`, `reports/tahap2-summary.md`

### 9. Susun Draft Laporan
```bash
python scripts/build_report.py
```
Output: `reports/audit-report-draft.md` (dibangun dari `findings.csv`, bagian manual ditandai "belum diuji")

### Ringkasan alur
```bash
python scripts/crawl_inventory.py --full-crawl --pdf-probe   # Tahap 0: inventaris
python scripts/run_axe.py --urls-file inventory/urls-all.txt --concurrency 3   # Tahap 1: scan (~38 mnt)
python scripts/check_media_access.py                        # verifikasi akses PDF/video
python scripts/check_layout.py --urls-file inventory/urls-all.txt # reflow, zoom, skip link, target size
python scripts/check_captions.py                                # caption 173 video
python scripts/check_pdfs.py                                    # struktur dasar 101 PDF
python scripts/summarize_axe.py                            # ringkasan Tahap 1
python scripts/merge_findings.py                            # Tahap 2: clustering + severity
python scripts/build_report.py                              # draft laporan
```

## Audit Otomatis (Tahap 1)
```bash
python scripts/run_axe.py --urls-file inventory/urls-all.txt --concurrency 3
python scripts/run_axe.py --urls-file inventory/urls-utama.txt --concurrency 3
python scripts/summarize_axe.py
```
Runner `scripts/axe_runner.js` memakai satu instance Chrome untuk seluruh URL dengan 3 tab paralel.
Scan 738 URL butuh ~38 menit. Bisa diulang (`resume`): JSON yang sudah ada dilewati.

## Uji Manual / Assistive Technology

Lihat `testing/test-plan.md` untuk matriks browser/AT:
- NVDA + Firefox / Chrome (Windows)
- VoiceOver + Safari / iOS (macOS/iOS)
- TalkBack + Chrome (Android)

Gunakan `testing/manual-checklist.md` per template.

## Laporan

- Template laporan: `reports/audit-report-template.md`
- Draft pernyataan aksesibilitas: `reports/accessibility-statement-draft.md`

## Feasibility Listen/TTS

Lihat `listen-tts/comparison.md` untuk perbandingan:
- ReadSpeaker
- Web Speech API
- Cloud TTS (Google, Azure, AWS)

PoC Web Speech API: `listen-tts/poc/`

## Kendala

Terisi setelah run `crawl_inventory.py` (11 Okt 2026):

1. **Sitemap Yoast duplikat** - `publication-sitemap.xml` berisi 1000 entri tapi hanya 619 URL unik
   (461 URL muncul 2x). Setelah dinormalisasi (buang query/fragment/trailing slash) total situs
   **738 URL unik**, bukan 1203.
2. **URL `?post_type=...&p=...`** - 4 URL di sitemap bentuk query, bukan permalink. Dilewati.
3. **65 dari 166 PDF membalas HTTP 403** - semua di direktori `/wp-content/uploads/securepdfs/`.
   Tetap 403 walau pakai User-Agent browser + `Referer` + `?download=1`. Cuma bisa dibuka lewat
   iframe plugin "PDF Embed" (`?pdfemb-data=`) yang membalas HTML viewer, bukan file PDF.
   Dari 65 itu, **59 PDF terikat ke parent post yang 404 di WP REST API** (draft/trash/post
   dihapus) - kemungkinan besar file sisa. Detail: `results/automated/media-access-YYYYMMDD/report.md`.
   `check_pdfs.py` hanya bisa mengunduh 101 PDF yang status 200.
4. **Base URL harus `www`** - `https://inovasi.or.id/...` (tanpa www) gagal koneksi di sisi kita;
   semua request diarahkan ke `https://www.inovasi.or.id`.
5. **`/404/` tidak bisa di-crawl** - Balas 404 (memang halaman error), jadi skip di fase berikutnya.
6. **Asumsi di xlsx meleset** - asumsi 8 template / 30 PDF / 10 media; kenyataan 13 template
   (11 post type + home ID/EN), 166 PDF, 211 media/embed. Fase 4 (Listen/TTS) dan item PDF di
   xlsx perlu dinaikkan.
7. **Python tanpa pip** - di mesin ini `pip` tidak ada; sudah dipasang via `python -m ensurepip`.
   `requirements.txt` sudah terinstall (requests, beautifulsoup4, lxml). Dependensi Node
   (`npm install`) sudah dijalankan.

8. **Caption video hanya bisa dicek sebagian** - `check_captions.py` membaca halaman
   `youtube.com/watch` tanpa login. YouTube kadang membalas `LOGIN_REQUIRED` dengan alasan
   "Login untuk mengonfirmasi bahwa Anda bukan bot" (bot-check, bukan age-restricted). Pada
   run 11 Okt 2026 hanya 2 dari 173 video yang kena, jadi 171 bisa dipastikan statusnya.
   Video yang kena bot-check ditandai `?` di `caption-check.csv`, tidak boleh dihitung sebagai
   "tanpa caption".

9. **Endpoint `timedtext` tanpa signature selalu kosong** - cross-check manual dengan
   `https://www.youtube.com/api/timedtext?v=<id>&lang=id` mengembalikan 200 dengan body kosong
   bahkan untuk video yang jelas punya caption. Endpoint itu butuh parameter signature
   (`ei`, `caps`, `opi`, `signature`) dari `baseUrl` di dalam `captionTracks`. Jadi bukti
   ketersediaan caption diambil dari metadata `captionTracks` itu sendiri, bukan dari
   unduhan track.

10. **`doc.is_tagged` dihapus di PyMuPDF 1.28** - `check_pdfs.py` sekarang membaca
    `/MarkInfo` dan `/StructTreeRoot` dari catalog PDF. `page.waitForTimeout` juga dihapus di
    Puppeteer 23, dipakai `setTimeout` biasa di `axe_runner.js`.

## Catatan Penting

- **Tes otomatis hanya mencakup ~30-50% SC WCAG** - Uji manual/AT wajib untuk kepatuhan penuh
- **Listen/TTS adalah fitur tambahan** - BUKAN pengganti kepatuhan WCAG
- Semua script idempotent (bisa dijalankan ulang), output bertanggal
- Dokumentasi dalam Bahasa Indonesia, istilah teknis tetap Inggris