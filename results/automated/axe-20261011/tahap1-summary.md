# Tahap 1 - Ringkasan Scan Otomatis (axe-core)

Folder hasil: `axe-20261011`  
Dihasilkan: 2026-10-11T07:50:17

## Cakupan

| Metrik | Nilai |
|--------|-------|
| File hasil diproses | 740 |
| URL unik tercakup | 738 |
| File duplikat (dilewati) | 2 |
| URL di luar `urls-all.txt` (diabaikan) | 0 |
| URL dengan violation | 738 |
| Total violation | 4172 |
| Rule aktif | 18 |

## Violasi per impact

| Impact | Jumlah |
|--------|--------|
| critical | 302 |
| serious | 1734 |
| moderate | 2134 |
| minor | 2 |

## Per rule (urut URL terdampak) - dengan pemetaan SC

| Rule | SC | Nama SC | Level | URL terdampak | Node | Impact tertinggi | Contoh target |
|------|----|----------|-------|---------------|------|-----------------|--------------|
| `link-name` | 2.4.4 | Link Purpose (In Context) | A | 738 | 3213 | serious | `.fy-canvas > .fy-header.fy-header-left.is-on-top > .fy-heade` |
| `aria-hidden-focus` | 4.1.2 | Name |  Role | 737 | 737 | serious | `.fy-pswp` |
| `landmark-no-duplicate-banner` | 1.3.1 | Info and Relationships | A | 737 | 737 | moderate | `.fy-canvas > .fy-header.fy-header-left.is-on-top` |
| `landmark-unique` | 1.3.1 | Info and Relationships | A | 737 | 737 | moderate | `.fy-canvas > .fy-header.fy-header-left.is-on-top` |
| `heading-order` | 1.3.1 | Info and Relationships | A | 618 | 662 | moderate | `h4` |
| `aria-allowed-attr` | 4.1.2 | Name |  Role | 169 | 169 | critical | `#\36 49424024` |
| `aria-prohibited-attr` | 4.1.2 | Name |  Role | 169 | 169 | serious | `#\36 49424024` |
| `button-name` | 4.1.2 | Name |  Role | 123 | 123 | critical | `#\36 49424024` |
| `page-has-heading-one` | 1.3.1 | Info and Relationships | A | 42 | 43 | moderate | `#top` |
| `frame-title` | 4.1.2 | Name |  Role | 35 | 35 | serious | `iframe[width="400"]` |
| `tabindex` | 2.4.3 | Focus Order | A | 32 | 32 | serious | `.pdfembed-iframe` |
| `color-contrast` | 1.4.3 | Contrast (Minimum) | AA | 22 | 467 | serious | `.no-thumbnail > .dpt-entry-wrapper > .sub-entry > .dpt-title` |
| `image-alt` | 1.1.1 | Non-text Content | A | 8 | 19 | critical | `iframe[width="100%"]` |
| `aria-allowed-role` | 4.1.2 | Name |  Role | 1 | 8 | minor | `.swiper-slide-prev` |
| `aria-required-children` | 1.3.1 | Info and Relationships | A | 1 | 1 | critical | `.pdfembed-iframe` |
| `aria-required-parent` | 1.3.1 | Info and Relationships | A | 1 | 2 | critical | `.pdfembed-iframe` |
| `link-in-text-block` | 1.4.1 | Use of Color | A | 1 | 2 | serious | `a[href$="letsreadasia.org/"]` |
| `empty-heading` | - |  | - | 1 | 1 | minor | `.wp-block-heading` |

## Per template

| Template | URL discan | URL bermasalah | Violation | Top 3 rule |
|----------|------------|----------------|-----------|------------|
| publication | 641 | 641 | 3624 | `aria-hidden-focus` (641), `landmark-no-duplicate-banner` (641), `landmark-unique` (641) |
| page | 36 | 36 | 229 | `link-name` (36), `aria-hidden-focus` (35), `landmark-no-duplicate-banner` (35) |
| publication-category | 16 | 16 | 79 | `aria-hidden-focus` (16), `landmark-no-duplicate-banner` (16), `landmark-unique` (16) |
| where-we-works | 10 | 10 | 50 | `aria-hidden-focus` (10), `heading-order` (10), `landmark-no-duplicate-banner` (10) |
| where-we-work | 8 | 8 | 48 | `aria-hidden-focus` (8), `heading-order` (8), `landmark-no-duplicate-banner` (8) |
| featured-article | 6 | 6 | 33 | `aria-hidden-focus` (6), `heading-order` (6), `landmark-no-duplicate-banner` (6) |
| gallery | 6 | 6 | 30 | `aria-hidden-focus` (6), `heading-order` (6), `landmark-no-duplicate-banner` (6) |
| press-release | 5 | 5 | 25 | `aria-hidden-focus` (5), `heading-order` (5), `landmark-no-duplicate-banner` (5) |
| opportunity | 4 | 4 | 24 | `aria-hidden-focus` (4), `heading-order` (4), `landmark-no-duplicate-banner` (4) |
| resources | 4 | 4 | 20 | `aria-hidden-focus` (4), `heading-order` (4), `landmark-no-duplicate-banner` (4) |
| opportunity-category | 1 | 1 | 5 | `aria-hidden-focus` (1), `heading-order` (1), `landmark-no-duplicate-banner` (1) |
| unknown | 1 | 1 | 5 | `aria-hidden-focus` (1), `heading-order` (1), `landmark-no-duplicate-banner` (1) |

## Catatan interpretasi

- Angka di atas adalah instance violation per URL, bukan jumlah isu unik. Satu isu template (mis. `landmark-unique`) yang muncul di 738 URL tetap dihitung 1 fix.
- `incomplete` (needs review) tidak dihitung sebagai violation; itu masuk Tahap 3 (manual).
- Scan ini hanya mencakup sebagian SC WCAG 2.2 AA. Evaluasi keyboard, focus order, reflow, error message, caption video, dan struktur PDF tetap wajib manual.
- Severity final (Critical/Serious/Moderate/Minor) ditentukan di Tahap 2, bukan dari impact axe.

