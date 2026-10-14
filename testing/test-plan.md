# Test Plan - Manual & Assistive Technology Testing

Matrix pengujian untuk audit aksesibilitas inovasi.or.id. Baseline: WCAG 2.2 Level AA.

---

## Matriks Browser & Assistive Technology

| Platform | Browser | Screen Reader | Versi | Catatan |
|----------|---------|---------------|-------|---------|
| Windows 10/11 | Firefox (latest) | NVDA (latest) | 2024.x | Kombinasi recommended |
| Windows 10/11 | Chrome (latest) | NVDA (latest) | 2024.x | Alternatif |
| macOS (latest) | Safari (latest) | VoiceOver (built-in) | macOS 14+ | Required untuk iOS parity |
| iOS (latest) | Safari (latest) | VoiceOver (built-in) | iOS 17+ | Mobile testing |
| Android (latest) | Chrome (latest) | TalkBack (latest) | Android 14+ | Mobile testing |

---

## Cakupan Uji per Template

Dari `inventory/templates.md` (akan diisi setelah crawl). Target: **8 template** (sesuai asumsi xlsx).

| Template | Halaman Contoh | Keyboard | Focus | Kontras | Reflow | Form | SR (NVDA) | SR (VoiceOver) | SR (TalkBack) |
|----------|----------------|----------|-------|---------|--------|------|-----------|----------------|---------------|
| Homepage | / | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Berita/Artikel | /berita/... | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Kategori/Arsip | /kategori/... | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Detail Program | /program/... | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Profil/About | /profil/... | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Kontak | /kontak/ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Pencarian | /search/... | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Error/404 | /404 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

*Centang setelah selesai diuji. Isi template setelah `crawl_inventory` dijalankan.*

---

## Skenario Uji Prioritas (WCAG 2.2 AA)

### Prioritas 1: Critical Path (Harus lolos)
1. **Keyboard Navigation** - Tab through all interactive elements, no trap (2.1.1, 2.1.2)
2. **Focus Visible** - Focus indicator jelas di semua elemen (2.4.7, 2.4.11, 2.4.13)
3. **Focus Not Obscured** - Focus tidak tertutup sticky header/footer (2.4.11)
4. **Form Accessibility** - Label, error, instruksi, autocomplete (1.3.5, 3.3.1, 3.3.2, 3.3.3)
5. **Reflow/Zoom 400%** - Konten reflow tanpa scroll horizontal (1.4.10)
6. **Non-text Contrast** - UI components, borders, icons ≥ 3:1 (1.4.11)
6. **Target Size** - Min 24x24 CSS px untuk touch (2.5.8)

### Prioritas 2: Screen Reader Compatibility
7. **Heading Structure** - Hierarki h1-h6 logis (1.3.1)
8. **Landmarks** - main, nav, aside, footer, header (1.3.1)
9. **Alt Text** - Gambar informatif punya alt, dekoratif alt="" (1.1.1)
10. **Link Purpose** - Teks link deskriptif, bukan "klik di sini" (2.4.4)
11. **Status Messages** - ARIA live regions untuk update dinamis (4.1.3)
12. **Table Headers** - th scope untuk tabel data (1.3.1)

### Prioritas 3: Multimedia & Documents
13. **Captions/Transcript** - Video punya caption, audio punya transcript (1.2.2, 1.2.1)
14. **PDF Accessibility** - Tagged, language, title, reading order (PDF/UA-1)

### Prioritas 4: New WCAG 2.2 Criteria
15. **Dragging Alternative** - Drag-drop punya alternatif keyboard (2.5.7)
16. **Consistent Help** - Bantuan lokasi konsisten (3.2.6)
17. **Redundant Entry** - Hindari input ulang data sama (3.3.7)
18. **Accessible Auth** - Login tanpa cognitive test (3.3.8)

---

## Prosedur Uji

### Setup NVDA + Firefox/Chrome
1. Install NVDA (gratis, nvaccess.org)
2. Buka Firefox/Chrome, navigasi ke URL test
3. Tekan `NVDA+Space` untuk browse mode
4. Gunakan `H` (heading), `K` (link), `F` (form), `T` (table) untuk navigasi cepat
10. Catat: apa yang tidak terbaca, urutan tidak logis, label hilang

### Setup VoiceOver + Safari (macOS)
1. `Cmd+F5` aktifkan VoiceOver
2. `Ctrl+Option+U` buka rotor, pilih "Headings", "Links", "Form Controls"
3. Navigasi dengan `Ctrl+Option+Panah`
4. Catat perbedaan dengan NVDA

### Setup VoiceOver + Safari (iOS)
1. Settings > Accessibility > VoiceOver > On
2. Rotor: `Two-finger rotate` pilih Headings/Links/Forms
3. Swipe kanan/kiri navigasi, double-tap aktifkan
4. Test orientasi portrait/landscape

### Setup TalkBack + Chrome (Android)
1. Settings > Accessibility > TalkBack > On
2. Swipe kanan/kiri navigasi, double-tap aktifkan
3. Menu lokal: `Three-finger tap` > "Headings", "Links", "Controls"
4. Test zoom 200%: Settings > Accessibility > Display size

---

## Pencatatan Hasil

Simpan di `results/manual/` dengan format:
- `manual-template-[nama]-[YYYYMMDD].md` - per template
- `manual-sr-nvda-[YYYYMMDD].md` - ringkasan NVDA
- `manual-sr-voiceover-[YYYYMMDD].md` - ringkasan VoiceOver
- `manual-sr-talkback-[YYYYMMDD].md` - ringkasan TalkBack

Masukkan temuan ke `findings/findings.csv` dengan `source=manual`.

---

## Kriteria Lulus / Gagal

| Status | Kriteria |
|--------|----------|
| **Lolos** | Semua skenario prioritas 1 & 2 lolos di minimal 1 kombinasi browser+SR per platform |
| **Perlu Perbaikan** | Ada temuan Critical/Serious di prioritas 1-2 |
| **Gagal** | Bloker keyboard trap, focus tidak visible, reflow gagal, form tidak accessible |

---

## Estimasi Waktu

| Aktivitas | Estimasi |
|-----------|----------|
| Setup AT & browser | 2 jam |
| Uji per template (keyboard + focus + kontras + reflow + form) | ~4 jam |
| Uji SR per template (NVDA) | ~1.5 jam |
| Uji SR per template (VoiceOver macOS) | ~1 jam |
| Uji SR per template (VoiceOver iOS) | ~1 jam |
| Uji SR per template (TalkBack) | ~1 jam |
| **Total per template** | **~8.5 jam** |
| **8 template** | **~68 jam (8.5 manday)** |