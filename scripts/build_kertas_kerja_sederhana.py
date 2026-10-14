"""Buat versi sederhana kertas kerja uji manual.

Berkas ini lebih ringan daripada ``kertas-kerja-manual.xlsx``. Isinya satu daftar
54 halaman utama, lalu dipakai untuk mengisi tanda L (Lolos), G (Gagal), atau
T (Tidak berlaku) pada setiap halaman.

Penguji mengisi. Koordinator hanya memeriksa daftar di sheet ``01-Daftar-Halaman``
dan ``07-Rekap``.

Jalankan:

    python scripts/build_kertas_kerja_sederhana.py
"""

import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INVENTORI = PROJECT_ROOT / "inventory" / "heuristics.csv"
OUTPUT = PROJECT_ROOT / "testing" / "kertas-kerja" / "kertas-kerja-sederhana.xlsx"

BIRU = "305496"
HILAU = "D9E1F2"
KUNING = "FFF2CC"
MERAH = "FFC7CE"
HIJAU = "C6EFCE"

FONT_JUDUL = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
FONT_HEADER = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
FONT_BOLD = Font(name="Calibri", size=11, bold=True)
FONT_Biasa = Font(name="Calibri", size=11)
TIPIS = Side(style="thin", color="BFBFBF")
GARIS = Border(left=TIPIS, right=TIPIS, top=TIPIS, bottom=TIPIS)
ATAS = Alignment(vertical="top", wrap_text=True)
TENGAH = Alignment(horizontal="center", vertical="center", wrap_text=True)

TANDA = '"L,G,T"'

CEK = [
    "Semua tombol bisa dipakai pakai keyboard saja",
    "Tidak terjebak di dalam galeri, menu, atau searching",
    "Urutan fokus masuk akal, mengikuti urutan yang dilihat mata",
    "Kotak fokus terlihat jelas saat memakai keyboard",
    "Ada tombol lompat langsung ke konten utama",
    "Hanya ada satu bagian header di halaman",
    "Ada tepat satu judul utama (h1)",
    "Urutan judul tidak melompat-lompat",
    "Semua tautan punya tulisan yang menjelaskan tujuan",
    "Logo utama terbaca oleh screen reader",
    "Semua tombol dan isian punya nama yang terbaca",
    "Semua isian formulir punya label yang terhubung",
    "Pesan kesalahan formulir dibacakan screen reader",
    "Warna teks utama cukup kontras dengan latar",
    "Teks masih terbaca saat halaman dizoom 200 persen",
    "Tidak ada gulir ke samping saat layar 320 piksel",
    "Gambar punya keterangan yang benar",
    "Video punya subtitle Bahasa Indonesia yang cocok dengan suara",
    "File PDF punya judul dan bahasa yang terisi",
    "Tidak ada dua gambar atau cahaya yang berkedip cepat",
    "Bahasa halaman ditandai dengan benar (id-ID)",
    "Ada cara melapor masalah aksesibilitas",
]

# Alat yang dipakai untuk tiap pemeriksaan (baris sepadan dengan daftar CEK)
ALAT = [
    "Keyboard saja (Tab, Shift+Tab, Enter, Spasi, Esc, tombol panah). Tetikus tidak dipakai.",
    "Keyboard saja + perekam layar (Windows: Win+Alt+R)",
    "Keyboard + DevTools: klik kanan elemen, pilih Inspect",
    "Perekam layar + DevTools tab Accessibility",
    "Keyboard saja. Tekan Tab sekali di awal halaman.",
    "NVDA: tekan NVDA+Insert+F7, pilih bagian Landmarks, hitung jumper banner",
    "DevTools: ketik document.querySelectorAll('h1').length di Console, "
    "atau NVDA tekan H",
    "NVDA: tekan H berulang, tulis urutan judul yang terdengar",
    "NVDA: tekan K, baca semua nama tautan tanpa melihat layar",
    "NVDA: tekan K, dengarkan tautan pertama",
    "DevTools tab Accessibility: klik Inspect, baca Computed Properties "
    "(Name, Role)",
    "DevTools: klik kanan isian, pilih Inspect, cari <label for=...>",
    "NVDA + Speech Viewer (NVDA+F5) untuk merekam apa yang diucapkan",
    "DevTools: klik kanan teks, Inspect > eyedropper. Catat 2 kode warna.",
    "Browser: tekan Ctrl lalu + dua kali",
    "DevTools: tekan Ctrl+Shift+M, set lebar 320 piksel",
    "DevTools Inspect + NVDA tekan G untuk pindah ke gambar",
    "Pemutar YouTube: klik tombol CC, putar di detik 0, tengah, dan hampir akhir",
    "Adobe Acrobat Reader: Tools > Accessibility > Check PDF Accessibility",
    "Pemutar video + Windows: Settings > Accessibility > Visual effects > "
    "Animation effects OFF",
    "DevTools: klik kanan html, Inspect, lihat atribut lang",
    "Cek kaki halaman. NVDA untuk memastikan tautannya terbaca.",
]

# (jenis halaman, potongan alamat untuk dicari di inventory/heuristics.csv)
DAFTAR_54 = [
    ("Beranda", "/"),
    ("Beranda", "/en/"),
    ("Halaman utama", "/about"),
    ("Halaman utama", "/our-approach"),
    ("Halaman utama", "/our-focus"),
    ("Halaman utama", "/our-partners"),
    ("Halaman utama", "/wilayah-kerja"),
    ("Halaman utama", "/profil-provinsi"),
    ("Halaman utama", "/peluang"),
    ("Halaman utama", "/kontak"),
    ("Halaman khusus", "/404"),
    ("Halaman khusus", "/no-access"),
    ("Halaman utama", "/pelaporan-kasus-kekerasan-terhadap-anak"),
    ("Halaman utama", "/career"),
    ("Halaman utama", "/procurement"),
    ("Kategori publikasi", "/publication-category/buku-cerita"),
    ("Kategori publikasi", "/publication-category/cerita-praktik-baik"),
    ("Kategori publikasi", "/publication-category/dokumen-program"),
    ("Kategori publikasi", "/publication-category/infographics"),
    ("Kategori publikasi", "/publication-category/kisah-inspiratif"),
    ("Kategori publikasi", "/publication-category/kumpulan-praktik-baik"),
    ("Kategori publikasi", "/publication-category/newsletters"),
    ("Kategori publikasi", "/publication-category/pengumuman"),
    ("Kategori publikasi", "/publication-category/perangkat-ajar"),
    ("Kategori publikasi", "/publication-category/risalah-kebijakan"),
    ("Detail publikasi", "/publication/32-buku-anak-non-fiksi-perubahan-iklim"),
    ("Detail publikasi", "/publication/abjad-bahasa-kodi-sebagai-inovasi"),
    ("Detail publikasi", "/publication/absensi-online-agar-guru-tahu-kehadiran-siswa"),
    ("Detail publikasi", "/publication/akselerasi-mutu-pendidikan-menuju-ntb"),
    ("Detail publikasi", "/en/publication/nuraga-the-teacher-a-story"),
    ("Detail publikasi", "/en/publication/nurturing-the-first-steps-of-reading"),
    ("Artikel unggulan", "/featured-article/belajar-jadi-lebih-mudah-kekuatan-bahasa"),
    ("Artikel unggulan", "/featured-article/mengatasi-tantangan-pembelajaran"),
    ("Artikel unggulan", "/featured-article/meningkatkan-kapasitas-gurufondasi"),
    ("Siaran pers", "/press-release/australia-dan-indonesia-perkuat-kemitraan"),
    ("Siaran pers", "/press-release/duta-besar-australia-kunjungi-maluku"),
    ("Siaran pers", "/press-release/wakil-bupati-sumba-barat-daya"),
    ("Galeri", "/gallery/curriculum-and-assessment"),
    ("Galeri", "/gallery/ekosistem-pembelajaran"),
    ("Galeri", "/gallery/kunjungan-stakeholder"),
    ("Wilayah kerja", "/where-we-work/ikn"),
    ("Wilayah kerja", "/where-we-work/jawa-barat"),
    ("Wilayah kerja", "/where-we-work/ntb"),
    ("Arsip wilayah kerja", "/where-we-works/cerita-praktik-baik"),
    ("Arsip wilayah kerja", "/where-we-works/nasional"),
    ("Arsip wilayah kerja", "/where-we-works/video"),
    ("Sumber daya", "/resources/for-children"),
    ("Sumber daya", "/resources/for-educators"),
    ("Sumber daya", "/resources/for-policy-makers"),
    ("Peluang", "/opportunity/invitation-to-tender-eo-for-education-reform"),
    ("Peluang", "/opportunity/request-for-grant-proposal-local-partnership"),
    ("Arsip peluang", "/opportunity-category/career"),
    ("Halaman khusus", "/video"),
    ("Halaman khusus", "/risalah-kebijakan"),
]

KOLOM_DAFTAR = ["No", "Nama Halaman", "Jenis", "Alamat Lengkap", "Penting",
                "Status Uji", "Penguji", "Tanggal Selesai", "Koordinator",
                "Tanggal Validasi", "Catatan Koordinator"]
LEBAR_DAFTAR = [5, 26, 20, 62, 9, 13, 16, 15, 16, 15, 42]

KOLOM_TEMUAN = ["No", "Halaman", "Pemeriksaan No", "Yang salah", "Aturan WCAG",
                "Tingkat", "Cara Mengecek", "Saran Perbaikan",
                "Nama Berkas Bukti", "Sudah Diperiksa"]
LEBAR_TEMUAN = [6, 11, 13, 52, 16, 15, 48, 48, 30, 13]

KOLOM_REKAP = ["No", "Nama Halaman", "Jenis", "Jumlah Gagal", "Jumlah Diuji",
               "Status", "Penguji", "Koordinator", "Catatan"]
LEBAR_REKAP = [5, 30, 20, 14, 14, 18, 16, 16, 45]

KOLOM_BANDING = ["Yang Diperiksa", "NVDA", "VoiceOver", "TalkBack", "Catatan"]
LEBAR_BANDING = [42, 18, 18, 18, 45]

JENIS_PENTING = {"Beranda", "Halaman utama", "Halaman khusus",
                 "Detail publikasi", "Kategori publikasi", "Galeri",
                 "Peluang", "Sumber daya"}


BASA = "https://www.inovasi.or.id"


def baca_url_tersedia():
    daftar = {}
    with open(INVENTORI, encoding="utf-8", newline="") as berkas:
        for baris in csv.DictReader(berkas):
            daftar[baris["url"].rstrip("/")] = baris["url"]
    for nama_berkas in ("urls.txt", "urls-all.txt", "urls-utama.txt"):
        jalur = INVENTORI.parent / nama_berkas
        if not jalur.exists():
            continue
        with open(jalur, encoding="utf-8") as berkas:
            for baris in berkas:
                alamat = baris.strip()
                if alamat.startswith("http"):
                    daftar.setdefault(alamat.rstrip("/"), alamat)
    return daftar


def cari_alamat(tersedia, potongan):
    ujung = potongan if potongan.startswith("/") else "/" + potongan
    if ujung.endswith("/") and len(ujung) > 1:
        ujung = ujung[:-1]
    if ujung == "/":
        cocok = [k for k in tersedia if k in (BASA, BASA + "/")]
    else:
        cocok = [k for k in tersedia
                 if k.startswith(BASA) and k[len(BASA):].startswith(ujung)]
    if not cocok:
        return None
    return tersedia[sorted(cocok, key=len)[0]]


def nama_pendek(alamat):
    jalan = alamat.rstrip("/")[len(BASA):]
    if not jalan or jalan == "":
        return "beranda (Indonesia)"
    if jalan == "/en":
        return "beranda (Inggris)"
    return jalan.rsplit("/", 1)[-1][:34]


def susun_halaman():
    tersedia = baca_url_tersedia()
    hasil = []
    hilang = []
    for nomor, (jenis, potongan) in enumerate(DAFTAR_54, start=1):
        alamat = cari_alamat(tersedia, potongan)
        if alamat is None:
            hilang.append(potongan)
            alamat = BASA + potongan
        nama = nama_pendek(alamat)
        hasil.append({
            "no": nomor,
            "jenis": jenis,
            "alamat": alamat,
            "nama": nama[:34],
        })
    return hasil, hilang


def style_header(ws, baris, jumlah):
    for kolom in range(1, jumlah + 1):
        sel = ws.cell(row=baris, column=kolom)
        sel.font = FONT_HEADER
        sel.fill = PatternFill("solid", fgColor=BIRU)
        sel.alignment = TENGAH
        sel.border = GARIS


def style_isian(ws, awal, akhir, jumlah):
    for baris in ws.iter_rows(min_row=awal, max_row=akhir, max_col=jumlah):
        for sel in baris:
            sel.font = FONT_Biasa
            sel.alignment = ATAS
            sel.border = GARIS


def set_lebar(ws, lebar):
    for indeks, nilai in enumerate(lebar, start=1):
        ws.column_dimensions[get_column_letter(indeks)].width = nilai


def buat_judul(ws, teks, jumlah_kolom):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=jumlah_kolom)
    sel = ws.cell(row=1, column=1, value=teks)
    sel.font = FONT_JUDUL
    sel.fill = PatternFill("solid", fgColor=BIRU)
    sel.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 26


def catat_tanda(ws, kolom, awal, akhir):
    validasi = DataValidation(type="list", formula1=TANDA, allow_blank=True)
    ws.add_data_validation(validasi)
    kolom_teks = get_column_letter(kolom)
    validasi.add(f"{kolom_teks}{awal}:{kolom_teks}{akhir}")
    ws.conditional_formatting.add(
        f"{kolom_teks}{awal}:{kolom_teks}{akhir}",
        CellIsRule(operator="equal", formula=['"G"'],
                   fill=PatternFill("solid", fgColor=MERAH),
                   font=Font(color="9C0006", bold=True)))
    ws.conditional_formatting.add(
        f"{kolom_teks}{awal}:{kolom_teks}{akhir}",
        CellIsRule(operator="equal", formula=['"L"'],
                   fill=PatternFill("solid", fgColor=HIJAU),
                   font=Font(color="006100")))


def buat_cara_pakai(wb):
    ws = wb.active
    ws.title = "00-Cara-Pakai"
    set_lebar(ws, [4, 34, 60, 60])
    buat_judul(ws, "Kartu Kerja Uji Manual (Versi Sederhana)", 3)

    blok = [
        ("Untuk siapa berkas ini",
         "Dua orang. Penguji (Tester) yang menguji. Koordinator hanya memeriksa, tidak menguji."),
        ("Isi berkas",
         "Daftar 54 halaman utama innovate.or.id, 22 pemeriksaan per halaman, daftar temuan, "
         "dan rekap jumlah kegagalan."),
        ("Cara memakai",
         "1. Buka sheet 01-Daftar-Halaman, cari halaman yang belum diuji.\n"
         "2. Buka sheet 02 sampai 05 sesuai nomor halaman itu.\n"
         "3. Isi tanda di kotak yang sesuai: L, G, atau T.\n"
         "4. Setiap tanda G dicatat lengkap di sheet 06-Daftar-Temuan.\n"
         "5. Koordinator mengisi kolom di sheet 01 dan reviewing di sheet 07-Rekap."),
        ("Arti tanda",
         "L = Lolos. G = Gagal. T = Tidak berlaku di halaman ini."),
        ("Warna kotak",
         "Hijau berarti Lolos. Merah berarti Gagal."),
        ("Perhatikan",
         "28 temuan dari pemindaian otomatis sudah tercatat. Jangan membuat nomor baru untuk "
         "masalah yang sama. Cek dulu dengan: git grep -n A11Y- findings/findings.csv"),
        ("Jangan mengirim data",
         "Jangan mengisi formulir dengan data sungguhan dan mengirimnya ke server asli."),
        ("Waktu",
         "Satu halaman maksimal 15 menit. Untuk 10 halaman, sekitar 2 jam 30 menit."),
        ("Bukti",
         "Simpan bukti di folder results/manual/evidence/. Untuk kotak fokus, pakai video "
         "60 detik, bukan tangkapan layar."),
        ("Aturan tingkat kerugian",
         "Sangat serius = orang tidak bisa menjalankan tugasnya sama sekali.\n"
         "Serius = bisa selesai tapi sangat susah.\n"
         "Sedang = bisa selesai tapi membingungkan.\n"
         "Kecil = cuma tidak rapi."),
        ("Pemeriksaan Koordinator",
         "Tidak ada kotak kosong. Setiap G punya bukti. Cara mengecek bisa diulang orang "
         "lain. Sudah dicek tidak sudah ada di 28 temuan lama. Saran perbaikan jelas."),
    ]
    baris = 3
    for label, teks in blok:
        sel = ws.cell(row=baris, column=2, value=label)
        sel.font = FONT_BOLD
        sel.fill = PatternFill("solid", fgColor=HILAU)
        sel.alignment = ATAS
        sel.border = GARIS
        sel = ws.cell(row=baris, column=3, value=teks)
        sel.alignment = ATAS
        sel.border = GARIS
        baris += 1

    baris += 1
    sel = ws.cell(row=baris, column=2, value="Pemeriksaan yang dipakai (22 buah)")
    sel.font = FONT_BOLD
    baris += 1
    ws.cell(row=baris, column=2, value="No").font = FONT_BOLD
    ws.cell(row=baris, column=3, value="Yang diperiksa").font = FONT_BOLD
    ws.cell(row=baris, column=4, value="Alat yang dipakai").font = FONT_BOLD
    baris += 1
    for nomor, teks in enumerate(CEK, start=1):
        ws.cell(row=baris, column=2, value=nomor).alignment = TENGAH
        ws.cell(row=baris, column=2).border = GARIS
        sel = ws.cell(row=baris, column=3, value=teks)
        sel.alignment = ATAS
        sel.border = GARIS
        sel = ws.cell(row=baris, column=4, value=ALAT[nomor - 1])
        sel.alignment = ATAS
        sel.border = GARIS
        baris += 1
    ws.freeze_panes = "A3"


def buat_daftar_halaman(wb, halaman):
    ws = wb.create_sheet("01-Daftar-Halaman")
    set_lebar(ws, LEBAR_DAFTAR)
    buat_judul(ws, "Daftar 54 Halaman Utama", len(KOLOM_DAFTAR))
    ws["A2"] = ("Penguji mengisi kolom Status Uji sampai Tanggal Selesai. "
                "Koordinator mengisi kolom Koordinator, Tanggal Validasi, dan Catatan.")
    ws["A2"].font = Font(italic=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(KOLOM_DAFTAR))
    for kolom, judul in enumerate(KOLOM_DAFTAR, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    style_header(ws, 3, len(KOLOM_DAFTAR))

    baris = 4
    for item in halaman:
        ws.cell(row=baris, column=1, value=item["no"])
        ws.cell(row=baris, column=2, value=item["nama"])
        ws.cell(row=baris, column=3, value=item["jenis"])
        ws.cell(row=baris, column=4, value=item["alamat"])
        ws.cell(row=baris, column=5,
                value="Penting" if item["jenis"] in JENIS_PENTING else "")
        baris += 1
    akhir = baris - 1
    style_isian(ws, 4, akhir, len(KOLOM_DAFTAR))
    for kolom in (1, 5):
        for sel in ws[get_column_letter(kolom)][3:akhir]:
            sel.alignment = TENGAH

    status = DataValidation(type="list",
                            formula1='"Belum,Sedang,Selesai,Ditolak"',
                            allow_blank=True)
    ws.add_data_validation(status)
    status.add(f"F4:F{akhir}")
    ws.auto_filter.ref = f"A3:{get_column_letter(len(KOLOM_DAFTAR))}{akhir}"
    ws.freeze_panes = "B4"


def buat_jaringan_uji(wb, halaman, mulai, selesai, urutan):
    ws = wb.create_sheet(f"{urutan:02d}-Uji-Halaman-{mulai:02d}-{selesai:02d}")
    lebar = [5, 34, 40] + [9] * (selesai - mulai + 1)
    set_lebar(ws, lebar)
    jumlah_kolom = 3 + (selesai - mulai + 1)
    buat_judul(ws, f"Halaman {mulai} sampai {selesai}", jumlah_kolom)

    ws.cell(row=2, column=2, value="Yang diperiksa").font = FONT_BOLD
    ws.cell(row=2, column=3, value="Alat yang dipakai").font = FONT_BOLD
    for indeks in range(mulai, selesai + 1):
        kolom = 3 + (indeks - mulai + 1)
        sel = ws.cell(row=2, column=kolom, value=indeks)
        sel.font = FONT_BOLD
        sel.alignment = TENGAH
        sel.fill = PatternFill("solid", fgColor=HILAU)
        sel.border = GARIS
    style_header(ws, 3, jumlah_kolom)
    ws.cell(row=3, column=1, value="No")
    ws.cell(row=3, column=2, value="Yang diperiksa")
    ws.cell(row=3, column=3, value="Alat yang dipakai")

    baris = 4
    for nomor, teks in enumerate(CEK, start=1):
        ws.cell(row=baris, column=1, value=nomor)
        ws.cell(row=baris, column=2, value=teks)
        ws.cell(row=baris, column=3, value=ALAT[nomor - 1])
        baris += 1
    akhir_cek = baris - 1
    style_isian(ws, 4, akhir_cek, jumlah_kolom)
    for indeks in range(mulai, selesai + 1):
        kolom = 3 + (indeks - mulai + 1)
        ws.cell(row=3, column=kolom, value=indeks)
        validasi = DataValidation(type="list", formula1=TANDA, allow_blank=True)
        ws.add_data_validation(validasi)
        huruf = get_column_letter(kolom)
        validasi.add(f"{huruf}4:{huruf}{akhir_cek}")
        ws.conditional_formatting.add(
            f"{huruf}4:{huruf}{akhir_cek}",
            CellIsRule(operator="equal", formula=['"G"'],
                       fill=PatternFill("solid", fgColor=MERAH),
                       font=Font(color="9C0006", bold=True)))
        ws.conditional_formatting.add(
            f"{huruf}4:{huruf}{akhir_cek}",
            CellIsRule(operator="equal", formula=['"L"'],
                       fill=PatternFill("solid", fgColor=HIJAU),
                       font=Font(color="006100")))

    baris = akhir_cek + 2
    ws.cell(row=baris, column=2, value="Jumlah gagal").font = FONT_BOLD
    baris += 1
    ws.cell(row=baris, column=2, value="Jumlah sudah diuji").font = FONT_BOLD
    for indeks in range(mulai, selesai + 1):
        kolom = 3 + (indeks - mulai + 1)
        huruf = get_column_letter(kolom)
        sel = ws.cell(row=baris - 1, column=kolom,
                      value=f'=COUNTIF({huruf}4:{huruf}{akhir_cek},"G")')
        sel.font = FONT_BOLD
        sel.alignment = TENGAH
        sel = ws.cell(row=baris, column=kolom,
                      value=f'=COUNTIF({huruf}4:{huruf}{akhir_cek},"L")'
                            f'+COUNTIF({huruf}4:{huruf}{akhir_cek},"G")')
        sel.alignment = TENGAH
    ws.freeze_panes = "D4"
    return ws.title


def buat_daftar_temuan(wb):
    ws = wb.create_sheet("06-Daftar-Temuan")
    set_lebar(ws, LEBAR_TEMUAN)
    buat_judul(ws, "Daftar Semua Temuan (Penguji isi, Koordinator periksa)", len(KOLOM_TEMUAN))
    ws["A2"] = ("Kolom Halaman diisi nomor halaman dari sheet 01-Daftar-Halaman. "
                "Satu baris satu masalah. Tinggalkan baris kosong yang tidak dipakai.")
    ws["A2"].font = Font(italic=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(KOLOM_TEMUAN))
    for kolom, judul in enumerate(KOLOM_TEMUAN, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    style_header(ws, 3, len(KOLOM_TEMUAN))

    akhir = 3 + 100
    style_isian(ws, 4, akhir, len(KOLOM_TEMUAN))

    tingkat = DataValidation(
        type="list", formula1='"Sangat serius,Serius,Sedang,Kecil"',
        allow_blank=True)
    ws.add_data_validation(tingkat)
    tingkat.add(f"E4:E{akhir}")
    ws.conditional_formatting.add(
        f"E4:E{akhir}",
        CellIsRule(operator="equal", formula=['"Sangat serius"'],
                   fill=PatternFill("solid", fgColor=MERAH),
                   font=Font(color="9C0006", bold=True)))
    ws.conditional_formatting.add(
        f"E4:E{akhir}",
        CellIsRule(operator="equal", formula=['"Serius"'],
                   fill=PatternFill("solid", fgColor=KUNING),
                   font=Font(color="974706")))

    diperiksa = DataValidation(type="list", formula1='"Ya,Belum"', allow_blank=True)
    ws.add_data_validation(diperiksa)
    diperiksa.add(f"I4:I{akhir}")
    ws.conditional_formatting.add(
        f"I4:I{akhir}",
        CellIsRule(operator="equal", formula=['"Ya"'],
                   fill=PatternFill("solid", fgColor=HIJAU),
                   font=Font(color="006100")))
    ws.freeze_panes = "C4"


def buat_rekap(wb, halaman, kelompok):
    ws = wb.create_sheet("07-Rekap")
    set_lebar(ws, LEBAR_REKAP)
    buat_judul(ws, "Rekap Jumlah Gagal per Halaman", len(KOLOM_REKAP))
    ws["A2"] = ("Jumlah Gagal dan Jumlah Diuji dihitung otomatis dari sheet 02 sampai 05. "
                "Koordinator hanya mengisi Status, nama, dan Catatan.")
    ws["A2"].font = Font(italic=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(KOLOM_REKAP))
    for kolom, judul in enumerate(KOLOM_REKAP, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    style_header(ws, 3, len(KOLOM_REKAP))

    baris = 4
    for item in halaman:
        ws.cell(row=baris, column=1, value=item["no"])
        ws.cell(row=baris, column=2, value=item["nama"])
        ws.cell(row=baris, column=3, value=item["jenis"])
        bagian_gagal = []
        bagian_uji = []
        for nama_sheet, mulai, selesai in kelompok:
            if not mulai <= item["no"] <= selesai:
                continue
            huruf = get_column_letter(4 + (item["no"] - mulai))
            bagian_gagal.append(f"'{nama_sheet}'!{huruf}26")
            bagian_uji.append(f"'{nama_sheet}'!{huruf}27")
        if bagian_gagal:
            ws.cell(row=baris, column=4, value="=" + "+".join(bagian_gagal))
            ws.cell(row=baris, column=5, value="=" + "+".join(bagian_uji))
        baris += 1
    akhir = baris - 1
    style_isian(ws, 4, akhir, len(KOLOM_REKAP))
    for baris_sel in ws[f"D4:E{akhir}"]:
        for sel in baris_sel:
            sel.alignment = TENGAH
            sel.font = FONT_BOLD

    status = DataValidation(
        type="list", formula1='"Belum,Selesai,Perlu perbaikan,Tidak diuji"',
        allow_blank=True)
    ws.add_data_validation(status)
    status.add(f"F4:F{akhir}")
    ws.conditional_formatting.add(
        f"D4:D{akhir}",
        CellIsRule(operator="greaterThan", formula=["0"],
                   fill=PatternFill("solid", fgColor=MERAH),
                   font=Font(color="9C0006", bold=True)))
    ws.auto_filter.ref = f"A3:{get_column_letter(len(KOLOM_REKAP))}{akhir}"
    ws.freeze_panes = "B4"


def buat_banding(wb):
    ws = wb.create_sheet("08-Banding-Tiga-SR")
    set_lebar(ws, LEBAR_BANDING)
    buat_judul(ws, "Perbandingan di Tiga Screen Reader", len(KOLOM_BANDING))
    ws["A2"] = "Isi dengan ya atau tidak. Tulis perbedaan di kolom Catatan."
    ws["A2"].font = Font(italic=True)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(KOLOM_BANDING))
    for kolom, judul in enumerate(KOLOM_BANDING, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    style_header(ws, 3, len(KOLOM_BANDING))

    isi = [
        "Cara pindah antar judul",
        "Cara pindah antar tautan",
        "Cara pindah ke isian formulir",
        "Cara pindah ke tabel",
        "Cara melihat daftar bagian halaman",
        "Nama tombol terbaca dengan benar",
        "Pesan kesalahan dibacakan otomatis",
        "Bisa masuk dan keluar dari galeri besar",
        "Judul tab browser dibacakan",
    ]
    baris = 4
    for teks in isi:
        ws.cell(row=baris, column=1, value=teks)
        baris += 1
    akhir = baris - 1
    style_isian(ws, 4, akhir, len(KOLOM_BANDING))
    for kolom in (2, 3, 4):
        validasi = DataValidation(type="list", formula1='"ya,tidak,berbeda"',
                                  allow_blank=True)
        ws.add_data_validation(validasi)
        huruf = get_column_letter(kolom)
        validasi.add(f"{huruf}4:{huruf}{akhir}")
    ws.freeze_panes = "B4"


def main():
    halaman, hilang = susun_halaman()
    wb = Workbook()
    buat_cara_pakai(wb)
    buat_daftar_halaman(wb, halaman)

    kelompok = []
    mulai = 1
    per_sheet = 14
    urutan = 2
    while mulai <= len(halaman):
        selesai = min(mulai + per_sheet - 1, len(halaman))
        nama_sheet = buat_jaringan_uji(wb, halaman, mulai, selesai, urutan)
        kelompok.append((nama_sheet, mulai, selesai))
        mulai = selesai + 1
        urutan += 1

    buat_daftar_temuan(wb)
    buat_rekap(wb, halaman, kelompok)
    buat_banding(wb)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT)
    print(f"Tersimpan: {OUTPUT}")
    print(f"Jumlah halaman: {len(halaman)}")
    print(f"Jumlah sheet: {len(wb.sheetnames)}")
    for nama in wb.sheetnames:
        print(f"  - {nama}")
    if hilang:
        print("Alamat tidak ada di inventory, memakai alamatdasar:")
        for potongan in hilang:
            print(f"  ! {potongan}")


if __name__ == "__main__":
    main()
