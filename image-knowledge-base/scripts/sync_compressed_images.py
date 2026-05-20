#!/usr/bin/env python3
"""Synchronize compressed preview images for an image-heavy knowledge base."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".heic", ".tif", ".tiff", ".gif"}
DEFAULT_COMPRESSED_DIR = "_compressed_2048_q95"
ALT_COMPRESSED_DIR = "_压缩版_2048_q95"
EXCLUDED_DIRS = {
    DEFAULT_COMPRESSED_DIR,
    ALT_COMPRESSED_DIR,
    "_压缩试验_10张",
    ".git",
    "__MACOSX",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or update compressed JPG copies of source images."
    )
    parser.add_argument("root", nargs="?", default=".", help="Knowledge-base root")
    parser.add_argument(
        "--compressed-dir",
        default=None,
        help="Derived compressed directory name or path",
    )
    parser.add_argument("--max-edge", type=int, default=2048, help="Maximum long edge")
    parser.add_argument("--quality", type=int, default=95, help="JPEG quality")
    parser.add_argument("--force", action="store_true", help="Recreate all outputs")
    parser.add_argument("--dry-run", action="store_true", help="Show work without writing")
    return parser.parse_args()


def choose_compressed_root(root: Path, requested: str | None) -> Path:
    if requested:
        compressed = Path(requested).expanduser()
        return (root / compressed).resolve() if not compressed.is_absolute() else compressed.resolve()
    if (root / ALT_COMPRESSED_DIR).exists():
        return (root / ALT_COMPRESSED_DIR).resolve()
    return (root / DEFAULT_COMPRESSED_DIR).resolve()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def iter_images(root: Path, compressed_root: Path):
    for current, dirs, files in os.walk(root):
        current_path = Path(current).resolve()
        dirs[:] = [
            d
            for d in dirs
            if d not in EXCLUDED_DIRS
            and not d.startswith(".")
            and not is_relative_to((current_path / d).resolve(), compressed_root)
        ]
        for name in files:
            if name.startswith("."):
                continue
            src = current_path / name
            if src.suffix.lower() in IMAGE_EXTS:
                yield src


def needs_update(src: Path, dest: Path, force: bool) -> bool:
    if force or not dest.exists():
        return True
    return src.stat().st_mtime > dest.stat().st_mtime


def compress_with_sips(
    sips: str, src: Path, dest: Path, max_edge: int, quality: int
) -> tuple[bool, str]:
    cmd = [
        sips,
        "-Z",
        str(max_edge),
        "-s",
        "format",
        "jpeg",
        "-s",
        "formatOptions",
        str(quality),
        str(src),
        "--out",
        str(dest),
    ]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    return result.returncode == 0, result.stderr.strip()


def compress_with_pillow(src: Path, dest: Path, max_edge: int, quality: int) -> tuple[bool, str]:
    try:
        from PIL import Image, ImageOps
    except Exception as exc:  # pragma: no cover - depends on local environment
        return False, f"Pillow unavailable: {exc}"

    try:
        with Image.open(src) as image:
            image = ImageOps.exif_transpose(image)
            image.thumbnail((max_edge, max_edge))
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
            image.save(dest, "JPEG", quality=quality, optimize=True)
        return True, ""
    except Exception as exc:  # pragma: no cover - depends on input files
        return False, str(exc)


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    compressed_root = choose_compressed_root(root, args.compressed_dir)

    sips = shutil.which("sips")
    sources = list(iter_images(root, compressed_root))
    created = skipped = failed = 0
    failures: list[str] = []

    for src in sources:
        rel = src.relative_to(root)
        dest = (compressed_root / rel).with_suffix(".jpg")
        if not needs_update(src, dest, args.force):
            skipped += 1
            continue

        if args.dry_run:
            print(f"would create: {dest.relative_to(root)}")
            created += 1
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        if sips:
            ok, err = compress_with_sips(sips, src, dest, args.max_edge, args.quality)
        else:
            ok, err = compress_with_pillow(src, dest, args.max_edge, args.quality)

        if ok:
            created += 1
        else:
            failed += 1
            failures.append(f"{src}\t{err}")

    if failures and not args.dry_run:
        compressed_root.mkdir(parents=True, exist_ok=True)
        (compressed_root / "_compression_failed_files.txt").write_text(
            "\n".join(failures) + "\n", encoding="utf-8"
        )

    print(f"source images: {len(sources)}")
    print(f"created/updated: {created}")
    print(f"skipped current: {skipped}")
    print(f"failed: {failed}")
    print(f"compressed root: {compressed_root}")
    if failed and not sips:
        print("tip: install Pillow with `python -m pip install pillow`", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
