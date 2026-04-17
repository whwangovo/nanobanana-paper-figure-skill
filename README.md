[English](README.md) | [中文](README_zh.md)

# Paper Figure Skill

A Claude Code skill for generating publication-quality CS paper figures using Gemini or OpenAI GPT-Image APIs.

Forked from [muxi-tk/nanobanana-image-generation](https://github.com/muxi-tk/nanobanana-image-generation) — the original skill provides general-purpose Gemini image generation and materials-science figure support. This fork adds a CS paper figure layer and multi-backend support.

## What's New (vs upstream)

- **Dual backend** — `--backend gemini|openai` to choose between Gemini and OpenAI GPT-Image (`gpt-image-1.5`)
- **CS paper figure templates** — `--cs-paper-figure` with types: `method-overview`, `pipeline`, `architecture`, `mechanism`, `teaser`, `comparison-schematic`
- **Venue-aware prompt styling** — `--venue` for NeurIPS, ICML, ICLR, CVPR, ICCV, ECCV, ACL, EMNLP, SIGGRAPH
- **CS prompt builder** — `scripts/build_cs_paper_figure_prompt.py` generates structured prompts locally without API calls
- **CS figure workflow guide** — `references/cs-paper-figure-workflow.md` covers mode selection, prompt patterns, and review checklist

## Inherited Features (from upstream)

- **Image mode** — Gemini-based generation and editing via `generateContent` API
- **Plot mode** — Exact publication-style bar charts, trend curves, heatmaps, scatter plots from numeric data
- **Reference image support** — `--input-image` (repeatable) for style-matched generation or editing (Gemini only)
- **Materials-science shortcuts** — Graphical abstracts, mechanism figures, device architectures, processing workflows

## Quick Start

### Gemini Backend (default)

```bash
export NANOBANANA_API_KEY="your-gemini-api-key"
export NANOBANANA_BASE_URL="https://generativelanguage.googleapis.com"

python3 scripts/generate_image.py \
  --cs-paper-figure method-overview \
  --venue neurips \
  "Two-stage pipeline: encoder extracts features, decoder produces predictions."
```

### OpenAI Backend

```bash
export OPENAI_API_KEY="your-openai-key"

python3 scripts/generate_image.py --backend openai \
  --cs-paper-figure architecture \
  --venue cvpr \
  --quality high \
  "ViT architecture with patch embedding, transformer encoder, and classification head."
```

### Other Examples

```bash
# Build a prompt locally (no API call, no backend needed)
python3 scripts/build_cs_paper_figure_prompt.py \
  --cs-paper-figure architecture --venue cvpr --lang en \
  "Backbone extracts features, FPN aligns scales, head outputs masks."

# Render an exact plot from a JSON spec
python3 scripts/plot_publication_figure.py spec.json

# Edit an image with Gemini
python3 scripts/generate_image.py \
  --input-image ref_style.png \
  "Replace the English labels with Chinese. Keep everything else the same."
```

## Backend Comparison

| Feature | Gemini | OpenAI GPT-Image |
|---|---|---|
| Generation | Yes | Yes |
| Editing (`--input-image`) | Yes | Not yet |
| Quality control | `--image-size` | `--quality low/medium/high` |
| Transparent background | No | `--background transparent` |
| Output format | PNG (default) | `--output-format png/jpeg/webp` |
| Text output alongside image | Yes | Only `revised_prompt` |

## Layout

```
SKILL.md                                        # Skill entry point and workflow
scripts/
  generate_image.py                             # Primary image CLI (Gemini + OpenAI)
  generate_image.js                             # Node.js parity CLI
  build_cs_paper_figure_prompt.py               # CS prompt builder
  build_materials_figure_prompt.py              # Materials-science prompt builder
  build_plot_spec.py                            # Concise request → full plot spec
  plot_publication_figure.py                    # Exact plot renderer
references/
  api-reference.md                              # Gemini API contract
  openai-api-reference.md                       # OpenAI API contract
  cs-paper-figure-templates.json                # CS prompt templates
  cs-paper-figure-workflow.md                   # CS figure workflow guide
  materials-science-figure-templates.json       # Materials-science templates
  publication-chart-patterns.md                 # Chart and multi-panel patterns
  publication-plot-api.md                       # Plotting API reference
  natural-language-plot-workflow.md              # NL → plot spec workflow
agents/                                         # Skill-side agent config
```

## Branches

- `main` — Core image generation + CS paper figure support + dual backend (stable)
- `dev` — Experimental raster-to-SVG vectorization pipeline

## Attribution

Based on [muxi-tk/nanobanana-image-generation](https://github.com/muxi-tk/nanobanana-image-generation).

## License

MIT
