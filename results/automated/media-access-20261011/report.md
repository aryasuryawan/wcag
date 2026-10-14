# Verifikasi Akses PDF & Video — 2026-10-11

Produced by `scripts/check_media_access.py`. Read-only HEAD/GET, jeda 1,5 detik.

## Ringkasan

| Item | Hasil |
|---|---|
| PDF terdaftar | 166 |
| PDF bisa diakses langsung (HTTP 200) | 101 |
| PDF diblokir (HTTP 403) | 65 |
| Embed video (YouTube) | 173 |
| Embed video bisa diakses (oEmbed 200) | 173 |
| Embed video tanpa `title` iframe | 0 |
| Iframe lain (Google Maps, PDF Embed) | 35 |
| Iframe lain tanpa `title` | 35 |
| Link ke kanal YouTube (bukan embed, di luar scope) | 3 |

File detail: `pdf-access.csv`, `video-access.csv`, `summary.json`.

## Temuan

### 1. 65 PDF membalas 403 (Critical, kandidat)

Semua berada di `/wp-content/uploads/securepdfs/`. Tetap 403 walau memakai User-Agent browser
plus header `Referer` ke halaman asal, dan tetap 403 dengan query tambahan `?download=1`.
Mekanismenya hotlink protection, bukan blokir bot.

Dampak: dokumen tidak bisa diunduh langsung. Satu-satunya jalur yang tersisa adalah iframe plugin
"PDF Embed" (`?pdfemb-data=`), yang membalas halaman HTML viewer, bukan file PDF. Keyboard user
dan screen reader user harus masuk ke iframe dulu untuk membaca dokumen.

### 2. 59 dari 65 PDF itu yatim (Critical, kandidat)

Pengecekan parent post via WordPress REST API:

```
GET /wp-json/wp/v2/media?mime_type=application/pdf&per_page=100&_fields=id,post,source_url
```

Semua 65 PDF punya `post` parent. Distribusi parent:

| Parent post | Jumlah PDF | Status parent |
|---|---|---|
| 20432 | 28 | 404 di semua endpoint WP REST |
| 20407 | 16 | 404 di semua endpoint WP REST |
| 20157 | 15 | 404 di semua endpoint WP REST |
| 21535, 22089, 21529, 1153, 1364, ... | 6 | sebagian ada (mis. `publication/risalah-kebijakan-...`) |

Artinya 59 PDF tidak menempel pada konten yang tayang publik (kemungkinan draft/trash atau
post yang dihapus), 6 sisanya menempel pada halaman yang ada tapi tetap 403.

### 3. 35 iframe tanpa accessible name (Serious, kandidat)

Semua iframe Google Maps dan PDF Embed tidak punya atribut `title`. Embed video YouTube 173
memiliki title, jadi template sisi konten lebih rapi dari sisi form/kontak.
SC kandidat: 4.1.2 Name, Role, Value (WCAG 2.1/2.2, level A).

### 4. Video YouTube (Minor/Moderate, belum dinilai)

173 embed semuanya publik atau unlisted (oEmbed balas 200), jadi tidak ada video private/removed
di inventaris. Ini hanya soal aksesibilitas embed, bukan konten video. Kelizability caption
dan transcript belum diuji di tahap ini.

## Yang BELUM Diperiksa

- Caption/transcript 173 video (butuh ASR + review native speaker).
- Struktur internal PDF: tag, heading hierarchy, bahasa, alternative text (butuh PDF/UA tool).
- Apakah PDF yang diblokir punya jalur undu alternatif yang ramah keyboard/screen reader.

## Perintah Reproduksi

```bash
python scripts/crawl_inventory.py --full-crawl --pdf-probe
python scripts/check_media_access.py
```