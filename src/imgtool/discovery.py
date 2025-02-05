"""Penemuan file gambar dari daftar path (file atau folder)."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

# Ekstensi gambar yang didukung sebagai input.
SUPPORTED_EXTENSIONS = frozenset(
    {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif"}
)


def is_image(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def discover(paths: Iterable[str | Path], recursive: bool = False) -> list[Path]:
    """Kumpulkan file gambar dari ``paths``.

    - Path berupa file: diambil bila ekstensinya didukung.
    - Path berupa folder: diambil semua gambar di dalamnya (rekursif bila diminta).

    Hasil di-dedup dan diurutkan agar deterministik.
    """
    found: set[Path] = set()
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            pattern = "**/*" if recursive else "*"
            for child in path.glob(pattern):
                if child.is_file() and is_image(child):
                    found.add(child.resolve())
        elif path.is_file() and is_image(path):
            found.add(path.resolve())
    return sorted(found)
