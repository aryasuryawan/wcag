# Accessibility Statement Draft - inovasi.or.id

Template pernyataan aksesibilitas sesuai **EN 301 549** / **WCAG 2.2** / **UU Aksesibilitas Indonesia (jika berlaku)**. Siap publish setelah audit selesai & remediation Phase 1-2.

---

## Pernyataan Aksesibilitas

**Terakhir diperbarui**: [Tanggal]

### Status Kepatuhan

Website **inovasi.or.id** berkomitmen memastikan aksesibilitas digital bagi semua pengguna, termasuk penyandang disabilitas. Kami berusaha mematuhi **WCAG 2.2 Level AA** sebagai standar baseline, dengan referensi ke **WCAG 2.0 Level AA** dan **ISO/IEC 40500**.

**Status saat ini**: **Sebagian mematuhi (Partially Conformant)**

> *Catatan: "Sebagian mematuhi" berarti beberapa bagian konten tidak sepenuhnya memenuhi standar aksesibilitas. Kami sedang melakukan perbaikan bertahap.*

---

### Hasil Evaluasi Terbaru

| Evaluasi | Tanggal | Metode | Hasil |
|----------|---------|--------|-------|
| Audit Mandiri Internal | [YYYY-MM-DD] | WCAG 2.2 AA Audit (Otomatis + Manual + AT) | [X]% SC mematuhi |
| Audit Eksternal (jika ada) | [YYYY-MM-DD] | [Nama Vendor] | [Ringkasan] |

**Cakupan Evaluasi**: [N] halaman representatif dari [M] template utama, [P] dokumen PDF, [Q] konten multimedia.

---

### Area yang Belum Sepenuhnya Mematuhi (Known Issues)

Berikut daftar kendala aksesibilitas yang diketahui dan sedang diperbaiki:

| No | Isu | SC Terkait | Dampak | Target Perbaikan | Workaround Sementara |
|----|-----|------------|--------|------------------|----------------------|
| 1 | Focus indicator tidak terlihat pada beberapa tombol & link | 2.4.7, 2.4.13 | Pengguna keyboard kesulitan melacak fokus | [Bulan/Tahun] | Gunakan Tab + visual inspection |
| 2 | Beberapa gambar informatif tidak memiliki alt text | 1.1.1 | Screen reader tidak menyampaikan informasi gambar | [Bulan/Tahun] | Konten teks di dekat gambar menyampaikan info sama |
| 3 | Kontras teks beberapa komponen di bawah 4.5:1 | 1.4.3 | Sulit dibaca pengguna low vision | [Bulan/Tahun] | Zoom browser 150-200% |
| 4 | Beberapa form tidak memiliki label terprogram | 1.3.1, 3.3.2 | Screen reader tidak mengucapkan fungsi input | [Bulan/Tahun] | - |
| 5 | Video tidak memiliki caption/transcript | 1.2.2, 1.2.1 | Pengguna tunarungu/tidak bisa dengar audio | [Bulan/Tahun] | Transcript tersedia on-request |
| 6 | PDF lama tidak tagged/accessible | PDF/UA-1 | Screen reader tidak bisa navigasi PDF | [Bulan/Tahun] | Versi HTML/Word tersedia on-request |
| 7 | Reflow gagal pada beberapa halaman di 320px | 1.4.10 | Horizontal scroll di mobile/zoom tinggi | [Bulan/Tahun] | Gunakan desktop view |

*Daftar lengkap temuan: [Link ke laporan audit atau repo findings]*

---

### Fitur Aksesibilitas yang Tersedia

- **Skip to Main Content**: Link pertama di halaman (Tekan `Tab` saat load)
- **Navigasi Heading**: Struktur heading h1-h6 logis untuk navigasi SR
- **Landmark Regions**: header, nav, main, aside, footer
- **Focus Visible**: Outline fokus pada elemen interaktif (dalam perbaikan)
- **Text Resize**: Mendukung zoom browser hingga 200% tanpa loss fungsi
- **Reflow**: Konten menyesuaikan layar 320px (dalam perbaikan)
- **Keyboard Accessible**: Semua fungsi erreichbar via keyboard
- **Screen Reader Tested**: NVDA (Windows), VoiceOver (macOS/iOS), TalkBack (Android)

---

### Fitur Listen / Text-to-Speech

Kami mengevaluasi fitur **Listen (TTS)** sebagai **fitur tambahan** (bukan pengganti WCAG). Saat ini:
- **Status**: [Dalam evaluasi / PoC tersedia / Tidak tersedia]
- **PoC Demo**: [Link ke PoC jika ada]
- **Catatan**: Fitur ini tidak menggantikan kebutuhan screen reader, caption, atau audio description.

---

### Feedback & Kontak Aksesibilitas

Kami menyambut masukan untuk meningkatkan aksesibilitas website ini.

**Cara Menyampaikan Keluhan/Feedback Aksesibilitas:**

| Saluran | Detail |
|---------|--------|
| **Form Kontak** | [URL form kontak aksesibilitas] |
| **Email** | aksesibilitas@inovasi.or.id |
| **Telepon** | [Nomor telepon, jam operasional] |
| **WhatsApp** | [Nomor WA jika ada] |

**Waktu Respon Target**: Maksimal 5 hari kerja untuk mengakui keluhan, 30 hari kerja untuk rencana perbaikan.

---

### Teknologi Pendukung

Website ini diuji dengan kombinasi berikut:

| Platform | Browser | Screen Reader |
|----------|---------|---------------|
| Windows 10/11 | Firefox, Chrome | NVDA (latest) |
| macOS | Safari | VoiceOver (built-in) |
| iOS | Safari | VoiceOver (built-in) |
| Android | Chrome | TalkBack (latest) |

**Teknologi Web**: HTML5, CSS3, JavaScript (ES6+), ARIA 1.2
**CMS/Framework**: [Isi jika pakai WordPress, Laravel, dll.]

---

### Standar & Regulasi Referensi

- **WCAG 2.2 Level AA** (W3C Recommendation, 2023)
- **WCAG 2.0 Level AA** (ISO/IEC 40500:2012)
- **EN 301 549 v3.2.1** (European Accessibility Standard)
- **ISO 30071-1** (ICT Accessibility - Process)
- **UU No. 8 Tahun 2016** (Penyandang Disabilitas) - *jika berlaku untuk entitas publik*
- **Peraturan Menteri Kominfo** (jika ada regulasi spesifik sektor)

---

### Penyusunan & Verifikasi

| Peran | Nama/Organisasi | Tanggal |
|-------|-----------------|---------|
| Disusun oleh | [Tim Aksesibilitas / Auditor] | [YYYY-MM-DD] |
| Direview oleh | [Reviewer Teknis] | [YYYY-MM-DD] |
| Disetujui oleh | [Pebertanggungjawab Organisasi] | [YYYY-MM-DD] |

---

### Lampiran

1. **Rencana Perbaikan (Remediation Roadmap)** - [Link/Attachment]
2. **Hasil Audit Lengkap** - [Link ke findings/findings.csv]
3. **Glossary Istilah** - WCAG, SC, AT, SR, TTS, PDF/UA, dll.

---

## Catatan untuk Publish

1. **Letakkan di**: Footer website (link "Aksesibilitas"), halaman `/accessibility-statement`, dan `/aksesibilitas`
2. **Bahasa**: Indonesia (utama), English (opsional)
3. **Format**: HTML (bukan PDF) agar accessible
4. **Update**: Setiap 6 bulan atau setelah major remediation
5. **Versi Arsip**: Simpan versi sebelumnya untuk audit trail

---

*Template ini mengacu pada: W3C Accessibility Statement Generator, EN 301 549 Annex B, dan praktik terbaik pemerintahan digital Indonesia.*