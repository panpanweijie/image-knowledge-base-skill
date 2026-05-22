---
name: drive-sync-auditor
description: Compare a local knowledge base with a Google Drive copy or desktop-synced Drive folder, then report or package only local files missing from Drive. Use when the user asks to sync local and Drive knowledge bases, compare local vs cloud folders, make a Drive sync package, or safely fill Drive gaps without overwriting existing Drive files.
---

# Drive Sync Auditor

Use this skill to compare a local knowledge base against its Google Drive copy. Default behavior is **audit first, then only add missing items**.

## Workflow

1. Identify the local knowledge-base root and the Drive target root.
2. Prefer the Google Drive connector for discovery and the local Google Drive desktop folder for bulk file writes when writable.
3. Exclude `.DS_Store`, AppleDouble files (`._*`), compressed-preview folders such as `_压缩版_2048_q95` and `_compressed_2048_q95`, and skipped folders from local rules such as `其他`.
4. Build three lists: missing directories, missing files, and Drive-only extras. Never delete Drive-only extras by default.
5. If the Drive desktop folder is writable, copy only missing local files and create parent folders as needed. Do not overwrite existing files.
6. If the Drive desktop folder is not writable or connector upload cannot preserve folders, create a local sync package with the missing files and a manifest.
7. Verify by re-running the comparison and report counts plus the package path or copied count.

## Safety Rules

- Never delete, rename, or overwrite Drive files unless the user explicitly asks.
- Treat Drive as possibly newer when a path exists in both places; do not replace it during gap-fill sync.
- Keep directory structure exactly relative to the knowledge-base root.
- For large gaps, package first and report size/count before suggesting manual drag-and-drop.

## Script

Run from any directory:

```bash
python image-knowledge-base-skill/drive-sync-auditor/scripts/drive_diff_package.py \
  --local /path/to/local/知识库 \
  --drive /path/to/GoogleDrive/我的云端硬盘/知识库
```

Useful modes:

```bash
python image-knowledge-base-skill/drive-sync-auditor/scripts/drive_diff_package.py --local ... --drive ... --dry-run
python image-knowledge-base-skill/drive-sync-auditor/scripts/drive_diff_package.py --local ... --drive ... --copy-missing
python image-knowledge-base-skill/drive-sync-auditor/scripts/drive_diff_package.py --local ... --drive ... --package-only
```
