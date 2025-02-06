"""Antarmuka baris perintah (CLI) berbasis click + rich."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from imgtool import __version__
from imgtool.core import (
    ProcessResult,
    ResizeSpec,
    build_output_path,
    normalize_format,
    process_image,
)
from imgtool.discovery import SUPPORTED_EXTENSIONS, discover

console = Console()


def _human(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if abs(size) < 1024:
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def _run(
    inputs: tuple[str, ...],
    *,
    target_format: str | None,
    spec: ResizeSpec,
    quality: int,
    out_dir: str | None,
    suffix: str,
    recursive: bool,
) -> None:
    files = discover(inputs, recursive=recursive)
    if not files:
        raise click.ClickException(
            "Tidak ada gambar ditemukan. Dukungan: "
            + ", ".join(sorted(SUPPORTED_EXTENSIONS))
        )

    results: list[ProcessResult] = []
    errors: list[tuple[Path, str]] = []
    out_path = Path(out_dir) if out_dir else None

    with console.status(f"Memproses {len(files)} gambar..."):
        for src in files:
            fmt = normalize_format(target_format) if target_format else normalize_format(src.suffix)
            dst = build_output_path(src, out_path, fmt, suffix=suffix)
            try:
                results.append(process_image(src, dst, fmt, spec, quality=quality))
            except Exception as exc:  # noqa: BLE001 - laporkan per file, lanjutkan sisanya
                errors.append((src, str(exc)))

    _print_results(results, errors)


def _print_results(results: list[ProcessResult], errors: list[tuple[Path, str]]) -> None:
    if results:
        table = Table(title=f"Selesai memproses {len(results)} gambar")
        table.add_column("File")
        table.add_column("Ukuran px")
        table.add_column("Berkas", justify="right")
        table.add_column("Hemat", justify="right")
        total_saved = 0
        for r in results:
            total_saved += r.saved_bytes
            dims = (
                f"{r.orig_size[0]}x{r.orig_size[1]}"
                if r.orig_size == r.new_size
                else f"{r.orig_size[0]}x{r.orig_size[1]} → {r.new_size[0]}x{r.new_size[1]}"
            )
            pct = (r.saved_bytes / r.orig_bytes * 100) if r.orig_bytes else 0
            table.add_row(
                r.output.name,
                dims,
                f"{_human(r.orig_bytes)} → {_human(r.new_bytes)}",
                f"{pct:+.0f}%",
            )
        console.print(table)
        sign = "hemat" if total_saved >= 0 else "bertambah"
        console.print(f"[bold green]Total {sign}: {_human(abs(total_saved))}[/]")

    for src, msg in errors:
        console.print(f"[red]Gagal[/] {src.name}: {msg}")


# --- opsi bersama ---
_out_option = click.option(
    "--out", "-o", default=None, help="Folder output (default: sebelah file asli)."
)
_recursive_option = click.option(
    "-r", "--recursive", is_flag=True, help="Telusuri folder rekursif."
)
_quality_option = click.option(
    "--quality", "-q", default=85, show_default=True, type=click.IntRange(1, 100),
    help="Kualitas untuk JPEG/WebP.",
)


@click.group(help="Konversi & resize gambar massal dari terminal.")
@click.version_option(__version__)
def main() -> None:
    pass


@main.command(help="Ubah format gambar (mis. PNG → WebP).")
@click.argument("inputs", nargs=-1, required=True)
@click.option("--format", "-f", "fmt", required=True, help="Format tujuan: jpg, png, webp, ...")
@_quality_option
@_out_option
@_recursive_option
def convert(inputs: tuple[str, ...], fmt: str, quality: int, out: str | None, recursive: bool):
    _run(
        inputs, target_format=fmt, spec=ResizeSpec(), quality=quality,
        out_dir=out, suffix="", recursive=recursive,
    )


@main.command(help="Resize gambar (lebar/tinggi/skala/sisi-terpanjang).")
@click.argument("inputs", nargs=-1, required=True)
@click.option("--width", "-w", type=int, default=None, help="Lebar target (px).")
@click.option("--height", "-h", type=int, default=None, help="Tinggi target (px).")
@click.option("--scale", "-s", type=float, default=None, help="Skala persen, mis. 50.")
@click.option("--max", "max_side", type=int, default=None, help="Batasi sisi terpanjang (px).")
@click.option("--exact", is_flag=True, help="Paksa lebar×tinggi persis (abaikan rasio).")
@click.option("--format", "-f", "fmt", default=None, help="Sekalian ubah format (opsional).")
@_quality_option
@_out_option
@_recursive_option
def resize(
    inputs: tuple[str, ...], width, height, scale, max_side, exact,
    fmt, quality, out, recursive,
):
    spec = ResizeSpec(
        width=width, height=height, scale=scale, max_side=max_side,
        keep_aspect=not exact,
    )
    if spec.is_noop:
        raise click.ClickException("Tentukan salah satu: --width/--height/--scale/--max.")
    _run(
        inputs, target_format=fmt, spec=spec, quality=quality,
        out_dir=out, suffix="" if (out or fmt) else "_resized", recursive=recursive,
    )


@main.command(help="Tampilkan info gambar (dimensi, format, ukuran berkas).")
@click.argument("inputs", nargs=-1, required=True)
@_recursive_option
def info(inputs: tuple[str, ...], recursive: bool):
    from PIL import Image

    files = discover(inputs, recursive=recursive)
    if not files:
        raise click.ClickException("Tidak ada gambar ditemukan.")
    table = Table(title=f"{len(files)} gambar")
    table.add_column("File")
    table.add_column("Format")
    table.add_column("Dimensi")
    table.add_column("Mode")
    table.add_column("Ukuran", justify="right")
    for f in files:
        try:
            with Image.open(f) as img:
                table.add_row(f.name, img.format or "?", f"{img.width}x{img.height}",
                              img.mode, _human(f.stat().st_size))
        except Exception as exc:  # noqa: BLE001
            table.add_row(f.name, "[red]ERROR[/]", str(exc), "-", "-")
    console.print(table)


if __name__ == "__main__":
    main()
