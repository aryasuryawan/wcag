# Audit Report Template

Template laporan audit aksesibilitas inovasi.or.id. Isi dari `findings/findings.csv` + uji manual.

---

## 1. Executive Summary

| Item | Detail |
|------|--------|
| **Website** | https://inovasi.or.id |
| **Tanggal Audit** | [YYYY-MM-DD] s.d. [YYYY-MM-DD] |
| **Standar** | WCAG 2.2 Level AA (baseline), dipetakan ke WCAG 2.0 Level AA |
| **Scope** | 10 kategori (prompt.md) |
| **Metodologi** | Automated (axe-core, Lighthouse) + Manual (Keyboard, NVDA, VoiceOver, TalkBack) + PDF Check |
| **Tools** | axe-core v4.x, Lighthouse v11.x, NVDA 2024.x, VoiceOver macOS 14/iOS 17, TalkBack Android 14 |
| **Total Temuan** | [XXX] (Critical: X, Serious: X, Moderate: X, Minor: X) |
| **Cakupan Otomatis** | ~[XX]% SC WCAG (otomatis hanya ~30-50%) |
| **Cakupan Manual** | [X] template diuji, [X] browser+AT kombinasi |

**Kesimpulan Singkat**: [1-2 paragraf: status kepatuhan umum, risiko utama, prioritas perbaikan]

---

## 2. Scope & Methodology

### 2.1 Halaman yang Diuji (Sample)
Dari `inventory/urls.txt` (total [N] URL, mewakili [M] template):
- [Tabel ringkas: Template | URL Contoh | Status Uji]

### 2.2 Assistive Technology Matrix
| Platform | Browser | Screen Reader | Template Diuji |
|----------|---------|---------------|----------------|
| Windows 11 | Firefox 128 | NVDA 2024.2 | [list] |
| Windows 11 | Chrome 128 | NVDA 2024.2 | [list] |
| macOS 14 | Safari 17 | VoiceOver | [list] |
| iOS 17 | Safari | VoiceOver | [list] |
| Android 14 | Chrome | TalkBack | [list] |

### 2.3 Keterbatasan
- Tes otomatis hanya ~30-50% SC WCAG
- Sample URL [N] dari total halaman (estimasi [M] halaman)
- PDF sample [N] dari [M] total PDF
- [Catat kendala: crawl blocked, no sitemap, dll.]

---

## 3. Findings Summary

### 3.1 Ringkasan per Severity
| Severity | Jumlah | % | Trend |
|----------|--------|---|-------|
| Critical | [X] | [X]% | → |
| Serious | [X] | [X]% | → |
| Moderate | [X] | [X]% | → |
| Minor | [X] | [X]% | → |
| **Total** | **[XXX]** | **100%** | |

### 3.2 Ringkasan per SC (Top 10)
| SC | Nama | Level | Jumlah | Severity Dominan |
|----|------|-------|--------|------------------|
| 1.1.1 | Non-text Content | A | [X] | Serious |
| 2.4.7 | Focus Visible | AA | [X] | Critical |
| 1.4.3 | Contrast (Minimum) | AA | [X] | Moderate |
| ... | ... | ... | ... | ... |

### 3.3 Ringkasan per Template
| Template | Critical | Serious | Moderate | Minor | Total |
|----------|----------|---------|----------|-------|-------|
| Homepage | X | X | X | X | X |
| Berita Detail | X | X | X | X | X |
| ... | ... | ... | ... | ... | ... |

### 3.4 Beyond WCAG 2.0 (WCAG 2.2 Only)
| SC | Nama | Jumlah | Catatan |
|----|------|--------|---------|
| 2.4.11 | Focus Not Obscured | X | Baru di 2.2 |
| 2.4.13 | Focus Appearance | X | Baru di 2.2 |
| 2.5.8 | Target Size (Minimum) | X | Baru di 2.2 |
| ... | ... | ... | ... |

---

## 4. Detailed Findings

### 4.1 Critical Findings
| ID | URL | Template | SC | Deskripsi | Rekomendasi |
|----|-----|----------|-----|-----------|-------------|
| A11Y-... | ... | ... | ... | ... | ... |

### 4.2 Serious Findings
[Same format]

### 4.3 Moderate Findings
[Same format]

### 4.4 Minor Findings
[Same format]

---

## 5. Manual Testing Results

### 5.1 Keyboard Navigation
- [Ringkasan: apakah semua template lolos keyboard navigation, focus order, focus visible, skip link]

### 5.2 Screen Reader Compatibility
| Template | NVDA+FF | NVDA+Chrome | VoiceOver macOS | VoiceOver iOS | TalkBack |
|----------|---------|-------------|-----------------|---------------|----------|
| Homepage | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ |
| ... | ... | ... | ... | ... | ... |

**Catatan per AT**: [Isu spesifik per screen reader]

### 5.3 Zoom & Reflow (320px / 400%)
- [Template yang gagal reflow, horizontal scroll issue]

### 5.4 Form Accessibility
- [Label, error, autocomplete, redundant entry, accessible auth]

---

## 6. PDF Accessibility

| PDF URL | Judul | Tagged | Language | Title | Pages | Issues |
|---------|-------|--------|----------|-------|-------|--------|
| ... | ... | Yes/No | id/none | Yes/No | N | [List] |

---

## 7. Listen/TTS Feasibility

Ringkasan dari `listen-tts/comparison.md`:
- **Rekomendasi**: [ReadSpeaker / Web Speech API Hybrid / Cloud TTS / Self-hosted]
- **Alasan**: [1-2 kalimat]
- **Estimasi Biaya Tahunan**: $[X]
- **PoC**: `listen-tts/poc/index.html` (Web Speech API demo)

---

## 8. Remediation Roadmap

### Phase 1: Quick Wins (1-2 sprints)
- [Critical/Serious yang fix mudah: CSS focus, alt text, label]

### Phase 2: Structural Fixes (3-5 sprints)
- [Heading hierarchy, landmark, form redesign, reflow]

### Phase 3: Complex Components (5-8 sprints)
- [Custom widgets: modal, tabs, carousel, autocomplete, drag-drop]

### Phase 4: PDF & Multimedia (Parallel)
- [PDF remediation, caption/transcript video]

### Phase 5: Verification & Maintenance
- [Regression test, monitoring, accessibility statement publish]

---

## 9. Accessibility Statement Draft

Lihat `reports/accessibility-statement-draft.md` untuk template pernyataan aksesibilitas yang siap publish.

---

## 10. Appendix

- A. Full Findings CSV (lampirkan `findings/findings.csv`)
- B. Automated Scan Raw Output (link ke `results/automated/`)
- C. Manual Test Notes (link ke `results/manual/`)
- D. Tool Versions & Config
- E. Glossary (WCAG, SC, AT, SR, dll.)

---

## Approval

| Role | Nama | Tanda Tangan | Tanggal |
|------|------|--------------|---------|
| Lead Auditor | | | |
| Technical Reviewer | | | |
| Stakeholder | | | |