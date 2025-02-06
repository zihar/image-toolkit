from pathlib import Path

from imgtool.discovery import discover, is_image


def test_is_image():
    assert is_image(Path("a.JPG"))
    assert is_image(Path("b.webp"))
    assert not is_image(Path("c.txt"))


def test_discover_file_tunggal(sample_jpg):
    found = discover([sample_jpg])
    assert found == [sample_jpg.resolve()]


def test_discover_folder_non_rekursif(image_dir):
    found = discover([image_dir], recursive=False)
    names = {p.name for p in found}
    assert names == {"a.jpg", "b.png"}  # subfolder diabaikan
    assert "notes.txt" not in names


def test_discover_folder_rekursif(image_dir):
    found = discover([image_dir], recursive=True)
    names = {p.name for p in found}
    assert names == {"a.jpg", "b.png", "c.webp"}


def test_discover_dedup_dan_terurut(image_dir):
    found = discover([image_dir, image_dir], recursive=False)
    assert len(found) == 2
    assert found == sorted(found)


def test_discover_kosong(tmp_path):
    assert discover([tmp_path / "tidak-ada"]) == []
