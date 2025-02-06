import pytest
from PIL import Image

from imgtool.core import (
    ResizeSpec,
    build_output_path,
    compute_size,
    normalize_format,
    process_image,
)

# ---- normalize_format ----

@pytest.mark.parametrize(
    "raw,expected",
    [("jpg", "jpeg"), ("JPEG", "jpeg"), (".png", "png"), ("WebP", "webp"), (".tif", "tiff")],
)
def test_normalize_format(raw, expected):
    assert normalize_format(raw) == expected


def test_normalize_format_invalid():
    with pytest.raises(ValueError):
        normalize_format("heic")


# ---- compute_size ----

def test_resize_by_width_jaga_rasio():
    assert compute_size((400, 200), ResizeSpec(width=200)) == (200, 100)


def test_resize_by_height_jaga_rasio():
    assert compute_size((400, 200), ResizeSpec(height=100)) == (200, 100)


def test_resize_by_scale():
    assert compute_size((400, 200), ResizeSpec(scale=50)) == (200, 100)


def test_resize_max_side_memperkecil():
    assert compute_size((1000, 500), ResizeSpec(max_side=500)) == (500, 250)


def test_resize_max_side_tidak_memperbesar():
    assert compute_size((300, 200), ResizeSpec(max_side=500)) == (300, 200)


def test_resize_fit_box_jaga_rasio():
    # muat dalam kotak 200x200 -> dibatasi lebar
    assert compute_size((400, 200), ResizeSpec(width=200, height=200)) == (200, 100)


def test_resize_exact_abaikan_rasio():
    spec = ResizeSpec(width=200, height=200, keep_aspect=False)
    assert compute_size((400, 200), spec) == (200, 200)


def test_resize_minimal_satu_piksel():
    assert compute_size((10, 10), ResizeSpec(scale=1)) == (1, 1)


def test_noop_kembalikan_ukuran_asli():
    assert compute_size((400, 200), ResizeSpec()) == (400, 200)


# ---- process_image ----

def test_convert_png_ke_jpg_flatten_alpha(sample_png, tmp_path):
    out = tmp_path / "out.jpg"
    result = process_image(sample_png, out, "jpeg", ResizeSpec(), quality=90)
    assert out.exists()
    with Image.open(out) as img:
        assert img.format == "JPEG"
        assert img.mode == "RGB"  # alpha sudah di-flatten
    assert result.orig_size == (200, 100)


def test_resize_dan_konversi_sekaligus(sample_jpg, tmp_path):
    out = tmp_path / "small.webp"
    result = process_image(sample_jpg, out, "webp", ResizeSpec(width=200))
    with Image.open(out) as img:
        assert img.size == (200, 150)
        assert img.format == "WEBP"
    assert result.new_size == (200, 150)


def test_process_mengembalikan_metadata_ukuran(sample_jpg, tmp_path):
    result = process_image(sample_jpg, tmp_path / "o.jpg", "jpeg", ResizeSpec(scale=50))
    assert result.orig_size == (400, 300)
    assert result.new_size == (200, 150)
    assert result.new_bytes > 0


# ---- build_output_path ----

def test_build_output_path_ganti_ekstensi(tmp_path):
    src = tmp_path / "foto.png"
    out = build_output_path(src, None, "jpeg")
    assert out.name == "foto.jpg"
    assert out.parent == tmp_path


def test_build_output_path_folder_tujuan(tmp_path):
    src = tmp_path / "foto.png"
    dest = tmp_path / "hasil"
    out = build_output_path(src, dest, "webp")
    assert out == dest / "foto.webp"


def test_build_output_path_hindari_timpa_sumber(tmp_path):
    src = tmp_path / "foto.jpg"
    src.touch()
    out = build_output_path(src, None, "jpeg")  # sama persis -> pakai suffix _out
    assert out.name == "foto_out.jpg"
