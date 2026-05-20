---
name: image-knowledge-base
description: Maintain a local image-heavy knowledge base with compressed preview copies and Markdown indexes. Use automatically when the user asks in natural language to update a knowledge base, organize a new image folder, scan new materials, update indexes, summarize image collections, compress images before analysis, process many images in batches, or avoid large-context failures while working with image collections. Also use for Chinese requests such as 整理知识库, 整理新增文件夹, 扫描新增资料, 更新索引, 整理图片, 看新增图片, 先压缩图片, 同步压缩版, or 补充资料索引. The user should not need to name this skill or provide a full invocation prompt.
---

# Image Knowledge Base

Use this skill for local knowledge bases where images are primary source material and Markdown indexes make retrieval practical.

Users do not need to name this skill. Treat requests such as "update my knowledge base", "organize the new image folder", "compress images first", "process these images in batches", "更新知识库", "整理新增文件夹", or "图片先压缩一下" as triggers.

## Default Workflow

1. Read the root usage-rules file first when it exists, such as `知识库使用规则.md`, `README.md`, or `INDEX.md`.
2. Treat compressed-preview folders as derived directories. Exclude `_compressed_2048_q95` and `_压缩版_2048_q95` from original-source scans.
3. Before analyzing newly added images, synchronize them into the compressed-preview directory with `scripts/sync_compressed_images.py`.
4. Analyze compressed images first. Open original images only when fine detail, noise, sharpening, color, or text legibility requires confirmation.
5. Process image sets in small batches, usually 10-30 images per pass.
6. Update the nearest local index after each batch, such as `资料索引.md`, `index.md`, or `README.md`. Update root-level indexes only when the folder structure, topic map, keywords, or global entry points change.
7. Keep chat summaries compact. Store durable findings in local Markdown indexes instead of relying on conversation context.

## Compression Rules

- Preserve originals in place. Never overwrite, move, rename, or downsample original files unless the user explicitly asks.
- Store compressed copies under `_compressed_2048_q95` by default. If the knowledge base already uses `_压缩版_2048_q95`, keep using that directory.
- Mirror the original relative directory structure inside the compressed directory.
- Convert image copies to `.jpg`, max long edge `2048px`, quality `95`.
- Skip compressed copies that are newer than their originals unless a refresh is needed.
- Exclude compressed-preview directories, hidden system files, and temporary experiment directories from original-source scans.

Run from the knowledge-base root:

```bash
python ~/.codex/skills/image-knowledge-base/scripts/sync_compressed_images.py .
```

Useful options:

```bash
python ~/.codex/skills/image-knowledge-base/scripts/sync_compressed_images.py . --dry-run
python ~/.codex/skills/image-knowledge-base/scripts/sync_compressed_images.py . --force
python ~/.codex/skills/image-knowledge-base/scripts/sync_compressed_images.py . --compressed-dir _compressed_2048_q95
```

## Indexing Rules

For each image folder, prefer a concise index with:

- folder purpose and source scope
- image count, file range, and update date
- batch-level content summaries
- key images or ranges worth opening
- retrieval keywords in relevant languages, abbreviations, and aliases
- links or relative paths back to originals

When updating root indexes:

- Update the main source index when adding a new topic, folder, material group, major count, or reading route.
- Update the keyword index when new concepts, terminology, abbreviations, or aliases appear.
- Update the topic map when the topic hierarchy or cross-topic relationships change.

## Context Safety

- Do not open hundreds of images in one pass.
- Do not paste long OCR dumps, huge file lists, or repetitive per-image notes into the chat.
- Prefer writing structured local notes and then reporting a short summary.
- If the session is already long or remote compact has failed recently, finish the current batch, write progress to disk, and continue in a new thread if needed.

## Rule Improvement

- If a better workflow, compression setting, batching strategy, indexing structure, or context-safety practice becomes apparent while using this skill, tell the user and ask whether to update the skill rules.
- Do not silently change the skill's rules or scripts unless the user explicitly asks for the update.
- When suggesting an update, explain the concrete benefit in one or two sentences and keep the proposed rule change small.

## Script

`scripts/sync_compressed_images.py` synchronizes source images into the compressed directory. It uses macOS `sips` when available and falls back to Pillow when installed. It reports created, skipped, and failed files, and writes failures to `_compression_failed_files.txt` inside the compressed directory.
