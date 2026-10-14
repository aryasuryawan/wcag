# Kertas Kerja Uji Manual — wcag

Tiga berkas untuk pengujian manual [inovasi.or.id](https://www.inovasi.or.id),
standar WCAG 2.2 Level AA.

| Berkas | Untuk siapa | Isi |
|--------|-------------|-----|
| `kertas-kerja-sederhana.xlsx` | **Dipakai sehari-hari** | 54 halaman utama, 22 pemeriksaan per halaman |
| `contoh-pengisian.xlsx` | Latihan | Cara mengisi, sudah ada isinya |
| `kertas-kerja-manual.xlsx` | Auditan detail | 12 sheet, cakupan lebih lengkap |

## Dua Orang

| Orang | Tugas |
|-------|-------|
| **Penguji (Tester)** | Menguji. Mengisi tanda L / G / T di sheet uji. |
| **Koordinator** | **Hanya memeriksa.** Mengisi kolom Koordinator, Tanggal Validasi, dan Sudah Diperiksa. |

> Baca dulu: [`../PANDUAN-MANUAL-TEST.md`](../PANDUAN-MANUAL-TEST.md).

## Cara Kerja Harian

```
1. Buka sheet 01-Daftar-Halaman
2. Pilih halaman yang Status Uji masih "Belum"
3. Buka sheet 02 sampai 05 sesuai nomor halamannya
   (halaman 1-14 memakai sheet 02, 15-28 memakai sheet 03, dan seterusnya)
4. Isi tanda di kotak yang sesuai:
      L = Lolos
      G = Gagal
      T = Tidak berlaku di halaman ini
5. Setiap tanda G wajib dicatat di sheet 06-Daftar-Temuan
6. Koordinator mengisi kolomnya di sheet 01 dan melihat hasil di sheet 07-Rekap
```

Satu halaman sekitar **15 menit**. Borr 10 halaman sudah sekitar 2 jam 30 menit.

Kolom **Jumlah Gagal** dan **Jumlah Diuji** di sheet `07-Rekap` dihitung otomatis.
Jangan diisi manual.

## Isi `kertas-kerja-sederhana.xlsx`

| Sheet | Isi |
|-------|-----|
| `00-Cara-Pakai` | Tata cara singkat, arti tanda, aturan tingkat kerugian |
| `01-Daftar-Halaman` | 54 halaman utama, lengkap dengan alamat dan jenisnya |
| `02-Uji-Halaman-01-14` | Pemeriksaan untuk halaman 1 sampai 14 |
| `03-Uji-Halaman-15-28` | Pemeriksaan untuk halaman 15 sampai 28 |
| `04-Uji-Halaman-29-42` | Pemeriksaan untuk halaman 29 sampai 42 |
| `05-Uji-Halaman-43-54` | Pemeriksaan untuk halaman 43 sampai 54 |
| `06-Daftar-Temuan` | Semua temuan, kolomnya mirip `findings/findings.csv` |
| `07-Rekap` | Jumlah gagal per halaman, dihitung otomatis |
| `08-Banding-Tiga-SR` | Perbandingan NVDA, VoiceOver, TalkBack |

Tanda diisi lewat daftar pilihan, jadi tidak bisa salah ketik.
Kotak hijau berarti Lolos, merah berarti Gagal.

## Contoh Pengisian

Buka `contoh-pengisian.xlsx`. Isinya:

- `00-Cara-Baca-Contoh` — penjelasan setiap kolom
- `01-Daftar-Halaman` — 3 baris contoh, sudah diisi status dan nama
- `02-Uji-Contoh` — 3 halaman (1, 2, 10) dengan tanda L, G, T
- `03-Daftar-Temuan` — 4 contoh temuan lengkap dengan cara mengecek dan sarannya
- `04-Rekap` — contoh hasil rekap

Contoh temuan di situ memakai masalah yang memang sudah ada di situs ini:
dua jumper banner, logo tanpa nama, pesan kesalahan yang tidak dibacakan,
dan isian formulir tanpa label.

## Dua Peringatan

1. **Jangan mengulang 28 temuan yang sudah ada.** Cek dulu:
   ```
   git grep -n A11Y- findings/findings.csv
   ```
   Kalau masalahnya sama, tambahkan jumlah halaman yang kena ke temuan lama.

2. **Jangan mengirim data sungguhan ke server asli.** Kalau formulir tidak bisa diuji
   tanpa mengirim data, tulis di kolom **Catatan**, jangan dipaksakan jadi temuan.

## Membuat Ulang Berkas

```
python scripts/build_kertas_kerja_sederhana.py
python scripts/build_contoh_pengisian.py
python scripts/build_kertas_kerja_xlsx.py
```

Alamat 54 halaman diambil otomatis dari `inventory/heuristics.csv`, jadi tetap sinkron
dengan hasil pemindaian. Kalau salah satu alamat tidak ada lagi, script akan mencetak
peringatan.

Tutup semua file Excel sebelum menjalankan script, karena Excel mengunci berkas yang sedang dibuka.

## Catatan Riwayat

Versi Markdown pernah ada di folder ini (`KK-00` sampai `KK-07`).
Semuanya sudah digabung ke berkas Excel lalu dihapus, supaya tidak ada dua versi
yang berbeda.
