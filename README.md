# Nanobanana Paper Figure Skill

A Claude Code skill for generating publication-quality figures using Google Gemini's image generation API.

## Features

- **Image mode** — Generate conceptual figures, method overviews, architecture diagrams, teasers, and schematics via Gemini API
- **Plot mode** — Render exact publication-style bar charts, trend curves, heatmaps, scatter plots, and multi-panel figures from numeric data
- **Reference image support** — Pass one or more `--input-image` for style-matched generation or editing
- **Venue-aware prompts** — Built-in templates for NeurIPS, ICML, ICLR, CVPR, ICCV, ECCV, ACL, EMNLP, SIGGRAPH
- **Materials-science shortcuts** — Graphical abstracts, mechanism figures, device architectures, processing workflows

## Quick Start

```bash
# Set up API credentials
export NANOBANANA_API_KEY="your-gemini-api-key"
export NANOBANANA_BASE_URL="https://generativelanguage.googleapis.com"

# Generate a CS paper figure
python3 scripts/generate_image.py \
  --cs-paper-figure method-overview \
  --venue neurips \
  "Two-stage pipeline: encoder extracts features, decoder produces predictions."

# Generate with reference images
python3 scripts/generate_image.py \
  --input-image ref_style.png \
  "Redraw this diagram in a cleaner academic style"

# Render an exact plot from a JSON spec
python3 scripts/plot_publication_figure.py spec.json

# Build a prompt locally (no API call)
python3 scripts/build_cs_paper_figure_prompt.py \
  --cs-paper-figure architecture --venue cvpr --lang en \
  "Backbone extracts features, FPN aligns scales, head outputs masks."
```

## Layout

```
SKILL.md              # Skill entry point and workflow
scripts/              # Python and Node CLIs
  generate_image.py   # Primary image generation CLI
  generate_image.js   # Node.js parity CLI
  plot_publication_figure.py   # Exact plot renderer
  build_plot_spec.py           # Concise request → full plot spec
  build_cs_paper_figure_prompt.py       # CS prompt builder
  build_materials_figure_prompt.py      # Materials-science prompt builder
references/           # Templates, APIs, and workflow docs
agents/               # Skill-side agent config
```

## Branches

- `main` — Core image generation and plotting (stable)
- `dev` — Experimental features including raster-to-SVG vectorization pipeline

## Attribution

This project is based on and continues development from [siyuliu/nanobanana-image-generation](https://github.com/siyuliu/nanobanana-image-generation), the original Nanobanana image generation skill for Claude Code.

## License

MIT
