---
name: image-knowledge-base
description: Maintain a local image-heavy knowledge base without overloading context. Use automatically when the user asks in natural language to update a knowledge base, organize a new image folder, scan new materials, update indexes, summarize image collections, make a contact sheet/collage overview, create a light index, compress images before analysis, process many images in batches, or avoid large-context failures while working with image collections. Also use for Chinese requests such as 整理知识库, 整理新增文件夹, 扫描新增资料, 更新索引, 整理图片, 看新增图片, 先压缩图片, 同步压缩版, 补充资料索引, 做拼图总览, or 轻量索引. The user should not need to name this skill or provide a full invocation prompt.
---

# Image Knowledge Base

Use this skill for local knowledge bases where images are primary source material and Markdown indexes make retrieval practical. The default mode is **low-context, folder-by-folder indexing**.

Users do not need to name this skill. Treat requests such as "update my knowledge base", "organize the new image folder", "compress images first", "make a collage overview", "process these images in batches", "更新知识库", "整理新增文件夹", "图片先压缩一下", "做个拼图", "先知道大概就行", or "别一次处理太多图片" as triggers.

## Default Workflow

1. Read the root usage-rules file first when it exists, such as `知识库使用规则.md`, `README.md`, or `INDEX.md`.
2. Treat compressed-preview folders as derived directories. Exclude `_compressed_2048_q95` and `_压缩版_2048_q95` from original-source scans.
3. First identify target folders and whether each already has a local index such as `资料索引.md`, `index.md`, or `README.md`; process folders one at a time.
4. For each folder, count files and determine file range, dimensions, and dates with shell/Python metadata. Do not open many images.
5. Prefer making a contact sheet/collage overview first when a collage tool exists in the knowledge base, such as `工具/拼图工具/拼图.sh`.
6. Open the collage plus only a few key originals: usually cover, table of contents, section divider, and final/action page.
7. Write or update the nearest local index with a light overview: scope, count, file range, rough sections, quick lookup, keywords, and follow-up rules.
8. Update parent indexes and root indexes only when folder structure, topic map, keywords, global entry points, counts, or moved paths changed.
9. After index updates, verify Markdown links in touched root/parent indexes and report a compact summary.

## Two Update Modes

Default to **Light Mode** unless the user asks for detailed analysis.

### Light Mode

- Goal: know the folder roughly and make it retrievable.
- Use collage overview + 3-6 key pages.
- Do not produce per-image notes.
- Do not OCR or summarize every page.
- Create/update the nearest local index first, then parent/root entries.

### Detail Mode

- Use only when the user asks for detailed content, page-level notes, exact conclusions, OCR, or a full read.
- Process images in batches of 10-20.
- Update the nearest local index after each batch.
- Stop after each meaningful batch if context is getting long.

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

## Folder Discovery Rules

- When the user says "update the knowledge base" broadly, first list new or unindexed folders, then handle them one by one.
- If the user gives a path, update that folder first and avoid scanning unrelated folders deeply.
- If a folder has a nonstandard index name, create a standard local index as the primary entry and link to the old detailed index.
- If files were moved, check the main source index, keyword index, topic map, and relevant parent indexes for stale absolute links.

## Indexing Rules

For each image folder, prefer a concise index with:

- folder purpose and source scope
- image count, file range, and update date
- collage overview link when available
- rough section summaries by file range
- key images or ranges worth opening
- retrieval keywords in relevant languages, abbreviations, and aliases
- links or relative paths back to originals

When updating root indexes:

- Update the main source index when adding a new topic, folder, material group, major count, or reading route.
- Update the keyword index when new concepts, terminology, abbreviations, or aliases appear.
- Update the topic map when the topic hierarchy or cross-topic relationships change.

## Context Safety

- Do not open hundreds of images in one pass.
- Do not open every image just to create a first-pass index.
- Prefer collage/contact-sheet over individual image inspection.
- Do not paste long OCR dumps, huge file lists, or repetitive per-image notes into the chat.
- Prefer writing structured local notes and then reporting a short summary.
- If the session is already long or remote compact has failed recently, finish the current batch, write progress to disk, and continue in a new thread if needed.

## Link Verification

After moving folders or updating global indexes, verify absolute Markdown links. A small Python check is acceptable:

```bash
python3 - <<'PY'
from pathlib import Path
import re, urllib.parse
root = Path.cwd()
bad = []
for file in root.rglob('*.md'):
    if '_compressed_2048_q95' in file.parts or '_压缩版_2048_q95' in file.parts:
        continue
    text = file.read_text(encoding='utf-8', errors='replace')
    for m in re.finditer(r'\[[^\]]*\]\((/[^)]+)\)', text):
        raw = m.group(1)
        if str(root) in raw and not Path(urllib.parse.unquote(raw)).exists():
            bad.append((file.relative_to(root), raw))
print('bad links:', len(bad))
for item in bad[:80]:
    print(item[0], '=>', item[1])
PY
```

## Rule Improvement

- If a better workflow, compression setting, batching strategy, indexing structure, or context-safety practice becomes apparent while using this skill, tell the user and ask whether to update the skill rules.
- Do not silently change the skill's rules or scripts unless the user explicitly asks for the update.
- When suggesting an update, explain the concrete benefit in one or two sentences and keep the proposed rule change small.

## Script

`scripts/sync_compressed_images.py` synchronizes source images into the compressed directory. It uses macOS `sips` when available and falls back to Pillow when installed. It reports created, skipped, and failed files, and writes failures to `_compression_failed_files.txt` inside the compressed directory.
