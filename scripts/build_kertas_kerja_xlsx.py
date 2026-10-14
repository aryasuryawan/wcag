"""Bangun file Excel ``testing/kertas-kerja/kertas-kerja-manual.xlsx``.

File Excel ini menggabungkan seluruh kertas kerja uji manual menjadi satu berkas
multi-sheet supaya bisa dibagikan ke tim tanpa banyak file terpisah.

Jalankan ulang setiap kali ada perubahan isi lembar:

    python scripts/build_kertas_kerja_xlsx.py

Semua isi lembar memakai bahasa Indonesia sederhana. Istilah teknis (nama aturan
WCAG, nama atribut HTML, nama program) tetap dalam bahasa Inggris karena itu
memang nama aslinya.
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT_ROOT / "testing" / "kertas-kerja" / "kertas-kerja-manual.xlsx"

WARN = {
    "Warna Isian": "F4B183",
    "Warna Header": "305496",
    "Warna Sub": "D9E1F2",
    "Warna Catatan": "FFF2CC",
}

FONT_HEADER = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
FONT_TITLE = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
FONT_BOLD = Font(name="Calibri", size=11, bold=True)
FONT_NORMAL = Font(name="Calibri", size=11)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP_TOP = Alignment(vertical="top", wrap_text=True)
WRAP_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)

TANDA = '"L,G,T,?"'

LEMBAR = [
    ("00-Panduan", "Tata cara memakai berkas ini. Baca dulu sebelum mengisi."),
    ("01-Koordinasi", "Daftar 13 jenis halaman: status, nama Penguji, persetujuan Koordinator."),
    ("02-Rincian-Uji", "Hasil uji per jenis halaman untuk 9 kelompok pemeriksaan. 117 baris, siap diisi."),
    ("03-Kesimpulan-Akhir", "Satu baris kesimpulan untuk tiap jenis halaman."),
    ("04-Keyboard-Fokus", "Lembar uji keyboard dan kotak fokus. Salin sheet ini per jenis halaman."),
    ("05-ScreenReader", "Lembar uji NVDA, VoiceOver, TalkBack. Salin sheet ini per jenis halaman."),
    ("06-Form-Error", "Lembar uji formulir dan pesan kesalahan. Salin sheet ini per jenis halaman."),
    ("07-Media-PDF", "Lembar uji video dan file PDF. Salin sheet ini per jenis halaman."),
    ("08-Zoom-Kontras", "Lembar uji zoom, layar kecil, warna, dan gerakan. Salin sheet ini per jenis halaman."),
    ("09-Daftar-Temuan", "Semua temuan baru. Kolomnya sama dengan findings/findings.csv."),
    ("10-Daftar-Bukti", "Daftar file bukti di folder results/manual/evidence/."),
    ("11-Banding-SR", "Perbandingan hasil baca di 4 screen reader."),
]

JENIS_HALAMAN = [
    (1, "Detail Publikasi", 641,
     "https://www.inovasi.or.id/en/publication/nuraga-the-teacher-a-story-of-diversity-in-inclusive-education-copy1",
     "Cukup uji 3 halaman: pertama, kedua, ketiga dari inventory/urls.txt"),
    (2, "Halaman Biasa", 36, "https://www.inovasi.or.id/",
     "Uji juga 1 halaman versi Inggris (/en/...) untuk cek aturan bahasa"),
    (3, "Arsip / Kategori Publikasi", 16,
     "https://www.inovasi.or.id/publication-category/buku-cerita",
     "Perhatikan link Baca Selengkapnya yang berulang dan halaman berikutnya"),
    (4, "Wilayah Kerja (slug jamak)", 10,
     "https://www.inovasi.or.id/where-we-works/cerita-praktik-baik",
     "Cek apakah 10 halaman ini benar-benar sama semua"),
    (5, "Detail Wilayah Kerja", 8, "https://www.inovasi.or.id/where-we-work/ikn",
     "Bisa ada peta Google Maps di dalam, cek namanya terbaca"),
    (6, "Artikel Unggulan", 6,
     "https://www.inovasi.or.id/featured-article/belajar-jadi-lebih-mudah-kekuatan-bahasa-daerah-di-sekolah",
     "Cek tombol berbagi dan daftar artikel terkait"),
    (7, "Galeri", 6, "https://www.inovasi.or.id/gallery/curriculum-and-assessment",
     "PENTING. Ada galeri besar yang bisa menjebak orang yang hanya pakai keyboard"),
    (8, "Siaran Pers", 5,
     "https://www.inovasi.or.id/press-release/australia-dan-indonesia-perkuat-kemitraan-untuk-tekan-angka-putus-sekolah-di-ntt",
     ""),
    (9, "Detail Peluang", 4,
     "https://www.inovasi.or.id/opportunity/invitation-to-tender-eo-for-education-reform-dialog-with-palestinian-moehe",
     "Biasanya ada formulir atau lampiran, isi juga sheet 06-Form-Error"),
    (10, "Sumber Daya", 4, "https://www.inovasi.or.id/resources/for-children",
     "Banyak file PDF di sini, isi juga sheet 07-Media-PDF"),
    (11, "Arsip / Kategori Peluang", 1,
     "https://www.inovasi.or.id/opportunity-category/career",
     "Cukup 1 halaman. Bandingkan dengan jenis halaman nomor 3"),
    (12, "Beranda Bahasa Indonesia", 1, "https://www.inovasi.or.id/",
     "PALING PENTING. Ada gambar yang berpindah sendiri, logo tanpa nama, dua header"),
    (13, "Beranda Bahasa Inggris", 1, "https://www.inovasi.or.id/en/",
     "Bandingkan dengan nomor 12: bahasa, terjemahan, menu yang berbeda"),
]

CAKUPAN = [
    ("Struktur halaman dan kode HTML", "02, 05"),
    ("Keyboard dan kotak fokus", "04"),
    ("Warna, zoom, tampilan layar kecil", "08"),
    ("Formulir dan isian", "06"),
    ("Screen reader", "05"),
    ("Gambar, video, audio", "07"),
    ("Dokumen PDF", "07"),
    ("Bahasa halaman", "05"),
    ("Cara melapor masalah aksesibilitas", "06"),
]

BARIS_KOORDINASI = ["No", "Jenis Halaman", "Jumlah Halaman", "Alamat Contoh",
                    "Alamat Tambahan yang Diuji", "Status", "Penguji",
                    "Tanggal Selesai", "Validator", "Tanggal Validasi",
                    "Catatan Koordinator"]
KOLOM_KOORDINASI = [7, 30, 14, 55, 40, 12, 16, 14, 16, 14, 45]

BARIS_RINCIAN = ["Jenis Halaman", "No", "Kelompok Pemeriksaan", "Lembar Kerja",
                 "Yang Wajib Dicek", "Hasil", "Nomor Temuan", "Catatan"]
KOLOM_RINCIAN = [30, 5, 30, 14, 45, 9, 16, 45]

YANG_WAJIB = {
    "Struktur halaman dan kode HTML": "Judul halaman (h1) ada dan hanya satu; bagian halaman (landmark) benar; daftar memakai tag daftar; tabel punya judul kolom",
    "Keyboard dan kotak fokus": "Semua tombol bisa ditekan pakai keyboard; tidak terjebak; urutan fokus masuk akal; kotak fokus terlihat; kotak fokus tidak tertutup header yang menempel",
    "Warna, zoom, tampilan layar kecil": "Warna teks cukup kontras; teks masih terbaca saat dizoom 200%; tidak ada gulir ke samping saat layar 320 px; jarak baris tidak merusak tampilan",
    "Formulir dan isian": "Setiap isian punya nama yang terbaca; field wajib ditandai; pesan kesalahan muncul dan dibaca screen reader; ada isian otomatis (autocomplete)",
    "Screen reader": "Semua tombol punya nama; perubahan di layar dibacakan otomatis; tabel dan judul bisa dinavigasi",
    "Gambar, video, audio": "Gambar informatif punya keterangan; gambar hiasan dikosongkan; video punya subtitle Bahasa Indonesia yang cocok; pemutar bisa dipakai keyboard",
    "Dokumen PDF": "PDF punya judul; bahasa ditandai; PDF bertanda (tagged); urutan baca benar; gambar di dalam PDF punya keterangan",
    "Bahasa halaman": "Halaman menandai bahasa Indonesia (lang=id); bagian bahasa Inggris ditandai lang=en; judul tab browser deskriptif",
    "Cara melapor masalah aksesibilitas": "Ada cara menghubungi; alamat email jadi tautan; lokasi cara melapor sama di semua halaman",
}

BARIS_UJI = ["No", "Yang diperiksa", "Aturan WCAG", "Cara Memeriksa", "Hasil",
             "Nomor Temuan", "Catatan"]
KOLOM_UJI = [5, 46, 16, 40, 8, 16, 42]

UJI_KEYBOARD = [
    ("Semua tautan bisa dibuka pakai keyboard", "2.1.1", "Tekan Tab dari atas sampai bawah tanpa memakai tetikus"),
    ("Semua tombol bisa dibuka pakai keyboard", "2.1.1", "Tekan Tab sampai semua tombol dilewati"),
    ("Semua isian formulir bisa dibuka pakai keyboard", "2.1.1", "Tekan Tab sampai semua isian dilewati"),
    ("Tidak ada Reduce Motion", "2.1.2", "Buka galeri, menu, dan searching. Coba keluar dari semuanya"),
    ("Tidak terjebak di galeri besar", "2.1.2", "Buka galeri, tekan Tab beberapa kali, coba tekan Esc"),
    ("Tidak terjebak di menu paling atas", "2.1.2", "Buka menu, tekan Esc, pastikan menu tertutup"),
    ("Tidak terjebak di searching", "2.1.2", "Buka searching, tekan Esc, pastikan tertutup"),
    ("Tidak terjebak di pemutar video", "2.1.2", "Klik masuk ke pemutar video, tekan Tab untuk keluar lagi"),
    ("Urutan fokus mengikuti urutan yang dilihat mata", "2.4.3", "Tulis urutan 20 tekan Tab pertama, bandingkan dengan tampilan"),
    ("Ada kotak fokus di setiap elemen", "2.4.7", "Rekam layar saat menekan Tab satu per satu"),
    ("Kotak fokus tidak cuma perubahan warna", "2.4.7", "Lihat apakah teksnya berubah juga"),
    ("Kotak fokus tidak tertutup header atau footer yang menempel", "2.4.11", "Tab ke elemen paling bawah, lihat apakah kotak fokus tertutup"),
    ("Kotak fokus cukup tebal dan kontras", "2.4.11, 2.4.13", "Buka DevTools, lihat ketebalan garis dan rasio warnanya"),
    ("Ada tombol lompat ke konten utama", "2.4.1", "Tekan Tab pertama, harus muncul tautan lompat"),
    ("Tautan lompat benar-benar memindahkan fokus", "2.4.1", "Tekan Enter, lihat apakah fokus masuk ke konten utama"),
    ("Hanya ada satu bagian header", "1.3.1", "Buka daftar bagian halaman di NVDA, hitung bagian banner"),
    ("Tombol ukuran teks minimal 24x24 piksel", "2.5.8", "Ukur dengan DevTools pada tampilan HP"),
    ("Tombol berbagi minimal 24x24 piksel", "2.5.8", "Ukur dengan DevTools"),
    ("Tombol halaman sebelumnya dan berikutnya minimal 24x24 piksel", "2.5.8", "Ukur dengan DevTools"),
    ("Tombol kirim formulir minimal 24x24 piksel", "2.5.8", "Ukur dengan DevTools"),
]

UJI_SCREENREADER = [
    ("Judul tab browser dibacakan saat halaman dibuka", "2.4.2", "Dengarkan NVDA"),
    ("Daftar bagian halaman terbaca (header, menu, konten utama, kaki halaman)", "1.3.1", "Tekan NVDA+Insert+F7, pilih bagian"),
    ("Hanya ada satu bagian header", "1.3.1", "Hitung di daftar bagian halaman"),
    ("Ada satu judul utama (h1) dan terbaca", "1.3.1", "Tekan H untuk pindah antar judul"),
    ("Urutan judul tidak melompat-lompat", "1.3.1", "Tekan H berulang, tulis urutannya"),
    ("Nama tombol utama terbaca", "4.1.2", "Dengarkan saat menekan Tab"),
    ("Nama tautan logo terbaca", "4.1.1, 4.1.2", "Tekan K untuk pindah ke tautan pertama"),
    ("Teks setiap tautan menjelaskan tujuannya", "2.4.4", "Tekan K, baca semua nama tautan tanpa melihat layar"),
    ("Tidak ada tautan kosong tanpa nama", "4.1.2", "Tekan K, cari yang tidak punya nama"),
    ("Tautan yang membuka tab baru ditandai", "3.2.4", "Baca nama tautannya"),
    ("Ada dua cara untuk menemukan halaman", "2.4.5", "Cari menu, searching, dan peta situs"),
    ("Kotak searching punya nama yang terbaca", "4.1.2", "Tekan F untuk pindah ke isian"),
    ("Menu membuka-tutup punya status yang terbaca", "4.1.2", "Buka menu, dengarkan kata terbuka atau tertutup"),
    ("Galeri besar punya nama dan tombol exit", "4.1.2", "Buka galeri, dengarkan"),
    ("Gambar yang bisa dibaca punya keterangan", "1.1.1", "Tekan G untuk pindah ke gambar"),
    ("Iframe peta dan Flipsnack punya nama", "4.1.2", "Tekan I untuk pindah antar bingkai"),
    ("Iframe YouTube punya nama", "4.1.2", "Tekan I untuk pindah antar bingkai"),
    ("Tombol berbagi punya nama", "4.1.2", "Dengarkan saat Tab"),
    ("Hasil pencarian baru dibacakan otomatis", "4.1.3", "Kirim pencarian, jangan geser fokus"),
    ("Daftar arsip yang berubah dibacakan otomatis", "4.1.3", "Ganti filter atau urutan"),
    ("Pesan kesalahan formulir dibacakan otomatis", "4.1.3, 3.3.1", "Kirim formulir kosong, jangan geser fokus"),
    ("Pesan succes atau notifikasi dibacakan otomatis", "4.1.3", "Pemicu notifikasi"),
    ("Gambar gagal dimuat punya pesan", "1.1.1", "Matikan jaringan, muat ulang halaman"),
    ("Tambah isi lebih banyak dibacakan otomatis", "4.1.3", "Klik tombol muat lebih banyak"),
    ("Tabel punya judul kolom yang terbaca lebih dulu", "1.3.1", "Tekan T lalu gunakan Ctrl+Alt+panah"),
    ("Halaman menandai bahasa Indonesia", "3.1.1", "Lihat kode html, cari lang="),
    ("Bagian bahasa Inggris ditandai terpisah", "3.1.2", "Lihat kode html, cari lang=en"),
]

UJI_FORM = [
    ("Setiap isian punya label yang terhubung", "1.3.1, 3.3.2", "Lihat kode html, cari label for"),
    ("Nama yang dibacakan sama dengan tulisan yang dilihat", "2.5.3", "Bandingkan keduanya"),
    ("Isian wajib ditandai di layar dan di kode", "3.3.2", "Lihat tanda bintang dan atribut required"),
    ("Ada petunjuk format sebelum diisi", "3.3.2", "Baca petunjuknya"),
    ("Ada isian otomatis untuk nama, email, telepon", "1.3.5", "Lihat kode html, cari autocomplete"),
    ("Grup isian punya judul kelompok", "1.3.1", "Lihat kode html, cari fieldset dan legend"),
    ("Tombol kirim punya nama yang jelas", "4.1.2", "Dengarkan nama tombolnya"),
    ("Urutan fokus mengikuti urutan yang dilihat mata", "2.4.3", "Tekan Tab dari isian pertama"),
    ("Kirim formulir kosong: pesan muncul", "3.3.1", "Kirim tanpa mengisi apa pun"),
    ("Pesan menyebut isian yang salah", "3.3.1", "Baca teks pesannya"),
    ("Pesan kesalahan dibacakan screen reader", "4.1.3", "Jangan geser fokus setelah menekan kirim"),
    ("Fokus pindah ke isian yang salah pertama", "3.3.1", "Kirim formulir kosong, lihat fokus"),
    ("Kesalahan ditandai dengan ikon dan teks, bukan cuma warna merah", "1.4.1", "Kirim dengan data salah"),
    ("Ada saran cara memperbaiki", "3.3.3", "Isi email dengan format salah"),
    ("Isi yang sudah diketik tidak hilang saat ada kesalahan", "3.3.1", "Isi sebagian, lalu kirim"),
    ("Ada captcha", "3.3.8", "Kirim formulir, lihat ada captcha atau tidak"),
    ("Captcha bisa diselesaikan tanpa menebak gambar", "3.3.8", "Coba kerjakan sendiri tanpa bantuan"),
    ("Halaman terima kasih ada dan dibaca screen reader", "4.1.3", "Kirim formulir yang valid"),
    ("Ada cara menghubungi yang bisa dipakai keyboard", "4.1.2", "Cek halaman kontak"),
    ("Alamat email jadi tautan", "4.1.2", "Klik atau tekan alamat emailnya"),
    ("Nomor telepon bisa dipanggil", "4.1.2", "Cek tautan teleponnya"),
    ("Ada cara melapor masalah aksesibilitas", "Best practice", "Cari di kaki halaman"),
    ("Lokasi cara melapor sama di semua halaman", "3.2.6", "Bandingkan 3 halaman berbeda"),
    ("Tautan pernyataan aksesibilitas ada di kaki halaman", "Best practice", "Lihat kaki halaman"),
]

UJI_MEDIA = [
    ("Ada tombol subtitle (CC) di video", "1.2.2", "Putar video, cari tombol CC"),
    ("Subtitle bisa dinyalakan", "1.2.2", "Klik tombol CC"),
    ("Bahasa subtitle Bahasa Indonesia", "1.2.2", "Buka pengaturan subtitle, lihat daftar bahasa"),
    ("Subtitle cocok dengan suara", "1.2.2", "Putar di detik 0, tengah, dan hampir akhir"),
    ("Subtitle menyebut hal penting yang terlihat di layar", "1.2.2", "Tonton sambil membaca subtitle"),
    ("Subtitle dari mesin ada tandanya dan ada teks lengkap", "1.2.2", "Lihat apakah ada catatan subtitle otomatis"),
    ("Ada jalur suara khusus (audio description)", "1.2.3, 1.2.5", "Lihat pengaturan video"),
    ("Kontrol pemutar bisa dipakai keyboard dan punya nama", "4.1.2", "Coba semua tombol pemutar pakai keyboard"),
    ("Video tidak berbunyi sendiri lebih dari 3 detik", "1.4.2", "Buka halaman, tunggu 10 detik"),
    ("Ada tautan ke halaman YouTube sebagai alternatif", "Best practice", "Lihat di bawah video"),
    ("Ada berkas audio di halaman ini", "1.2.1", "Lihat apakah ada pemutar audio"),
    ("Ada teks lengkap atau ringkasan di dekat pemutar audio", "1.2.1", "Baca teks di sekitar pemutar"),
]

UJI_PDF_INT = [
    ("PDF punya judul di informasinya", "2.4.2", "Acrobat: File > Properties"),
    ("Bahasa PDF ditandai Indonesia", "3.1.1", "Acrobat: File > Properties"),
    ("PDF bertanda (tagged)", "1.3.1", "Acrobat: Tools > Accessibility > Check PDF Accessibility"),
    ("Ada struktur tag di dalam PDF", "1.3.1", "Acrobat: panel Accessibility"),
    ("Judul di dalam PDF memakai tag heading dengan urutan benar", "1.3.1", "Acrobat: Edit > Preferences > Accessibility"),
    ("Urutan baca sama dengan urutan yang dilihat mata", "1.3.1", "Acrobat: Reading Order panel"),
    ("Gambar di dalam PDF punya keterangan", "1.1.1", "Acrobat: panel Accessibility"),
    ("Tabel di dalam PDF punya judul kolom yang ditandai", "1.3.1", "Acrobat: panel Accessibility"),
    ("Tautan di dalam PDF punya teks yang masuk akal", "2.4.4", "Klik tautan di Acrobat"),
    ("PDF bisa dibuka pakai keyboard", "2.1.1", "Buka PDF, pakai Tab saja"),
    ("Teks di PDF bisa disalin", "Best practice", "Blok teks dan salin"),
]

UJI_ZOOM = [
    ("Teks masih terbaca saat diperbesar 200 persen", "1.4.4", "Tekan Ctrl dan + dua kali di browser"),
    ("Tidak ada teks yang terpotong atau bertumpuk saat diperbesar", "1.4.4", "Periksa setelah zoom"),
    ("Tidak ada isi yang hilang saat diperbesar", "1.4.4", "Bandingkan dengan tampilan normal"),
    ("Tombol masih bisa dipakai setelah diperbesar", "1.4.4", "Coba klik tautan dan tombol"),
    ("Tombol ukuran teks milik situs bekerja", "1.4.4", "Klik tombol tambah ukuran teks"),
    ("Tidak ada gulir ke samping saat layar 320 piksel", "1.4.10", "DevTools: Ctrl+Shift+M, set lebar 320"),
    ("Isi jadi satu kolom di layar 320 piksel", "1.4.10", "Perhatikan bentuk halaman"),
    ("Semua tombol masih terjangkau di layar 320 piksel", "1.4.10", "Coba semua tombol"),
    ("Kotak fokus tetap terlihat di layar 320 piksel", "2.4.7", "Tekan Tab di tampilan kecil"),
    ("Tabel lebar tidak merusak halaman", "1.4.10", "Lihat tabel yang lebar"),
    ("Tampilan 400 persen tidak merusak halaman", "1.4.10", "Tekan Ctrl dan + beberapa kali"),
    ("Tidak ada isi yang hilang setelah jarak baris dan huruf diperbesar", "1.4.12", "Pasang gaya pengguna di browser"),
    ("Tidak ada teks yang bertumpuk setelah jarak baris diperbesar", "1.4.12", "Periksa setiap bagian"),
    ("Tombol dan isian masih bisa dipakai setelah jarak baris diperbesar", "1.4.12", "Coba semua tombol"),
    ("Warna teks utama cukup kontras", "1.4.3", "DevTools: ambil warnanya, tulis di kolom Catatan"),
    ("Warna tautan di dalam paragraf cukup kontras", "1.4.3, 1.4.1", "DevTools: ambil warnanya"),
    ("Warna tulisan di dalam tombol cukup kontras", "1.4.3", "DevTools: ambil warnanya"),
    ("Warna tanggal dan keterangan cukup kontras", "1.4.3", "DevTools: ambil warnanya"),
    ("Warna tulisan di kaki halaman cukup kontras", "1.4.3", "DevTools: ambil warnanya"),
    ("Kotak fokus punya kontras cukup", "1.4.11", "DevTools saat elemen difokuskan"),
    ("Garis isian formulir punya kontras cukup", "1.4.11", "DevTools"),
    ("Ikon tanpa tulisan punya kontras cukup", "1.4.11", "DevTools"),
    ("Kesalahan tidak ditandai hanya dengan warna merah", "1.4.1", "Kirim formulir dengan data salah"),
    ("Keterangan balloon bisa ditutup dengan Esc", "1.4.13", "Arahkan tetikus ke elemen"),
    ("Keterangan balloon tetap muncul saat tetikus ada di atasnya", "1.4.13", "Arahkan dan tunggu"),
    ("Gambar yang berpindah punya tombol jeda atau berhenti", "2.2.2", "Cari tombol jeda pada gambar slider"),
    ("Gambar yang berpindah tidak berjalan sendiri lebih dari 5 detik", "2.2.2", "Tunggu tanpa menekan apa pun"),
    ("Tidak ada cahaya berkedip cepat", "2.3.1", "Tonton video dan animasi"),
    ("Animasi hilang saat mode gerak dikurangi di sistem", "2.3.3", "Nyalakan Reduce Motion di sistem"),
]

META = [
    ("Kode jenis halaman (dari sheet 01-Koordinasi)", ""),
    ("Alamat halaman yang diuji", ""),
    ("Tanggal", ""),
    ("Penguji", ""),
    ("Perangkat dan browser", ""),
    ("Screen reader dan versi", ""),
]

BARIS_TEMUAN = ["Nomor Temuan", "Alamat Halaman", "Jenis Halaman", "Aturan WCAG",
                "Level", "Tingkat Kerugian", "Sumber", "Deskripsi Masalah",
                "Cara Mereproduksi", "Saran Perbaikan", "Kode Elemen",
                "Nomor Bukti", "Status"]
KOLOM_TEMUAN = [20, 45, 26, 16, 8, 18, 12, 60, 60, 55, 20, 40, 10, 12]

BARIS_BUKTI = ["Nama Berkas", "Nomor Temuan", "Jenis Bukti", "Keterangan",
               "Diperiksa Oleh", "Tanggal"]
KOLOM_BUKTI = [45, 20, 22, 60, 18, 14]

BARIS_BANDING = ["Yang Diperiksa", "NVDA (Windows)", "VoiceOver (macOS)",
                 "VoiceOver (iOS)", "TalkBack (Android)", "Catatan"]
KOLOM_BANDING = [40, 26, 26, 26, 26, 45]

BANDING = [
    ("Cara pindah antar judul", "Tekan H", "Rotor > Headings", "Rotor > Headings", "Menu > Headings", ""),
    ("Cara pindah antar tautan", "Tekan K", "Rotor > Links", "Rotor > Links", "Menu > Links", ""),
    ("Cara pindah ke isian formulir", "Tekan F", "Rotor > Form Controls", "Rotor > Forms", "Menu > Controls", ""),
    ("Cara pindah ke tabel", "Tekan T", "Rotor > Tables", "Rotor > Tables", "Menu > Tables", ""),
    ("Cara pindah ke gambar", "Tekan G", "Rotor > Images", "Rotor > Images", "Menu > Images", ""),
    ("Cara pindah antar bingkai", "Tekan I", "Rotor > Iframes", "Rotor > Iframes", "Menu > Iframes", ""),
    ("Cara melihat daftar bagian halaman", "NVDA+Insert+F7", "Rotor > Landmarks", "Rotor > Landmarks", "Menu > Landmarks", ""),
    ("Nama tombol tanpa nama yang jelas", "dibaca apa adanya", "dibaca apa adanya", "dibaca apa adanya", "dibaca apa adanya", ""),
    ("Pesan kesalahan dibacakan otomatis", "tidak / ya", "tidak / ya", "tidak / ya", "tidak / ya", ""),
    ("Galeri besar: fokus masuk ke dalam", "tidak / ya", "tidak / ya", "tidak / ya", "tidak / ya", ""),
    ("Galeri besar: bisa keluar dari galeri", "tidak / ya", "tidak / ya", "tidak / ya", "tidak / ya", ""),
    ("Judul tab browser dibacakan", "tidak / ya", "tidak / ya", "tidak / ya", "tidak / ya", ""),
]


def gaya_header(ws, baris, jumlah_kolom):
    for kolom in range(1, jumlah_kolom + 1):
        sel = ws.cell(row=baris, column=kolom)
        sel.font = FONT_HEADER
        sel.fill = PatternFill("solid", fgColor=WARN["Warna Header"])
        sel.alignment = WRAP_CENTER
        sel.border = BORDER


def gaya_sel(ws, baris_awal, baris_akhir, jumlah_kolom):
    for baris in ws.iter_rows(min_row=baris_awal, max_row=baris_akhir,
                              max_col=jumlah_kolom):
        for sel in baris:
            sel.font = FONT_NORMAL
            sel.alignment = WRAP_TOP
            sel.border = BORDER


def set_lebar(ws, lebar_kolom):
    for indeks, lebar in enumerate(lebar_kolom, start=1):
        ws.column_dimensions[get_column_letter(indeks)].width = lebar


def buat_judul(ws, judul, baris_terakhir):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=baris_terakhir)
    sel = ws.cell(row=1, column=1, value=judul)
    sel.font = FONT_TITLE
    sel.fill = PatternFill("solid", fgColor=WARN["Warna Header"])
    sel.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 28


def buat_panduan(wb):
    ws = wb.active
    ws.title = "00-Panduan"
    set_lebar(ws, [4, 40, 95])
    buat_judul(ws, "Panduan Uji Manual - inovasi.or.id", 3)

    ws["A3"] = 1
    ws["A3"].font = FONT_BOLD
    isi = [
        ("Untuk siapa berkas ini",
         "Untuk dua orang: satu Penguji (Tester) yang menguji, satu Koordinator yang hanya "
         "memeriksa hasil. Koordinator tidak perlu menguji."),
        ("Standar yang dipakai", "WCAG 2.2 Level AA."),
        ("Sudah dikerjakan sebelumnya",
         "Scan otomatis atas 738 halaman sudah selesai dan menghasilkan 28 temuan di "
         "findings/findings.csv. Berkas ini untuk pekerjaan yang tidak bisa dilakukan alat."),
        ("Cara memakai",
         "Buka sheet 01-Koordinator, pilih satu jenis halaman. Isi sheet 02 sampai 08 untuk "
         "jenis halaman itu. Semua temuan baru ditulis di sheet 09-Daftar-Temuan. "
         "Bukti disimpan di folder results/manual/evidence/ lalu didaftarkan di sheet 10."),
        ("Menyalin sheet",
         "Sheet 04 sampai 08 dipakai untuk satu jenis halaman saja. Untuk jenis halaman "
         "berikutnya, klik kanan nama sheet lalu pilih Duplicate (Salin), lalu ganti isinya."),
        ("Jangan mengulang temuan lama",
         "28 temuan sudah tercatat. Jangan membuat nomor baru untuk masalah yang sama. "
         "Cek dulu dengan perintah: git grep -n A11Y- findings/findings.csv"),
        ("Waktu per sesi", "Satu jenis halaman maksimal 90 menit. Lebih dari itu, istirahat 15 menit."),
        ("Syarat sebelum mulai",
         "NVDA dengan Speech Viewer menyala, Firefox atau Chrome terbaru, HP untuk cek tampilan "
         "kecil, perekam layar, dan tidak mengirim data ke server asli."),
    ]
    baris = 4
    for label, teks in isi:
        ws.cell(row=baris, column=2, value=label).font = FONT_BOLD
        ws.cell(row=baris, column=2).fill = PatternFill("solid", fgColor=WARN["Warna Sub"])
        ws.cell(row=baris, column=2).alignment = WRAP_TOP
        ws.cell(row=baris, column=2).border = BORDER
        sel = ws.cell(row=baris, column=3, value=teks)
        sel.alignment = WRAP_TOP
        sel.font = FONT_NORMAL
        sel.border = BORDER
        baris += 1

    baris += 1
    ws.cell(row=baris, column=2, value="Arti tanda pada kolom Hasil").font = FONT_BOLD
    baris += 1
    tanda = [
        ("L", "Lolos - tidak ada masalah."),
        ("G", "Gagal - ada masalah. Langsung tulis di sheet 09-Daftar-Temuan."),
        ("T", "Tidak berlaku - fitur ini memang tidak ada. Wajib tulis alasan di kolom Catatan."),
        ("?", "Belum diuji. Sesi belum selesai kalau masih ada tanda ini."),
    ]
    for kode, arti in tanda:
        ws.cell(row=baris, column=2, value=kode).font = FONT_BOLD
        ws.cell(row=baris, column=2).alignment = WRAP_CENTER
        ws.cell(row=baris, column=2).border = BORDER
        sel = ws.cell(row=baris, column=3, value=arti)
        sel.alignment = WRAP_TOP
        sel.border = BORDER
        baris += 1

    baris += 1
    ws.cell(row=baris, column=2, value="Tingkat kerugian").font = FONT_BOLD
    baris += 1
    for tingkat, arti in [
        ("Sangat serius", "Orang tidak bisa menjalankan tugasnya sama sekali."),
        ("Serius", "Bisa selesai, tapi sangat susah dan perlu bantuan luar."),
        ("Sedang", "Bisa selesai, tapi membingungkan dan makan waktu."),
        ("Kecil", "Tidak mengganggu, cuma tidak rapi."),
    ]:
        ws.cell(row=baris, column=2, value=tingkat).font = FONT_BOLD
        ws.cell(row=baris, column=2).border = BORDER
        sel = ws.cell(row=baris, column=3, value=arti)
        sel.alignment = WRAP_TOP
        sel.border = BORDER
        baris += 1

    baris += 1
    ws.cell(row=baris, column=2, value="Pemeriksaan Koordinator sebelum menerima").font = FONT_BOLD
    baris += 1
    for cek in [
        "Tidak ada baris kosong dan tidak ada tanda ? yang tertinggal.",
        "Setiap tanda G punya bukti di sheet 10-Daftar-Bukti.",
        "Cara mereproduksi bisa dijalankan orang lain tanpa bertanya.",
        "Setiap temuan menyebut elemen tertentu, bukan hanya \"tombol di bawah\".",
        "Sudah dicek tidak sudah ada di 28 temuan lama.",
        "Ada alasan tertulis kalau tingkatnya Sangat serius atau Serius.",
        "Saran perbaikannya jelas dan menyebut warna hex atau kode yang harus diubah.",
    ]:
        sel = ws.cell(row=baris, column=2, value="[ ] " + cek)
        sel.alignment = WRAP_TOP
        ws.merge_cells(start_row=baris, start_column=2, end_row=baris, end_column=3)
        baris += 1

    baris += 1
    ws.cell(row=baris, column=2, value="Daftar sheet").font = FONT_BOLD
    baris += 1
    gaya_header(ws, baris, 3)
    ws.cell(row=baris, column=1, value="No")
    ws.cell(row=baris, column=2, value="Nama Sheet")
    ws.cell(row=baris, column=3, value="Isi")
    baris += 1
    for nomor, (nama, isi_sheet) in enumerate(LEMBAR, start=1):
        ws.cell(row=baris, column=1, value=nomor).alignment = WRAP_CENTER
        ws.cell(row=baris, column=2, value=nama).font = FONT_BOLD
        ws.cell(row=baris, column=3, value=isi_sheet).alignment = WRAP_TOP
        gaya_sel(ws, baris, baris, 3)
        baris += 1
    ws.freeze_panes = "A4"


def buat_koordinasi(wb):
    ws = wb.create_sheet("01-Koordinasi")
    set_lebar(ws, KOLOM_KOORDINASI)
    buat_judul(ws, "Koordinasi Uji per Jenis Halaman", len(BARIS_KOORDINASI))
    ws["A2"] = ("Penguji mengisi kolom sampai Tanggal Selesai. Koordinator mengisi kolom "
                "Validator, Tanggal Validasi, dan Catatan Koordinator.")
    ws["A2"].font = Font(italic=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(BARIS_KOORDINASI))
    for kolom, judul in enumerate(BARIS_KOORDINASI, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    gaya_header(ws, 3, len(BARIS_KOORDINASI))

    baris = 4
    for nomor, nama, jumlah, alamat, catatan in JENIS_HALAMAN:
        ws.cell(row=baris, column=1, value=nomor)
        ws.cell(row=baris, column=2, value=nama)
        ws.cell(row=baris, column=3, value=jumlah)
        ws.cell(row=baris, column=4, value=alamat)
        ws.cell(row=baris, column=11, value=catatan)
        baris += 1
    akhir = baris - 1
    gaya_sel(ws, 4, akhir, len(BARIS_KOORDINASI))
    for kolom in (1, 3):
        for sel in ws[get_column_letter(kolom)][3:akhir]:
            sel.alignment = WRAP_CENTER

    daftar_status = DataValidation(
        type="list", formula1='"Belum,Sedang,Selesai,Ditolak"', allow_blank=True)
    ws.add_data_validation(daftar_status)
    daftar_status.add(f"F4:F{akhir}")

    ws.auto_filter.ref = f"A3:{get_column_letter(len(BARIS_KOORDINASI))}{akhir}"
    ws.freeze_panes = "C4"


def buat_rincian(wb):
    ws = wb.create_sheet("02-Rincian-Uji")
    set_lebar(ws, KOLOM_RINCIAN)
    buat_judul(ws, "Rincian Hasil Uji per Jenis Halaman", len(BARIS_RINCIAN))
    ws["A2"] = ("Satu baris untuk satu kelompok pemeriksaan pada satu jenis halaman. "
                "Isi kolom Hasil dengan L, G, T, atau ?.")
    ws["A2"].font = Font(italic=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(BARIS_RINCIAN))
    for kolom, judul in enumerate(BARIS_RINCIAN, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    gaya_header(ws, 3, len(BARIS_RINCIAN))

    baris = 4
    for nomor, nama, _jumlah, _alamat, _catatan in JENIS_HALAMAN:
        for indeks, (cakupan, lembar) in enumerate(CAKUPAN, start=1):
            ws.cell(row=baris, column=1, value=nama)
            ws.cell(row=baris, column=2, value=indeks)
            ws.cell(row=baris, column=3, value=cakupan)
            ws.cell(row=baris, column=4, value=lembar)
            ws.cell(row=baris, column=5, value=YANG_WAJIB[cakupan])
            baris += 1
    akhir = baris - 1
    gaya_sel(ws, 4, akhir, len(BARIS_RINCIAN))

    daftar = DataValidation(type="list", formula1=TANDA, allow_blank=True)
    ws.add_data_validation(daftar)
    daftar.add(f"F4:F{akhir}")

    merah = PatternFill("solid", fgColor="FFC7CE")
    hijau = PatternFill("solid", fgColor="C6EFCE")
    ws.conditional_formatting.add(
        f"F4:F{akhir}",
        CellIsRule(operator="equal", formula=['"G"'], fill=merah,
                   font=Font(color="9C0006", bold=True)))
    ws.conditional_formatting.add(
        f"F4:F{akhir}",
        CellIsRule(operator="equal", formula=['"L"'], fill=hijau,
                   font=Font(color="006100")))

    ws.auto_filter.ref = f"A3:{get_column_letter(len(BARIS_RINCIAN))}{akhir}"
    ws.freeze_panes = "C4"


def buat_kesimpulan(wb):
    ws = wb.create_sheet("03-Kesimpulan-Akhir")
    judul_baris = ["No", "Jenis Halaman", "Kesimpulan", "Jumlah Temuan Baru",
                   "Jumlah Temuan Lama yang Dikuatkan", "Yang Belum Bisa Diuji",
                   "Penguji", "Tanggal", "Koordinator", "Tanggal Validasi"]
    lebar = [5, 32, 24, 16, 22, 60, 16, 14, 16, 14]
    set_lebar(ws, lebar)
    buat_judul(ws, "Kesimpulan Akhir per Jenis Halaman", len(judul_baris))
    ws["A2"] = ("Gagal berarti ada orang yang tidak bisa keluar dari halaman dengan keyboard, "
                "kotak fokus sama sekali tidak terlihat, tampilan 320 px rusak total, atau "
                "formulir utama tidak bisa dipakai. Selain itu: Perlu Perbaikan.")
    ws["A2"].font = Font(italic=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(judul_baris))
    for kolom, judul in enumerate(judul_baris, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    gaya_header(ws, 3, len(judul_baris))

    baris = 4
    for nomor, nama, _jumlah, _alamat, _catatan in JENIS_HALAMAN:
        ws.cell(row=baris, column=1, value=nomor)
        ws.cell(row=baris, column=2, value=nama)
        baris += 1
    akhir = baris - 1
    gaya_sel(ws, 4, akhir, len(judul_baris))

    for kolom, isi in [(3, '"Lolos,Perlu Perbaikan,Gagal"'), (4, "0-99"), (5, "0-99")]:
        validasi = DataValidation(type="list" if kolom == 3 else "whole",
                                  operator="between", formula1=isi,
                                  allow_blank=True)
        ws.add_data_validation(validasi)
        huruf = get_column_letter(kolom)
        if kolom == 3:
            validasi.add(f"{huruf}4:{huruf}{akhir}")
        else:
            validasi.formula1 = 0
            validasi.formula2 = 99
            validasi.add(f"{huruf}4:{huruf}{akhir}")

    ws.conditional_formatting.add(
        f"C4:C{akhir}",
        CellIsRule(operator="equal", formula=['"Gagal"'],
                   fill=PatternFill("solid", fgColor="FFC7CE"),
                   font=Font(color="9C0006", bold=True)))
    ws.conditional_formatting.add(
        f"C4:C{akhir}",
        CellIsRule(operator="equal", formula=['"Lolos"'],
                   fill=PatternFill("solid", fgColor="C6EFCE"),
                   font=Font(color="006100")))
    ws.freeze_panes = "C4"


def buat_lembar_uji(wb, nama, judul, daftar, baris_awal_data=10):
    ws = wb.create_sheet(nama)
    set_lebar(ws, KOLOM_UJI)
    buat_judul(ws, judul, len(BARIS_UJI))
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(BARIS_UJI))
    sel = ws.cell(row=2, column=1,
                  value="Salin sheet ini untuk setiap jenis halaman yang diuji. "
                        "Isi kolom Hasil dengan L, G, T, atau ?.")
    sel.font = Font(italic=True)
    baris = 3
    for label, nilai in META:
        ws.cell(row=baris, column=1, value=label).font = FONT_BOLD
        ws.cell(row=baris, column=1).fill = PatternFill("solid", fgColor=WARN["Warna Sub"])
        ws.cell(row=baris, column=1).alignment = WRAP_TOP
        ws.cell(row=baris, column=1).border = BORDER
        sel = ws.cell(row=baris, column=2, value=nilai)
        sel.border = BORDER
        sel.alignment = WRAP_TOP
        ws.merge_cells(start_row=baris, start_column=2, end_row=baris, end_column=3)
        baris += 1

    baris_header = baris_awal_data - 1
    for kolom, judul_kolom in enumerate(BARIS_UJI, start=1):
        ws.cell(row=baris_header, column=kolom, value=judul_kolom)
    gaya_header(ws, baris_header, len(BARIS_UJI))

    baris = baris_awal_data
    for nomor, (yang, sc, cara) in enumerate(daftar, start=1):
        ws.cell(row=baris, column=1, value=nomor)
        ws.cell(row=baris, column=2, value=yang)
        ws.cell(row=baris, column=3, value=sc)
        ws.cell(row=baris, column=4, value=cara)
        baris += 1
    akhir = baris - 1
    gaya_sel(ws, baris_awal_data, akhir, len(BARIS_UJI))
    for sel in ws[f"A{baris_awal_data}:A{akhir}"]:
        sel[0].alignment = WRAP_CENTER
    for sel in ws[f"C{baris_awal_data}:C{akhir}"]:
        sel[0].alignment = WRAP_CENTER

    daftar_tanda = DataValidation(type="list", formula1=TANDA, allow_blank=True)
    ws.add_data_validation(daftar_tanda)
    daftar_tanda.add(f"E{baris_awal_data}:E{akhir}")
    ws.conditional_formatting.add(
        f"E{baris_awal_data}:E{akhir}",
        CellIsRule(operator="equal", formula=['"G"'],
                   fill=PatternFill("solid", fgColor="FFC7CE"),
                   font=Font(color="9C0006", bold=True)))
    ws.conditional_formatting.add(
        f"E{baris_awal_data}:E{akhir}",
        CellIsRule(operator="equal", formula=['"L"'],
                   fill=PatternFill("solid", fgColor="C6EFCE"),
                   font=Font(color="006100")))
    ws.freeze_panes = f"B{baris_awal_data}"
    return ws


def buat_media(wb):
    ws = buat_lembar_uji(wb, "07-Media-PDF", "Uji Video, Audio, dan Dokumen PDF", UJI_MEDIA,
                        baris_awal_data=10)
    baris = 10 + len(UJI_MEDIA) + 2
    ws.merge_cells(start_row=baris, start_column=1, end_row=baris,
                   end_column=len(BARIS_UJI))
    sel = ws.cell(row=baris, column=1, value="Dokumen PDF - salin dari inventory/pdfs.csv")
    sel.font = FONT_BOLD
    sel.fill = PatternFill("solid", fgColor=WARN["Warna Sub"])
    baris += 1
    for kolom, judul in enumerate(BARIS_UJI, start=1):
        ws.cell(row=baris, column=kolom, value=judul)
    gaya_header(ws, baris, len(BARIS_UJI))
    baris += 1
    awal_pdf = baris
    for nomor, (yang, sc, cara) in enumerate(UJI_PDF_INT, start=1):
        ws.cell(row=baris, column=1, value=nomor)
        ws.cell(row=baris, column=2, value=yang)
        ws.cell(row=baris, column=3, value=sc)
        ws.cell(row=baris, column=4, value=cara)
        baris += 1
    akhir = baris - 1
    gaya_sel(ws, awal_pdf, akhir, len(BARIS_UJI))

    validasi = DataValidation(type="list", formula1=TANDA, allow_blank=True)
    ws.add_data_validation(validasi)
    validasi.add(f"E{awal_pdf}:E{akhir}")
    ws.conditional_formatting.add(
        f"E{awal_pdf}:E{akhir}",
        CellIsRule(operator="equal", formula=['"G"'],
                   fill=PatternFill("solid", fgColor="FFC7CE"),
                   font=Font(color="9C0006", bold=True)))

    baris = akhir + 2
    ws.merge_cells(start_row=baris, start_column=1, end_row=baris, end_column=len(BARIS_UJI))
    sel = ws.cell(row=baris, column=1, value="Catatan untuk Pemeriksa")
    sel.font = FONT_BOLD
    sel.fill = PatternFill("solid", fgColor=WARN["Warna Catatan"])
    baris += 1
    catatan = [
        "Temuan lama yang sudah tercatat: A11Y-019 (65 PDF gagal dibuka), A11Y-020 "
        "(7 PDF tidak punya teks), A11Y-021 (43 PDF tidak bertanda), A11Y-022 (43 PDF "
        "tanpa bahasa), A11Y-023 (71 PDF tanpa judul), A11Y-025 sampai A11Y-028 (video "
        "dan subtitle). Jangan buat nomor baru untuk masalah yang sama.",
        "Yang baru dan perlu dicek di sini: subtitle ada tapi tidak cocok dengan suara, "
        "subtitle tidak menyebut hal penting yang terlihat di layar, urutan baca di dalam "
        "PDF salah, dan pemutar video tidak bisa dipakai keyboard.",
        "Cukup 10 PDF untuk pengujian. Pilih dari 5 jenis halaman berbeda.",
        "Kalau sebagian besar PDF gagal dengan pola yang sama, buat satu temuan saja "
        "dan lampirkan daftar alamatnya.",
    ]
    for teks in catatan:
        ws.merge_cells(start_row=baris, start_column=1, end_row=baris, end_column=len(BARIS_UJI))
        sel = ws.cell(row=baris, column=1, value=teks)
        sel.alignment = WRAP_TOP
        sel.border = BORDER
        baris += 1


def buat_temuan(wb):
    ws = wb.create_sheet("09-Daftar-Temuan")
    set_lebar(ws, KOLOM_TEMUAN)
    buat_judul(ws, "Daftar Semua Temuan Uji Manual", len(BARIS_TEMUAN))
    ws["A2"] = ("Nomor temuan manual memakai pola MAN-YYYYMMDD-NNN, contoh MAN-20261015-001. "
                "Isi kolom Sumber dengan kata manual. Koordinator menyalin baris ini ke "
                "findings/findings.csv setelah diperiksa.")
    ws["A2"].font = Font(italic=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(BARIS_TEMUAN))
    for kolom, judul in enumerate(BARIS_TEMUAN, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    gaya_header(ws, 3, len(BARIS_TEMUAN))

    akhir = 3 + 80
    gaya_sel(ws, 4, akhir, len(BARIS_TEMUAN))
    pilihan = {
        "F": '"Sangat serius,Serius,Sedang,Kecil"',
        "G": '"manual,axe,layout-check,pdf-check"',
        "N": '"Open,In Progress,Closed"',
    }
    for kolom, isi in pilihan.items():
        validasi = DataValidation(type="list", formula1=isi, allow_blank=True)
        ws.add_data_validation(validasi)
        validasi.add(f"{kolom}4:{kolom}{akhir}")

    ws.conditional_formatting.add(
        f"F4:F{akhir}",
        CellIsRule(operator="equal", formula=['"Sangat serius"'],
                   fill=PatternFill("solid", fgColor="FFC7CE"),
                   font=Font(color="9C0006", bold=True)))
    ws.conditional_formatting.add(
        f"F4:F{akhir}",
        CellIsRule(operator="equal", formula=['"Serius"'],
                   fill=PatternFill("solid", fgColor="FFD9CC"),
                   font=Font(color="974706")))
    ws.auto_filter.ref = f"A3:{get_column_letter(len(BARIS_TEMUAN))}{akhir}"
    ws.freeze_panes = "C4"


def buat_bukti(wb):
    ws = wb.create_sheet("10-Daftar-Bukti")
    set_lebar(ws, KOLOM_BUKTI)
    buat_judul(ws, "Daftar Berkas Bukti", len(BARIS_BUKTI))
    ws["A2"] = ("Simpan berkas di folder results/manual/evidence/. Bukti untuk kotak fokus "
                "harus berupa video, bukan tangkapan layar.")
    ws["A2"].font = Font(italic=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(BARIS_BUKTI))
    for kolom, judul in enumerate(BARIS_BUKTI, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    gaya_header(ws, 3, len(BARIS_BUKTI))
    akhir = 3 + 60
    gaya_sel(ws, 4, akhir, len(BARIS_BUKTI))
    validasi = DataValidation(
        type="list",
        formula1='"Video 60 detik,Salin teks Speech Viewer,Tangkapan layar,Daftar warna dan rasio,Kode HTML"',
        allow_blank=True)
    ws.add_data_validation(validasi)
    validasi.add(f"C4:C{akhir}")
    ws.freeze_panes = "A4"


def buat_banding(wb):
    ws = wb.create_sheet("11-Banding-SR")
    set_lebar(ws, KOLOM_BANDING)
    buat_judul(ws, "Perbandingan Hasil Baca di Empat Screen Reader", len(BARIS_BANDING))
    ws["A2"] = ("Isi kolom tengah dengan \"ya\" atau \"tidak\" sesuai pengamatan. "
                "Kalau berbeda antar screen reader, tulis detailnya di kolom Catatan.")
    ws["A2"].font = Font(italic=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(BARIS_BANDING))
    for kolom, judul in enumerate(BARIS_BANDING, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    gaya_header(ws, 3, len(BARIS_BANDING))
    baris = 4
    for item in BANDING:
        for kolom, nilai in enumerate(item, start=1):
            ws.cell(row=baris, column=kolom, value=nilai)
        baris += 1
    akhir = baris - 1
    gaya_sel(ws, 4, akhir, len(BARIS_BANDING))
    for kolom in range(2, 6):
        validasi = DataValidation(type="list", formula1='"ya,tidak,berbeda"',
                                  allow_blank=True)
        ws.add_data_validation(validasi)
        huruf = get_column_letter(kolom)
        validasi.add(f"{huruf}4:{huruf}{akhir}")
    ws.freeze_panes = "B4"


def main():
    wb = Workbook()
    buat_panduan(wb)
    buat_koordinasi(wb)
    buat_rincian(wb)
    buat_kesimpulan(wb)
    buat_lembar_uji(wb, "04-Keyboard-Fokus", "Uji Keyboard dan Kotak Fokus", UJI_KEYBOARD)
    buat_lembar_uji(wb, "05-ScreenReader", "Uji Screen Reader (NVDA, VoiceOver, TalkBack)",
                    UJI_SCREENREADER)
    buat_lembar_uji(wb, "06-Form-Error", "Uji Formulir dan Pesan Kesalahan", UJI_FORM)
    buat_media(wb)
    buat_lembar_uji(wb, "08-Zoom-Kontras",
                    "Uji Zoom, Tampilan Layar Kecil, Warna, dan Gerakan", UJI_ZOOM)
    buat_temuan(wb)
    buat_bukti(wb)
    buat_banding(wb)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT)
    print(f"Tersimpan: {OUTPUT}")
    print(f"Jumlah sheet: {len(wb.sheetnames)}")
    for nama in wb.sheetnames:
        print(f"  - {nama}")


if __name__ == "__main__":
    main()
