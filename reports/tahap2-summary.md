# Tahap 2 - Ringkasan Temuan (clustering + severity)

Dihasilkan: 2026-10-11T13:06:43  
Sumber: `results/automated/axe-*/` (738 URL), `results/automated/media-access-*/`, `standards/sc-mapping.csv`

## Ringkasan

| Metrik | Nilai |
|--------|-------|
| URL hasil scan | 738 |
| Node gagal di axe (Tahap 1) | 7157 |
| Rule aktif | 18 |
| Isu unik setelah clustering | 28 |

## Temuan per severity

| Severity | Jumlah |
|----------|--------|
| Critical | 4 |
| Serious | 14 |
| Moderate | 9 |
| Minor | 1 |

## Temuan per SC

| SC | Nama | Level | Temuan |
|----|------|-------|--------|
| 1.3.1 | Info and Relationships | A | 8 |
| 4.1.2 | Name, Role, Value | A | 6 |
| 1.2.2 | Captions (Prerecorded) | A | 4 |
| 1.1.1 | Non-text Content | A | 3 |
| 2.4.4 | Link Purpose (In Context) | A | 1 |
| 1.4.3 | Contrast (Minimum) | AA | 1 |
| 2.4.3 | Focus Order | A | 1 |
| 1.4.1 | Use of Color | A | 1 |
| 3.1.1 | Language of Page | A | 1 |
| 2.4.2 | Page Titled | A | 1 |
| 2.5.8 | Target Size (Minimum) | AA | 1 |

## Temuan per sumber

| Source | Jumlah |
|--------|--------|
| axe | 22 |
| layout-check | 1 |
| pdf-check | 5 |

## Split ownership (situs vs vendor)

- Dimiliki situs (bisa langsung diperbaiki): 21 temuan
- Markup vendor di dalam iframe (perlu opsi/workaround): 7 temuan

## Daftar temuan (urut severity)

| ID | Severity | SC | Temuan | URL terdampak |
|----|----------|----|--------|---------------|
| A11Y-20261011-001 | Critical | 2.4.4 | [Critical] Link logo mitra di header/footer dibungkus <a> dengan <img alt="">, s... | 738 |
| A11Y-20261011-002 | Serious | 4.1.2 | [Serious] Lightbox galeri (PhotoSwipe) memakai <div class="fy-pswp" role="dialog... | 737 |
| A11Y-20261011-003 | Serious | 1.3.1 | [Serious] Halaman punya lebih dari satu landmark `banner`. Penyebabnya header de... | 737 |
| A11Y-20261011-004 | Serious | 1.3.1 | [Serious] Heading landmark `banner` tidak punya label unik, sehingga dua header ... | 737 |
| A11Y-20261011-005 | Serious | 1.3.1 | [Serious] Hierarki heading melompat, misalnya <h4> muncul tanpa <h2>/<h3> sebelu... | 618 |
| A11Y-20261011-006 | Moderate | 4.1.2 | [Moderate] Widget YouTube di dalam iframe memakai atribut ARIA yang tidak diizin... | 169 |
| A11Y-20261011-007 | Moderate | 4.1.2 | [Moderate] Player YouTube memakai `aria-label` pada <div class="html5-video-play... | 169 |
| A11Y-20261011-008 | Moderate | 4.1.2 | [Moderate] Tombol di dalam iframe YouTube tanpa accessible name, contoh <button ... | 123 |
| A11Y-20261011-009 | Serious | 4.1.2 | [Serious] Iframe tanpa accessible name: 35 titik, yaitu iframe Google Maps di ha... | 35 |
| A11Y-20261011-010 | Serious | 1.4.3 | [Serious] Kontras teks gagal, rasio 1.12:1 (foreground #e3e3e4 di atas backgroun... | 22 |
| A11Y-20261011-011 | Serious | 1.1.1 | [Serious] Gambar halaman majalah Flipsnack di dalam iframe tanpa atribut alt: <i... | 8 |
| A11Y-20261011-012 | Serious | 2.4.3 | [Serious] Elemen dengan tabindex positif: <body id="wppdf-iframe-body" tabindex=... | 32 |
| A11Y-20261011-013 | Serious | 1.3.1 | [Serious] Struktur ARIA tabel tidak valid di dalam iframe PDF: <span role="table... | 1 |
| A11Y-20261011-014 | Serious | 1.3.1 | [Serious] Role ARIA table/row/columnheader di iframe PDF tidak punya parent yang... | 1 |
| A11Y-20261011-015 | Moderate | 4.1.2 | [Moderate] role="group" dipakai pada <article class="fy-slide"> di slider homepa... | 1 |
| A11Y-20261011-016 | Moderate | 1.3.1 | [Moderate] Sebagian halaman tidak punya heading level 1 sama sekali. Tanpa <h1>,... | 42 |
| A11Y-20261011-017 | Minor | 1.3.1 | [Minor] Ada heading kosong (<h*> tanpa teks) di 1 halaman. Mengacaukan heading l... | 1 |
| A11Y-20261011-018 | Serious | 1.4.1 | [Serious] Link teks di dalam paragraf punya kontras 1.08:1 terhadap teks sekitar... | 1 |
| A11Y-20261011-019 | Critical | 1.1.1 | [Critical] 65 dari 166 PDF membalas HTTP 403 saat diakses langsung. Semua berada... | 65 PDF / 166 |
| A11Y-20261011-020 | Critical | 1.1.1 | [Critical] 7 dari 101 PDF yang bisa diunduh tidak punya layer teks sama sekali (... | 65 PDF / 166 |
| A11Y-20261011-021 | Serious | 1.3.1 | [Serious] 43 dari 101 PDF tidak tagged (tidak ada /MarkInfo /Marked true dan tid... | 65 PDF / 166 |
| A11Y-20261011-022 | Serious | 3.1.1 | [Serious] 43 dari 101 PDF tidak punya penanda bahasa (tidak ada /Lang di catalog... | 65 PDF / 166 |
| A11Y-20261011-023 | Moderate | 2.4.2 | [Moderate] 71 dari 101 PDF tidak punya metadata /Title. Pembaca file dan screen ... | 65 PDF / 166 |
| A11Y-20261011-024 | Moderate | 2.5.8 | [Moderate] 507 dari 738 URL punya tombol pengatur ukuran teks milik situs sendir... | - |
| A11Y-20261011-025 | Critical | 1.2.2 | [Critical] 159 dari 173 video YouTube di situs ini tidak punya caption sama seka... | - |
| A11Y-20261011-026 | Serious | 1.2.2 | [Serious] Hanya 4 dari 173 video punya caption Bahasa Indonesia. Sisanya hanya p... | - |
| A11Y-20261011-027 | Moderate | 1.2.2 | [Moderate] 12 video punya caption, tapi semuanya auto-generated (ASR) tanpa trac... | - |
| A11Y-20261011-028 | Moderate | 1.2.2 | [Moderate] 2 video membalas LOGIN_REQUIRED dari server YouTube (age-restricted a... | - |

## Yang BELUM diuji (bukan temuan, ini gap)

- Caption/transcript 173 video YouTube (hanya dicek aksesibilitas embed, bukan subtitle).
- Struktur internal 101 PDF yang bisa diunduh (tagged, heading, bahasa, alt gambar).
- 65 PDF yang 403 - tidak bisa diunduh tanpa akses ke direktori securepdfs.
- Evaluasi manual: keyboard navigation, focus order, visible focus, reflow 320px, zoom 200%, error message form, mekanisme feedback.
- `incomplete` dari axe (needs review) yang sengaja tidak dihitung di Tahap 2.

