# CS Paper Figure Workflow

Use this reference when the paper is in computer science rather than materials science.
This file is a practical overlay for NeurIPS, ICML, ICLR, CVPR, ICCV, ECCV, ACL, EMNLP, SIGGRAPH, and related venues.

## First Decision

Choose the mode based on whether the figure is conceptual or quantitative.

- Use `image` mode for:
  - method overview figures
  - pipeline diagrams
  - system architecture schematics
  - model mechanism illustrations
  - teaser figures
  - style-matched redraws of existing conceptual figures
- Use `plot` mode for:
  - bar charts
  - line charts
  - scatter plots
  - heatmaps with exact values
  - ablation figures
  - scaling curves
  - any figure where axis values or bar heights must be exact

Rule of thumb:

- `image` mode is for explanation
- `plot` mode is for evidence

## CS Image Workflow

1. Identify the figure role.
   Common roles are `overview`, `pipeline`, `architecture`, `mechanism`, `teaser`, or `comparison schematic`.
2. Write the narrative in one sentence.
   Example: `Input video frames are encoded, memory retrieves relevant history, and the decoder produces temporally consistent outputs.`
3. List the fixed semantic entities.
   Examples: `input`, `encoder`, `memory bank`, `retrieval`, `fusion`, `decoder`, `output`, `baseline`, `ours`.
4. Define the reading order.
   Usually left-to-right for pipelines and top-to-bottom for training or inference workflows.
5. Define a stable color mapping.
   Example:
   - blue for the proposed method
   - gray for shared context or background
   - red for baseline or failure mode
   - green for improvements or retrieved useful context
6. State what must not be fabricated.
   Examples:
   - no fake numbers
   - no extra modules
   - no benchmark scores
   - no text beyond short labels
7. Generate the figure in `image` mode.
8. Review the output manually and fix it by iteration or redraw.

## Recommended Figure Types

These are usually good candidates for `image` mode in CS papers.

- Method overview
- Model architecture
- Multi-stage pipeline
- Data curation workflow
- Retrieval or memory mechanism
- Training and inference comparison
- Failure taxonomy diagram
- Human-in-the-loop workflow
- Embodied agent loop
- Vision-language or multimodal interaction schematic

## Avoid Using Image Mode For

- Main results plots
- Exact improvement numbers
- Calibration curves
- Confusion matrices that must match real values
- Any figure where reviewers may interpret visual area or position as quantitative evidence

## Prompt Structure

Use this structure instead of the materials-science template.

```text
Create a clean publication-style computer science paper figure for [venue/style].
Figure type: [overview | pipeline | architecture | mechanism | teaser].
Goal: [one-sentence purpose].
Reading order: [left-to-right | top-to-bottom].
Main components: [component list].
Visual semantics:
- blue = [proposed method]
- gray = [context/shared modules]
- red = [baseline/failure/contrast]
- green = [improvement/useful signal]
Layout constraints:
- white background
- balanced multi-panel or single-panel layout
- short professional labels
- clear arrows with unambiguous direction
- no decorative textures
- vector-like clean shapes
- no tiny unreadable text
Do not add:
- fake numbers
- unsupported claims
- extra modules not listed above
- watermarks
- paragraphs of text
```

## Prompt Patterns

### Method Overview

```text
Create a clean NeurIPS-style method overview figure on a white background.
Show a left-to-right pipeline with short labels and clear arrows.
Components: input sequence, encoder, memory bank, retrieval, fusion block, decoder, output prediction.
Use blue for our method blocks, gray for shared inputs and outputs, green for retrieved helpful context, and red only for baseline comparison if needed.
Keep the composition minimal, balanced, and publication-ready. Use concise labels only. Do not include any fake metrics or benchmark numbers.
```

### CVPR Architecture Figure

```text
Create a CVPR-style architecture diagram with a white background and crisp vector-like shapes.
Show image input, backbone, multi-scale features, cross-modal alignment module, temporal memory, prediction head, and output map.
Preserve a strict left-to-right reading order.
Use blue for the proposed modules, gray for standard backbone parts, and green for beneficial aligned features.
Use short labels, frameless legends if needed, and clear directional arrows.
No decorative art, no photorealism, no fake numbers.
```

### Teaser Figure

```text
Create a paper teaser for a computer vision method in a publication style.
Use a clean multi-panel layout on a white background.
Panel 1 shows the task input, panel 2 shows the key idea or mechanism, panel 3 shows the improved output qualitatively.
Use concise labels and consistent semantic colors.
Do not include numerical claims unless they are already provided and must be redrawn exactly.
```

## Venue Style Notes

- `NeurIPS` or `ICML`: minimalist, diagrammatic, low decoration, clear panel logic
- `CVPR` or `ICCV`: strong visual hierarchy, architecture or pipeline readability, good teaser composition
- `ACL` or `EMNLP`: simpler boxes and arrows, readable text, less visual ornament
- `SIGGRAPH`: cleaner geometry and stronger visual polish are acceptable, but still avoid decorative clutter in paper figures

## Human Review Checklist

Before using the result in a paper, check all of the following.

- Every module shown exists in the method
- Arrow directions are correct
- Color meanings are consistent
- No text is misspelled
- No labels are too small to read in the paper layout
- No visual element suggests a claim the paper does not support
- No quantitative implication is accidentally encoded by size, height, or area
- The figure still reads clearly after scaling down to paper width

## Recommended Hybrid Workflow

The most reliable CS workflow is:

1. Use `image` mode to draft composition and visual direction.
2. Redraw the final figure in Figma, Illustrator, PowerPoint, SVG, or another editable format.
3. Use `plot` mode or script-based plotting for quantitative panels.
4. Assemble the final paper figure from the editable redraw plus exact plots.

## One-Line Policy

For CS papers, use `image` mode to explain the method and `plot` mode to prove the result.
