---
name: image-contact-sheet-qa
description: Generate and verify contact sheets/collages for image-heavy knowledge-base folders. Use when the user asks to find folders missing collages, make 拼图, check for white/blank thumbnails, repair HEIC/HEIF collage output, or validate that collage image counts match source images.
---

# Image Contact Sheet QA

Use this skill for collage generation and quality checks before image analysis or indexing.

## Workflow

1. Read the local knowledge-base rules first.
2. Inventory image-containing second-level folders and whether each has `_拼图输出`.
3. Exclude `_拼图输出`, compressed-preview folders, hidden files, and skipped folders such as `其他`.
4. Generate only missing or explicitly requested collages.
5. Prefer the local verified tool when present, such as `工具/拼图工具/bin/kb_contact_sheet`.
6. For HEIC/HEIF-heavy folders, use verified JPG previews, converted thumbnails, or compressed JPGs before generating the collage. Direct macOS drawing may create white/gray placeholder thumbnails.
7. After generation, open representative outputs. Check HEIC-heavy folders and any folder with unexpectedly low image counts.
8. If a collage has blank placeholders, missing subfolder images, or wrong counts, fix the source scan or preview source and overwrite the bad collage.

## QA Checks

- Source image count equals the count shown in the collage header.
- No large uniform white/gray blocks where thumbnails should appear.
- Nested material folders are included unless skipped by rule.
- Output lives under the source folder's `_拼图输出`.
- Do not keep duplicate bad generated outputs.
