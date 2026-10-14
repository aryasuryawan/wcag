# Estimasi Waktu Mesin (Fase 1-2)

Dihasilkan: 2026-10-11T05:56:17

Waktu mesin = durasi tool berjalan tanpa intervensi manusia. Tidak termasuk waktu analisis/penulisan.

## Angka terukur saat crawl

| Metrik | Nilai |
|--------|-------|
| URL unik di sitemap | 738 |
| URL di-crawl pada run ini | 738 |
| Halaman utama (post type `page` + home ID/EN) | 49 |
| Post type / template | 11 |
| PDF ditemukan | 166 |
| Media/embed ditemukan | 211 |
| Request HTTP | 18 |
| Data terunduh | 1.1 MB |
| Error | 0 |
| Durasi crawl aktual | 1m 3d |
| Rata-rata per URL | 3.52 detik |

## Konstanta perkiraan (dari kode script)

- `run_axe.py`: 1 URL = 1 launch Puppeteer + `networkidle2` + 2 detik tunggu -> asumsi 60 detik/URL
- `run_lighthouse.py`: 1 URL = gather desktop + hanya kategori accessibility -> asumsi 45 detik/URL
- `check_pdfs.py`: unduh + parse PDF -> asumsi 8 detik/file

## Skenario A - Halaman utama

| Step | Perkiraan |
|------|-----------|
| `crawl_inventory.py` (terukur, cache) | 1m 0d |
| `run_axe.py` (49 URL) | 49m 0d |
| `run_lighthouse.py` (49 URL) | 36m 45d |
| `check_pdfs.py` (166 PDF) | 22m 8d |
| `merge_findings.py` + ringkasan | 5m 0d |
| **Total mesin skenario A** | **1j 53m 56d** |

## Skenario B - Full site

| Step | Perkiraan |
|------|-----------|
| `crawl_inventory.py` (terukur, 738 URL) | 1m 3d |
| `run_axe.py` (738 URL) | 12j 18m 0d |
| `run_lighthouse.py` (738 URL) | 9j 13m 30d |
| `check_pdfs.py` (166 PDF) | 22m 8d |
| `merge_findings.py` + ringkasan | 10m 0d |
| **Total mesin skenario B** | **22j 17m 38d** |

Catatan: `run_axe.py` dan `run_lighthouse.py` di repo ini me-launch Chrome per URL (tanpa reuse),
jadi waktu didominasi proses start/stop browser, bukan jaringan. Optimasi: reuse 1 instance
Chrome untuk seluruh URL bisa memangkas 30-50% dari durasi di atas.

