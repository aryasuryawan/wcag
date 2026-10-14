# Findings Template

Format standar untuk `findings/findings.csv`. Setiap temuan = 1 baris.

---

## Kolom CSV

| Kolom | Tipe | Contoh | Deskripsi |
|-------|------|--------|-----------|
| ID | string | A11Y-20241007-001 | Unik, format: A11Y-YYYYMMDD-NNN (urut per tanggal) |
| URL | string | https://inovasi.or.id/berita/detail-123 | URL halaman tempat temuan ditemukan |
| template | string | Berita Detail | Nama template dari `inventory/templates.md` |
| SC | string | 2.4.7 | Success Criterion WCAG (format: X.Y.Z) |
| level | enum | AA | Level: A / AA |
| versi | enum | 2.2 | Versi WCAG: 2.0 / 2.2 |
| kategori_scope | int | 2 | Kategori scope 1-10 (lihat prompt.md) |
| severity | enum | Serious | Critical / Serious / Moderate / Minor |
| source | enum | axe | axe / lighthouse / manual / pdf-check |
| deskripsi | string | Tombol "Kirim" tidak memiliki focus indicator yang terlihat | Deskripsi singkat isu (max 200 char) |
| langkah_reproduksi | string | 1. Buka halaman<br>2. Tab ke tombol Kirim<br>3. Focus tidak terlihat | Langkah reproduksi jelas, terpisah dengan `<br>` |
| rekomendasi | string | Tambahkan CSS `:focus-visible { outline: 3px solid #0066cc; }` | Rekomendasi perbaikan konkret, actionable |
| status | enum | Open | Open / Fixed / Won't Fix / False Positive |

---

## Severity Guidelines

| Severity | Kriteria | Contoh |
|----------|----------|--------|
| **Critical** | Bloker total untuk pengguna AT, keyboard trap, tidak bisa menyelesaikan tugas utama | Keyboard trap di modal, form tidak bisa submit via keyboard, halaman tidak reflow 320px |
| **Serious** | Penghalang signifikan, user AT kesulitan besar, melanggar SC Level A/AA inti | Fokus tidak visible, heading hierarchy broken, alt text hilang di gambar informatif, label form hilang |
| **Moderate** | Pengguna AT bisa akses tapi dengan usaha ekstra, melanggu SC tapi ada work-around | Kontras 4.0:1 (butuh 4.5:1), link "klik di sini", skip link tidak ada, live region missing |
| **Minor** | Pelanggaran best practice, tidak langsung blokir, cosmetic | Heading level skip (h1→h3), landmark redundant, ARIA label verbose, PDF metadata missing |

---

## Source Mapping

| Source | Tools | Cakupan |
|--------|-------|---------|
| axe | axe-core / Pa11y | ~30-40% SC WCAG (otomatis) |
| lighthouse | Lighthouse CLI (accessibility) | ~25-35% SC WCAG (otomatis) |
| manual | Manual testing + AT | ~60-80% SC WCAG (manual) |
| pdf-check | PDF parser (PyMuPDF, pdfplumber) | PDF/UA-1 basics |

---

## ID Generation Rule

```
A11Y-YYYYMMDD-NNN
```

- YYYYMMDD = tanggal scan/penemuan
- NNN = urut 001, 002... per tanggal
- Contoh: A11Y-20241007-001, A11Y-20241007-002

Script `merge_findings.py` generate ID otomatis.

---

## Status Workflow

```
Open → (Fix implemented) → Fixed → (Verified) → Closed
Open → (Won't Fix approved) → Won't Fix
Open → (False Positive verified) → False Positive
```

---

## Contoh Baris CSV

```csv
ID,URL,template,SC,level,versi,kategori_scope,severity,source,deskripsi,langkah_reproduksi,rekomendasi,status
A11Y-20241007-001,https://inovasi.or.id/berita/detail-123,Berita Detail,2.4.7,AA,2.2,2,Serious,axe,"Focus indicator tidak terlihat pada tombol CTA","1. Buka URL<br>2. Tab ke tombol 'Baca Selengkapnya'<br>3. Focus ring tidak muncul","Tambahkan CSS: .btn:focus-visible { outline: 3px solid #0066cc; outline-offset: 2px; }",Open
A11Y-20241007-002,https://inovasi.or.id/kategori/teknologi,Kategori Arsip,1.1.1,A,2.2,1,Critical,manual,"Gambar thumbnail artikel tidak punya alt text","1. Buka URL<br>2. NVDA: G untuk navigasi gambar<br>3. Dibaca 'graphic' tanpa deskripsi","Tambahkan alt text deskriptif pada img.thumbnail di template kategori",Open
A11Y-20241007-003,https://inovasi.or.id/program/beasiswa,Program Detail,1.4.3,AA,2.2,3,Moderate,lighthouse,"Kontras teks abu-abu pada background putih 3.8:1","1. Buka URL<br>2. Inspect teks '.card-description'<br>3. DevTools contrast ratio 3.8:1","Ubah warna teks ke #595959 (ratio 4.5:1) atau background ke #f0f0f0",Open
```

---

## Deduplication Rules (merge_findings.py)

1. **Same URL + Same SC + Same Element Selector** → Gabung, keep highest severity, merge sources (pipe-separated: `axe|manual`)
2. **Same URL + Same SC + Different Element** → Separate rows (different element = different fix)
3. **Different URL + Same Template + Same SC + Same Component Pattern** → Flag as "Pattern Issue" di catatan, tapi tetap separate rows per URL

---

## Export untuk Laporan

Untuk laporan audit, bisa di-pivot:
- Per SC: `df.groupby('SC').agg(count=('ID','count'), severity=('severity', lambda x: x.value_counts().to_dict()))`
- Per Template: `df.groupby('template').agg(...)`
- Per Severity: `df['severity'].value_counts()`
- Per Source: `df['source'].value_counts()`
- Beyond WCAG 2.0: `df[df['versi']=='2.2' & ~df['SC'].isin(wcag20_sc)]`