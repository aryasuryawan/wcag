# Cek Layout: Reflow, Zoom, Skip Link, Target Size

Dihasilkan: 2026-10-11T12:06:22  
URL diperiksa: 738 (dari 738 di file urls)

Metode: viewport 1280px (desktop), 320px (SC 1.4.10 Reflow), 640px (setara zoom 200% pada 1280px, SC 1.4.4). Headless Chrome, tanpa interaksi keyboard.

## Ringkasan

| Pemeriksaan | SC | URL gagal | Persentase |
|-------------|----|-----------|------------|
| Scroll horizontal di 320px | 1.4.10 | 0 | 0% |
| Scroll horizontal di 640px (zoom 200%) | 1.4.4 | 0 | 0% |
| Tidak ada skip link yang berfungsi | 2.4.1 | 0 | 0% |
| Ada target interaktif < 24x24 px | 2.5.8 | 507 | 69% |
| Ada tabindex positif | 2.4.3 | 0 | 0% |
| Scroll horizontal bahkan di 1280px | - | 0 | 0% |

## 10 URL terburuk untuk reflow 320px

| URL | scrollWidth @320 | Contoh elemen melebar |
|-----|------------------|------------------------|

## 10 URL dengan target terkecil

| URL | jumlah target < 24px | Contoh |
|-----|----------------------|--------|
| https://www.inovasi.or.id/pelaporan-kasus-kekerasan-terhadap-anak | 15 | `button.accessibility-scale-decrease(23.5x23.5); button.accessibility-scale-increase(23.5x23.5); button.accessibility-scale-decrease(23.5x23.5)` |
| https://www.inovasi.or.id/featured-article/tbm-untuk-anak-anak-kaltara-menyiapkan-generasi-hebat-dan-tangguh | 12 | `button.accessibility-scale-decrease(23.5x23.5); button.accessibility-scale-increase(23.5x23.5); button.accessibility-scale-decrease(23.5x23.5)` |
| https://www.inovasi.or.id/cerita-praktik-baik | 8 | `button.accessibility-scale-decrease(23.5x23.5); button.accessibility-scale-increase(23.5x23.5); button.accessibility-scale-decrease(23.5x23.5)` |
| https://www.inovasi.or.id/dokumen-program | 8 | `button.accessibility-scale-decrease(23.5x23.5); button.accessibility-scale-increase(23.5x23.5); button.accessibility-scale-decrease(23.5x23.5)` |
| https://www.inovasi.or.id/en/publication/nuraga-the-teacher-a-story-of-diversity-in-inclusive-education-copy1 | 8 | `button.accessibility-scale-decrease(23.5x23.5); button.accessibility-scale-increase(23.5x23.5); button.accessibility-scale-decrease(23.5x23.5)` |
| https://www.inovasi.or.id/en/publication/nurturing-the-first-steps-of-reading-in-cirebon | 8 | `button.accessibility-scale-decrease(23.5x23.5); button.accessibility-scale-increase(23.5x23.5); button.accessibility-scale-decrease(23.5x23.5)` |
| https://www.inovasi.or.id/featured-article/mengatasi-tantangan-pembelajaran-dan-merangkul-keberagaman | 8 | `button.accessibility-scale-decrease(23.5x23.5); button.accessibility-scale-increase(23.5x23.5); button.accessibility-scale-decrease(23.5x23.5)` |
| https://www.inovasi.or.id/featured-article/meningkatkan-kapasitas-gurufondasi-pendidikan-inklusif-di-indonesia | 8 | `button.accessibility-scale-decrease(23.5x23.5); button.accessibility-scale-increase(23.5x23.5); button.accessibility-scale-decrease(23.5x23.5)` |
| https://www.inovasi.or.id/featured-article/rayakan-hari-guru-nasional-pelita-tanpa-tanda-jasa-di-sumbawa | 8 | `button.accessibility-scale-decrease(23.5x23.5); button.accessibility-scale-increase(23.5x23.5); button.accessibility-scale-decrease(23.5x23.5)` |
| https://www.inovasi.or.id/info-daerah-update | 8 | `button.accessibility-scale-decrease(23.5x23.5); button.accessibility-scale-increase(23.5x23.5); button.accessibility-scale-decrease(23.5x23.5)` |

## Catatan interpretasi

- Ukuran target diukur pada viewport 1280px. Pada 320px banyak target justru lebih besar karena layout berubah, jadi angka ini konservatif untuk SC 2.5.8.
- Dua pengecualian SC 2.5.8 sudah diterapkan: link inline di dalam blok teks, dan spacing (lingkaran 24px tidak beririsan dengan lingkaran target lain). Target 24x24 dianggap memenuhi batas minimum.
- Kehadiran skip link di sini hanya berarti ada link anchor yang menunjuk ke element yang ada. Apakah link itu terlihat saat fokus dan apakah pengguna bisa menemukannya lewat keyboard tetap perlu uji manual.
- Scroll horizontal di 320px bisa menyebabkan dua arah baca pada mobile dan termasuk kegagalan SC 1.4.10 kalau tidak ada cara scroll dua arah yang disengaja.
- Pemeriksaan ini tidak menggantikan uji keyboard sungguhan: urutan fokus, focus trap, dan perilaku reader layar belum diperiksa.

