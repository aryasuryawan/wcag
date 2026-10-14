# Tasklist & Estimasi - Audit Aksesibilitas inovasi.or.id

Tasklist & estimasi effort (jam / manday) - audit aksesibilitas inovasi.or.id.

Estimasi effort ini bersifat internal. Data komersial (tarif, biaya, nilai penawaran) tidak disimpan di repo ini.

---

## Fase 1: Persiapan & Inventory

| No | Task | PIC | Estimasi (Jam) | Estimasi (Manday) | Catatan |
|----|------|-----|----------------|-------------------|---------|
| 1.1 | Setup workspace, dependencies, AGENTS.md, README | AI | 2 | 0.25 |  | Sudah dibuat |
| 1.2 | Crawl inventory (sitemap/homepage) → urls.txt, templates.md, pdfs.csv, media.csv | AI | 4 | 0.5 |  | Script crawl_inventory.py |
| 1.3 | Validasi inventory vs asumsi xlsx (8 template, 30 PDF, 10 media) | AI | 1 | 0.125 |  | Bandingkan & laporkan |
| 1.4 | Setup standar: wcag-2.0-vs-2.2.md, sc-mapping.csv | AI | 3 | 0.375 |  | Referensi mapping SC |

**Subtotal Fase 1**: 10 jam (1.25 manday)

---

## Fase 2: Automated Scanning

| No | Task | PIC | Estimasi (Jam) | Estimasi (Manday) | Catatan |
|----|------|-----|----------------|-------------------|---------|
| 2.1 | Jalankan axe-core/Pa11y batch pada urls.txt | AI | 3 | 0.375 |  | Script run_axe.py |
| 2.2 | Jalankan Lighthouse CLI (accessibility only) pada urls.txt | AI | 3 | 0.375 |  | Script run_lighthouse.py |
| 2.3 | Cek PDF dasar (tagged, bahasa, judul, halaman) | AI | 4 | 0.5 |  | Script check_pdfs.py |
| 2.4 | Merge findings → findings/findings.csv (dedup, map SC) | AI | 3 | 0.375 |  | Script merge_findings.py |
| 2.5 | Ringkasan temuan per SC & severity | AI | 2 | 0.25 |  | Laporan otomatis |

**Subtotal Fase 2**: 15 jam (1.875 manday)

---

## Fase 3: Manual Testing & AT

| No | Task | PIC | Estimasi (Jam) | Estimasi (Manday) | Catatan |
|----|------|-----|----------------|-------------------|---------|
| 3.1 | Siapkan test-plan.md (matrix browser/AT) | AI | 2 | 0.25 |  | NVDA, VoiceOver, TalkBack |
| 3.2 | Siapkan manual-checklist.md per template (WCAG 2.2 AA) | AI | 4 | 0.5 |  | Keyboard, focus, kontras, reflow, form, dll |
| 3.3 | Siapkan screen-reader-script.md | AI | 2 | 0.25 |  | Skenario uji SR |
| 3.4 | Eksekusi uji manual per template (8 template × ~4 jam) | Tester | 32 | 4 |  | Butuh tester manusia |
| 3.5 | Eksekusi uji AT (NVDA, VoiceOver, TalkBack) | Tester | 24 | 3 |  | Butuh tester manusia |
| 3.6 | Catat temuan manual ke findings/findings.csv | AI | 4 | 0.5 |  | Merge dengan otomatis |

**Subtotal Fase 3**: 68 jam (8.5 manday) - *Butuh tester manusia*

---

## Fase 4: Listen/TTS Feasibility

| No | Task | PIC | Estimasi (Jam) | Estimasi (Manday) | Catatan |
|----|------|-----|----------------|-------------------|---------|
| 4.1 | Riset & bandingkan: ReadSpeaker vs Web Speech API vs Cloud TTS | AI | 4 | 0.5 |  | Kriteria: EN/ID, kualitas, highlight, biaya, privasi, maintenance |
| 4.2 | Buat comparison.md | AI | 2 | 0.25 |  | Tabel perbandingan |
| 4.3 | PoC Web Speech API (1 file HTML, 1 template) | AI | 4 | 0.5 |  | listen-tts/poc/ |

**Subtotal Fase 4**: 10 jam (1.25 manday)

---

## Fase 5: Laporan & Deliverables

| No | Task | PIC | Estimasi (Jam) | Estimasi (Manday) | Catatan |
|----|------|-----|----------------|-------------------|---------|
| 5.1 | Buat audit-report-template.md | AI | 3 | 0.375 |  | Template laporan lengkap |
| 5.2 | Buat accessibility-statement-draft.md | AI | 2 | 0.25 |  | Draft pernyataan aksesibilitas |
| 5.3 | Isi laporan audit akhir (dari findings.csv + manual) | AI | 8 | 1 |  | Butuh data dari Fase 2 & 3 |
| 5.4 | Review & finalisasi semua deliverables | AI | 4 | 0.5 |  | |

**Subtotal Fase 5**: 17 jam (2.125 manday)

---

## Ringkasan Total

| Fase | Jam | Manday | Catatan |
|------|-----|--------|---------|
| 1. Persiapan & Inventory | 10 | 1.25 | AI only |
| 2. Automated Scanning | 15 | 1.875 | AI only |
| 3. Manual Testing & AT | 68 | 8.5 | **Butuh tester manusia** |
| 4. Listen/TTS Feasibility | 10 | 1.25 | AI only |
| 5. Laporan & Deliverables | 17 | 2.125 | AI only |
| **TOTAL** | **120** | **15** | |

---

## Pembagian 3 Tahap (realisasi, 738 URL)

Asumsi sheet xlsx (8 template / 30 PDF / 10 media) tidak berlaku. Kenyataannya: 738 URL unik,
13 template, 166 PDF, 211 media. Audit dipecah 3 tahap supaya bisa dijadwalkan per blok 4-5 jam.

### Tahap 1 - Scan Otomatis (SELESAI, 11 Okt 2026)

| Item | Nilai |
|------|-------|
| URL discan | 738/738 |
| Durasi | 38 mnt (concurrency 3, 1 Chrome) |
| Rule aktif | 18 |
| Total violation | 4172 |
| Critical / Serious / Moderate / Minor | 302 / 1734 / 2134 / 2 |

Output: `results/automated/axe-20261011/` (`tahap1-summary.md`, `violations-by-rule.csv`, `violations-by-url.csv`)

Top rule (URL terdampak): `link-name` 740, `aria-hidden-focus` 739, `landmark-no-duplicate-banner` 739,
`landmark-unique` 739, `heading-order` 620, `aria-allowed-attr` 169, `aria-prohibited-attr` 169,
`button-name` 123, `page-has-heading-one` 43, `frame-title` 35, `tabindex` 32, `color-contrast` 23.

### Tahap 2 - Cluster, Severity, findings.csv (BERIKUTNYA, ~8 jam)

| Blok | Isi | Jam |
|------|-----|-----|
| 2.1 | Cluster 4172 violation jadi isu unik per template | 3 |
| 2.2 | Tetapkan severity Critical/Serious/Moderate/Minor + dedup | 2 |
| 2.3 | Tulis `findings/findings.csv` + ringkasan per SC | 3 |

### Tahap 3 - Manual Testing & AT per template (~40 jam)

| Blok | Isi | Jam |
|------|-----|-----|
| 3.1 | Setup NVDA/VoiceOver/TalkBack | 4 |
| 3.2 | Keyboard + focus visible, 4 template inti | 6 |
| 3.3 | Heading/landmark/semantic, kontras, reflow 320px + zoom 200% | 10 |
| 3.4 | Form, error message, mekanisme feedback aksesibilitas | 5 |
| 3.5 | NVDA/VoiceOver/TalkBack pada 3 template inti | 10 |
| 3.6 | Sampling publikasi (40 URL) + verifikasi pola isu berulang | 5 |

Di luar 3 tahap: `check_pdfs.py` struktur PDF (101 file yang bisa diunduh) dan laporan akhir.