---
name: image-batch-recognizer
description: Recognize image-heavy folders one small batch at a time with local checkpoints, per-image notes, and resumable progress. Use when the user asks for逐图识别,逐页识别, detailed image indexing, OCR-like image summaries, batch image recognition, or wants to avoid context compaction/freezing while processing many images.
---

# Image Batch Recognizer

Use this skill when image recognition needs to go beyond a collage overview. The default is **resumable, file-backed batch processing**: never keep the only copy of progress in chat.

## Core Rule

Process at most 5-10 images per batch, then write results to disk before continuing. If the folder is large or the session feels long, stop after the current batch with a clear resume point.

## Workflow

1. Read root rules first and apply skip rules such as `其他`, `_拼图输出`, compressed-preview folders, `.DS_Store`, and AppleDouble files.
2. Prefer existing compressed JPG previews or verified JPG contact-sheet sources for HEIC/HEIF. Do not open many original HEIC files directly.
3. Initialize or read the folder checkpoint files:
   - `逐图识别进度.json`
   - `逐图识别明细.md`
4. Build a stable ordered image list and mark each item `pending`, `done`, `failed`, or `skipped`.
5. Process only the next pending batch. Default batch size is 5; use 10 only for simple screenshots or already-compressed previews.
6. For each image, write a compact fixed record to `逐图识别明细.md` and update `逐图识别进度.json`. Prefer the bundled `record_image_note.py` helper so status stays consistent.
7. Every 20-30 completed images, or at folder end, summarize useful retrieval entries into the nearest `资料索引.md`.
8. Report only the batch result, next resume point, and files updated.

## Per-Image Record Shape

Use this compact structure for each image:

```markdown
### filename.ext

- 资料类型：
- 标题/主题：
- 关键文字：
- 核心结论：
- 涉及模块/概念：
- 问题现象：
- 检索关键词：
- 后续精读：是/否，原因
```

Keep each field short. Do not paste full OCR unless the user explicitly asks.

## Context-Safety Rules

- Do not open more than one batch of original images before writing progress.
- Do not summarize hundreds of images in chat. Write the detailed notes locally and give a compact status update.
- If context compaction happens, resume from `逐图识别进度.json` and `逐图识别明细.md`.
- Before stopping, ensure the progress file contains `next_pending_index` and `last_processed`.
- If an image is unreadable or blank, mark it `failed` with the reason and continue.

## Script

Initialize or inspect a batch state:

```bash
python image-knowledge-base-skill/image-batch-recognizer/scripts/init_image_batch.py /path/to/folder
```

Useful options:

```bash
python image-knowledge-base-skill/image-batch-recognizer/scripts/init_image_batch.py /path/to/folder --batch-size 5
python image-knowledge-base-skill/image-batch-recognizer/scripts/init_image_batch.py /path/to/folder --reset
```

Append one image note and mark progress:

```bash
python image-knowledge-base-skill/image-batch-recognizer/scripts/record_image_note.py /path/to/folder filename.jpg --status done --note-file /tmp/note.md
```
