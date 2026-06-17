# 🖼️ image-toolkit (`imgtool`)

> Lightweight CLI for **bulk image conversion & resizing** from the terminal — built on [Pillow](https://python-pillow.org/).

![CI](https://github.com/zihar/image-toolkit/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Convert formats (PNG ↔ JPG ↔ WebP …), shrink/resize a single file or an entire folder at once, and compress to save file size — all with a single command. Comes with colored table output (`rich`), automatic transparency handling, a full **test** suite, and **CI**.

> ⚠️ Replace `zihar` in the badges & URLs above with your GitHub username if it's different.

## ✨ Features

- **Batch** — process a single file, many files, or an entire folder (`-r` for recursive).
- **Format conversion** — jpg, png, webp, bmp, tiff, gif.
- **Flexible resize** — by width, height, percent scale, or longest-side limit; preserves aspect ratio automatically (or `--exact`).
- **Compress** — set `--quality` for JPEG/WebP, automatic PNG optimization.
- **Safe** — transparency (RGBA) is flattened to white when converting to JPEG; original files are not overwritten accidentally.
- **Clear reports** — table of px dimensions, file size, and total savings.

## 🚀 Installation

```bash
git clone https://github.com/zihar/image-toolkit.git
cd image-toolkit

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

## 🧑‍💻 Usage

```bash
# Convert a single PNG image → WebP
imgtool convert foto.png --format webp

# Convert all images in a folder → JPG (quality 80), save to another folder
imgtool convert ./gambar -f jpg -q 80 --out ./hasil -r

# Resize to 800px width (height automatically preserves the ratio)
imgtool resize foto.jpg --width 800

# Shrink all images so the longest side is at most 1200px
imgtool resize ./album --max 1200 -r --out ./web

# Resize 50% while converting to WebP
imgtool resize foto.png --scale 50 --format webp

# View image info (dimensions, format, size)
imgtool info ./gambar -r
```

Example output:

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

## 🧩 `resize` Options

| Option | Meaning |
|---|---|
| `--width, -w` | Target width (px), height follows the ratio |
| `--height, -h` | Target height (px), width follows the ratio |
| `--scale, -s` | Percent scale (e.g. `50` = 50%) |
| `--max` | Limit the longest side (shrink only) |
| `--exact` | Force exact width×height, ignore ratio |
| `--format, -f` | Change format at the same time |
| `--quality, -q` | JPEG/WebP quality (1–100) |
| `--out, -o` | Output folder |
| `-r` | Traverse folders recursively |

## 🏗️ Project Structure

```
src/imgtool/
├── discovery.py   # find image files from a path/folder
├── core.py        # compute sizes, convert formats, process images (Pillow)
└── cli.py         # CLI (click + rich): convert / resize / info
tests/             # pytest — images created on-the-fly via Pillow
```

## 🧪 Running Tests

```bash
pytest             # all tests (images created automatically, no external files)
ruff check .       # linting
```

## 📄 License

[MIT](LICENSE)
