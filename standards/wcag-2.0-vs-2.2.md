# Perbandingan WCAG 2.0 vs 2.2 - Level A & AA

Referensi untuk mapping temuan audit inovasi.or.id. Baseline: **WCAG 2.2 Level AA**. Hasil dipetakan ke **WCAG 2.0 Level AA**.

---

## Success Criteria Baru di WCAG 2.1 (Tambahan dari 2.0)

| SC | Nama | Level | Kategori Scope (1-10) | Task Terkait |
|----|------|-------|----------------------|--------------|
| 1.3.4 | Orientation | AA | 3 | Responsive/reflow testing |
| 1.3.5 | Identify Input Purpose | AA | 4 | Form autocomplete |
| 1.4.10 | Reflow | AA | 3 | Mobile/reflow, zoom 400% |
| 1.4.11 | Non-text Contrast | AA | 3 | UI components, graphics |
| 1.4.12 | Text Spacing | AA | 3 | Custom text spacing override |
| 1.4.13 | Content on Hover or Focus | AA | 2 | Tooltip, dropdown, focus visible |
| 2.1.4 | Character Key Shortcuts | A | 2 | Keyboard shortcuts |
| 2.2.6 | Timeouts | AAA | - | (AAA - tidak baseline) |
| 2.3.3 | Animation from Interactions | AAA | - | (AAA - tidak baseline) |
| 2.5.1 | Pointer Gestures | A | 2 | Touch/pointer gestures |
| 2.5.2 | Pointer Cancellation | A | 2 | Touch cancellation |
| 2.5.3 | Label in Name | A | 4 | Accessible name contains visible label |
| 2.5.4 | Motion Actuation | A | 2 | Motion-based input |
| 2.5.5 | Target Size | AAA | - | (AAA - tidak baseline) |
| 2.5.6 | Concurrent Input Mechanisms | AAA | - | (AAA - tidak baseline) |
| 4.1.3 | Status Messages | AA | 1 | Live regions, ARIA status |

---

## Success Criteria Baru di WCAG 2.2 (Tambahan dari 2.1)

| SC | Nama | Level | Kategori Scope (1-10) | Task Terkait |
|----|------|-------|----------------------|--------------|
| 2.4.11 | Focus Not Obscured (Minimum) | AA | 2 | Focus visible, not hidden by sticky header/footer |
| 2.4.12 | Focus Not Obscured (Enhanced) | AAA | - | (AAA - tidak baseline) |
| 2.4.13 | Focus Appearance | AA | 2 | Focus indicator contrast, thickness |
| 2.5.7 | Dragging Movements | AA | 2 | Drag-drop alternative |
| 2.5.8 | Target Size (Minimum) | AA | 2 | Min 24x24 CSS pixels |
| 3.2.6 | Consistent Help | A | 9 | Help mechanism consistent location |
| 3.3.7 | Redundant Entry | A | 4 | Avoid re-entering same info |
| 3.3.8 | Accessible Authentication (Minimum) | AA | 4 | Auth without cognitive test |
| 3.3.9 | Accessible Authentication (Enhanced) | AAA | - | (AAA - tidak baseline) |

---

## SC yang Diubah/Direname di WCAG 2.2

| SC Lama (2.0/2.1) | SC Baru (2.2) | Perubahan |
|-------------------|---------------|-----------|
| 2.4.7 Focus Visible | 2.4.11/2.4.13 (Focus Not Obscured + Focus Appearance) | Dipecah jadi 2 SC baru, lebih spesifik |

---

## Mapping ke Kategori Scope Audit (prompt.md)

| Kategori | Deskripsi | SC Utama (2.2 AA) |
|----------|-----------|-------------------|
| 1 | Struktur aksesibilitas (heading, alt text, link, tabel, semantic HTML) | 1.1.1, 1.3.1, 1.3.2, 2.4.4, 2.4.6, 2.4.10 |
| 2 | Keyboard navigation dan visible focus | 2.1.1, 2.1.2, 2.1.4, **2.4.7**, **2.4.11**, **2.4.13**, 2.5.7, 2.5.8 |
| 3 | Kontras warna, text resize, mobile/reflow | 1.4.3, 1.4.4, **1.4.10**, **1.4.11**, **1.4.12** |
| 4 | Aksesibilitas form dan navigasi | 1.3.5, 2.5.3, 3.2.6, 3.3.1, 3.3.2, 3.3.3, 3.3.4, **3.3.7**, **3.3.8** |
| 5 | Kompatibilitas screen reader (NVDA, VoiceOver) | 1.1.1, 1.3.1, 1.3.2, 2.4.4, 2.4.6, 4.1.2, **4.1.3** |
| 6 | Caption/transcript multimedia | 1.2.1, 1.2.2, 1.2.3, 1.2.4, 1.2.5 |
| 7 | Aksesibilitas dokumen/PDF | PDF/UA-1, WCAG2ICT mapping |
| 8 | Pengujian otomatis + manual/AT | Semua SC |
| 9 | Mekanisme kontak/feedback aksesibilitas | **3.2.6**, 4.1.3 |
| 10 | Feasibility Listen/TTS | Bukan WCAG - fitur tambahan |

**Bold** = SC baru di WCAG 2.1/2.2 yang tidak ada di 2.0

---

## Catatan Mapping ke WCAG 2.0 AA

- SC baru di 2.1/2.2 **tidak ada di 2.0** → catat sebagai "Beyond 2.0 AA" di findings
- Untuk kepatuhan 2.0 AA: hanya cek SC yang ada di 2.0
- Untuk kepatuhan 2.2 AA: cek semua SC di atas (Level A + AA)
- Prioritas: Critical/Serious findings pada SC baru 2.2 = high priority fix