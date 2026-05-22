#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff", ".bmp"}
SKIP_DIRS = {"_拼图输出", "_压缩版_2048_q95", "_compressed_2048_q95", "其他"}
SKIP_FILES = {".DS_Store"}


def natural_key(path: Path) -> list[object]:
    import re

    parts: list[object] = []
    for token in re.split(r"(\d+)", str(path)):
        parts.append(int(token) if token.isdigit() else token.lower())
    return parts


def should_skip(rel: Path) -> bool:
    return (
        any(part in SKIP_DIRS or part.startswith(".git") for part in rel.parts)
        or rel.name in SKIP_FILES
        or rel.name.startswith("._")
    )


def image_list(root: Path) -> list[str]:
    items: list[Path] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if should_skip(rel):
            continue
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            items.append(rel)
    return [str(p) for p in sorted(items, key=natural_key)]


def load_state(progress_path: Path) -> dict | None:
    if not progress_path.exists():
        return None
    return json.loads(progress_path.read_text(encoding="utf-8"))


def make_state(folder: Path, batch_size: int) -> dict:
    files = image_list(folder)
    return {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "folder": str(folder),
        "batch_size": batch_size,
        "total_images": len(files),
        "next_pending_index": 0,
        "last_processed": None,
        "images": [{"path": item, "status": "pending", "updated_at": None, "note_anchor": None} for item in files],
    }


def update_summary(state: dict) -> dict:
    counts = {"pending": 0, "done": 0, "failed": 0, "skipped": 0}
    for item in state["images"]:
        counts[item.get("status", "pending")] = counts.get(item.get("status", "pending"), 0) + 1
    next_index = None
    for i, item in enumerate(state["images"]):
        if item.get("status") == "pending":
            next_index = i
            break
    state["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    state["next_pending_index"] = next_index
    state["counts"] = counts
    return state


def ensure_notes(notes_path: Path, folder: Path, state: dict) -> None:
    if notes_path.exists():
        return
    notes_path.write_text(
        "\n".join([
            f"# 逐图识别明细",
            "",
            f"资料夹：`{folder}`",
            f"图片数量：{state['total_images']}",
            "",
            "## 记录",
            "",
        ]),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize or inspect resumable image recognition batch files.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    folder = args.folder.expanduser().resolve()
    if not folder.exists() or not folder.is_dir():
        raise SystemExit(f"folder not found: {folder}")

    progress_path = folder / "逐图识别进度.json"
    notes_path = folder / "逐图识别明细.md"
    state = None if args.reset else load_state(progress_path)
    if state is None:
        state = make_state(folder, args.batch_size)
    else:
        state["batch_size"] = args.batch_size
    state = update_summary(state)
    progress_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    ensure_notes(notes_path, folder, state)

    start = state["next_pending_index"]
    batch: list[str] = []
    if start is not None:
        pending = [item["path"] for item in state["images"] if item.get("status") == "pending"]
        batch = pending[: args.batch_size]

    print(json.dumps({
        "folder": str(folder),
        "progress": str(progress_path),
        "notes": str(notes_path),
        "total_images": state["total_images"],
        "counts": state.get("counts", {}),
        "next_pending_index": start,
        "next_batch": batch,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
