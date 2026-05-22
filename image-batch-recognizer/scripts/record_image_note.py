#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


TEMPLATE = """### {image}

- 资料类型：{kind}
- 标题/主题：{title}
- 关键文字：{text}
- 核心结论：{conclusion}
- 涉及模块/概念：{concepts}
- 问题现象：{issues}
- 检索关键词：{keywords}
- 后续精读：{followup}
"""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def update_counts(state: dict) -> None:
    counts = {"pending": 0, "done": 0, "failed": 0, "skipped": 0}
    next_pending = None
    for idx, item in enumerate(state["images"]):
        status = item.get("status", "pending")
        counts[status] = counts.get(status, 0) + 1
        if next_pending is None and status == "pending":
            next_pending = idx
    state["counts"] = counts
    state["next_pending_index"] = next_pending
    state["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")


def main() -> int:
    parser = argparse.ArgumentParser(description="Append one image recognition note and update batch progress.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("image")
    parser.add_argument("--status", choices=["done", "failed", "skipped"], default="done")
    parser.add_argument("--note-file", type=Path, help="Markdown note body to append. If omitted, fields are used.")
    parser.add_argument("--kind", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--text", default="")
    parser.add_argument("--conclusion", default="")
    parser.add_argument("--concepts", default="")
    parser.add_argument("--issues", default="")
    parser.add_argument("--keywords", default="")
    parser.add_argument("--followup", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    folder = args.folder.expanduser().resolve()
    progress = folder / "逐图识别进度.json"
    notes = folder / "逐图识别明细.md"
    if not progress.exists():
        raise SystemExit(f"progress file not found: {progress}")
    if not notes.exists():
        notes.write_text("# 逐图识别明细\n\n## 记录\n\n", encoding="utf-8")

    state = load_json(progress)
    image = args.image
    note_anchor = image.replace(" ", "-")

    if args.note_file:
        note = args.note_file.read_text(encoding="utf-8")
    else:
        note = TEMPLATE.format(
            image=image,
            kind=args.kind,
            title=args.title,
            text=args.text,
            conclusion=args.conclusion,
            concepts=args.concepts,
            issues=args.issues,
            keywords=args.keywords,
            followup=args.followup,
        )
    if args.status in {"failed", "skipped"} and args.reason:
        note += f"\n- 状态说明：{args.reason}\n"

    existing = notes.read_text(encoding="utf-8")
    if f"### {image}" not in existing:
        with notes.open("a", encoding="utf-8") as f:
            if not existing.endswith("\n"):
                f.write("\n")
            f.write("\n" + note.strip() + "\n")

    found = False
    for item in state["images"]:
        if item["path"] == image:
            item["status"] = args.status
            item["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            item["note_anchor"] = note_anchor
            if args.reason:
                item["reason"] = args.reason
            found = True
            break
    if not found:
        raise SystemExit(f"image not found in progress list: {image}")
    state["last_processed"] = image
    update_counts(state)
    write_json(progress, state)
    print(json.dumps({
        "image": image,
        "status": args.status,
        "progress": str(progress),
        "notes": str(notes),
        "counts": state["counts"],
        "next_pending_index": state["next_pending_index"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
