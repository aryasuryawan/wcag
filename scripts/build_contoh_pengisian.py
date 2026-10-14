"""Buat contoh pengisian kartu kerja versi sederhana.

Contoh ini terpisah dari ``kertas-kerja-sederhana.xlsx`` supaya berkas kerja
tetap kosong dan tidak tercemar data contoh.

Jalankan:

    python scripts/build_contoh_pengisian.py
"""

import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_kertas_kerja_sederhana as sederhana  # noqa: E402

OUTPUT = (sederhana.PROJECT_ROOT / "testing" / "kertas-kerja"
          / "contoh-pengisian.xlsx")

CONTOH_DAFTAR = {
    1: ("Selesai", "Andi", "2026-10-15", "Budi", "2026-10-16",
        "Diterima. Bukti kotak fokus ada."),
    2: ("Selesai", "Andi", "2026-10-15", "Budi", "2026-10-16",
        "Diterima."),
    10: ("Selesai", "Andi", "2026-10-15", "", "",
         "Menunggu pemeriksaan Koordinator."),
}

CONTOH_TANDA = {
    1: {1: "L", 2: "L", 3: "L", 4: "L", 5: "L", 6: "G", 7: "L", 8: "L",
        9: "L", 10: "G", 11: "L", 12: "L", 13: "T", 14: "L", 15: "L",
        16: "G", 17: "L", 18: "T", 19: "T", 20: "L", 21: "L", 22: "T"},
    2: {1: "L", 2: "L", 3: "L", 4: "L", 5: "L", 6: "L", 7: "L", 8: "L",
        9: "L", 10: "L", 11: "L", 12: "T", 13: "T", 14: "L", 15: "L",
        16: "L", 17: "L", 18: "T", 19: "T", 20: "L", 21: "G", 22: "T"},
    10: {1: "L", 2: "L", 3: "L", 4: "L", 5: "L", 6: "L", 7: "L", 8: "L",
         9: "L", 10: "L", 11: "G", 12: "G", 13: "G", 14: "L", 15: "L",
         16: "L", 17: "L", 18: "T", 19: "T", 20: "L", 21: "L", 22: "L"},
}

CONTOH_TEMUAN = [
    (1, 1, 6, "Ada dua bagian header yang aktif bersamaan, jadi NVDA "
              "membaca jumper banner dua kali",
     "1.3.1", "Serius",
     "Buka beranda di Firefox dengan NVDA menyala, tekan NVDA+Insert+F7, "
     "pilih bagian Landmarks, lalu hitung jumlah banner.",
     "Sembunyikan header HP dengan display:none saat header desktop aktif, "
     "dan sebaliknya.",
     "ev-halaman01-banner.txt", "Ya"),
    (1, 2, 10, "Logo utama dibungkus tautan tanpa nama yang terbaca, "
               "jadi NVDA melewati tautan itu",
     "4.1.2", "Serius",
     "Buka beranda, tekan K untuk pindah ke tautan pertama, "
     "dengarkan nama tautannya.",
     "Tambahkan alt=\"INOVASI\" pada gambar logo, atau teks layar "
     "penyembunyi di dalam tautan.",
     "ev-halaman01-logo.txt", "Ya"),
    (2, 3, 13, "Pesan kesalahan formulir kontak tidak dibacakan otomatis "
               "setelah tombol kirim ditekan",
     "4.1.3", "Serius",
     "Buka halaman kontak, tekan kirim tanpa mengisi apa pun, "
     "jangan geser fokus, dengarkan apakah ada suara.",
     "Tambahkan aria-live=\"assertive\" pada wadah pesan kesalahan.",
     "ev-halaman10-error.txt", "Belum"),
    (2, 4, 12, "Isian surel dan pesan belum punya label yang terhubung",
     "1.3.1", "Serius",
     "Buka halaman kontak, klik kolom pesan, lihat apakah ada tulisan label "
     "yang menempel saat diklik.",
     "Tambahkan <label for=\"pesan\"> pada setiap isian, bukan hanya "
     "tulisan di atasnya.",
     "ev-halaman10-label.txt", "Belum"),
]

KETERANGAN = [
    ("Di sheet mana contoh ini?",
     "Semua contoh ada di berkas ini (contoh-pengisian.xlsx). "
     "Berkas kerja sungguhan tetap kosong."),
    ("Contoh tanda di sheet uji",
     "Kolom Alat yang dipakai menjelaskan alat untuk setiap baris. "
     "Kolom paling kiri adalah nomor pemeriksaan dari daftar 22 pemeriksaan. "
     "L berarti Lolos, G berarti Gagal, T berarti Tidak berlaku."),
    ("Alat yang paling sering dipakai",
     "Keyboard dan NVDA. DevTools hanya dipakai untuk melihat kode dan nama tombol. "
     "Perekam layar dipakai sebagai bukti."),
    ("Contoh tanda G",
     "Tanda G selalu harus punya baris di sheet Daftar Temuan. "
     "Kolom Halaman diisi nomor halaman dari sheet Daftar Halaman."),
    ("Contoh tanda T",
     "T dipakai kalau fiturnya memang tidak ada di halaman itu. "
     "Contohnya halaman tanpa formulir tidak punya baris pesan kesalahan."),
    ("Nomor halaman",
     "Buka sheet Daftar Halaman, kolom No. Halaman beranda bernomor 1."),
    ("Tingkat kerugian",
     "Serius berarti orang bisa menyelesaikan tugasnya tapi sangat susah. "
     "Bukan Sangat serius, karena halamannya masih bisa dipakai."),
    ("Cara mengecek",
     "Tulis langkah yang bisa diulang orang lain tanpa perlu bertanya. "
     "Sebutkan kombinasi tombol dan apa yang didengar."),
    ("Nama berkas bukti",
     "Bukti disimpan di folder results/manual/evidence/ dengan nama yang "
     "sama seperti ditulis di kolom ini."),
    ("Kolom Sudah Diperiksa",
     "Diisi Koordinator. Ya berarti sudah diperiksa dan setuju, "
     "Belum berarti masih menunggu."),
    ("Contoh isi sheet Rekap",
     "Jumlah Gagal dan Jumlah Diuji dihitung otomatis dari tanda di sheet uji."),
]


def buat_keterangan(wb):
    ws = wb.active
    ws.title = "00-Cara-Baca-Contoh"
    sederhana.set_lebar(ws, [4, 30, 92])
    sederhana.buat_judul(ws, "Cara Membaca Contoh Pengisian", 3)
    baris = 3
    for label, teks in KETERANGAN:
        sel = ws.cell(row=baris, column=2, value=label)
        sel.font = sederhana.FONT_BOLD
        sel.fill = PatternFill("solid", fgColor=sederhana.HILAU)
        sel.alignment = sederhana.ATAS
        sel.border = sederhana.GARIS
        sel = ws.cell(row=baris, column=3, value=teks)
        sel.alignment = sederhana.ATAS
        sel.border = sederhana.GARIS
        baris += 1


def isi_daftar_halaman(wb, halaman):
    ws = wb.create_sheet("01-Daftar-Halaman")
    sederhana.set_lebar(ws, sederhana.LEBAR_DAFTAR)
    sederhana.buat_judul(ws, "Contoh Pengisian Daftar Halaman (hanya 3 baris)", 11)
    for kolom, judul in enumerate(sederhana.KOLOM_DAFTAR, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    sederhana.style_header(ws, 3, 11)
    baris = 4
    for item in halaman:
        isi = CONTOH_DAFTAR.get(item["no"])
        ws.cell(row=baris, column=1, value=item["no"])
        ws.cell(row=baris, column=2, value=item["nama"])
        ws.cell(row=baris, column=3, value=item["jenis"])
        ws.cell(row=baris, column=4, value=item["alamat"])
        if isi:
            for urutan, nilai in enumerate(isi, start=6):
                ws.cell(row=baris, column=urutan, value=nilai)
        else:
            ws.cell(row=baris, column=6, value="Belum")
        baris += 1
    akhir = baris - 1
    sederhana.style_isian(ws, 4, akhir, 11)
    status = sederhana.DataValidation(
        type="list", formula1='"Belum,Sedang,Selesai,Ditolak"', allow_blank=True)
    ws.add_data_validation(status)
    status.add(f"F4:F{akhir}")
    ws.freeze_panes = "B4"


def isi_sheet_uji(wb):
    halaman_terisi = sorted(CONTOH_TANDA)
    ws = wb.create_sheet("02-Uji-Contoh")
    sederhana.set_lebar(ws, [5, 38, 42, 11, 11, 11])
    sederhana.buat_judul(ws, "Contoh Pengisian Sheet Uji", 6)
    ws.cell(row=2, column=2, value="Yang diperiksa").font = sederhana.FONT_BOLD
    ws.cell(row=2, column=3, value="Alat yang dipakai").font = sederhana.FONT_BOLD
    for urutan, nomor in enumerate(halaman_terisi, start=4):
        sel = ws.cell(row=2, column=urutan, value=f"Halaman {nomor}")
        sel.font = sederhana.FONT_BOLD
        sel.alignment = sederhana.TENGAH
        sel.fill = PatternFill("solid", fgColor=sederhana.HILAU)
        sel.border = sederhana.GARIS
    sederhana.style_header(ws, 3, 6)
    ws.cell(row=3, column=1, value="No")
    ws.cell(row=3, column=2, value="Yang diperiksa")
    ws.cell(row=3, column=3, value="Alat yang dipakai")
    baris = 4
    for nomor, teks in enumerate(sederhana.CEK, start=1):
        ws.cell(row=baris, column=1, value=nomor)
        ws.cell(row=baris, column=2, value=teks)
        ws.cell(row=baris, column=3, value=sederhana.ALAT[nomor - 1])
        for urutan, nomor_halaman in enumerate(halaman_terisi, start=4):
            ws.cell(row=baris, column=urutan,
                    value=CONTOH_TANDA[nomor_halaman].get(nomor, ""))
        baris += 1
    akhir = baris - 1
    sederhana.style_isian(ws, 4, akhir, 6)
    for baris_sel in ws.iter_rows(min_row=4, max_row=akhir, min_col=4, max_col=6):
        for sel in baris_sel:
            nilai = sel.value
            if nilai == "G":
                sel.fill = PatternFill("solid", fgColor=sederhana.MERAH)
                sel.font = Font(color="9C0006", bold=True)
            elif nilai == "L":
                sel.fill = PatternFill("solid", fgColor=sederhana.HIJAU)
                sel.font = Font(color="006100")
            elif nilai == "T":
                sel.fill = PatternFill("solid", fgColor=sederhana.KUNING)
            sel.alignment = sederhana.TENGAH
    baris = akhir + 2
    ws.cell(row=baris, column=2, value="Jumlah gagal").font = sederhana.FONT_BOLD
    baris += 1
    ws.cell(row=baris, column=2,
            value="Jumlah sudah diuji").font = sederhana.FONT_BOLD
    for urutan in range(4, 4 + len(halaman_terisi)):
        huruf = get_column_letter(urutan)
        ws.cell(row=baris - 1, column=urutan,
                value=f'=COUNTIF({huruf}4:{huruf}{akhir},"G")')
        ws.cell(row=baris, column=urutan,
                value=f'=COUNTIF({huruf}4:{huruf}{akhir},"L")'
                      f'+COUNTIF({huruf}4:{huruf}{akhir},"G")')
    ws.freeze_panes = "D4"


def isi_daftar_temuan(wb):
    ws = wb.create_sheet("03-Daftar-Temuan")
    sederhana.set_lebar(ws, sederhana.LEBAR_TEMUAN)
    sederhana.buat_judul(ws, "Contoh Pengisian Daftar Temuan", 10)
    for kolom, judul in enumerate(sederhana.KOLOM_TEMUAN, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    sederhana.style_header(ws, 3, 10)
    baris = 4
    for nomor_temuan, item in enumerate(CONTOH_TEMUAN, start=1):
        (kode, halaman, nomor_cek, yang_salah, aturan, tingkat,
         cara, saran, bukti, dicek) = item
        nilai_baris = [nomor_temuan, halaman, nomor_cek, yang_salah, aturan,
                       tingkat, cara, saran, bukti, dicek]
        for kolom, nilai in enumerate(nilai_baris, start=1):
            ws.cell(row=baris, column=kolom, value=nilai)
        baris += 1
    sederhana.style_isian(ws, 4, baris - 1, 10)
    tingkat = sederhana.DataValidation(
        type="list", formula1='"Sangat serius,Serius,Sedang,Kecil"',
        allow_blank=True)
    ws.add_data_validation(tingkat)
    tingkat.add(f"F4:F{baris - 1}")
    ws.freeze_panes = "D4"


def isi_rekap(wb):
    ws = wb.create_sheet("04-Rekap")
    sederhana.set_lebar(ws, sederhana.LEBAR_REKAP)
    sederhana.buat_judul(ws, "Contoh Isi Rekap", 9)
    for kolom, judul in enumerate(sederhana.KOLOM_REKAP, start=1):
        ws.cell(row=3, column=kolom, value=judul)
    sederhana.style_header(ws, 3, 9)
    isi = [
        (1, "beranda", "Beranda", 3, 12, "Selesai", "Andi", "Budi",
         "Tercatat 3 masalah baru"),
        (2, "en", "Beranda", 1, 13, "Selesai", "Andi", "Budi",
         "Tercatat 1 masalah baru"),
        (10, "kontak", "Halaman utama", 3, 13, "Selesai", "Andi", "",
         "Menunggu pemeriksaan Koordinator"),
    ]
    baris = 4
    for isi_baris in isi:
        for kolom, nilai in enumerate(isi_baris, start=1):
            ws.cell(row=baris, column=kolom, value=nilai)
        baris += 1
    sederhana.style_isian(ws, 4, baris - 1, 9)
    for baris_sel in ws.iter_rows(min_row=4, max_row=baris - 1, min_col=4, max_col=5):
        for sel in baris_sel:
            sel.alignment = sederhana.TENGAH
            sel.font = sederhana.FONT_BOLD
    ws.freeze_panes = "B4"


def main():
    halaman, _hilang = sederhana.susun_halaman()
    wb = Workbook()
    buat_keterangan(wb)
    isi_daftar_halaman(wb, halaman)
    isi_sheet_uji(wb)
    isi_daftar_temuan(wb)
    isi_rekap(wb)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT)
    print(f"Tersimpan: {OUTPUT}")
    print(f"Jumlah sheet: {len(wb.sheetnames)}")
    for nama in wb.sheetnames:
        print(f"  - {nama}")


if __name__ == "__main__":
    main()

