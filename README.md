# Nanobanana Paper Figure Skill

Standalone maintenance repo for the `nanobanana-image-generation` skill.

This snapshot includes:

- Gemini-compatible `image` generation and editing helpers
- exact `plot` rendering for publication figures
- materials-science prompt shortcuts
- CS paper figure prompt shortcuts for venues such as `NeurIPS`, `ICML`, `ICLR`, `CVPR`, `ICCV`, `ECCV`, `ACL`, `EMNLP`, and `SIGGRAPH`

## Layout

- `SKILL.md`: skill entry and operator-facing workflow
- `scripts/`: Python and Node CLIs
- `references/`: templates, APIs, and workflow docs
- `agents/`: skill-side agent config

## Common Commands

Print a CS figure prompt locally:

```bash
python3 scripts/build_cs_paper_figure_prompt.py \
  --cs-paper-figure architecture \
  --venue cvpr \
  --lang en \
  "Image input goes through a backbone, multi-scale features are aligned with text, temporal memory stabilizes predictions, and the head outputs segmentation masks."
```

Print the final prompt through the main image CLI:

```bash
python3 scripts/generate_image.py \
  --print-prompt \
  --cs-paper-figure method-overview \
  --venue neurips \
  "Video frames are encoded, memory retrieves relevant history, and the decoder produces temporally consistent predictions."
```

Render an exact plot:

```bash
python3 scripts/plot_publication_figure.py spec.json
```

## Maintenance Notes

- This repo was initialized from `/Users/kiren/.claude/skills/nanobanana-image-generation`.
- Both `/Users/kiren/.claude/skills/nanobanana-image-generation` and `/Users/kiren/.agents/skills/nanobanana-image-generation` are now symlinks to this repo.
- Keep `image` mode conceptual and route exact numeric figures to `plot` mode.

## Quick Validation

```bash
python3 -m py_compile scripts/*.py
node --check scripts/generate_image.js
```
