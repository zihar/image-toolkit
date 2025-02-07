# 🖼️ image-toolkit (`imgtool`)

> CLI ringan untuk **konversi & resize gambar massal** dari terminal — berbasis [Pillow](https://python-pillow.org/).

![CI](https://github.com/zihar/image-toolkit/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Konversi format (PNG ↔ JPG ↔ WebP …), perkecil/ubah ukuran satu file atau seluruh folder sekaligus, dan kompres untuk menghemat ukuran berkas — semuanya dengan satu perintah. Dilengkapi output tabel berwarna (`rich`), penanganan transparansi otomatis, **test** lengkap, dan **CI**.

> ⚠️ Ganti `zihar` pada badge & URL di atas dengan username GitHub-mu bila berbeda.

## ✨ Fitur

- **Batch** — proses satu file, banyak file, atau seluruh folder (`-r` untuk rekursif).
- **Konversi format** — jpg, png, webp, bmp, tiff, gif.
- **Resize fleksibel** — berdasarkan lebar, tinggi, skala persen, atau batas sisi terpanjang; jaga rasio otomatis (atau `--exact`).
- **Kompres** — atur `--quality` untuk JPEG/WebP, optimasi PNG otomatis.
- **Aman** — transparansi (RGBA) di-flatten ke putih saat ke JPEG; file asli tidak tertimpa tanpa sengaja.
- **Laporan jelas** — tabel ukuran px, ukuran berkas, dan total penghematan.

## 🚀 Instalasi

```bash
git clone https://github.com/zihar/image-toolkit.git
cd image-toolkit

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

## 🧑‍💻 Penggunaan

```bash
# Konversi satu gambar PNG → WebP
imgtool convert foto.png --format webp

# Konversi semua gambar di folder → JPG (kualitas 80), simpan ke folder lain
imgtool convert ./gambar -f jpg -q 80 --out ./hasil -r

# Resize ke lebar 800px (tinggi otomatis menjaga rasio)
imgtool resize foto.jpg --width 800

# Perkecil semua gambar agar sisi terpanjang maksimal 1200px
imgtool resize ./album --max 1200 -r --out ./web

# Resize 50% sekaligus konversi ke WebP
imgtool resize foto.png --scale 50 --format webp

# Lihat info gambar (dimensi, format, ukuran)
imgtool info ./gambar -r
```

Contoh keluaran:

```
        Selesai memproses 3 gambar
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ File      ┃ Ukuran px         ┃ Berkas        ┃ Hemat ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━┩
│ a.webp    │ 4000x3000 → 1200… │ 3.2MB → 410KB │  +87% │
│ b.webp    │ 3000x2000 → 1200… │ 2.1MB → 280KB │  +87% │
└───────────┴───────────────────┴───────────────┴───────┘
Total hemat: 4.6MB
```

## 🧩 Opsi `resize`

| Opsi | Arti |
|---|---|
| `--width, -w` | Lebar target (px), tinggi mengikuti rasio |
| `--height, -h` | Tinggi target (px), lebar mengikuti rasio |
| `--scale, -s` | Skala persen (mis. `50` = 50%) |
| `--max` | Batasi sisi terpanjang (hanya memperkecil) |
| `--exact` | Paksa lebar×tinggi persis, abaikan rasio |
| `--format, -f` | Sekalian ubah format |
| `--quality, -q` | Kualitas JPEG/WebP (1–100) |
| `--out, -o` | Folder output |
| `-r` | Telusuri folder rekursif |

## 🏗️ Struktur Proyek

```
src/imgtool/
├── discovery.py   # temukan file gambar dari path/folder
├── core.py        # hitung ukuran, konversi format, proses gambar (Pillow)
└── cli.py         # CLI (click + rich): convert / resize / info
tests/             # pytest — gambar dibuat on-the-fly via Pillow
```

## 🧪 Menjalankan Test

```bash
pytest             # seluruh test (gambar dibuat otomatis, tanpa file eksternal)
ruff check .       # linting
```

## 📄 Lisensi

[MIT](LICENSE)
