#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
import zipfile
from pathlib import Path


DEFAULT_SKIP_DIRS = {".git", "_压缩版_2048_q95", "_compressed_2048_q95", "其他"}
DEFAULT_SKIP_FILES = {".DS_Store"}


def should_skip(rel: Path, skip_dirs: set[str], skip_files: set[str]) -> bool:
    return (
        any(part in skip_dirs or part.startswith(".git") for part in rel.parts)
        or rel.name in skip_files
        or rel.name.startswith("._")
    )


def collect(root: Path, skip_dirs: set[str], skip_files: set[str]) -> tuple[set[str], set[str]]:
    dirs: set[str] = set()
    files: set[str] = set()
    if not root.exists():
        return dirs, files
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if should_skip(rel, skip_dirs, skip_files):
            continue
        if path.is_dir():
            dirs.add(str(rel))
        elif path.is_file():
            files.add(str(rel))
    return dirs, files


def package_missing(local: Path, drive: Path, missing_files: list[str], out_dir: Path) -> Path:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    for rel_text in missing_files:
        src = local / rel_text
        dest = out_dir / rel_text
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": str(local),
        "drive_target": str(drive),
        "policy": "only local files missing from Drive; no overwrite/delete",
        "file_count": len(missing_files),
        "files": missing_files,
    }
    (out_dir / "同步清单.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    zip_path = out_dir.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in out_dir.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(out_dir))
    return zip_path


def copy_missing(local: Path, drive: Path, missing_files: list[str], missing_dirs: list[str]) -> tuple[int, int]:
    created_dirs = 0
    copied_files = 0
    for rel_text in missing_dirs:
        dest = drive / rel_text
        if not dest.exists():
            dest.mkdir(parents=True, exist_ok=True)
            created_dirs += 1
    for rel_text in missing_files:
        src = local / rel_text
        dest = drive / rel_text
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied_files += 1
    return created_dirs, copied_files


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare local knowledge base to Drive and package/copy missing files.")
    parser.add_argument("--local", required=True, type=Path)
    parser.add_argument("--drive", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--copy-missing", action="store_true")
    parser.add_argument("--package-only", action="store_true")
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()

    local = args.local.expanduser().resolve()
    drive = args.drive.expanduser().resolve()
    if not local.exists():
        print(f"local root not found: {local}", file=sys.stderr)
        return 2

    local_dirs, local_files = collect(local, DEFAULT_SKIP_DIRS, DEFAULT_SKIP_FILES)
    drive_dirs, drive_files = collect(drive, DEFAULT_SKIP_DIRS, DEFAULT_SKIP_FILES)
    missing_dirs = sorted(local_dirs - drive_dirs)
    missing_files = sorted(local_files - drive_files)
    extra_drive_files = sorted(drive_files - local_files)

    print(json.dumps({
        "local_dirs": len(local_dirs),
        "drive_dirs": len(drive_dirs),
        "missing_dirs": len(missing_dirs),
        "local_files": len(local_files),
        "drive_files": len(drive_files),
        "missing_files": len(missing_files),
        "extra_drive_files": len(extra_drive_files),
    }, ensure_ascii=False, indent=2))

    if args.dry_run:
        for rel_text in missing_files[:120]:
            print(rel_text)
        return 0

    if args.copy_missing and not args.package_only:
        created_dirs, copied_files = copy_missing(local, drive, missing_files, missing_dirs)
        print(json.dumps({"created_dirs": created_dirs, "copied_files": copied_files}, ensure_ascii=False, indent=2))
        return 0

    out_dir = args.out_dir or local / f"_待同步到Drive_{time.strftime('%Y%m%d_%H%M%S')}_缺失文件"
    zip_path = package_missing(local, drive, missing_files, out_dir)
    print(json.dumps({
        "package_dir": str(out_dir),
        "zip_path": str(zip_path),
        "missing_files_packaged": len(missing_files),
        "zip_size_mb": round(zip_path.stat().st_size / 1024 / 1024, 2),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
