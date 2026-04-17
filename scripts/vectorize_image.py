#!/usr/bin/env python3
"""Convert AI-generated raster images to editable SVG vectors.

Four-stage pipeline:
  1. dewatermark  — remove Gemini watermark (py-gemini-watermark-remover)
  2. upscale      — super-resolution to 4K (realesrgan-ncnn-vulkan)
  3. background   — remove background (rembg)
  4. vectorize    — raster to SVG (vtracer)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STEPS = ("dewatermark", "upscale", "background", "vectorize")
DEFAULT_OUTPUT_DIR = "output/vectorize"


# ── step 1: dewatermark ─────────────────────────────────────────────

def step_dewatermark(src: Path, dst: Path, *, verbose: bool = False) -> None:
    try:
        from gemini_watermark_remover import process_image
    except ImportError:
        raise SystemExit(
            "Missing dependency: py-gemini-watermark-remover\n"
            "Install with:  pip install py-gemini-watermark-remover"
        )
    if verbose:
        print(f"  dewatermark: {src} → {dst}")
    process_image(str(src), str(dst))


# ── step 2: upscale ─────────────────────────────────────────────────

def _find_realesrgan(explicit: str | None) -> str:
    if explicit:
        return explicit
    found = shutil.which("realesrgan-ncnn-vulkan")
    if found:
        return found
    raise SystemExit(
        "Missing tool: realesrgan-ncnn-vulkan\n"
        "Download from: https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan/releases\n"
        "Place the binary on $PATH or pass --realesrgan-bin <path>"
    )


def step_upscale(
    src: Path,
    dst: Path,
    *,
    factor: int = 4,
    model: str = "realesrgan-x4plus",
    realesrgan_bin: str | None = None,
    verbose: bool = False,
) -> None:
    binary = _find_realesrgan(realesrgan_bin)
    cmd = [binary, "-i", str(src), "-o", str(dst), "-s", str(factor), "-n", model]
    if verbose:
        print(f"  upscale: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"realesrgan-ncnn-vulkan failed:\n{result.stderr}")


# ── step 3: background removal ──────────────────────────────────────

def step_background(src: Path, dst: Path, *, verbose: bool = False) -> None:
    try:
        from rembg import remove
    except ImportError:
        raise SystemExit(
            "Missing dependency: rembg\n"
            'Install with:  pip install "rembg[cpu]"'
        )
    if verbose:
        print(f"  background: {src} → {dst}")
    input_bytes = src.read_bytes()
    output_bytes = remove(input_bytes)
    dst.write_bytes(output_bytes)


# ── step 4: vectorize ───────────────────────────────────────────────

def step_vectorize(
    src: Path,
    dst: Path,
    *,
    colormode: str = "color",
    mode: str = "spline",
    filter_speckle: int = 4,
    color_precision: int = 6,
    verbose: bool = False,
) -> None:
    try:
        import vtracer
    except ImportError:
        raise SystemExit(
            "Missing dependency: vtracer\n"
            "Install with:  pip install vtracer"
        )
    if verbose:
        print(f"  vectorize: {src} → {dst}")
    vtracer.convert_image_to_svg_py(
        str(src),
        str(dst),
        colormode=colormode,
        mode=mode,
        filter_speckle=filter_speckle,
        color_precision=color_precision,
    )


# ── crop helper ──────────────────────────────────────────────────────

def crop_image(src: Path, dst: Path, region: tuple[int, int, int, int]) -> None:
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit(
            "Missing dependency: Pillow (needed for --crop)\n"
            "Install with:  pip install Pillow"
        )
    x, y, w, h = region
    img = Image.open(src)
    img.crop((x, y, x + w, y + h)).save(dst)


# ── pipeline orchestration ───────────────────────────────────────────

def resolve_steps(
    skip: list[str],
    only: str | None,
    start_from: str | None,
) -> list[str]:
    if only:
        if only not in STEPS:
            raise SystemExit(f"Unknown step: {only}. Choose from {STEPS}")
        return [only]

    active = list(STEPS)
    if start_from:
        if start_from not in STEPS:
            raise SystemExit(f"Unknown step: {start_from}. Choose from {STEPS}")
        idx = active.index(start_from)
        active = active[idx:]

    return [s for s in active if s not in skip]


def run_pipeline(args: argparse.Namespace) -> int:
    src = Path(args.input)
    if not src.is_file():
        raise SystemExit(f"Input file not found: {src}")

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = src.stem

    active = resolve_steps(args.skip or [], args.only, args.start_from)

    if args.dry_run:
        print(f"Input:  {src}")
        print(f"Output: {out_dir}")
        print(f"Steps:  {' → '.join(active)}")
        return 0

    current = src

    # optional crop
    if args.crop:
        parts = [int(x) for x in args.crop.split(",")]
        if len(parts) != 4:
            raise SystemExit("--crop expects X,Y,W,H (four integers)")
        cropped = out_dir / f"{stem}-0-crop.png"
        crop_image(current, cropped, tuple(parts))
        current = cropped

    step_map = {
        "dewatermark": lambda s, d: step_dewatermark(s, d, verbose=args.verbose),
        "upscale": lambda s, d: step_upscale(
            s, d,
            factor=args.upscale_factor,
            model=args.upscale_model,
            realesrgan_bin=args.realesrgan_bin,
            verbose=args.verbose,
        ),
        "background": lambda s, d: step_background(s, d, verbose=args.verbose),
        "vectorize": lambda s, d: step_vectorize(
            s, d,
            colormode=args.vtracer_colormode,
            mode=args.vtracer_mode,
            filter_speckle=args.filter_speckle,
            color_precision=args.color_precision,
            verbose=args.verbose,
        ),
    }

    suffixes = {
        "dewatermark": ("-1-dewatermark", ".png"),
        "upscale": ("-2-upscale", ".png"),
        "background": ("-3-nobg", ".png"),
        "vectorize": ("-4-vector", ".svg"),
    }

    for step_name in active:
        tag, ext = suffixes[step_name]
        dst = out_dir / f"{stem}{tag}{ext}"
        step_map[step_name](current, dst)
        current = dst
        print(f"[{step_name}] → {dst}")

    print(f"\nDone. Final output: {current}")
    return 0


# ── CLI ──────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Convert AI-generated images to editable SVG vectors.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s gemini_output.png\n"
            "  %(prog)s logo.png --skip dewatermark upscale\n"
            "  %(prog)s logo.png --only vectorize\n"
            "  %(prog)s logo.png --crop 100,200,300,300\n"
        ),
    )
    p.add_argument("input", help="Input image path")
    p.add_argument("-o", "--output", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="Show steps without running")

    flow = p.add_argument_group("flow control")
    flow.add_argument("--skip", nargs="*", default=[], choices=STEPS, metavar="STEP",
                       help="Steps to skip")
    flow.add_argument("--only", choices=STEPS, help="Run only this step")
    flow.add_argument("--start-from", choices=STEPS, help="Start from this step")
    flow.add_argument("--crop", metavar="X,Y,W,H",
                       help="Crop region before processing (single element extraction)")

    up = p.add_argument_group("upscale options")
    up.add_argument("--upscale-factor", type=int, default=4, choices=[2, 3, 4])
    up.add_argument("--upscale-model", default="realesrgan-x4plus")
    up.add_argument("--realesrgan-bin", help="Path to realesrgan-ncnn-vulkan binary")

    vec = p.add_argument_group("vectorize options")
    vec.add_argument("--vtracer-colormode", default="color", choices=["color", "binary"])
    vec.add_argument("--vtracer-mode", default="spline", choices=["spline", "polygon", "none"])
    vec.add_argument("--filter-speckle", type=int, default=4)
    vec.add_argument("--color-precision", type=int, default=6)

    return p


def main() -> int:
    args = build_parser().parse_args()
    return run_pipeline(args)


if __name__ == "__main__":
    sys.exit(main())
