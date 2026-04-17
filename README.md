# Nanobanana Paper Figure Skill

A Claude Code skill for generating publication-quality CS paper figures using Google Gemini's image generation API.

Forked from [muxi-tk/nanobanana-image-generation](https://github.com/muxi-tk/nanobanana-image-generation) — the original skill provides general-purpose Gemini image generation and materials-science figure support. This fork adds a CS paper figure layer on top.

## What's New (vs upstream)

- **CS paper figure templates** — `--cs-paper-figure` flag with built-in types: `method-overview`, `pipeline`, `architecture`, `mechanism`, `teaser`, `comparison-schematic`
- **Venue-aware prompt styling** — `--venue` flag for NeurIPS, ICML, ICLR, CVPR, ICCV, ECCV, ACL, EMNLP, SIGGRAPH, each with tuned style notes (e.g. NeurIPS: minimalist diagrammatic; CVPR: strong visual hierarchy)
- **CS prompt builder** — `scripts/build_cs_paper_figure_prompt.py` generates structured prompts locally without API calls, following a semantic entity → color mapping → reading order workflow
- **CS figure workflow guide** — `references/cs-paper-figure-workflow.md` covers mode selection (image vs plot), prompt patterns for common figure types, venue style notes, and a human review checklist
- **CS prompt template library** — `references/cs-paper-figure-templates.json` with executable prompt templates per figure type × venue

## Inherited Features (from upstream)

- **Image mode** — Gemini-based generation and editing via `generateContent` API
- **Plot mode** — Exact publication-style bar charts, trend curves, heatmaps, scatter plots from numeric data
- **Reference image support** — `--input-image` (repeatable) for style-matched generation or editing
- **Materials-science shortcuts** — Graphical abstracts, mechanism figures, device architectures, processing workflows

## Quick Start

```bash
export NANOBANANA_API_KEY="your-gemini-api-key"
export NANOBANANA_BASE_URL="https://generativelanguage.googleapis.com"

# Generate a NeurIPS method overview figure
python3 scripts/generate_image.py \
  --cs-paper-figure method-overview \
  --venue neurips \
  "Two-stage pipeline: encoder extracts features, decoder produces predictions."

# Generate a CVPR architecture diagram with a reference image
python3 scripts/generate_image.py \
  --cs-paper-figure architecture \
  --venue cvpr \
  --input-image ref_style.png \
  "Backbone extracts multi-scale features, cross-modal alignment fuses text, head outputs masks."

# Build a prompt locally (no API call)
python3 scripts/build_cs_paper_figure_prompt.py \
  --cs-paper-figure architecture --venue cvpr --lang en \
  "Backbone extracts features, FPN aligns scales, head outputs masks."

# Render an exact plot from a JSON spec
python3 scripts/plot_publication_figure.py spec.json
```

## Layout

```
SKILL.md              # Skill entry point and workflow
scripts/
  generate_image.py                     # Primary image generation CLI
  generate_image.js                     # Node.js parity CLI
  build_cs_paper_figure_prompt.py       # CS prompt builder (new)
  build_materials_figure_prompt.py      # Materials-science prompt builder
  build_plot_spec.py                    # Concise request → full plot spec
  plot_publication_figure.py            # Exact plot renderer
references/
  cs-paper-figure-templates.json        # CS prompt templates (new)
  cs-paper-figure-workflow.md           # CS figure workflow guide (new)
  materials-science-figure-template.md  # Materials-science templates
  publication-chart-patterns.md         # Chart and multi-panel patterns
  publication-plot-api.md               # Plotting API reference
  natural-language-plot-workflow.md     # NL → plot spec workflow
agents/               # Skill-side agent config
```

## Branches

- `main` — Core image generation + CS paper figure support (stable)
- `dev` — Experimental raster-to-SVG vectorization pipeline (dewatermark → upscale → background removal → vectorization)

## Attribution

Based on [muxi-tk/nanobanana-image-generation](https://github.com/muxi-tk/nanobanana-image-generation).

## License

MIT
