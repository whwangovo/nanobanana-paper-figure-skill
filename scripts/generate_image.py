#!/usr/bin/env python3
"""Generate or edit images with Gemini or OpenAI image APIs."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GEMINI_OFFICIAL_BASE_URL = "https://generativelanguage.googleapis.com"
GEMINI_OFFICIAL_HOSTNAME = "generativelanguage.googleapis.com"
GEMINI_DEFAULT_MODEL = "gemini-3.1-flash-image-preview"

OPENAI_DEFAULT_BASE_URL = "https://api.openai.com"
OPENAI_DEFAULT_MODEL = "gpt-image-1.5"

DEFAULT_TIMEOUT = 120

CS_VENUE_LABELS = {
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

ASPECT_RATIO_TO_OPENAI_SIZE = {
    "1:1": "1024x1024",
    "3:2": "1536x1024",
    "2:3": "1024x1536",
    "16:9": "1536x1024",
    "9:16": "1024x1536",
    "21:9": "1536x1024",
}


# ---------------------------------------------------------------------------
# Template loaders (shared)
# ---------------------------------------------------------------------------

def load_materials_figure_templates() -> dict:
    template_path = Path(__file__).resolve().parent.parent / "references" / "materials-science-figure-templates.json"
    return json.loads(template_path.read_text(encoding="utf-8"))


def load_cs_paper_figure_templates() -> dict:
    template_path = Path(__file__).resolve().parent.parent / "references" / "cs-paper-figure-templates.json"
    return json.loads(template_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Argument parsing (shared)
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate or edit images with Gemini or OpenAI.")
    parser.add_argument("prompt", nargs="?", help="Prompt text or scientific background for shortcut modes.")
    parser.add_argument(
        "--prompt-file",
        help="Read prompt text or scientific background from a text or markdown file.",
    )

    # Backend selection
    parser.add_argument(
        "--backend",
        choices=("gemini", "openai"),
        default=None,
        help="Image generation backend. Default: gemini. Override with PAPER_FIGURE_BACKEND env var.",
    )

    # Shortcut modes
    shortcut_group = parser.add_mutually_exclusive_group()
    shortcut_group.add_argument(
        "--materials-figure",
        choices=tuple(load_materials_figure_templates().keys()),
        help="Use a built-in materials-science figure template.",
    )
    shortcut_group.add_argument(
        "--cs-paper-figure",
        choices=tuple(load_cs_paper_figure_templates().keys()),
        help="Use a built-in computer-science paper figure template.",
    )
    parser.add_argument(
        "--lang",
        choices=("en", "zh"),
        default="en",
        help="Template output language for shortcut modes.",
    )
    parser.add_argument(
        "--venue",
        choices=tuple(CS_VENUE_LABELS.keys()),
        default="generic",
        help="Computer-science venue style used by --cs-paper-figure.",
    )
    parser.add_argument(
        "--style-note",
        help="Optional extra style constraint appended after a shortcut template.",
    )

    # Input images (for editing)
    parser.add_argument(
        "--input-image",
        action="append",
        default=[],
        help="Path to an input image for editing or reference. May be repeated.",
    )

    # Gemini-specific options
    parser.add_argument("--base-url", help="Gemini base URL. Default from NANOBANANA_BASE_URL.")
    parser.add_argument("--model", help="Model name. Default from env or built-in default.")
    parser.add_argument("--api-key", help="API key. Default from env.")
    parser.add_argument("--aspect-ratio", help="Aspect ratio (e.g. 1:1, 16:9).")
    parser.add_argument("--image-size", help="Gemini image size (512, 1K, 2K, 4K).")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--allow-third-party",
        action="store_true",
        help="Allow non-official Gemini endpoints.",
    )

    # OpenAI-specific options
    parser.add_argument(
        "--quality",
        choices=("low", "medium", "high", "auto"),
        default="high",
        help="Image quality (OpenAI only). Default: high.",
    )
    parser.add_argument(
        "--output-format",
        choices=("png", "jpeg", "webp"),
        default="png",
        help="Output image format (OpenAI only). Default: png.",
    )
    parser.add_argument(
        "--background",
        choices=("transparent", "opaque"),
        default="opaque",
        help="Background type (OpenAI only). Default: opaque.",
    )

    # Output
    parser.add_argument("--out-dir", default="output", help="Output directory.")
    parser.add_argument("--prefix", default="gen", help="Output filename prefix.")
    parser.add_argument(
        "--print-prompt",
        action="store_true",
        help="Print the resolved prompt and exit without calling the API.",
    )

    return parser


# ---------------------------------------------------------------------------
# Prompt resolution (shared — backend-agnostic)
# ---------------------------------------------------------------------------

def resolve_prompt(args: argparse.Namespace) -> str:
    if args.materials_figure:
        templates = load_materials_figure_templates()
        template_text = templates[args.materials_figure][args.lang]
        background = _read_background(args)
        prompt = template_text.replace("{background}", background)
        if args.style_note:
            prompt += f"\n\nAdditional style note: {args.style_note}"
        return prompt

    if args.cs_paper_figure:
        templates = load_cs_paper_figure_templates()
        template_text = templates[args.cs_paper_figure][args.lang]
        background = _read_background(args)
        venue_label = CS_VENUE_LABELS.get(args.venue, args.venue)
        prompt = template_text.replace("{background}", background).replace("{venue_label}", venue_label)
        if args.style_note:
            prompt += f"\n\nAdditional style note: {args.style_note}"
        return prompt

    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()

    if args.prompt:
        return args.prompt

    raise SystemExit("Provide a prompt, --prompt-file, --materials-figure, or --cs-paper-figure.")


def _read_background(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()
    if args.prompt:
        return args.prompt
    raise SystemExit("Shortcut modes require a prompt or --prompt-file for the background text.")


# ---------------------------------------------------------------------------
# Backend resolution
# ---------------------------------------------------------------------------

def resolve_backend(args: argparse.Namespace) -> str:
    if args.backend:
        return args.backend
    return os.environ.get("PAPER_FIGURE_BACKEND", "gemini")


# ---------------------------------------------------------------------------
# Gemini backend
# ---------------------------------------------------------------------------

def _gemini_resolve_api_key(args: argparse.Namespace) -> str:
    key = args.api_key or os.environ.get("NANOBANANA_API_KEY")
    if not key:
        key_file = os.environ.get("NANOBANANA_API_KEY_FILE")
        if key_file:
            key = Path(key_file).read_text(encoding="utf-8").strip()
    if not key:
        raise SystemExit(
            "Gemini backend requires an API key. Set NANOBANANA_API_KEY, "
            "NANOBANANA_API_KEY_FILE, or pass --api-key."
        )
    return key


def _gemini_resolve_base_url(args: argparse.Namespace) -> str:
    base_url = args.base_url or os.environ.get("NANOBANANA_BASE_URL")
    if not base_url:
        raise SystemExit(
            "Gemini backend requires a base URL. Set NANOBANANA_BASE_URL or pass --base-url."
        )
    return base_url.rstrip("/")


def _gemini_check_third_party(base_url: str, args: argparse.Namespace) -> None:
    hostname = urllib.parse.urlparse(base_url).hostname or ""
    if hostname == GEMINI_OFFICIAL_HOSTNAME:
        return
    allowed = args.allow_third_party or os.environ.get("NANOBANANA_ALLOW_THIRD_PARTY", "") == "1"
    if not allowed:
        raise SystemExit(
            f"Base URL {base_url!r} is not the official Gemini endpoint. "
            "Pass --allow-third-party or set NANOBANANA_ALLOW_THIRD_PARTY=1 to proceed."
        )


def gemini_request(prompt: str, args: argparse.Namespace) -> dict:
    api_key = _gemini_resolve_api_key(args)
    base_url = _gemini_resolve_base_url(args)
    _gemini_check_third_party(base_url, args)
    model = args.model or os.environ.get("NANOBANANA_MODEL", GEMINI_DEFAULT_MODEL)

    parts: list[dict[str, Any]] = [{"text": prompt}]
    for img_path in args.input_image:
        data = Path(img_path).read_bytes()
        mime = mimetypes.guess_type(img_path)[0] or "image/png"
        parts.append({"inlineData": {"mimeType": mime, "data": base64.b64encode(data).decode()}})

    body: dict[str, Any] = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }
    image_config: dict[str, str] = {}
    if args.aspect_ratio:
        image_config["aspectRatio"] = args.aspect_ratio
    if args.image_size:
        image_config["imageSize"] = args.image_size
    if image_config:
        body["generationConfig"]["imageConfig"] = image_config

    url = f"{base_url}/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json", "X-goog-api-key": api_key}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode(errors="replace")
        raise SystemExit(f"Gemini API error {exc.code}: {error_body}") from exc


def gemini_parse_response(response_json: dict) -> list[dict]:
    """Parse Gemini response into unified parts: [{type, data, mime}]."""
    try:
        parts = response_json["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError) as exc:
        raise SystemExit(f"Unexpected Gemini response: {json.dumps(response_json, ensure_ascii=False)}") from exc

    unified: list[dict] = []
    for part in parts:
        text = part.get("text")
        if text:
            unified.append({"type": "text", "data": text, "mime": "text/plain"})
            continue
        inline_data = part.get("inlineData") or part.get("inline_data")
        if inline_data:
            mime = inline_data.get("mimeType") or inline_data.get("mime_type") or "image/png"
            unified.append({"type": "image", "data": base64.b64decode(inline_data["data"]), "mime": mime})
    return unified


# ---------------------------------------------------------------------------
# OpenAI backend
# ---------------------------------------------------------------------------

def _openai_resolve_api_key(args: argparse.Namespace) -> str:
    key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        key_file = os.environ.get("OPENAI_API_KEY_FILE")
        if key_file:
            key = Path(key_file).read_text(encoding="utf-8").strip()
    if not key:
        raise SystemExit(
            "OpenAI backend requires an API key. Set OPENAI_API_KEY, "
            "OPENAI_API_KEY_FILE, or pass --api-key."
        )
    return key


def _openai_resolve_size(args: argparse.Namespace) -> str:
    if args.aspect_ratio:
        size = ASPECT_RATIO_TO_OPENAI_SIZE.get(args.aspect_ratio)
        if size:
            return size
        print(f"Warning: aspect ratio {args.aspect_ratio!r} has no OpenAI mapping, using 'auto'.", file=sys.stderr)
    return "auto"


def openai_request(prompt: str, args: argparse.Namespace) -> dict:
    api_key = _openai_resolve_api_key(args)
    base_url = (args.base_url or os.environ.get("OPENAI_BASE_URL", OPENAI_DEFAULT_BASE_URL)).rstrip("/")
    model = args.model or os.environ.get("OPENAI_IMAGE_MODEL", OPENAI_DEFAULT_MODEL)

    if args.input_image:
        raise SystemExit(
            "OpenAI image editing (--input-image) is not yet supported. "
            "Use --backend gemini for editing, or remove --input-image for generation."
        )

    body: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": _openai_resolve_size(args),
        "quality": args.quality,
        "output_format": args.output_format,
        "background": args.background,
    }

    url = f"{base_url}/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode(errors="replace")
        raise SystemExit(f"OpenAI API error {exc.code}: {error_body}") from exc


def openai_parse_response(response_json: dict, output_format: str = "png") -> list[dict]:
    """Parse OpenAI response into unified parts: [{type, data, mime}]."""
    data_list = response_json.get("data")
    if not data_list:
        raise SystemExit(f"Unexpected OpenAI response: {json.dumps(response_json, ensure_ascii=False)}")

    mime_map = {"png": "image/png", "jpeg": "image/jpeg", "webp": "image/webp"}
    mime = mime_map.get(output_format, "image/png")

    unified: list[dict] = []
    for item in data_list:
        b64 = item.get("b64_json")
        if b64:
            unified.append({"type": "image", "data": base64.b64decode(b64), "mime": mime})
        revised = item.get("revised_prompt")
        if revised:
            unified.append({"type": "text", "data": revised, "mime": "text/plain"})
    return unified


# ---------------------------------------------------------------------------
# Unified output saving (shared)
# ---------------------------------------------------------------------------

def save_parts(parts: list[dict], out_dir: Path, prefix: str) -> list[str]:
    """Save unified parts to disk. Returns list of output file paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[str] = []
    text_index = 0
    image_index = 0

    for part in parts:
        if part["type"] == "text":
            text_index += 1
            path = out_dir / f"{prefix}-text-{text_index}.txt"
            path.write_text(part["data"], encoding="utf-8")
            outputs.append(str(path))
        elif part["type"] == "image":
            image_index += 1
            extension = mimetypes.guess_extension(part["mime"]) or ".png"
            path = out_dir / f"{prefix}-{image_index}{extension}"
            path.write_bytes(part["data"])
            outputs.append(str(path))

    if not outputs:
        raise SystemExit("No text or image parts found in API response.")
    return outputs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    args = build_parser().parse_args()

    if args.print_prompt:
        print(resolve_prompt(args))
        return 0

    prompt = resolve_prompt(args)
    backend = resolve_backend(args)

    if backend == "gemini":
        response_json = gemini_request(prompt, args)
        parts = gemini_parse_response(response_json)
    elif backend == "openai":
        response_json = openai_request(prompt, args)
        parts = openai_parse_response(response_json, args.output_format)
    else:
        raise SystemExit(f"Unknown backend: {backend!r}")

    for output in save_parts(parts, Path(args.out_dir), args.prefix):
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
