#!/usr/bin/env python3
"""Build computer-science paper figure prompts without calling the image API."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TEMPLATE_CHOICES = (
    "method-overview",
    "pipeline",
    "architecture",
    "mechanism",
    "teaser",
    "comparison-schematic",
)
VENUE_LABELS = {
    "generic": "a top-tier computer science venue",
    "neurips": "NeurIPS",
    "icml": "ICML",
    "iclr": "ICLR",
    "cvpr": "CVPR",
    "iccv": "ICCV",
    "eccv": "ECCV",
    "acl": "ACL",
    "emnlp": "EMNLP",
    "siggraph": "SIGGRAPH",
}


def load_templates() -> dict:
    template_path = Path(__file__).resolve().parent.parent / "references" / "cs-paper-figure-templates.json"
    return json.loads(template_path.read_text(encoding="utf-8"))


def build_prompt(background: str, figure_type: str, lang: str, venue: str, style_note: str | None) -> str:
    templates = load_templates()
    try:
        prompt = templates[figure_type][lang].format(
            background=background.strip(),
            venue_label=VENUE_LABELS[venue],
        )
    except KeyError as exc:
        raise SystemExit(f"Unknown template selection: {figure_type}/{lang}/{venue}") from exc

    if style_note:
        prompt = f"{prompt}\n\nAdditional Style Requirement:\n{style_note.strip()}"
    return prompt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a computer-science paper figure prompt.")
    parser.add_argument("background", nargs="?", help="Paper or method context text.")
    parser.add_argument("--background-file", help="Read paper or method context from a text or markdown file.")
    parser.add_argument(
        "--cs-paper-figure",
        required=True,
        choices=TEMPLATE_CHOICES,
        help="Built-in computer-science paper figure subtype.",
    )
    parser.add_argument("--lang", choices=("en", "zh"), default="en", help="Template output language.")
    parser.add_argument(
        "--venue",
        choices=tuple(VENUE_LABELS.keys()),
        default="generic",
        help="Computer-science venue style.",
    )
    parser.add_argument("--style-note", help="Optional extra style requirement appended after the template.")
    return parser.parse_args()


def resolve_background(args: argparse.Namespace) -> str:
    if args.background_file:
        path = Path(args.background_file)
        if not path.is_file():
            raise SystemExit(f"Background file not found: {path}")
        return path.read_text(encoding="utf-8")
    if args.background:
        return args.background
    raise SystemExit("Provide paper context as an argument or via --background-file.")


def main() -> int:
    args = parse_args()
    sys.stdout.write(build_prompt(resolve_background(args), args.cs_paper_figure, args.lang, args.venue, args.style_note))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
