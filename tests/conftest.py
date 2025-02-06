"""Fixture: buat gambar contoh memakai Pillow (tanpa file eksternal)."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def sample_png(tmp_path: Path) -> Path:
    """PNG 200x100 dengan transparansi (RGBA)."""
    img = Image.new("RGBA", (200, 100), (255, 0, 0, 128))
    path = tmp_path / "sample.png"
    img.save(path)
    return path


@pytest.fixture
def sample_jpg(tmp_path: Path) -> Path:
    """JPEG 400x300 (RGB)."""
    img = Image.new("RGB", (400, 300), (0, 128, 255))
    path = tmp_path / "photo.jpg"
    img.save(path)
    return path


@pytest.fixture
def image_dir(tmp_path: Path) -> Path:
    """Folder berisi beberapa gambar + subfolder + file non-gambar."""
    Image.new("RGB", (50, 50), "white").save(tmp_path / "a.jpg")
    Image.new("RGB", (50, 50), "black").save(tmp_path / "b.png")
    (tmp_path / "notes.txt").write_text("bukan gambar")
    sub = tmp_path / "sub"
    sub.mkdir()
    Image.new("RGB", (50, 50), "red").save(sub / "c.webp")
    return tmp_path
