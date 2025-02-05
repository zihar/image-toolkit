"""Logika inti: hitung ukuran target, konversi format, dan proses gambar."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

# Pemetaan ekstensi -> format Pillow & nama yang dinormalisasi.
_FORMAT_ALIASES = {
    "jpg": "jpeg",
    "jpeg": "jpeg",
    "png": "png",
    "webp": "webp",
    "bmp": "bmp",
    "tif": "tiff",
    "tiff": "tiff",
    "gif": "gif",
}

# Format yang tidak mendukung alpha channel -> butuh flatten ke RGB.
_NO_ALPHA = {"jpeg", "bmp"}


def normalize_format(fmt: str) -> str:
    """Normalisasi nama/ekstensi format ('JPG', '.jpeg' -> 'jpeg')."""
    key = fmt.lower().lstrip(".")
    if key not in _FORMAT_ALIASES:
        raise ValueError(
            f"Format tidak didukung: {fmt}. Pilihan: {', '.join(sorted(set(_FORMAT_ALIASES)))}"
        )
    return _FORMAT_ALIASES[key]


@dataclass(frozen=True)
class ResizeSpec:
    """Spesifikasi resize. Hanya salah satu mode yang dipakai (prioritas dari atas)."""

    width: int | None = None
    height: int | None = None
    scale: float | None = None  # persen, mis. 50 = 50%
    max_side: int | None = None  # sisi terpanjang dibatasi (hanya memperkecil)
    keep_aspect: bool = True

    @property
    def is_noop(self) -> bool:
        return not any((self.width, self.height, self.scale, self.max_side))


def compute_size(orig: tuple[int, int], spec: ResizeSpec) -> tuple[int, int]:
    """Hitung ukuran target (w, h) dari ukuran asli dan spesifikasi resize."""
    w, h = orig
    if w <= 0 or h <= 0:
        raise ValueError("Ukuran gambar tidak valid")

    if spec.scale is not None:
        factor = spec.scale / 100.0
        return _clamp(round(w * factor), round(h * factor))

    if spec.max_side is not None:
        longest = max(w, h)
        if longest <= spec.max_side:
            return (w, h)  # sudah cukup kecil, jangan diperbesar
        factor = spec.max_side / longest
        return _clamp(round(w * factor), round(h * factor))

    if spec.width and spec.height:
        if not spec.keep_aspect:
            return _clamp(spec.width, spec.height)
        # fit di dalam kotak (width x height) tanpa mengubah rasio
        factor = min(spec.width / w, spec.height / h)
        return _clamp(round(w * factor), round(h * factor))

    if spec.width:
        factor = spec.width / w
        return _clamp(spec.width, round(h * factor))

    if spec.height:
        factor = spec.height / h
        return _clamp(round(w * factor), spec.height)

    return (w, h)


def _clamp(w: int, h: int) -> tuple[int, int]:
    """Pastikan dimensi minimal 1 piksel."""
    return (max(1, w), max(1, h))


def _prepare_mode(img: Image.Image, target_format: str) -> Image.Image:
    """Sesuaikan mode warna agar kompatibel dengan format tujuan."""
    if target_format in _NO_ALPHA and img.mode in ("RGBA", "LA", "P"):
        # tempel di atas latar putih agar transparansi tidak jadi hitam
        rgba = img.convert("RGBA")
        background = Image.new("RGB", rgba.size, (255, 255, 255))
        background.paste(rgba, mask=rgba.split()[-1])
        return background
    if target_format in _NO_ALPHA and img.mode != "RGB":
        return img.convert("RGB")
    return img


@dataclass
class ProcessResult:
    source: Path
    output: Path
    orig_size: tuple[int, int]
    new_size: tuple[int, int]
    orig_bytes: int
    new_bytes: int

    @property
    def saved_bytes(self) -> int:
        return self.orig_bytes - self.new_bytes


def process_image(
    source: Path,
    output: Path,
    target_format: str,
    spec: ResizeSpec,
    quality: int = 85,
) -> ProcessResult:
    """Buka, (opsional) resize, konversi, dan simpan satu gambar."""
    source = Path(source)
    output = Path(output)
    orig_bytes = source.stat().st_size

    with Image.open(source) as img:
        img.load()
        orig_size = img.size
        new_size = compute_size(orig_size, spec)
        if new_size != orig_size:
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        img = _prepare_mode(img, target_format)

        output.parent.mkdir(parents=True, exist_ok=True)
        save_kwargs: dict = {}
        if target_format in ("jpeg", "webp"):
            save_kwargs["quality"] = quality
        if target_format == "jpeg":
            save_kwargs["optimize"] = True
        elif target_format == "png":
            save_kwargs["optimize"] = True
        img.save(output, format=target_format.upper(), **save_kwargs)

    return ProcessResult(
        source=source,
        output=output,
        orig_size=orig_size,
        new_size=new_size,
        orig_bytes=orig_bytes,
        new_bytes=output.stat().st_size,
    )


def build_output_path(
    source: Path,
    out_dir: Path | None,
    target_format: str,
    suffix: str = "",
) -> Path:
    """Tentukan path output: folder tujuan + nama asli + ekstensi format baru.

    Bila path hasil sama persis dengan sumber, tambahkan suffix default agar
    file asli tidak tertimpa secara tak sengaja.
    """
    ext = "jpg" if target_format == "jpeg" else target_format
    directory = Path(out_dir) if out_dir else source.parent
    candidate = directory / f"{source.stem}{suffix}.{ext}"
    if candidate.resolve() == source.resolve() and not suffix:
        candidate = directory / f"{source.stem}_out.{ext}"
    return candidate
