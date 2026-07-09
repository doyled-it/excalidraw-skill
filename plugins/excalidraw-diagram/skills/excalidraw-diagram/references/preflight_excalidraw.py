"""Preflight geometry checks for Excalidraw JSON files.

This catches deterministic issues before the render loop:
- text that cannot fit inside its container
- text that overlaps foreign elements, dividers, or other text
- overlapping non-arrow elements
- arrow binding and routing problems that often survive visual spot checks
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from geometry import analyze_excalidraw


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight geometry checks for Excalidraw files")
    parser.add_argument("input", type=Path, help="Path to .excalidraw file")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of human-readable output")
    parser.add_argument(
        "--fail-on-issues",
        action="store_true",
        help="Exit non-zero when overflows or overlaps are found",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.input.read_text(encoding="utf-8"))
    report = analyze_excalidraw(data.get("elements", []))
    issue_count = (
        len(report["text_overflows"])
        + len(report.get("text_collisions", []))
        + len(report.get("zone_issues", []))
        + len(report["overlaps"])
        + len(report["arrow_issues"])
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"text_overflows={len(report['text_overflows'])}")
        for item in report["text_overflows"]:
            print(
                f"  overflow: text={item['textId']} container={item['containerId']} "
                f"text={item['textWidth']}x{item['textHeight']} "
                f"available={item['availableWidth']}x{item['availableHeight']}"
            )

        print(f"text_collisions={len(report.get('text_collisions', []))}")
        for item in report.get("text_collisions", []):
            print(
                f"  text_collision: text={item['textId']} target={item['targetId']} "
                f"issue={item['issue']} area={item['area']} detail={item['detail']}"
            )

        print(f"zone_issues={len(report.get('zone_issues', []))}")
        for item in report.get("zone_issues", []):
            print(
                f"  zone_issue: text={item['textId']} container={item['containerId']} "
                f"issue={item['issue']} area={item['area']} detail={item['detail']}"
            )

        print(f"overlaps={len(report['overlaps'])}")
        for item in report["overlaps"]:
            print(
                f"  overlap: left={item['leftId']} right={item['rightId']} area={item['area']}"
            )

        print(f"arrow_issues={len(report['arrow_issues'])}")
        for item in report["arrow_issues"]:
            print(
                f"  arrow: id={item['arrowId']} issue={item['issue']} detail={item['detail']}"
            )

    if args.fail_on_issues and issue_count:
        sys.exit(2)


if __name__ == "__main__":
    main()
