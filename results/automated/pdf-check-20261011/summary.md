# Cek Aksesibilitas Dasar PDF

Dihasilkan: 2026-10-11T11:29:54  
Durasi: 3.9 menit

## Ringkasan

| Aspek | Hasil |
|-------|-------|
| PDF terdaftar | 166 |
| Tidak bisa diakses (403) | 65 |
| Gagal diunduh | 0 |
| Berhasil diperiksa | 95 (dari cache: 6) |
| Tagged (ada MarkInfo/StructTreeRoot) | 53/101 |
| Punya bahasa (/Lang atau dc:language) | 53/101 |
| Punya judul metadata | 30/101 |
| Tanpa layer teks (hasil scan) | 7/101 |

## Yang Dipakai sebagai Patokan

- Tagged: `/MarkInfo <</Marked true>>` atau `/StructTreeRoot` ada di catalog PDF. Ini prasyarat PDF/UA; tanpa itu, screen reader hanya membaca urutan visual.
- Bahasa: entri `/Lang` di catalog, fallback ke metadata dokumen, lalu XMP `dc:language`.
- Judul: metadata `/Title`. Layar baca file sering membacakan nama file kalau judul kosong.
- Layer teks: 3 halaman pertama. PDF hasil scan tanpa OCR punya 0 karakter - tidak bisa dibaca screen reader sama sekali (SC 1.1.1).

## Yang BELUM Diperiksa

- Alt text gambar di dalam PDF (butuh parser struktur tag, mis. veraPDF/PAC).
- Heading hierarchy dan reading order (butuh tools PDF/UA penuh).
- Tab order form, kontras teks, dan ukuran font.
- Isi bahasa dokumen (apakah teksnya Bahasa Indonesia yang benar).
- 65 PDF yang membalas 403 tidak bisa diperiksa tanpa akses ke direktori `securepdfs`.

