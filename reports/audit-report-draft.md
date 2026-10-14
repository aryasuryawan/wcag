# Draft Laporan Audit Aksesibilitas - inovasi.or.id

**Status: DRAFT - baru menyelesaikan Tahap 1 (scan otomatis) dan Tahap 2 (clustering).**  
Uji manual dan assistive technology (Tahap 3) **belum dikerjakan**, jadi laporan ini 
bukan pernyataan kepatuhan. Bagian yang belum ada datanya ditandai eksplisit.

- Dibuat: 2026-10-11T13:07:02
- Sumber data: `results/automated/axe-20261011/`, `results/automated/media-access-20261011/`, `findings/findings.csv`, `inventory/`
- Regenerasi: `python scripts/merge_findings.py && python scripts/build_report.py`

## 1. Ringkasan Eksekutif

| Item | Detail |
|------|--------|
| Website | https://inovasi.or.id (canonical `www`) |
| Tanggal audit | 2026-10-11 (Tahap 1-2) |
| Standar | WCAG 2.2 Level AA sebagai baseline, dipetakan ke WCAG 2.0 Level AA |
| Scope | 10 kategori di `prompt.md`; cakupan data: 738 URL, 11 tipe halaman, 166 PDF, 211 media/embed |
| Metodologi (sudah) | Scan otomatis penuh (axe-core 4.14, 738 URL) + verifikasi akses PDF/video |
| Metodologi belum | Keyboard, focus, reflow, kontras manual, NVDA/VoiceOver/TalkBack, struktur PDF, caption video |
| Total temuan unik | **28** (Critical 4, Serious 14, Moderate 9, Minor 1) |
| Temuan dimiliki situs | 21 (bisa langsung dikerjakan) |
| Temuan markup vendor | 7 (perlu dokumentasi + mitigasi) |
| Node gagal di axe | 7157 |

**Kesimpulan singkat**

Situs punya fondasi struktur yang cukup baik: 736 dari 738 halaman (100%) punya tepat satu `<h1>`, 738 halaman (100%) punya atribut `lang`, dan dari 8295 elemen `<img>` tidak ada satu pun yang kehilangan atribut `alt` (kualitas isi alt tetap perlu diperiksa manual). Yang berat justru lapisan global: header/footer, landmark, dan heading hierarchy. Empat isu menutup 100% dari 738 URL dan berasal dari satu template header/footer - memperbaikinya di sana menutup hampir seluruh temuan otomatis tanpa menyentuh isi halaman.

Di luar lapisan global, ada dua masalah dokumen: 65 dari 166 PDF tidak bisa diunduh (HTTP 403 karena hotlink protection), dan seluruh video YouTube memakai widget dengan markup ARIA bermasalah. Yang terakhir bukan kesalahan kode situs, tapi tetap berdampak ke pengguna screen reader dan harus ditangani dengan mitigasi, bukan diabaikan.

Prioritas perbaikan: **9 temuan Phase 1** (estimasi 20 jam) sudah menutup sebagian besar risiko Critical dan Serious.

## 2. Scope & Metodologi

### 2.1 Cakupan

- Sitemap: 12 child sitemap, 738 URL unik setelah normalisasi (sitemap Yoast memuat 461 URL duplikat dan 4 URL query-param yang dibuang)
- Halaman discan penuh: 738 dari 738 URL
- PDF terdaftar: 166 (101 bisa diakses, 65 403)
- Media: 211 entri, termasuk 173 embed video

| Template | URL | Status uji otomatis | Uji manual |
|----------|-----|--------------------|------------|
| Detail Publikasi (`publication`) | 641 | Selesai | Belum |
| Halaman Statis (ID/EN) (`page`) | 36 | Selesai | Belum |
| Arsip / Kategori Publikasi (`publication-category`) | 16 | Selesai | Belum |
| Wilayah Kerja (slug jamak) (`where-we-works`) | 10 | Selesai | Belum |
| Detail Wilayah Kerja (`where-we-work`) | 8 | Selesai | Belum |
| Artikel Unggulan (`featured-article`) | 6 | Selesai | Belum |
| Galeri (`gallery`) | 6 | Selesai | Belum |
| Siaran Pers (`press-release`) | 5 | Selesai | Belum |
| Detail Peluang (`opportunity`) | 4 | Selesai | Belum |
| Sumber Daya (`resources`) | 4 | Selesai | Belum |
| Halaman Utama (home ID/EN) (`main-halaman-utama`) | 1 | Selesai | Belum |
| Arsip / Kategori Peluang (`opportunity-category`) | 1 | Selesai | Belum |

### 2.2 Matriks Assistive Technology

| Platform | Browser | Screen Reader | Status |
|----------|---------|---------------|--------|
| Windows | Firefox | NVDA | Belum diuji (Tahap 3) |
| Windows | Chrome | NVDA | Belum diuji (Tahap 3) |
| macOS / iOS | Safari | VoiceOver | Belum diuji (Tahap 3) |
| Android | Chrome | TalkBack | Belum diuji (Tahap 3) |

### 2.3 Keterbatasan

- Scan otomatis hanya menutup sebagian SC WCAG. Keyboard, focus order, visible focus, reflow 320px, zoom 200%, error message form, dan pemahaman pengguna dengan AT tidak disentuh sama sekali pada tahap ini.
- Temuan ber-`impact` dari axe yang masuk kategori `incomplete` (needs review) sengaja tidak dihitung, karena butuh verifikasi manual.
- 65 PDF tidak bisa diunduh tanpa akses ke direktori `securepdfs`, jadi struktur internalnya sama sekali belum diperiksa.
- 173 video hanya dicek apakah embed-nya bisa diakses, bukan apakah caption/transkrip tersedia.
- Scan dilakukan pada viewport desktop 1280x720 headless. Perilaku reflow dan zoom belum diuji.

## 3. Ringkasan Temuan

### 3.1 Per severity

| Severity | Jumlah | Persentase | Arti |
|----------|--------|-----------|------|
| Critical | 4 | 14% | mengganggu akses inti, harus-first |
| Serious | 14 | 50% | mengganggu tugas utama |
| Moderate | 9 | 32% | menyulitkan, ada jalur lain |
| Minor | 1 | 4% | kelemahan kecil |
| **Total** | **28** | 100% | |

### 3.2 Per Success Criterion

| SC | Nama | Level | Versi | Temuan | Severity dominan |
|----|------|-------|-------|--------|------------------|
| 1.3.1 | Info and Relationships | A | 2.0 | 8 | Serious |
| 4.1.2 | Name, Role, Value | A | 2.0 | 6 | Serious |
| 1.2.2 | Captions (Prerecorded) | A | 2.0 | 4 | Critical |
| 1.1.1 | Non-text Content | A | 2.0 | 3 | Critical |
| 2.4.4 | Link Purpose (In Context) | A | 2.0 | 1 | Critical |
| 1.4.3 | Contrast (Minimum) | AA | 2.0 | 1 | Serious |
| 2.4.3 | Focus Order | A | 2.0 | 1 | Serious |
| 1.4.1 | Use of Color | A | 2.0 | 1 | Serious |
| 3.1.1 | Language of Page | A | 2.0 | 1 | Serious |
| 2.4.2 | Page Titled | A | 2.0 | 1 | Moderate |
| 2.5.8 | Target Size (Minimum) | AA | 2.2 | 1 | Moderate |

### 3.3 Sebaran per template (dari rule otomatis)

Jumlah node gagal per tipe halaman, berdasarkan rule yang terpicu:

| Template | Node gagal | Temuan dominan |
|----------|-----------|-----------------|
| Detail Publikasi | 3624 | `link-name` (641), `landmark-unique` (641), `landmark-no-duplicate-banner` (641) |
| Halaman Statis (ID/EN) | 229 | `link-name` (36), `landmark-unique` (35), `landmark-no-duplicate-banner` (35) |
| Arsip / Kategori Publikasi | 79 | `link-name` (16), `landmark-unique` (16), `landmark-no-duplicate-banner` (16) |
| Wilayah Kerja (slug jamak) | 50 | `link-name` (10), `landmark-unique` (10), `landmark-no-duplicate-banner` (10) |
| Detail Wilayah Kerja | 48 | `page-has-heading-one` (8), `link-name` (8), `landmark-unique` (8) |
| Artikel Unggulan | 33 | `link-name` (6), `landmark-unique` (6), `landmark-no-duplicate-banner` (6) |
| Galeri | 30 | `link-name` (6), `landmark-unique` (6), `landmark-no-duplicate-banner` (6) |
| Siaran Pers | 25 | `link-name` (5), `landmark-unique` (5), `landmark-no-duplicate-banner` (5) |
| Detail Peluang | 24 | `link-name` (4), `landmark-unique` (4), `landmark-no-duplicate-banner` (4) |
| Sumber Daya | 20 | `link-name` (4), `landmark-unique` (4), `landmark-no-duplicate-banner` (4) |
| Halaman Utama (home ID/EN) | 0 |  |
| Arsip / Kategori Peluang | 5 | `link-name` (1), `landmark-unique` (1), `landmark-no-duplicate-banner` (1) |

### 3.4 Temuan di luar WCAG 2.0

Tidak ada temuan otomatis yang secara khusus masuk SC baru WCAG 2.2 - bukan karena situs sudah patuh, tapi karena aturan yang diuji axe memang lebih banyak menunjuk ke SC 2.0. SC 2.2 berikut **belum diuji** dan wajib masuk checklist Tahap 3:

| SC | Nama | Level di 2.2 | Kenapa penting |
|----|------|--------------|----------------|
| 2.4.11 | Focus Not Obscured (Minimum) | AA | Header sticky (`js-sticky js-autohide`) berpotensi menutupi elemen yang sedang difokus |
| 2.4.13 | Focus Appearance | AAA | Indikator fokus standar perlu dipastikan terlihat |
| 2.5.8 | Target Size (Minimum) | AA | Ikon carousel/partner kecil, risiko target undersized |
| 3.2.6 | Consistent Help | A | Belum tahu apakah ada mekanisme feedback konsisten |
| 3.3.7 | Redundant Entry | A | Form newsletter di 738 halaman |
| 2.5.7 | Dragging Movements | AA | Slider/carousel homepage dan galeri |

## 4. Detail Temuan

### 4.1 Critical (4)

#### A11Y-20261011-001 · SC 2.4.4 (A) · `link-name`

- **Severity**: Critical
- **Template**: publication, page, publication-category, where-we-works
- **URL contoh**: https://www.inovasi.or.id
- **URL terdampak**: 738 URL
- **Deskripsi**: [Critical] Link logo mitra di header/footer dibungkus <a> dengan <img alt="">, sehingga tidak ada accessible name. Reader screen reader hanya mengumumkan "link" tanpa tujuan. Contoh node yang gagal: <a href="https://kemendikdasmen.go.id/"><img src="partner-1.png" alt=""></a> Terjadi di 738 URL (3213 node gagal; impact axe: serious 3213). Contoh URL: https://www.inovasi.or.id (pemilik: situs).
- **Langkah reproduksi**: 1. Buka halaman mana pun. 2. Aktifkan NVDA. 3. Tekan Tab sampai masuk ke blok logo mitra di header/footer. 4. Dengarkan nama yang dibacakan untuk tiap link logo. (selector contoh: .fy-canvas > .fy-header.fy-header-left.is-on-top > .fy-header-container > .fy-flex-container-center.fy-flex-gutter-0.fy-flex-container > .fy-mobile-hi)
- **Rekomendasi**: Isi alt deskriptif pada tiap logo (mis. "Kementerian Pendidikan, Republik Indonesia"), atau tambahkan teks link yang terlihat. Jangan sekadar `alt="logo"` karena itu tidak menjelaskan tujuan link.

#### A11Y-20261011-019 · SC 1.1.1 (A) · `pdf-403`

- **Severity**: Critical
- **Template**: publication, opportunity, resources
- **URL contoh**: https://www.inovasi.or.id/wp-content/uploads/securepdfs/2025/11/MALINAU_ebook_21-9-2025_compressed.pdf
- **Deskripsi**: [Critical] 65 dari 166 PDF membalas HTTP 403 saat diakses langsung. Semua berada di direktori /wp-content/uploads/securepdfs/. Tetap 403 walau memakai User-Agent browser + header Referer + query ?download=1. Satu-satunya jalur tersedia adalah iframe plugin PDF Embed yang membalas halaman HTML viewer, bukan file PDF. Contoh: https://www.inovasi.or.id/wp-content/uploads/securepdfs/2025/11/MALINAU_ebook_21-9-2025_compressed.pdf (SC 1.1.1 dipakai sebagai proksi: dokumen tidak punya jalur teks yang bisa diakses, bukan karena teksnya hilang)
- **Langkah reproduksi**: 1. Ambil URL PDF dari inventory/pdfs.csv. 2. Buka URL di browser. 3. Perhatikan respons 403 Forbidden. 4. Bandingkan dengan PDF di direktori uploads/ biasa yang bisa dibuka.
- **Rekomendasi**: Terbitkan dokumen sebagai HTML (dan atau PDF accessible) tanpa hotlink protection, atau sediakan jalur unduh yang tetap bisa diakses screen reader. Kalau proteksi hotlink memang dibutuhkan, berikan mekanisme unduh yang menghasilkan response 200 untuk pengguna browser biasa.

#### A11Y-20261011-020 · SC 1.1.1 (A) · `pdf-no-text-layer`

- **Severity**: Critical
- **Template**: publication, resources
- **URL contoh**: https://www.inovasi.or.id/wp-content/uploads/2021/11/Cover-A4.pdf
- **Deskripsi**: [Critical] 7 dari 101 PDF yang bisa diunduh tidak punya layer teks sama sekali (hasil scan tanpa OCR). Screen reader tidak membaca apa-apa dari dokumen ini. Contoh: Cover-A4
- **Langkah reproduksi**: 1. Buka salah satu PDF pada daftar. 2.coba select all + salin teks di Acrobat: tidak ada teks yang bisa disalin. 3. Bandingkan dengan PDF lain yang teksnya bisa dipilih.
- **Rekomendasi**: Jalankan OCR (dan/atau sumber ulang dokumen dari file yang teksnya bisa dipilih), lalu pastikan hasilnya tagged PDF. Untuk dokumen sekolah, jauh lebih baik menerbitkan versi HTML.

#### A11Y-20261011-025 · SC 1.2.2 (A) · `video-no-caption`

- **Severity**: Critical
- **Template**: publication, featured-article, page
- **URL contoh**: https://www.inovasi.or.id/publication/voxpop-how-will-the-partnership-with-inovasi-strengthen-learning-outcomes-tbp/
- **Deskripsi**: [Critical] 159 dari 173 video YouTube di situs ini tidak punya caption sama sekali (dicek dari `captionTracks` di `ytInitialPlayerResponse`; status player OK, jadi ini bukan efek blokir). SC 1.2.2 adalah level A. Video contoh: `00jJiROIffc`, `0BgLzmzgfj4`, `0TjeLsLeUPQ`, `0ejaIchCJpE`, `0tNGZ3afGRA`. Identitas video ada di `results/automated/caption-check-20261011/caption-check.csv`
- **Langkah reproduksi**: 1. Buka salah satu halaman yang punya video. 2. Klik play atau buka langsung `youtube.com/watch?v=<id>`. 3. Klik ikon CC / subtitle: tidak ada. 4. Ulangi tanpa menyalakan subtitle: tidak ada teks pengganti.
- **Rekomendasi**: Tambah caption Bahasa Indonesia untuk video yang berisi suara. Untuk 159 video, ini pekerjaan batch: pakai transkrip otomatis lalu review manual, atau upstreamkan ke NFJS/rumah baca komunitas. Minimal sediakan transkrip teks di bawah video.

### 4.2 Serious (14)

#### A11Y-20261011-002 · SC 4.1.2 (A) · `aria-hidden-focus`

- **Severity**: Serious
- **Template**: publication, page, publication-category, where-we-works
- **URL contoh**: https://www.inovasi.or.id/about
- **URL terdampak**: 737 URL
- **Deskripsi**: [Serious] Lightbox galeri (PhotoSwipe) memakai <div class="fy-pswp" role="dialog" aria-hidden="true" tabindex="-1"> yang tetap berisi konten fokusable di dalam DOM. Konten yang disembunyikan dari AT tapi masih bisaAGING focus. Terjadi di 737 URL (737 node gagal; impact axe: serious 737). Contoh URL: https://www.inovasi.or.id/about (pemilik: situs).
- **Langkah reproduksi**: 1. Buka halaman yang punya galeri. 2. Tekan Tab berulang kali tanpa membuka lightbox. 3. Perhatikan apakah fokus bisa masuk ke area lightbox yang tidak terlihat. (selector contoh: .fy-pswp)
- **Rekomendasi**: Tambahkan `inert` pada lightbox saat tertutup, atau pindahkan lightbox ke luar DOM sampai dibuka. Kalau tetap perlu `tabindex="-1"`, pastikan lightbox di-`display:none` saat tertutup.

#### A11Y-20261011-003 · SC 1.3.1 (A) · `landmark-no-duplicate-banner`

- **Severity**: Serious
- **Template**: publication, page, publication-category, where-we-works
- **URL contoh**: https://www.inovasi.or.id/about
- **URL terdampak**: 737 URL
- **Deskripsi**: [Serious] Halaman punya lebih dari satu landmark `banner`. Penyebabnya header desktop dan header mobile dirender bersamaan: <header class="fy-header fy-header-left is-on-top ...">. Terjadi di 737 URL (737 node gagal; impact axe: moderate 737). Contoh URL: https://www.inovasi.or.id/about (pemilik: situs).
- **Langkah reproduksi**: 1. BukaNVDA landmark list (D key). 2. Cek berapa entri `banner` yang muncul pada satu halaman. 3. Ulangi di viewport mobile. (selector contoh: .fy-canvas > .fy-header.fy-header-left.is-on-top)
- **Rekomendasi**: Pastikan hanya satu header yang aktif pada satu waktu: sembunyikan header mobile dengan `display:none` (bukan hanya `visibility:hidden` atau off-screen) saat desktop aktif, dan sebaliknya.

#### A11Y-20261011-004 · SC 1.3.1 (A) · `landmark-unique`

- **Severity**: Serious
- **Template**: publication, page, publication-category, where-we-works
- **URL contoh**: https://www.inovasi.or.id/about
- **URL terdampak**: 737 URL
- **Deskripsi**: [Serious] Heading landmark `banner` tidak punya label unik, sehingga dua header (desktop dan mobile) tidak bisa dibedakan screen reader. Terjadi di 737 URL (737 node gagal; impact axe: moderate 737). Contoh URL: https://www.inovasi.or.id/about (pemilik: situs).
- **Langkah reproduksi**: 1. Buka NVDA landmark list. 2. Pilih tiap entri banner. 3. Dengarkan label yang dibacakan - keduanya sama. (selector contoh: .fy-canvas > .fy-header.fy-header-left.is-on-top)
- **Rekomendasi**: Beri `aria-label="Header utama"` pada header aktif, dan hilangkan landmark dari header yang non-aktif (ubah ke `role="presentation"`).

#### A11Y-20261011-005 · SC 1.3.1 (A) · `heading-order`

- **Severity**: Serious
- **Template**: publication, page, publication-category, where-we-works
- **URL contoh**: https://www.inovasi.or.id
- **URL terdampak**: 618 URL
- **Deskripsi**: [Serious] Hierarki heading melompat, misalnya <h4> muncul tanpa <h2>/<h3> sebelumnya. Contoh: <h4 class="wp-block-heading"> di hero homepage, dan <h6> di dalam slider galeri. Headings jadi cara utama screen reader user berpindah section. Terjadi di 618 URL (662 node gagal; impact axe: moderate 662). Contoh URL: https://www.inovasi.or.id (pemilik: situs).
- **Langkah reproduksi**: 1. Buka halaman. 2. NVDA heading list (H). 3. Perhatikan level yang melompat turun lebih dari 1 tanpa naik dulu. (selector contoh: h4)
- **Rekomendasi**: Perbaiki urutan heading di konten WordPress: pakai satu <h1> judul halaman, <h2> untuk section, <h3>/<h4> untuk sub-item. Ganti style, jangan ganti level tag.

#### A11Y-20261011-009 · SC 4.1.2 (A) · `frame-title`

- **Severity**: Serious
- **Template**: publication, page, opportunity
- **URL contoh**: https://www.inovasi.or.id/kontak
- **URL terdampak**: 35 URL
- **Deskripsi**: [Serious] Iframe tanpa accessible name: 35 titik, yaitu iframe Google Maps di halaman kontak (`<iframe src="https://www.google.c..." width="400">`) dan iframe plugin PDF (`.pdfembed-iframe`). Screen reader hanya membacakan "iframe" tanpa penjelasan isinya. Terjadi di 35 URL (35 node gagal; impact axe: serious 35). Contoh URL: https://www.inovasi.or.id/kontak (pemilik: situs).
- **Langkah reproduksi**: 1. Buka /kontak. 2. NVDA, navigasi ke iframe peta. 3. Perhatikan tidak ada nama yang dibacakan. 4. Ulangi pada halaman publikasi yang punya PDF embedded. (selector contoh: iframe[width="400"])
- **Rekomendasi**: Tambah `title` pada setiap iframe: Maps -> "Peta lokasi kantor INOVASI di Jakarta"; PDF -> "Pratinjau dokumen: <judul dokumen>" (isi dinamis dari hook plugin).

#### A11Y-20261011-010 · SC 1.4.3 (AA) · `color-contrast`

- **Severity**: Serious
- **Template**: page, publication
- **URL contoh**: https://www.inovasi.or.id
- **URL terdampak**: 22 URL
- **Deskripsi**: [Serious] Kontras teks gagal, rasio 1.12:1 (foreground #e3e3e4 di atas background #f0f0f0) pada judul kartu-konten `.dpt-title-link` dan elemen <time>. 468 node gagal di 23 URL, jadi masalahnya systemic di komponen kartu bukan acak. Terjadi di 22 URL (467 node gagal; impact axe: serious 467). Contoh URL: https://www.inovasi.or.id (pemilik: situs).
- **Langkah reproduksi**: 1. Buka homepage. 2. Inspect judul kartu konten dan tanggal di bawahnya. 3. Hitung rasio foreground vs background (atau pakai tool kontras). 4. Konfirmasi juga di 320px dan zoom 200%. (selector contoh: .no-thumbnail > .dpt-entry-wrapper > .sub-entry > .dpt-title > .dpt-title-link[rel="bookmark"])
- **Rekomendasi**: Naikkan kontras teks kartu ke minimal 4.5:1 (AA untuk teks normal). Nilai #e3e3e4 di #f0f0f0 hampir tidak terlihat - kemungkinan warna teks lama tidak ikut diubah saat redesign background card.

#### A11Y-20261011-011 · SC 1.1.1 (A) · `image-alt`

- **Severity**: Serious
- **Template**: publication
- **URL contoh**: https://www.inovasi.or.id/publication/berita-inovasi-edisi-iii-mei-2022
- **URL terdampak**: 8 URL
- **Deskripsi**: [Serious] Gambar halaman majalah Flipsnack di dalam iframe tanpa atribut alt: <img class="page-image" data-page="1"> pada 8 URL. Screen reader user tidak tahu isi dokumen yang sedang dibaca. Terjadi di 8 URL (19 node gagal; impact axe: critical 19). Contoh URL: https://www.inovasi.or.id/publication/berita-inovasi-edisi-iii-mei-2022 (pemilik: vendor).
- **Langkah reproduksi**: 1. Buka salah satu URL publikasi yang Flipsnack-nya gagal. 2. NVDA, masuk ke iframe. 3. Dengarkan deskripsi gambar - tidak ada. (selector contoh: iframe[width="100%"] > img[data-page="1"])
- **Rekomendasi**: Kalau dokumen Flipsnack memang dipakai, sediakan transkrip atau versi HTML teks sebagai alternatif di luar iframe (SC 1.1.1). Alt untuk gambar halaman majalah sebaiknya describing isi halaman, bukan "halaman 1".

#### A11Y-20261011-012 · SC 2.4.3 (A) · `tabindex`

- **Severity**: Serious
- **Template**: publication, opportunity
- **URL contoh**: https://www.inovasi.or.id/opportunity/invitation-to-tender-eo-for-education-reform-dialog-with-palestinian-moehe
- **URL terdampak**: 32 URL
- **Deskripsi**: [Serious] Elemen dengan tabindex positif: <body id="wppdf-iframe-body" tabindex="1"> di dalam iframe PDF plugin, dan <div id="accessibility" tabindex="1"> di iframe Flipsnack. tabindex positif memutus urutan focus natural. Terjadi di 32 URL (32 node gagal; impact axe: serious 32). Contoh URL: https://www.inovasi.or.id/opportunity/invitation-to-tender-eo-for-education-reform-dialog-with-palestinian-moehe (pemilik: vendor).
- **Langkah reproduksi**: 1. Buka halaman dengan PDF embedded atau Flipsnack. 2. Tekan Tab dari awal halaman. 3. Perhatikan fokus melompat atau terlempar ke area iframe secara tidak wajar. (selector contoh: .pdfembed-iframe > #wppdf-iframe-body)
- **Rekomendasi**: Hindari tabindex positif. Untuk iframe PDF, pastikan plugin memakai tabindex="0" atau "-1", atau ganti dengan embed yang mendukung navigasi keyboard (dan sediakan link unduh sebagai alternatif).

#### A11Y-20261011-013 · SC 1.3.1 (A) · `aria-required-children`

- **Severity**: Serious
- **Template**: opportunity
- **URL contoh**: https://www.inovasi.or.id/opportunity/invitation-to-tender-eo-for-education-reform-dialog-with-palestinian-moehe
- **URL terdampak**: 1 URL
- **Deskripsi**: [Serious] Struktur ARIA tabel tidak valid di dalam iframe PDF: <span role="table"> punya anak <span role="columnheader"> yang struktur role-nya tidak sesuai (butuh parent row/rowgroup). Reader screen reader bisa kehilangan konteks tabel. Terjadi di 1 URL (1 node gagal; impact axe: critical 1). Contoh URL: https://www.inovasi.or.id/opportunity/invitation-to-tender-eo-for-education-reform-dialog-with-palestinian-moehe (pemilik: vendor).
- **Langkah reproduksi**: 1. Buka halaman yang punya PDF embedded. 2. NVDA, masuk ke iframe PDF, coba mode tabel. 3. Perhatikan navigasi baris/kolom tidak konsisten. (selector contoh: .pdfembed-iframe > span[role="table"])
- **Rekomendasi**: Markup dari plugin PDF. Mitigasi situs: sediakan versi HTML atau transkrip dokumen sebagai alternatif utama, dan jadikan iframe PDF sebagai bonus.

#### A11Y-20261011-014 · SC 1.3.1 (A) · `aria-required-parent`

- **Severity**: Serious
- **Template**: opportunity
- **URL contoh**: https://www.inovasi.or.id/opportunity/invitation-to-tender-eo-for-education-reform-dialog-with-palestinian-moehe
- **URL terdampak**: 1 URL
- **Deskripsi**: [Serious] Role ARIA table/row/columnheader di iframe PDF tidak punya parent yang diperlukan (butuh grid, rowgroup, table, atau treegrid). Lanjutan dari aria-required-children di iframe yang sama. Terjadi di 1 URL (2 node gagal; impact axe: critical 2). Contoh URL: https://www.inovasi.or.id/opportunity/invitation-to-tender-eo-for-education-reform-dialog-with-palestinian-moehe (pemilik: vendor).
- **Langkah reproduksi**: Sama dengan aria-required-children, periksa di dalam iframe PDF dengan NVDA mode tabel. (selector contoh: .pdfembed-iframe > span[role="table"] > span[role="columnheader"])
- **Rekomendasi**: Sama seperti di atas: sediakan alternative HTML atau transkrip di luar iframe sebagai jalur utama.

#### A11Y-20261011-018 · SC 1.4.1 (A) · `link-in-text-block`

- **Severity**: Serious
- **Template**: publication
- **URL contoh**: https://www.inovasi.or.id/publication/belajar-bareng-pemanfaatan-aplikasi-digital-untuk-meningkatkan-literasi-dan-numerasi-anak
- **URL terdampak**: 1 URL
- **Deskripsi**: [Serious] Link teks di dalam paragraf punya kontras 1.08:1 terhadap teks sekitarnya (#2850aa di #3f4f77) tanpa underline, sehingga hilang bagi pengguna low vision (SC 1.4.1 Use of Color). Terjadi di 1 URL (2 node gagal; impact axe: serious 2). Contoh URL: https://www.inovasi.or.id/publication/belajar-bareng-pemanfaatan-aplikasi-digital-untuk-meningkatkan-literasi-dan-numerasi-anak (pemilik: situs).
- **Langkah reproduksi**: 1. Buka URL publikasi terkait. 2. Lihat link di dalam paragraf. 3. Cek apakah ada bedanya dari teks biasa selain warna. (selector contoh: a[href$="letsreadasia.org/"])
- **Rekomendasi**: Naikkan kontras link teks minimal 3:1 terhadap teks sekitarnya, dan/atau tambahkan underline pada link di dalam blok teks.

#### A11Y-20261011-021 · SC 1.3.1 (A) · `pdf-not-tagged`

- **Severity**: Serious
- **Template**: publication, resources
- **URL contoh**: https://inovasi.or.id/wp-content/uploads/2025/10/2023-public-inovasi-modul-numerasi-kelas-tinggi.pdf
- **Deskripsi**: [Serious] 43 dari 101 PDF tidak tagged (tidak ada /MarkInfo /Marked true dan tidak ada /StructTreeRoot). Struktur baca screen reader mengikuti urutan visual, bukan struktur dokumen. Contoh: Unduh
- **Langkah reproduksi**: 1. Buka PDF di Acrobat > File > Properties. 2. Lihat tagged/tidak. 3. Coba navigasi dengan keyboard: urutan baca tidak mengikuti kolom/heading.
- **Rekomendasi**: Publikasikan ulang sebagai tagged PDF (PDF/UA), atau lebih baik sebagai HTML. Kalau sumber dokumen tidak tersedia, gunakan tools untuk meng-generate PDF/UA dari HTML yang sudah accessible.

#### A11Y-20261011-022 · SC 3.1.1 (A) · `pdf-no-language`

- **Severity**: Serious
- **Template**: publication, resources
- **URL contoh**: https://inovasi.or.id/wp-content/uploads/2025/10/2023-public-inovasi-modul-numerasi-kelas-tinggi.pdf
- **Deskripsi**: [Serious] 43 dari 101 PDF tidak punya penanda bahasa (tidak ada /Lang di catalog maupun dc:language di XMP). Layar baca tidak tahu pronounounce-nya Bahasa Indonesia atau Inggris.
- **Langkah reproduksi**: 1. Buka PDF. 2. properties > Advanced > Language: kosong. 3. Dengarkan beberapa paragraf: lafal screen reader menggunakan aturan suara default yang bisa salah.
- **Rekomendasi**: Set /Lang ke id-ID (atau en bila dokumennya Inggris) saat ekspor PDF. Ini satu baris di tool exporting.

#### A11Y-20261011-026 · SC 1.2.2 (A) · `video-caption-no-id`

- **Severity**: Serious
- **Template**: publication, featured-article
- **URL contoh**: https://www.inovasi.or.id/publication/belajar-iklim-seru-dengan-teks-informatif/
- **Deskripsi**: [Serious] Hanya 4 dari 173 video punya caption Bahasa Indonesia. Sisanya hanya punya caption Inggris, atau caption dalam bahasa lain, atau tidak punya caption. Untuk konten berbahasa Indonesia, caption Inggris tidak memenuhi kebutuhan pengguna.
- **Langkah reproduksi**: 1. Buka video. 2. Nyalakan subtitle. 3. Lihat daftar bahasa yang tersedia di ikon settings subtitle.
- **Rekomendasi**: Prioritaskan caption Bahasa Indonesia. Caption Inggris tidak pengganti untuk konten yang perkecilannya berbahasa Indonesia.

### 4.3 Moderate (9)

#### A11Y-20261011-006 · SC 4.1.2 (A) · `aria-allowed-attr`

- **Severity**: Moderate
- **Template**: publication, page, featured-article
- **URL contoh**: https://www.inovasi.or.id
- **URL terdampak**: 169 URL
- **Deskripsi**: [Moderate] Widget YouTube di dalam iframe memakai atribut ARIA yang tidak diizinkan pada elemennya: <a class="ytmVideoInfoVideoTitle" aria-level="2">. Markup ini dibuat oleh player YouTube, bukan oleh kode situs. Terjadi di 169 URL (169 node gagal; impact axe: critical 169). Contoh URL: https://www.inovasi.or.id (pemilik: vendor).
- **Langkah reproduksi**: 1. Buka halaman yang punya embed video. 2. Jalankan axe atau DevTools ARIA inspection pada iframe video. 3. Lihat atribut pada elemen ytmVideoInfoVideoTitle. (selector contoh: #\36 49424024 > .ytmVideoInfoVideoTitle)
- **Rekomendasi**: Tidak bisa diperbaiki dari sisi situs. Opsi: pakai privacy mode YouTube (`youtube-nocookie.com`) yang kadang punya markup lebih bersih, atau catat sebagai known third-party issue dengan workaround caption manual. Jangan dipakai sebagai alasan membiarkan isu tanpa keterangan di laporan.

#### A11Y-20261011-007 · SC 4.1.2 (A) · `aria-prohibited-attr`

- **Severity**: Moderate
- **Template**: publication, page, featured-article
- **URL contoh**: https://www.inovasi.or.id
- **URL terdampak**: 169 URL
- **Deskripsi**: [Moderate] Player YouTube memakai `aria-label` pada <div class="html5-video-player"> tanpa role yang valid, yang dilarang WCAG. Markup ini berasal dari vendor. Terjadi di 169 URL (169 node gagal; impact axe: serious 169). Contoh URL: https://www.inovasi.or.id (pemilik: vendor).
- **Langkah reproduksi**: 1. Buka halaman ber-embed video. 2. DevTools > Elements > cari html5-video-player. 3. Perhatikan aria-label tanpa role. (selector contoh: #\36 49424024 > #movie_player)
- **Rekomendasi**: Sama seperti aria-allowed-attr: isu vendor. Dokumentasikan sebagai known issue dengan bukti (URL + screenshot), usulkan privacy-enhanced embed, dan pastikan caption tetap tersedia sebagai konten sendiri.

#### A11Y-20261011-008 · SC 4.1.2 (A) · `button-name`

- **Severity**: Moderate
- **Template**: publication, page, featured-article
- **URL contoh**: https://www.inovasi.or.id
- **URL terdampak**: 123 URL
- **Deskripsi**: [Moderate] Tombol di dalam iframe YouTube tanpa accessible name, contoh <button class="ytmVideoInfoLink ytmVideoInfoChannelAvatar"> yang hanya berisi <img> tanpa alt. Terjadi di 123 URL (123 node gagal; impact axe: critical 123). Contoh URL: https://www.inovasi.or.id (pemilik: vendor).
- **Langkah reproduksi**: 1. Buka halaman ber-embed. 2. NVDA, tekan Tab-M untuk masuk ke iframe video. 3. Dengarkan nama tombol yang dibacakan. (selector contoh: #\36 49424024 > .ytmVideoInfoChannelAvatar)
- **Rekomendasi**: Isu vendor. Mitigasi yang bisa dilakukan situs: jangan menjadikan iframe video sebagai satu-satunya cara akses video (beri link transkrip video di bawahnya).

#### A11Y-20261011-015 · SC 4.1.2 (A) · `aria-allowed-role`

- **Severity**: Moderate
- **Template**: page
- **URL contoh**: https://www.inovasi.or.id
- **URL terdampak**: 1 URL
- **Deskripsi**: [Moderate] role="group" dipakai pada <article class="fy-slide"> di slider homepage, padahal role group tidak diizinkan untuk elemen article. Terjadi di 1 URL (8 node gagal; impact axe: minor 8). Contoh URL: https://www.inovasi.or.id (pemilik: situs).
- **Langkah reproduksi**: 1. Buka homepage. 2. DevTools > inspect elemen slider. 3. Lihat role="group" pada article. (selector contoh: .swiper-slide-prev)
- **Rekomendasi**: Hapus role="group" dari article slider, atau ganti elemennya menjadi <div> yang memang boleh memakai role group.

#### A11Y-20261011-016 · SC 1.3.1 (A) · `page-has-heading-one`

- **Severity**: Moderate
- **Template**: page, where-we-work
- **URL contoh**: https://www.inovasi.or.id/buku-cerita-2
- **URL terdampak**: 42 URL
- **Deskripsi**: [Moderate] Sebagian halaman tidak punya heading level 1 sama sekali. Tanpa <h1>, reader screen reader tidak punya titik awal untuk memahami topik halaman (best practice, bukan kegagalan SC eksak). Terjadi di 42 URL (43 node gagal; impact axe: moderate 43). Contoh URL: https://www.inovasi.or.id/buku-cerita-2 (pemilik: situs).
- **Langkah reproduksi**: 1. Buka salah satu halaman yang gagal. 2. NVDA heading list (H). 3. Level pertama yang muncul bukan level 1. (selector contoh: #top)
- **Rekomendasi**: Tambahkan satu <h1> per halaman - boleh disembunyikan secara visual kalau desain tidak menyediakan, tapi tetap ada di accessibility tree.

#### A11Y-20261011-023 · SC 2.4.2 (A) · `pdf-no-title`

- **Severity**: Moderate
- **Template**: publication, resources
- **URL contoh**: https://inovasi.or.id/wp-content/uploads/2025/10/2023-public-inovasi-modul-numerasi-kelas-tinggi.pdf
- **Deskripsi**: [Moderate] 71 dari 101 PDF tidak punya metadata /Title. Pembaca file dan screen reader membacakan nama file sebagai gantinya, misalnya "modul-literasi-dasar-fase-a-fonik". Contoh: 2023-public-inovasi-modul-numerasi-kelas-tinggi.pdf
- **Langkah reproduksi**: 1. Buka daftar file PDF. 2. Perhatikan nama file yang penuh dengan tanda hubung dan angka. 3. Buka properties: kolom Title kosong.
- **Rekomendasi**: Isi /Title saat ekspor PDF dengan judul dokumen yang memb intelligible, bukan nama file.

#### A11Y-20261011-024 · SC 2.5.8 (AA) · `layout-target-size`

- **Severity**: Moderate
- **Template**: semua template
- **URL contoh**: https://www.inovasi.or.id
- **Deskripsi**: [Moderate] 507 dari 738 URL punya tombol pengatur ukuran teks milik situs sendiri (kelas `accessibility-scale-increase` / `accessibility-scale-decrease`) berukuran 23,5 x 23,5 CSS px, di bawah minimum 24 x 24 SC 2.5.8. Selisihnya kecil (0,5 px) tapi tetap gagal. Kontrol aksesibilitas yang justru ukurannya tidak memenuhi target size.
- **Langkah reproduksi**: 1. Buka halaman mana pun. 2. Inspect tombol zoom in/out di sudut layar. 3. Ukur lewat DevTools: 23,5 x 23,5 px.
- **Rekomendasi**: Naikkan ukuran tombol ke minimal 24 x 24 CSS px, idealnya 44 x 44 (praktik terbaik untuk touch). Periksa juga spacing antar tombol.

#### A11Y-20261011-027 · SC 1.2.2 (A) · `video-caption-auto-only`

- **Severity**: Moderate
- **Template**: publication, featured-article
- **URL contoh**: https://www.inovasi.or.id/publication/belajar-iklim-seru-dengan-teks-informatif/
- **Deskripsi**: [Moderate] 12 video punya caption, tapi semuanya auto-generated (ASR) tanpa track manual. Caption seperti ini biasanya menyalah pada nama diri, istilah pendidikan, dan angka.
- **Langkah reproduksi**: 1. Buka video. 2. Nyalakan caption. 3. Dengarkan nama pribadi dan istilah teknis - bandingkan dengan teks aslinya.
- **Rekomendasi**: Review manual caption ASR, minimal untuk nama diri, nama lembaga, dan angka statistik yang muncul di video.

#### A11Y-20261011-028 · SC 1.2.2 (A) · `video-login-required`

- **Severity**: Moderate
- **Template**: publication, featured-article
- **URL contoh**: https://www.youtube.com/watch?v=-XvHN041K4k
- **Deskripsi**: [Moderate] 2 video membalas LOGIN_REQUIRED dari server YouTube (age-restricted atau member-only). Video seperti ini hanya bisa dilihat setelah login, sehingga caption dan transkripnya juga tidak bisa diakses tanpa akun. Alasan yang dikembalikan: "Login untuk mengonfirmasi bahwa Anda bukan bot"
- **Langkah reproduksi**: 1. Buka video dalam jendela penyamaran (tanpa login). 2. Muncul layar "Login untuk mengonfirmasi". 3. Video tidak bisa diputar.
- **Rekomendasi**: Pastikan embed memakai parameter privacy (`youtube-nocookie.com`) dan tidak memerlukan login. Bila video memangricted, sertakan transkrip teks di halaman sebagai alternatif.

### 4.4 Minor (1)

#### A11Y-20261011-017 · SC 1.3.1 (A) · `empty-heading`

- **Severity**: Minor
- **Template**: publication
- **URL contoh**: https://www.inovasi.or.id/publication/road-to-international-womens-day-2026
- **URL terdampak**: 1 URL
- **Deskripsi**: [Minor] Ada heading kosong (<h*> tanpa teks) di 1 halaman. Mengacaukan heading list reader screen reader. Terjadi di 1 URL (1 node gagal; impact axe: minor 1). Contoh URL: https://www.inovasi.or.id/publication/road-to-international-womens-day-2026 (pemilik: situs).
- **Langkah reproduksi**: 1. Buka halaman yang gagal. 2. NVDA heading list. 3. Cari entri heading tanpa nama. (selector contoh: .wp-block-heading)
- **Rekomendasi**: Isi teksnya, atau hapus elemen heading kosong tersebut.


---

## 5. Hasil Uji Manual

Sebagian butir di bawah sudah diverifikasi **secara mesin** oleh `scripts/check_layout.py` atas 738 URL (headless Chrome, viewport 1280 / 320 / 640 px). Sisanya masih perlu tester manusia dengan perangkat.

| Topik | SC | Metode | Hasil |
|-------|-----|--------|-------|
| Reflow: scroll horizontal di 320px | 1.4.10 | Mesin | Lolos - 0 URL gagal |
| Resize text: scroll horizontal di 640px (zoom 200%) | 1.4.4 | Mesin | Lolos - 0 URL gagal |
| Skip link menuju anchor yang ada | 2.4.1 | Mesin | Ada di semua URL |
| Tabindex positif | 2.4.3 | Mesin | None URL punya tabindex positif |

Topik yang masih harus diuji manusia (butuh interaksi keyboard dan perangkat AT):

| Topik | Status | Catatan |
|-------|--------|---------|
| Urutan fokus (tab order) nyata | Belum diuji | - |
| Focus visible / indikator fokus | Belum diuji | - |
| Focus tidak tertutup header sticky (SC 2.4.11) | Belum diuji | - |
| Heading & landmark (baca manual) | Belum diuji | - |
| Kontras warna (verifikasi visual) | Belum diuji | - |
| Form: label, pesan error, validasi | Belum diuji | - |
| Mekanisme feedback aksesibilitas | Belum diuji | - |
| NVDA + Firefox/Chrome | Belum diuji | - |
| VoiceOver macOS/iOS | Belum diuji | - |
| TalkBack Android | Belum diuji | - |
| Akurasi isi caption (yang ada) dan video tanpa suara (SC 1.2.1) | Belum diuji | - |

## 6. Aksesibilitas PDF

| Aspek | Status |
|-------|--------|
| PDF terdaftar | 166 |
| Bisa diunduh langsung (HTTP 200) | 101 |
| Diblokir (HTTP 403) | 65 |
| Berhasil diperiksa struktur | 101 (total 269 MB) |
| Tagged PDF | 58/101 |
| Punya penanda bahasa | 58/101 |
| Punya judul metadata | 30/101 |
| Tanpa layer teks (hasil scan) | 7/101 |
| Alt text gambar di dalam PDF | **Belum diperiksa** (butuh parser struktur tag) |
| Heading hierarchy & reading order | **Belum diperiksa** (butuh PDF/UA checker penuh) |

### Temuan struktur dokumen

- **7 PDF tanpa layer teks** (hasil scan, tidak ada teks sama sekali). Screen reader tidak membaca apa-apa dari dokumen ini - kegagalan paling berat di kelompok PDF.
- **43 dari 101 PDF tidak tagged.** Struktur baca mengikuti urutan visual, bukan struktur dokumen.
- **43 PDF tanpa penanda bahasa.** Layar baca akan pronounounce dengan aturan suara yang salah.
- **71 PDF tanpa metadata /Title.** Yang dibacakan justru nama file.

Detail per file: `results/automated/pdf-check-*/pdf-check-summary.csv`

Temuan lain: 65 PDF di direktori `securepdfs` membalas 403 walau dipakai User-Agent browser dengan header `Referer` dan query `?download=1`. Mekanismenya hotlink protection. Satu-satunya jalur akses adalah iframe plugin PDF Embed yang membalas halaman HTML viewer.

Catatan: 59 dari PDF yang diblokir terikat ke parent post yang tidak ada di WordPress REST API (kemungkinan draft atau trash). Tidak semua 65 terindeks orfan - 6 di antaranya tertempel pada halaman publik yang ada.

Detail lengkap: `results/automated/media-access-*/report.md`

## 7. Video dan Listen / TTS

### Status caption video (173 embed diperiksa)

| Aspek | Jumlah |
|-------|--------|
| Embed video | 173 |
| **Tanpa caption (pasti)** | **159** |
| Hanya auto-generated, tanpa track manual | 12 |
| Punya caption Bahasa Indonesia | 4 |
| Tidak bisa dipastikan (butuh login) | 2 |

Metode: parse `captionTracks` dari `ytInitialPlayerResponse` pada halaman `youtube.com/watch`. Status player dibaca dari `playabilityStatus` supaya video yang hanya bisa dibuka setelah login tidak salah dihitung sebagai "tanpa caption". Detail: `results/automated/caption-check-20261011/caption-check.csv`

SC 1.2.2 adalah level A, jadi ini termasuk temuan paling serius di laporan ini. Untuk konten berskala 173 video, jalur yang masuk akal adalah transkrip otomatis lalu review manual oleh tim natively, bukan membuat subtitle manual satu per satu.

### Listen / TTS

**Belum dikerjakan.** Referensi: `listen-tts/comparison.md`.

Catatan konteks untuk Tahap berikutnya: ada 173 embed video dan 166 PDF, jadi kalau Read/TTS jadi prioritas, cakupan kontennya jauh lebih besar daripada asumsi awal 10 media. Verifikasi dulu apakah permintaan ini untuk pembaca dokumen atau untuk video.

## 8. Remediation Roadmap

### Phase 1 (9 temuan, estimasi 20 jam kerja)

- **A11Y-20261011-010** (Serious, SC 1.4.3, `color-contrast`) - Ubah token warna teks kartu ke rasio >= 4.5:1 [~4 jam]
- **A11Y-20261011-009** (Serious, SC 4.1.2, `frame-title`) - Quick win: tambah title pada iframe Maps + PDF Embed [~3 jam]
- **A11Y-20261011-023** (Moderate, SC 2.4.2, `pdf-no-title`) - Isi /Title saat ekspor PDF dengan judul dokumen [~3 jam]
- **A11Y-20261011-001** (Critical, SC 2.4.4, `link-name`) - Quick win: isi alt pada 6-10 logo mitra di header/footer [~2 jam]
- **A11Y-20261011-018** (Serious, SC 1.4.1, `link-in-text-block`) - Naikkan kontras link in-text + underline [~2 jam]
- **A11Y-20261011-022** (Serious, SC 3.1.1, `pdf-no-language`) - Set /Lang saat ekspor PDF (satu baris per file) [~2 jam]
- **A11Y-20261011-024** (Moderate, SC 2.5.8, `layout-target-size`) - Naikkan tombol zoom teks ke minimal 24x24 CSS px [~2 jam]
- **A11Y-20261011-015** (Moderate, SC 4.1.2, `aria-allowed-role`) - Hapus role=group dari <article> slider [~1 jam]
- **A11Y-20261011-017** (Minor, SC 1.3.1, `empty-heading`) - Isi atau hapus heading kosong [~1 jam]

### Phase 2 (5 temuan, estimasi 25 jam kerja)

- **A11Y-20261011-005** (Serious, SC 1.3.1, `heading-order`) - Rapikan hierarki heading di konten per template [~10 jam]
- **A11Y-20261011-016** (Moderate, SC 1.3.1, `page-has-heading-one`) - Tambah satu h1 per halaman [~6 jam]
- **A11Y-20261011-003** (Serious, SC 1.3.1, `landmark-no-duplicate-banner`) - Sembunyikan header non-aktif dengan display:none [~4 jam]
- **A11Y-20261011-002** (Serious, SC 4.1.2, `aria-hidden-focus`) - Tambahkan inert pada lightbox saat tertutup [~3 jam]
- **A11Y-20261011-004** (Serious, SC 1.3.1, `landmark-unique`) - Beri aria-label pada header aktif [~2 jam]

### Phase 3 (5 temuan, estimasi 11 jam kerja)

- **A11Y-20261011-012** (Serious, SC 2.4.3, `tabindex`) - Ganti tabindex positif di iframe PDF/Flipsnack [~4 jam]
- **A11Y-20261011-006** (Moderate, SC 4.1.2, `aria-allowed-attr`) - Known issue vendor YouTube - dokumentasikan + privacy embed [~2 jam]
- **A11Y-20261011-008** (Moderate, SC 4.1.2, `button-name`) - Known issue vendor YouTube - mitigasi dengan transkrip sendiri [~2 jam]
- **A11Y-20261011-028** (Moderate, SC 1.2.2, `video-login-required`) - Ganti embed ke youtube-nocookie + sertakan transkrip [~2 jam]
- **A11Y-20261011-007** (Moderate, SC 4.1.2, `aria-prohibited-attr`) - Known issue vendor YouTube - dokumentasikan [~1 jam]

### Phase 4 (9 temuan, estimasi 152 jam kerja)

- **A11Y-20261011-025** (Critical, SC 1.2.2, `video-no-caption`) - Buat caption Bahasa Indonesia untuk 159 video (batch ASR + review) [~60 jam]
- **A11Y-20261011-021** (Serious, SC 1.3.1, `pdf-not-tagged`) - Terbitkan ulang PDF sebagai tagged PDF/UA atau HTML [~30 jam]
- **A11Y-20261011-026** (Serious, SC 1.2.2, `video-caption-no-id`) - Tambah caption Bahasa Indonesia untuk video berbahasa Indonesia [~25 jam]
- **A11Y-20261011-020** (Critical, SC 1.1.1, `pdf-no-text-layer`) - OCR atau terbitkan ulang 7 PDF hasil scan sebagai HTML [~12 jam]
- **A11Y-20261011-027** (Moderate, SC 1.2.2, `video-caption-auto-only`) - Review caption ASR yang sudah ada [~12 jam]
- **A11Y-20261011-019** (Critical, SC 1.1.1, `pdf-403`) - Buka jalur unduh PDF yang tidak diblokir hotlink protection [~6 jam]
- **A11Y-20261011-011** (Serious, SC 1.1.1, `image-alt`) - Sediakan transkrip HTML untuk dokumen Flipsnack [~4 jam]
- **A11Y-20261011-013** (Serious, SC 1.3.1, `aria-required-children`) - Sediakan versi HTML dokumen, iframe PDF jadi bonus [~2 jam]
- **A11Y-20261011-014** (Serious, SC 1.3.1, `aria-required-parent`) - Sama dengan aria-required-children [~1 jam]

Urutan ini disusun dari `findings/findings.csv`, bukan placeholder. Estimasi jam adalah perkiraan engineering untuk implementasi + verifikasi sekali pada 1 template.

## 9. Histori

- 2026-10-11 - Audit awal (Tahap 1 scan otomatis + Tahap 2 clustering). 19 temuan unik dari 738 URL.

## 10. Appendix

- A. Daftar temuan lengkap: `findings/findings.csv` (28 baris, skema sesuai `AGENTS.md`)
- B. Index temuan + statistik per rule: `findings/findings-index.json`
- C. Output scan mentah: `results/automated/axe-20261011/`
- D. Ringkasan scan: `results/automated/axe-20261011/tahap1-summary.md`
- E. Verifikasi PDF/video: `results/automated/media-access-20261011/report.md`
- F. Struktur PDF: `results/automated/pdf-check-20261011/pdf-check-summary.csv` dan `summary.md`
- G. Inventaris: `inventory/templates.md`, `inventory/heuristics.csv`, `inventory/pdfs.csv`
- G. Template laporan: `reports/audit-report-template.md`
- H. Pernyataan aksesibilitas: `reports/accessibility-statement-draft.md` (draft, jangan publish sebelum Tahap 3 selesai)

## Persetujuan

| Peran | Nama | Tanda Tangan | Tanggal |
|-------|------|---------------|---------|
| Lead Auditor | | | |
| Technical Reviewer | | | |
| Stakeholder | | | |

