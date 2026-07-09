"""Measure Excalidraw-style text bounds using the skill's render environment.

Usage:
    uv run python measure_text_bounds.py --text "Process" --font-family 3 --font-size 16
    printf 'line one\nline two\n' | uv run python measure_text_bounds.py --stdin --font-family 3 --font-size 16
"""

from __future__ import annotations

import argparse
import json
import sys

from geometry import FONT_FAMILIES, measure_text_block


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure Excalidraw-style text bounds")
    text_group = parser.add_mutually_exclusive_group(required=True)
    text_group.add_argument("--text", help="Text to measure")
    text_group.add_argument("--stdin", action="store_true", help="Read text from stdin")
    parser.add_argument(
        "--font-family",
        type=int,
        required=True,
        choices=sorted(FONT_FAMILIES),
        help="Excalidraw font family code",
    )
    parser.add_argument("--font-size", type=int, required=True, help="Font size in pixels")
    parser.add_argument("--padding-x", type=int, default=12, help="Horizontal container padding")
    parser.add_argument("--padding-y", type=int, default=12, help="Vertical container padding")
    parser.add_argument(
        "--heuristic",
        action="store_true",
        help="Use the fast heuristic instead of exact Playwright measurement",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = sys.stdin.read() if args.stdin else args.text
    result = measure_text_block(
        text=text,
        font_family=args.font_family,
        font_size=args.font_size,
        padding_x=args.padding_x,
        padding_y=args.padding_y,
        exact=not args.heuristic,
    )
    print(
        json.dumps(
            {
                "text": result.text,
                "fontFamilyCode": result.font_family_code,
                "resolvedFontFamily": result.resolved_font_family,
                "fontSize": result.font_size,
                "lineHeight": result.line_height,
                "textWidth": result.text_width,
                "textHeight": result.text_height,
                "reqWidth": result.required_width,
                "reqHeight": result.required_height,
            }
        )
    )


if __name__ == "__main__":
    main()
