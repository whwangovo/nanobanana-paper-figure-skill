# Handoff

## Current State

- Repo path: `/Users/kiren/work/project/nanobanana-paper-figure-skill`
- Git status at handoff time: clean
- Current HEAD: `637447b` `Initial skill snapshot`
- This repo is now the single maintenance source for the skill

Installed skill paths now point here via symlink:

- `/Users/kiren/.claude/skills/nanobanana-image-generation`
- `/Users/kiren/.agents/skills/nanobanana-image-generation`

Backup copies of the old installed directories were preserved here:

- `/Users/kiren/.claude/skills/nanobanana-image-generation.backup-20260417-163638`
- `/Users/kiren/.agents/skills/nanobanana-image-generation.backup-20260417-163638`

## What Was Changed

### OpenAI GPT-Image Backend (2026-04-17)

Added OpenAI GPT-Image (`gpt-image-1.5`) as a second backend alongside Gemini. The script was refactored with a backend abstraction layer.

Key changes:
- `scripts/generate_image.py` refactored: Gemini-specific code extracted into `gemini_request()` / `gemini_parse_response()`, new `openai_request()` / `openai_parse_response()` added, unified `save_parts()` accepts backend-agnostic format
- New `--backend gemini|openai` flag (default: gemini, env var: `PAPER_FIGURE_BACKEND`)
- New OpenAI-specific flags: `--quality`, `--output-format`, `--background`
- New `references/openai-api-reference.md` documenting the OpenAI Images API contract
- `SKILL.md` updated with dual-backend docs, OpenAI env vars, and examples
- `agents/openai.yaml` updated with new description

OpenAI editing (`--input-image` with `--backend openai`) is not yet implemented. Use Gemini for editing.

### CS Paper Figure Support (initial)

The repo was created from the installed `.claude` copy of the skill and then turned into the live source by symlinking both installed locations back to this repo.

The main functional change already present in this repo is that CS paper figure support is now wired into the executable `image` flow rather than existing only as documentation.

That means:

- `scripts/generate_image.py` supports `--cs-paper-figure` and `--venue`
- `scripts/generate_image.js` supports the same CS shortcut path
- `scripts/build_cs_paper_figure_prompt.py` can build CS prompts locally without hitting the API
- `references/cs-paper-figure-templates.json` is the new CS template source
- `references/cs-paper-figure-workflow.md` is the operator-facing CS usage guide

## File Map

- `SKILL.md`: skill entry, workflow, options, examples
- `scripts/generate_image.py`: primary Python image CLI
- `scripts/generate_image.js`: Node parity CLI
- `scripts/build_cs_paper_figure_prompt.py`: local CS prompt builder
- `scripts/build_materials_figure_prompt.py`: local materials-science prompt builder
- `scripts/build_plot_spec.py`: concise plot request -> full plot spec
- `scripts/plot_publication_figure.py`: exact plot renderer
- `references/cs-paper-figure-templates.json`: executable CS prompt templates
- `references/cs-paper-figure-workflow.md`: CS paper figure guidance

## Verified Commands

These were run successfully in this repo:

```bash
python3 -m py_compile scripts/*.py
node --check scripts/generate_image.js

# Gemini backend (default, backward compatible)
python3 scripts/build_cs_paper_figure_prompt.py \
  --cs-paper-figure method-overview \
  --venue neurips \
  --lang en \
  "Video frames are encoded, memory retrieves relevant history, and the decoder predicts temporally consistent masks."

python3 scripts/generate_image.py \
  --print-prompt \
  --cs-paper-figure architecture \
  --venue cvpr \
  --lang en \
  "Image input goes through a backbone, multi-scale features are aligned with text, temporal memory stabilizes predictions, and the head outputs segmentation masks."

# OpenAI backend (print-prompt only, no API call)
python3 scripts/generate_image.py \
  --print-prompt --backend openai \
  --cs-paper-figure architecture \
  --venue cvpr \
  --lang en \
  "ViT architecture with patch embedding, transformer encoder, and classification head."
```

## Working Rules

- Use `image` mode for conceptual figures, method overviews, architectures, teasers, and schematics.
- Use `plot` mode for exact quantitative figures.
- Choose backend with `--backend gemini|openai`. Default is `gemini`.
- `--venue` is only valid together with `--cs-paper-figure`.
- Do not use both `--materials-figure` and `--cs-paper-figure` together.
- `--quality`, `--output-format`, `--background` are OpenAI-only; ignored by Gemini backend.
- `--input-image` editing is only supported with Gemini backend for now.

## Recommended Next Steps

1. Add lightweight regression tests for prompt resolution.
2. Decide whether this repo should keep the old skill name `nanobanana-image-generation` or be renamed more explicitly around paper figures.
3. Add a remote if you want this maintained on GitHub.
4. If you want repeatable installs elsewhere, add a small sync or install script later.

## Quick Start

```bash
cd /Users/kiren/work/project/nanobanana-paper-figure-skill
git status
python3 scripts/generate_image.py --help
```
