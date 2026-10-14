# Kertas Kerja Uji Manual — wcag

Kertas kerja uji manual untuk [inovasi.or.id](https://www.inovasi.or.id),
standar WCAG 2.2 Level AA.

## Satu Berkas untuk Dua Orang

Seluruh kertas kerja sudah digabung menjadi **satu berkas Excel**:

```
testing/kertas-kerja/kertas-kerja-manual.xlsx
```

Dua orang saja yang memakai:

| Orang | Tugas |
|-------|-------|
| **Penguji (Tester)** | Menguji satu jenis halaman dari awal sampai akhir. Mengisi kolom pengujian. |
| **Koordinator** | **Hanya memeriksa** hasil Penguji. Tidak menguji. Mengisi kolom validasi dan menyetujui. |

> Baca dulu: [`../PANDUAN-MANUAL-TEST.md`](../PANDUAN-MANUAL-TEST.md).

## Isi Berkas Excel

| Sheet | Isi | Diisi oleh |
|-------|-----|------------|
| `00-Panduan` | Tata cara memakai berkas, arti tanda L/G/T/?, daftar periksa Koordinator | — (baca saja) |
| `01-Koordinasi` | 13 jenis halaman: status, nama Penguji, persetujuan Koordinator | Penguji + Koordinator |
| `02-Rincian-Uji` | 13 jenis halaman × 9 kelompok pemeriksaan = 117 baris siap isi | Penguji |
| `03-Kesimpulan-Akhir` | Satu baris kesimpulan per jenis halaman | Penguji + Koordinator |
| `04-Keyboard-Fokus` | 20 pemeriksaan keyboard, urutan fokus, kotak fokus, ukuran tombol | Penguji |
| `05-ScreenReader` | 27 pemeriksaan NVDA / VoiceOver / TalkBack | Penguji |
| `06-Form-Error` | 24 pemeriksaan formulir dan pesan kesalahan | Penguji |
| `07-Media-PDF` | 12 pemeriksaan video dan audio + 11 pemeriksaan isi PDF | Penguji |
| `08-Zoom-Kontras` | 30 pemeriksaan zoom, layar 320 px, warna, gerakan | Penguji |
| `09-Daftar-Temuan` | Semua temuan baru. Kolomnya sama dengan `findings/findings.csv` | Penguji |
| `10-Daftar-Bukti` | Daftar berkas bukti di `results/manual/evidence/` | Penguji |
| `11-Banding-SR` | Perbandingan hasil baca di empat screen reader | Penguji |

Bantuan di dalam berkas: pilihan dropdown untuk kolom **Hasil** (L/G/T/?),
warna otomatis (hijau = Lolos, merah = Gagal), dan filter di sheet besar.

## Alur Kerja

```
1. Buka sheet 01-Koordinasi, pilih satu jenis halaman yang belum diuji
2. Salin sheet 04 sampai 08 untuk jenis halaman itu
3. Isi kolom Hasil. Setiap tanda G langsung dicatat di sheet 09-Daftar-Temuan
4. Simpan bukti ke results/manual/evidence/, daftarkan di sheet 10-Daftar-Bukti
5. Isi sheet 02-Rincian-Uji dan 03-Kesimpulan-Akhir untuk jenis halaman itu
6. Koordinator memeriksa, lalu mengisi kolom Validator di sheet 01-Koordinasi
```

Maksimal **90 menit per jenis halaman**. Lebih dari itu, istirahat 15 menit.

## Menyalin Sheet

Sheet `04` sampai `08` hanya untuk satu jenis halaman. Untuk jenis halaman berikutnya:

1. Klik kanan nama sheet di bagian bawah
2. Pilih **Move or Copy**, centang **Create a copy**, lalu **OK**
3. Ganti isinya dengan jenis halaman yang baru

## Dua Peringatan Penting

1. **Jangan mengulang 28 temuan yang sudah ada.** Cek dulu:
   ```
   git grep -n A11Y- findings/findings.csv
   ```
   Kalau masalahnya sama, tambahkan jumlah halaman atau screen reader yang kena ke temuan lama.

2. **Jangan mengirim data ke server asli.** Kalau formulir tidak bisa diuji tanpa
   mengirim data sungguhan, tulis di kolom **Yang Belum Bisa Diuji**, jangan dipaksakan.

## Buat Ulang Berkas Excel

```
python scripts/build_kertas_kerja_xlsx.py
```

Script ini membuat ulang `kertas-kerja-manual.xlsx` dari data yang ada di dalam script.
Jangan mengedit isi Excel secara manual lalu menjalankan ulang script, karena perubahan
manual akan hilang.

## Catatan Riwayat

Kertas kerja versi Markdown pernah ada di folder ini (`KK-00` sampai `KK-07`).
Semuanya sudah digabung ke berkas Excel dan dihapus supaya tidak ada dua versi
yang berbeda. Kalau butuh perubahan isi, ubah `scripts/build_kertas_kerja_xlsx.py`
lalu jalankan ulang.
