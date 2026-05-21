# Image Knowledge Base Skill

A Codex skill for maintaining image-heavy local knowledge bases without overwhelming the conversation context.

It helps Codex:

- keep original images untouched
- create lightweight compressed preview copies before analysis
- process folders one at a time
- create contact-sheet/collage overviews before opening individual images
- build light first-pass indexes without reading every page
- fall back to small detailed batches only when requested
- update local Markdown indexes
- verify moved-path Markdown links
- avoid large-context failures when working with many images

## Install

Copy the skill folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R image-knowledge-base ~/.codex/skills/
```

Restart Codex after installing.

## Usage

You do not need to invoke the skill with a rigid prompt. Natural requests such as these should trigger it:

- "Update my knowledge base"
- "Organize this new image folder"
- "Compress the new images first"
- "Make a collage overview"
- "Just index it roughly first"
- "Scan new materials and update the index"
- "Process these images in small batches"

## Default Behavior

The default mode is light indexing:

1. Identify target folders and existing indexes.
2. Count files and gather metadata.
3. Prefer a contact sheet/collage overview when a collage tool is available.
4. Open only a few key originals, such as cover, table of contents, section divider, and final/action page.
5. Create or update the nearest local index with scope, count, rough sections, quick lookup, keywords, and follow-up rules.
6. Update parent/root indexes only when structure, global entry points, counts, keywords, or moved paths changed.

Use detailed page-by-page batches only when the user explicitly asks for detailed analysis.

## Compression

The skill expects a local knowledge-base folder. When it finds images, it creates compressed copies in:

```text
_compressed_2048_q95
```

For Chinese knowledge bases, it also recognizes the existing derived directory name:

```text
_压缩版_2048_q95
```

Compressed copies mirror the original directory structure and use:

- max long edge: `2048px`
- format: `jpg`
- quality: `95`

Original files are never overwritten.

## Script

Run from the knowledge-base root:

```bash
python ~/.codex/skills/image-knowledge-base/scripts/sync_compressed_images.py .
```

Preview changes:

```bash
python ~/.codex/skills/image-knowledge-base/scripts/sync_compressed_images.py . --dry-run
```

Force refresh:

```bash
python ~/.codex/skills/image-knowledge-base/scripts/sync_compressed_images.py . --force
```

Use a custom compressed directory:

```bash
python ~/.codex/skills/image-knowledge-base/scripts/sync_compressed_images.py . --compressed-dir _compressed_2048_q95
```

## Notes

On macOS, the script uses `sips` when available. On other systems, install Pillow for the Python fallback:

```bash
python -m pip install pillow
```

## License

MIT
