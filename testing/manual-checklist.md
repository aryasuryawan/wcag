# Manual Checklist WCAG 2.2 AA per Template

Checklist untuk uji manual per template halaman. Gunakan bersama `testing/test-plan.md` dan `testing/screen-reader-script.md`.

---

## 1. Keyboard Navigation & Focus (Scope 2)

| No | Checkpoint | SC | Test Method | Pass/Fail | Catatan |
|----|------------|-----|-------------|-----------|---------|
| 1.1 | Semua fungsi erreichbar via keyboard saja | 2.1.1 | Tab melalui seluruh halaman | ☐ | |
| 1.2 | Tidak ada keyboard trap | 2.1.2 | Tab masuk & keluar komponen (modal, menu) | ☐ | |
| 1.3 | Focus order logis (kiri-kanan, atas-bawah) | 2.4.3 | Tab sequence visual = DOM order | ☐ | |
| 1.4 | Focus visible di semua elemen interaktif | 2.4.7 | Outline/ring jelas, tidak hanya color change | ☐ | |
| 1.5 | Focus tidak tertutup sticky header/footer | 2.4.11 | Scroll sampai focus di tepi viewport | ☐ | |
| 1.6 | Focus appearance: contrast ≥ 3:1, thickness ≥ 2px | 2.4.13 | Cek outline di light/dark mode | ☐ | |
| 1.7 | Skip link berfungsi (jump ke main content) | 2.4.1 | Tab pertama = skip link, Enter works | ☐ | |
| 1.8 | Character key shortcuts: bisa dinonaktifkan/remap | 2.1.4 | Cek shortcut custom | ☐ | |
| 1.9 | Drag-drop punya alternatif keyboard | 2.5.7 | Cek sortable list, upload, dll | ☐ | |
| 1.10 | Target size minimal 24x24 CSS px | 2.5.8 | Ukuran tombol, link, checkbox, radio | ☐ | |

---

## 2. Struktur & Semantic HTML (Scope 1)

| No | Checkpoint | SC | Test Method | Pass/Fail | Catatan |
|----|------------|-----|-------------|-----------|---------|
| 2.1 | Heading hierarchy h1-h6 logis, tidak lompat level | 1.3.1 | Outline view / WAVE toolbar | ☐ | |
| 2.2 | Landmarks: header, nav, main, aside, footer | 1.3.1 | NVDA: `Insert+F7` > Landmarks | ☐ | |
| 2.3 | List markup untuk daftar (ul/ol/li) | 1.3.1 | Inspect element | ☐ | |
| 2.4 | Tabel data: th scope, caption, header cellules | 1.3.1 | Inspect tabel, test NVDA `T` | ☐ | |
| 2.5 | Link purpose jelas dari teks link saja | 2.4.4 | Baca link out of context | ☐ | |
| 2.6 | Multiple ways: nav, search, sitemap, breadcrumb | 2.4.5 | Cek minimal 2 cara cari halaman | ☐ | |
| 2.7 | Section headings untuk area konten | 2.4.10 | Heading di setiap section | ☐ | |
| 2.8 | Page title unik & deskriptif | 2.4.2 | `<title>` di tab browser | ☐ | |
| 2.9 | Bypass blocks (skip link, heading nav) | 2.4.1 | Skip to main, heading navigation | ☐ | |
| 2.10 | Parsing: valid HTML, no duplicate ID | 4.1.1 | Validator.w3.org | ☐ | |

---

## 3. Non-Text Content & Media (Scope 1, 6)

| No | Checkpoint | SC | Test Method | Pass/Fail | Catatan |
|----|------------|-----|-------------|-----------|---------|
| 3.1 | Gambar informatif: alt text deskriptif | 1.1.1 | Inspect img, test SR | ☐ | |
| 3.2 | Gambar dekoratif: alt="" atau role=presentation | 1.1.1 | Inspect img | ☐ | |
| 3.3 | Gambar kompleks (chart, infografis): long desc | 1.1.1 | Cek longdesc / adjacent text | ☐ | |
| 3.4 | Video prerecorded: caption synchronized | 1.2.2 | Play video, cek CC button | ☐ | |
| 3.5 | Audio prerecorded: transcript tersedia | 1.2.1 | Link transcript dekat player | ☐ | |
| 3.6 | Video live: caption live | 1.2.4 | Cek live stream | ☐ | |
| 3.7 | Video: audio description (prerecorded) | 1.2.3, 1.2.5 | Cek AD track / extended desc | ☐ | |
| 3.8 | Audio control: pause/stop/volume independen | 1.4.2 | Auto-play audio > 3 detik | ☐ | |
| 3.9 | Media player accessible (keyboard, SR labels) | 4.1.2 | Test controls via keyboard | ☐ | |

---

## 4. Kontras, Resize & Reflow (Scope 3)

| No | Checkpoint | SC | Test Method | Pass/Fail | Catatan |
|----|------------|-----|-------------|-----------|---------|
| 4.1 | Text contrast ≥ 4.5:1 (normal), ≥ 3:1 (large) | 1.4.3 | Colour Contrast Analyser / DevTools | ☐ | |
| 4.2 | Non-text contrast (UI, border, icon) ≥ 3:1 | 1.4.11 | Cek focus, button border, icon | ☐ | |
| 4.3 | Text resize 200% tanpa loss content/function | 1.4.4 | Browser zoom 200% (Ctrl++) | ☐ | |
| 4.4 | Reflow 400% (320px width) tanpa horizontal scroll | 1.4.10 | Resize viewport 320px / zoom 400% | ☐ | |
| 4.5 | Text spacing override: line 1.5x, paragraph 2x, letter 0.12x, word 0.16x | 1.4.12 | Bookmarklet / user stylesheet | ☐ | |
| 4.6 | Content on hover/focus: dismissible, hoverable, persistent | 1.4.13 | Test tooltip, dropdown, menu | ☐ | |
| 4.7 | Use of color: info tidak hanya warna | 1.4.1 | Error state, required field, links | ☐ | |
| 4.8 | Images of text: hindari, gunakan text CSS | 1.4.5 | Cek logo, button image, banner | ☐ | |

---

## 5. Form & Input (Scope 4)

| No | Checkpoint | SC | Test Method | Pass/Fail | Catatan |
|----|------------|-----|-------------|-----------|---------|
| 5.1 | Label terprogram (label for, aria-label, aria-labelledby) | 1.3.1, 3.3.2 | Inspect input, test SR | ☐ | |
| 5.2 | Required field ditandai (aria-required, visual) | 3.3.2 | Cek asterisk + aria-required="true" | ☐ | |
| 5.3 | Error identification: teks error jelas, spesifik | 3.3.1 | Submit kosong/salah, cek pesan | ☐ | |
| 5.4 | Error suggestion: saran perbaikan | 3.3.3 | Format email, password, dll | ☐ | |
| 5.5 | Error prevention: review/confirm untuk legal/financial/data | 3.3.4 | Cek checkout, pendaftaran | ☐ | |
| 5.6 | Autocomplete: autocomplete attribute benar | 1.3.5 | name, email, tel, address, dll | ☐ | |
| 5.7 | Label in Name: accessible name mengandung visible label | 2.5.3 | Cek aria-label vs visible text | ☐ | |
| 5.8 | Redundant entry: hindari input ulang data sama | 3.3.7 | Cek multi-step form | ☐ | |
| 5.9 | Accessible authentication: tidak cognitive test (captcha puzzle) | 3.3.8 | Cek login, register | ☐ | |
| 5.10 | On focus/input: tidak trigger nav/perubahan konteks tak terduga | 3.2.1, 3.2.2 | Tab through form, input data | ☐ | |

---

## 6. Screen Reader Compatibility (Scope 5)

| No | Checkpoint | SC | Test Method | Pass/Fail | Catatan |
|----|------------|-----|-------------|-----------|---------|
| 6.1 | Name, Role, Value: semua kontrol punya accessible name | 4.1.2 | NVDA: `Insert+Tab` pada kontrol | ☐ | |
| 6.2 | Status messages: ARIA live region (polite/assertive) | 4.1.3 | Trigger update (search, filter, cart) | ☐ | |
| 6.3 | ARIA landmarks & roles digunakan benar | 1.3.1 | NVDA Landmarks dialog | ☐ | |
| 6.4 | Modal dialog: focus trap, aria-modal, label | 4.1.2 | Buka modal, Tab cycle di dalam | ☐ | |
| 6.5 | Expand/collapse: aria-expanded, aria-controls | 4.1.2 | Test accordion, dropdown, menu | ☐ | |
| 6.6 | Tabpanel: role=tablist, tab, tabpanel, aria-selected | 4.1.2 | Test tabs component | ☐ | |
| 6.7 | Menu/menubar: role, aria-orientation, keyboard nav | 4.1.2 | Test navigation menu | ☐ | |
| 6.8 | Toast/alert: role=alert/status, live region | 4.1.3 | Trigger notifikasi | ☐ | |
| 6.9 | Language of page & parts: lang attribute | 3.1.1, 3.1.2 | `<html lang="id">`, `<span lang="en">` | ☐ | |
| 6.10 | Consistent navigation & identification | 3.2.3, 3.2.4 | Nav & Komponen konsisten across pages | ☐ | |

---

## 7. Timing & Motion (Scope 2, 3)

| No | Checkpoint | SC | Test Method | Pass/Fail | Catatan |
|----|------------|-----|-------------|-----------|---------|
| 7.1 | Timing adjustable: bisa extend/disable timeout | 2.2.1 | Cek session timeout, carousel auto-advance | ☐ | |
| 7.2 | Pause, stop, hide: moving content > 5 detik | 2.2.2 | Carousel, animation, ticker | ☐ | |
| 7.3 | Three flashes or below threshold | 2.3.1 | Cek animasi cepat, video | ☐ | |
| 7.4 | Animation from interactions: bisa disable | 2.3.3 | prefers-reduced-motion | ☐ | |
| 7.5 | Motion actuation: alternatif untuk motion input | 2.5.4 | Shake, tilt, gesture | ☐ | |
| 7.6 | Pointer gestures: path-based → single pointer | 2.5.1 | Swipe carousel, map drag | ☐ | |
| 7.7 | Pointer cancellation: up-event = cancel | 2.5.2 | Click drag, release outside | ☐ | |

---

## 8. Consistent Help & Feedback (Scope 9)

| No | Checkpoint | SC | Test Method | Pass/Fail | Catatan |
|----|------------|-----|-------------|-----------|---------|
| 8.1 | Help mechanism: contact, FAQ, chat lokasi konsisten | 3.2.6 | Cek header/footer semua halaman | ☐ | |
| 8.2 | Accessibility statement link di footer | Best practice | Link ke accessibility-statement | ☐ | |
| 8.3 | Feedback mechanism aksesibel (form kontak accessible) | 4.1.2 | Test form kontak | ☐ | |

---

## Cara Pakai

1. Isi template ini untuk **setiap template** dari `inventory/templates.md`
2. Simpan hasil di `results/manual/manual-checklist-[template]-[YYYYMMDD].md`
3. Temuan yang **Fail** → masukkan ke `findings/findings.csv` dengan `source=manual`
4. Screenshot/evidence simpan di `results/manual/evidence/`

---

## Catatan

- Checklist ini mencakup **semua SC Level A & AA WCAG 2.2** + mapping ke 2.0
- Prioritaskan kolom **Pass/Fail** dan **Catatan** untuk temuan
- Uji SR (NVDA, VoiceOver, TalkBack) terpisah di `screen-reader-script.md`