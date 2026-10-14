# Panduan Uji Manual —UNTUK TIM YANG BARU

Panduan ini untuk **dua orang saja**:

- **Penguji (Tester)** — orang yang benar-benar membuka website dan mencoba semua fiturnya.
- **Koordinator** — orang yang **hanya memeriksa** hasil kerja Penguji. Tidak menguji.

Standar yang dipakai: **WCAG 2.2 Level AA**. Tidak perlu hafal semua aturannya, cukup pakai
lembar kerja yang sudah disiapkan.

---

## 1. Kenapa harus diuji manual?

Tahap sebelumnya (scan otomatis) **sudah selesai**:

- 738 halaman sudah discan pakai alat otomatis
- 7157 masalah mentah ditemukan
- Setelah digabung, jadi **28 masalah** yang sudah tercatat di `findings/findings.csv`

Yang **tidak bisa** dilihat oleh alat, dan harus diuji manual:

| Yang belum dicek | Kenapa alat tidak bisa |
|-----------------|----------------------|
| Tekan tombol Tab satu-satu | Butuh orang menekan |
| Penanda fokus (kotak fokus) terlihat atau tidak | Butuh mata manusia |
| Tampilan saat layar hanya 320 px | Butuh orang melihat |
| Pesan error saat form dikosongkan | Butuh orang mengisi form |
| Video 173 buah: Subtitle-nya benar atau tidak | Alat cuma cek tombolnya ada |
| Isi 101 file PDF | Yang dicek cuma metadata, bukan isi |

> **Aturan emas:** kalau orang lain tidak bisa mengulangiujinya dari tulisan Anda,
> itu **belum** layak jadi temuan. Tulis saja di bagian "Yang belum bisa diuji".

---

## 2. Pembagian Tugas Dua Orang

| Orang | Tugas | Kertas Kerja |
|-------|-------|-------------|
| **Penguji** | Menguji 1 jenis halaman dari awal sampai akhir. Mengisi semua lembar. | `KK-02` sampai `KK-07` |
| **Koordinator** | Membaca hasil Penguji, memastikan tidak ada yang terlewat atau berlebihan. | `KK-00`, `KK-01`, `KK-08` sampai `KK-10` |

**Tidak ada pembagian khusus.** Satu orang bisa mengerjakan semuanya. Kalau satu jenis halaman
mengFuealkan waktu lebih dari 90 menit, pindahkan ke sesi berikutnya.

---

## 3. Yang Harus Disiapkan Dulu

### Alat (wajib, kalau tidak ada hasilnya tidak sah)

- [ ] NVDA (program screen reader gratis untuk Windows) sudah terpasang
- [ ] NVDA **Speech Viewer** sudah dinyalakan (`NVDA+F5`) — ini alat untuk merekam apa yang diucapkan
- [ ] Firefox atau Chrome versi terbaru. Jangan pakai Edge.
- [ ] Mobile (HP) untuk mengecek tampilan layar kecil
- [ ] Perekam layar (OBS atau `Win+Alt+R` di Windows)
- [ ] Browser DevTools sudah terbuka (tekan `F12`)

### Sebelum menguji, baca aturan ini

- [ ] Baca `robots.txt` dulu
- [ ] Tunggu **1 detik** sebelum membuka halaman berikutnya
- [ ] **Jangan** login, jangan isi data pribadi, jangan kirim form ke server asli
- [ ] Kalau ada yang tidak boleh diperiksa, tulis di `KK-00` bagian Gap

---

## 4. Jenis Halaman yang Harus Diuji

Ada **13 jenis halaman**, bukan 8. Daftar lengkap ada di `inventory/templates.md`.

| No | Jenis halaman | Jumlah halaman | Contoh alamat |
|----|--------------|----------------|---------------|
| 1 | Detail Publikasi | 641 | `/en/publication/nuraga-the-teacher-a-story...` |
| 2 | Halaman Biasa | 36 | `/` |
| 3 | Arsip / Kategori Publikasi | 16 | `/publication-category/buku-cerita` |
| 4 | Wilayah Kerja (banyak slug) | 10 | `/where-we-works/cerita-praktik-baik` |
| 5 | Detail Wilayah Kerja | 8 | `/where-we-work/ikn` |
| 6 | Artikel Unggulan | 6 | `/featured-article/belajar-jadi-lebih-mudah...` |
| 7 | Galeri | 6 | `/gallery/curriculum-and-assessment` |
| 8 | Siaran Pers | 5 | `/press-release/australia-dan-indonesia...` |
| 9 | Detail Peluang | 4 | `/opportunity/invitation-to-tender...` |
| 10 | Sumber Daya | 4 | `/resources/for-children` |
| 11 | Arsip / Kategori Peluang | 1 | `/opportunity-category/career` |
| 12 | Beranda Bahasa Indonesia | 1 | `/` |
| 13 | Beranda Bahasa Inggris | 1 | `/en/` |

**Contoh halaman (nomor 1)**, punya 641 halaman. Tidak perlu diuji semuanya.
Cukup **3 halaman**: yang pertama, kedua, dan ketiga. Kalau ketiganya hasilnya sama,
tulis "sama di 3 halaman, kemungkinan sama juga di halaman lain".

Halaman 12 dan 13 paling penting. Halaman 7 (Galeri) juga penting karena ada galeri besar
yang sering membuat orang yang hanya pakai keyboard terjebak di dalam.

---

## 5. Cara Kerja Satu Sesi

```
Mulai
  |
  |-- Isi KK-00 (tanggal, nama, alat yang dipakai)
  |
  |-- Buka 1 jenis halaman dari KK-01
  |
  |-- Isi KK-03 (keyboard), KK-04 (screen reader),
  |     KK-05 (form), KK-06 (video & PDF), KK-07 (zoom & kontras)
  |
  |-- Tiap ada masalah: LANGSUNG tulis di KK-08
  |     (jangan ditunggu sampai akhir, nanti lupa)
  |
  |-- Simpan bukti ke results/manual/evidence/, catat di KK-09
  |
  |-- Isi KK-02 (kesimpulan untuk jenis halaman ini)
  |
  Selesai (maksimal 90 menit)
  |
  |-- Koordinator memeriksa, isi kolom validasi di KK-01
```

---

## 6. Cara Memberi Tanda pada Setiap Baris

Pakai empat tanda ini, sama di semua lembar:

| Tanda | Arti |
|-------|------|
| **L** | **Lolos** — tidak ada masalah |
| **G** | **Gagal** — ada masalah, langsung tulis di `KK-08` |
| **T** | **Tidak berlaku** — fitur ini memang tidak ada di halaman ini |
| **?** | **Belum diuji** |

Kalau wrote **T**, wajib tulis alasan di kolom catatan.
Kalau masih ada tanda **?** di akhir sesi, sesi itu **belum selesai**.

---

## 7. Menentukan Tingkat Kerugian

Ada empat tingkat. Pilih satu, tidak ada tingkat di antaranya.

| Tingkat | Kalau | Contoh nyata di situs ini |
|---------|-------|--------------------------|
| **Sangat serius** | Orang sama sekali tidak bisa menjalankan tugasnya | Logo utama tidak dibaca screen reader (A11Y-001). Orang yang pakai keyboard terjebak di galeri dan tidak bisa keluar |
| **Serius** | Tugas bisa selesai, tapi sangat susah | Ada dua header aktif sekaligus sehingga orang tidak tahu sedang di bagian mana (A11Y-003/004). Pesan error tidak pernah dibacakan |
| **Sedang** | Bisa selesai, tapi membingungkan dan makan waktu | Struktur judul melompat-lompat (A11Y-005) |
| **Kecil** | Tidak mengganggu, cuma tidak rapi | Ada judul kosong tanpa tulisan (A11Y-017) |

Tiga pertanyaan untuk memutuskan:

1. **Apakah orang bisa menyelesaikan tugasnya?** Tidak → Sangat serius.
2. **Apakah orang butuh bantuan luar (tahu cara kompensasinya)?** Ya → Serius.
3. **Apakah cuma lambat atau membingungkan?** Ya → Sedang. Tidak masalah → Kecil.

Kalau ragu antara "Sangat serius" dan "Serius", **pilih Serius** dan tulis alasannya.
Terlalu dramatis membuat laporan sulit dipercaya.

---

## 8. Aturan Jangan Mengulang Temuan yang Sudah Ada

**28 masalah sudah tercatat.** Jangan tulis ulang.

Kalau uji manual membuktikan masalah yang sama, **tambahkan informasi baru** ke temuan lama:
berapa halaman kena, atau screen reader mana yang kena. Jangan buat nomor baru.

Cara cek:

```
git grep -n "A11Y-2026" findings/findings.csv
```

Masalah yang paling sering ditulis ulang:

| Sudah ada | Jangan tulis lagi sebagai |
|-----------|--------------------------|
| A11Y-001 Logo tanpa nama | "linknya kosong" yang baru |
| A11Y-003/004 Dua header | "header dobel" di halaman lain |
| A11Y-005 Judul melompat | "struktur judul berantakan" |
| A11Y-010 Kontras teks 1,12:1 | "warnanya kurang kontras" tanpa menyebut elemen yang sama |
| A11Y-012 Tabindex positif | "tabindex salah" |
| A11Y-019/020 PDF tidak bisa dibuka / tidak ada teksnya | "PDFnya tidak ramah" |
| A11Y-021/022 PDF tidak bertanda / tidak ada bahasanya | "struktur PDF berantakan" |
| A11Y-025/026 Video tanpa subtitle Indonesia | "video tidak ada subtitlenya" |

**Yang benar-benar baru** (belum ada di 28 masalah): orang yang pakai keyboard terjebak,
urutan fokus yang membingungkan, fokus tertutup header yang menempel, tombol kecil di
HP, pesan error yang tidak dibacakan, subtitle ada tapi tidak cocok dengan suaranya,
situs tidak punya cara melapor masalah aksesibilitas.

---

## 9. Bukti yang Wajib Disimpan

Temuan tanpa bukti tidak akan diterima.

| Jenis masalah | Bukti yang benar | Nama file |
|---------------|------------------|-----------|
| Fokus / urutan tombol | Video 60 detik, **jangan** screenshot | `ev-ID-fokus-20261015.mp4` |
| Yang diucapkan screen reader | Salin teks dari Speech Viewer | `ev-ID-sr-20261015.txt` |
| Pesan error form | Screenshot **sebelum** dan **sesudah** dikirim | `ev-ID-form-20261015.png` |
| Warna kurang kontras | Angka rasio + 2 kode warna hex | `ev-ID-kontras-20261015.txt` |
| Tampilan layar kecil | Screenshot layar 320 px seluruh halaman | `ev-ID-320px-20261015.png` |
| Kode elemen | Salin kode HTML dari DevTools | `ev-ID-kode-20261015.html` |

Simpan di `results/manual/evidence/`. Tulis setiap file yang ditambahkan ke `KK-09`.

---

## 10. Yang Wajib Diperiksa Koordinator

Koordinator menolak lembar yang belum lengkap:

- [ ] Setiap baris sudah diisi — tidak boleh kosong, tidak boleh masih tanda **?**
- [ ] Setiap tanda **G** punya bukti di `KK-09`
- [ ] Cara mereproduksinya bisa dilakukan orang lain tanpa bertanya
- [ ] Setiap temuan menyebut elemen tertentu (kode elemen atau nama tombolnya),
      bukan cuma "tombol di bawah"
- [ ] Sudah dicek tidak sudah ada di 28 temuan lama
- [ ] Ada alasan tertulis kalau menolak severity-nya jadi "Sangat serius" atau "Serius"
- [ ] Saran perbaikannya jelas dan bisa dikerjakan. "Perbaiki warnanya" bukan saran.
      Tulis warna hex yang harusnya dipakai.

Kalau ada lembar yang ditolak, kembalikan ke Penguji. Kalau ada yang meragukan, ajukan
pertanyaan ke Penguji — jangan menebak sendiri.

---

## 11. Jebakan yang Perlu Diperhatikan

| Jebakan | Akibat | Yang Harus Dilakukan |
|---------|--------|-----------------------|
| Memakai zoom browser untuk mengecek tampilan 320 px | Hasilnya tidak sama dengan HP sungguhan | Gunakan mode perangkat di DevTools, atur lebar 320 px |
| Menganggap `alt=""` itu sudah benar | `alt=""` artinya gambar ini cuma hiasan. Kalau gambarnya berisi informasi, ini tetap masalah | Tanya: "kalau gambarnya hilang, informasinya ikut hilang?" |
| Mengira kontras dari mata | Angka pasti salah, khususnya teks kecil | Ambil warna dari DevTools, tulis di lembar `KK-07` |
| Membuka NVDA dalam mode yang salah | Mode "Fokus" hanya untuk mengisi form, hasilnya berbeda dari pengguna biasa | Untuk baca halaman, pakai **Mode Jelajah** (Mode Browse) |
| Hanya menguji di komputer | Banyak masalah hanya muncul di HP | Setiap jenis halamanminimal diuji satu kali di HP |
| Tidak mematikan video otomatis | Tidak bisa memeriksa aturan autoplay | Matikan dulu, uji terpisah di `KK-06` |
| Menulis "semua halaman" tanpa angka | Klaim tidak bisa diperiksa | Hitung dulu, contoh: "507 dari 738 halaman" |

---

## 12. Jadwal yang Disarankan

| Sesi | Yang Dikerjakan | Perkiraan Waktu |
|------|----------------|-----------------|
| 1 | Pasang NVDA, nyalakan Speech Viewer, belajar tombol dasarnya | 4 jam |
| 2 | Keyboard dan fokus pada 4 jenis halaman utama | 6 jam |
| 3 | Judul, bagian halaman, warna, tampilan 320 px dan zoom 200% | 10 jam |
| 4 | Form, pesan error, cara melapor masalah aksesibilitas | 5 jam |
| 5 | NVDA / VoiceOver / TalkBack pada 3 jenis halaman utama | 10 jam |
| 6 | Cek 40 halaman publikasi untuk memastikan polanya sama | 5 jam |

---

## 13. Contoh Catatan Temuan yang Benar

**Buruk** — tidak bisa diuji ulang:

```
Linknya kurang jelas.
```

**Baik** — bisa diuji ulang, ada buktinya, ada sarannya:

```
Nomor temuan  : MAN-20261015-014
Aturan         : 2.4.4 (A) Link Purpose (In Context)
Jenis halaman  : Arsip / Kategori Publikasi
Alamat         : https://www.inovasi.or.id/publication-category/buku-cerita
Tingkat        : Serius
Sumber         : manual (NVDA 2025.2 + Firefox 128, Windows 11)
Langkah        : 1. Buka alamat di Firefox dengan NVDA menyala
                 2. Tekan K untuk pindah ke daftar link
                 3. Dengarkan 8 link terakhir
Masalah        : 8 link semuanya bertuliskan "Baca Selengkapnya", tapi menuju 8 buku yang berbeda.
                 Dengan NVDA, orang tidak tahu link mana untuk buku mana.
                 Sudah mirip dengan A11Y-001.
Saran          : Ganti tulisan link dengan judul bukunya, atau tambahkan
                 aria-label="Baca detail: <judul>" pada <a class="fy-card-link">
Kode elemen    : .publication-card > h3 > a
Bukti          : ev-MAN-20261015-014-sr-20261015.txt
```

---

## 14. Setelah Semua Selesai

1. Koordinator menggabungkan semua baris `KK-08` ke `findings/findings.csv`
2. Nomor temuan manual: `MAN-YYYYMMDD-NNN`, contoh `MAN-20261015-001`
3. Koordinator mengisi kolom validasi di `KK-01`
4. Tulis ringkasan di `reports/tahap3-summary.md` (ikuti format `reports/tahap2-summary.md`)
5. Commit:
   ```
   git add results/manual findings/findings.csv testing/kertas-kerja
   git commit -m "docs: hasil uji manual tahap 3"
   ```
6. Yang **tidak bisa** diuji → tulis di bagian "Yang BELUM diuji" pada
   `reports/tahap3-summary.md`. Jangan dipaksakan jadi temuan.
