"""Deterministic geometry helpers for Excalidraw diagram generation.

This module gives diagram-generation scripts reusable primitives for:
- exact text measurement in the same Playwright/Chromium environment as rendering
- deterministic text wrapping and box sizing
- simple row/column layout helpers
- orthogonal arrow routing around rectangular obstacles
- preflight checks for text overflow and element overlap
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import json
import math
from typing import Iterable, Sequence


FONT_FAMILIES: dict[int, str] = {
    1: "Virgil, Segoe UI Emoji, Apple Color Emoji, sans-serif",
    2: "Helvetica, Arial, Segoe UI Emoji, Apple Color Emoji, sans-serif",
    3: "Cascadia Code, Cascadia Mono, Menlo, Monaco, Consolas, monospace",
}

DEFAULT_LINE_HEIGHT = 1.25
DEFAULT_PADDING_X = 12
DEFAULT_PADDING_Y = 12


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float
    id: str | None = None

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def expanded(self, padding: float) -> "Rect":
        return Rect(
            x=self.x - padding,
            y=self.y - padding,
            width=self.width + (padding * 2),
            height=self.height + (padding * 2),
            id=self.id,
        )

    def intersects(self, other: "Rect") -> bool:
        return not (
            self.right <= other.left
            or self.left >= other.right
            or self.bottom <= other.top
            or self.top >= other.bottom
        )

    def intersection_area(self, other: "Rect") -> float:
        if not self.intersects(other):
            return 0.0
        overlap_w = min(self.right, other.right) - max(self.left, other.left)
        overlap_h = min(self.bottom, other.bottom) - max(self.top, other.top)
        return max(0.0, overlap_w) * max(0.0, overlap_h)


@dataclass(frozen=True)
class TextMeasurement:
    text: str
    font_family_code: int
    resolved_font_family: str
    font_size: int
    line_height: float
    text_width: int
    text_height: int
    required_width: int
    required_height: int


@dataclass(frozen=True)
class FitResult:
    text: str
    font_size: int
    line_height: float
    text_width: int
    text_height: int
    required_width: int
    required_height: int
    fits: bool


@dataclass(frozen=True)
class TextFragment:
    text_id: str
    rect: Rect
    line_index: int


@dataclass
class InferredContainer:
    container_id: str
    rect: Rect
    owned_text_ids: set[str] = field(default_factory=set)
    divider_id: str | None = None
    divider_rect: Rect | None = None


def _load_sync_playwright():
    from playwright.sync_api import sync_playwright  # type: ignore

    return sync_playwright


def _normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


@lru_cache(maxsize=2048)
def _measure_exact_cached(
    text: str,
    font_family: int,
    font_size: int,
    line_height: float,
) -> tuple[int, int, float, str]:
    sync_playwright = _load_sync_playwright()

    css_font_family = FONT_FAMILIES[font_family]
    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      background: #ffffff;
    }}
    #measure {{
      position: absolute;
      left: 0;
      top: 0;
      display: inline-block;
      white-space: pre;
      font-family: {css_font_family};
      font-size: {font_size}px;
      line-height: {line_height};
      font-weight: 400;
      letter-spacing: 0;
      color: #000000;
    }}
  </style>
</head>
<body>
  <div id="measure"></div>
  <script>
    document.getElementById("measure").textContent = {json.dumps(text)};
  </script>
</body>
</html>
"""

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 4096, "height": 4096},
            device_scale_factor=1,
        )
        page.set_content(html)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_function("document.fonts && document.fonts.status !== 'loading'")
        measurement = page.evaluate(
            """
() => {
  const element = document.getElementById("measure");
  const rect = element.getBoundingClientRect();
  const style = window.getComputedStyle(element);
  return {
    width: rect.width,
    height: rect.height,
    lineHeight: parseFloat(style.lineHeight),
    fontFamily: style.fontFamily,
  };
}
"""
        )
        browser.close()

    return (
        math.ceil(measurement["width"]),
        math.ceil(measurement["height"]),
        measurement["lineHeight"],
        measurement["fontFamily"],
    )


def _measure_heuristic(
    text: str,
    font_family: int,
    font_size: int,
    line_height: float,
) -> tuple[int, int, float, str]:
    lines = _normalize_text(text).split("\n")
    multiplier = 0.62 if font_family == 3 else 0.56
    width = math.ceil(max((len(line) for line in lines), default=0) * font_size * multiplier)
    height = math.ceil(len(lines) * font_size * line_height)
    return width, height, font_size * line_height, FONT_FAMILIES[font_family]


def measure_text_block(
    text: str,
    font_family: int,
    font_size: int,
    *,
    line_height: float = DEFAULT_LINE_HEIGHT,
    padding_x: int = DEFAULT_PADDING_X,
    padding_y: int = DEFAULT_PADDING_Y,
    exact: bool = True,
) -> TextMeasurement:
    normalized = _normalize_text(text)
    try:
        if exact:
            text_width, text_height, resolved_line_height, resolved_font = _measure_exact_cached(
                normalized,
                font_family,
                font_size,
                line_height,
            )
        else:
            raise RuntimeError("heuristic requested")
    except Exception:
        text_width, text_height, resolved_line_height, resolved_font = _measure_heuristic(
            normalized,
            font_family,
            font_size,
            line_height,
        )

    return TextMeasurement(
        text=normalized,
        font_family_code=font_family,
        resolved_font_family=resolved_font,
        font_size=font_size,
        line_height=resolved_line_height,
        text_width=text_width,
        text_height=text_height,
        required_width=text_width + (padding_x * 2),
        required_height=text_height + (padding_y * 2),
    )


def wrap_text_to_width(
    text: str,
    *,
    max_text_width: int,
    font_family: int,
    font_size: int,
    line_height: float = DEFAULT_LINE_HEIGHT,
    exact: bool = True,
) -> str:
    normalized = _normalize_text(text)
    paragraphs = normalized.split("\n")
    wrapped_lines: list[str] = []

    def line_width(candidate: str) -> int:
        return measure_text_block(
            candidate,
            font_family,
            font_size,
            line_height=line_height,
            padding_x=0,
            padding_y=0,
            exact=exact,
        ).text_width

    def break_long_word(word: str) -> list[str]:
        pieces: list[str] = []
        current = ""
        for char in word:
            candidate = current + char
            if current and line_width(candidate) > max_text_width:
                pieces.append(current)
                current = char
            else:
                current = candidate
        if current:
            pieces.append(current)
        return pieces

    for paragraph in paragraphs:
        if paragraph == "":
            wrapped_lines.append("")
            continue

        words = paragraph.split(" ")
        current = ""
        for word in words:
            if line_width(word) > max_text_width:
                if current:
                    wrapped_lines.append(current)
                    current = ""
                wrapped_lines.extend(break_long_word(word))
                continue

            candidate = word if not current else f"{current} {word}"
            if current and line_width(candidate) > max_text_width:
                wrapped_lines.append(current)
                current = word
            else:
                current = candidate

        if current:
            wrapped_lines.append(current)

    return "\n".join(wrapped_lines)


def fit_text_to_box(
    text: str,
    *,
    font_family: int,
    font_size: int,
    max_width: int,
    max_height: int,
    min_font_size: int = 12,
    padding_x: int = DEFAULT_PADDING_X,
    padding_y: int = DEFAULT_PADDING_Y,
    line_height: float = DEFAULT_LINE_HEIGHT,
    exact: bool = True,
) -> FitResult:
    current_size = font_size
    while current_size >= min_font_size:
        wrapped = wrap_text_to_width(
            text,
            max_text_width=max_width - (padding_x * 2),
            font_family=font_family,
            font_size=current_size,
            line_height=line_height,
            exact=exact,
        )
        measurement = measure_text_block(
            wrapped,
            font_family,
            current_size,
            line_height=line_height,
            padding_x=padding_x,
            padding_y=padding_y,
            exact=exact,
        )
        if measurement.required_width <= max_width and measurement.required_height <= max_height:
            return FitResult(
                text=wrapped,
                font_size=current_size,
                line_height=measurement.line_height,
                text_width=measurement.text_width,
                text_height=measurement.text_height,
                required_width=measurement.required_width,
                required_height=measurement.required_height,
                fits=True,
            )
        current_size -= 1

    wrapped = wrap_text_to_width(
        text,
        max_text_width=max_width - (padding_x * 2),
        font_family=font_family,
        font_size=min_font_size,
        line_height=line_height,
        exact=exact,
    )
    measurement = measure_text_block(
        wrapped,
        font_family,
        min_font_size,
        line_height=line_height,
        padding_x=padding_x,
        padding_y=padding_y,
        exact=exact,
    )
    return FitResult(
        text=wrapped,
        font_size=min_font_size,
        line_height=measurement.line_height,
        text_width=measurement.text_width,
        text_height=measurement.text_height,
        required_width=measurement.required_width,
        required_height=measurement.required_height,
        fits=False,
    )


def size_container_to_text(
    text: str,
    *,
    font_family: int,
    font_size: int,
    padding_x: int = DEFAULT_PADDING_X,
    padding_y: int = DEFAULT_PADDING_Y,
    max_width: int | None = None,
    line_height: float = DEFAULT_LINE_HEIGHT,
    exact: bool = True,
) -> dict[str, object]:
    content = text
    if max_width is not None:
        content = wrap_text_to_width(
            text,
            max_text_width=max_width - (padding_x * 2),
            font_family=font_family,
            font_size=font_size,
            line_height=line_height,
            exact=exact,
        )
    measurement = measure_text_block(
        content,
        font_family,
        font_size,
        line_height=line_height,
        padding_x=padding_x,
        padding_y=padding_y,
        exact=exact,
    )
    return {
        "text": content,
        "width": measurement.required_width,
        "height": measurement.required_height,
        "text_width": measurement.text_width,
        "text_height": measurement.text_height,
        "font_size": font_size,
        "line_height": measurement.line_height,
    }


def layout_row(rects: Sequence[Rect], *, start_x: float, y: float, gap: float) -> list[Rect]:
    laid_out: list[Rect] = []
    current_x = start_x
    for rect in rects:
        laid_out.append(Rect(current_x, y, rect.width, rect.height, rect.id))
        current_x += rect.width + gap
    return laid_out


def layout_column(rects: Sequence[Rect], *, x: float, start_y: float, gap: float) -> list[Rect]:
    laid_out: list[Rect] = []
    current_y = start_y
    for rect in rects:
        laid_out.append(Rect(x, current_y, rect.width, rect.height, rect.id))
        current_y += rect.height + gap
    return laid_out


def _segment_intersects_rect(start: Point, end: Point, rect: Rect) -> bool:
    expanded = rect
    if start.x == end.x:
        x = start.x
        seg_top = min(start.y, end.y)
        seg_bottom = max(start.y, end.y)
        return expanded.left < x < expanded.right and not (
            seg_bottom <= expanded.top or seg_top >= expanded.bottom
        )
    if start.y == end.y:
        y = start.y
        seg_left = min(start.x, end.x)
        seg_right = max(start.x, end.x)
        return expanded.top < y < expanded.bottom and not (
            seg_right <= expanded.left or seg_left >= expanded.right
        )
    raise ValueError("Only orthogonal segments are supported")


def _path_clear(points: Sequence[Point], obstacles: Iterable[Rect], padding: float) -> bool:
    expanded = [rect.expanded(padding) for rect in obstacles]
    for start, end in zip(points, points[1:]):
        if start == end:
            continue
        for rect in expanded:
            if _segment_intersects_rect(start, end, rect):
                return False
    return True


def orthogonal_route(
    start: Point,
    end: Point,
    *,
    obstacles: Sequence[Rect] = (),
    padding: float = 24,
) -> list[Point]:
    direct = [start, end]
    if _path_clear(direct, obstacles, padding):
        return direct

    candidate_y = {start.y, end.y}
    candidate_x = {start.x, end.x}
    for rect in obstacles:
        candidate_y.update({rect.top - padding, rect.bottom + padding})
        candidate_x.update({rect.left - padding, rect.right + padding})

    candidates: list[list[Point]] = []
    for lane_y in sorted(candidate_y):
        candidates.append([start, Point(start.x, lane_y), Point(end.x, lane_y), end])
    for lane_x in sorted(candidate_x):
        candidates.append([start, Point(lane_x, start.y), Point(lane_x, end.y), end])

    valid = [route for route in candidates if _path_clear(route, obstacles, padding)]
    if not valid:
        return [start, Point(start.x, end.y), end]

    def route_length(route: Sequence[Point]) -> float:
        total = 0.0
        for a, b in zip(route, route[1:]):
            total += abs(a.x - b.x) + abs(a.y - b.y)
        return total

    return min(valid, key=route_length)


def _element_rect(element: dict) -> Rect | None:
    if element.get("isDeleted"):
        return None
    if element.get("type") not in {"rectangle", "ellipse", "diamond", "text"}:
        return None
    width = abs(element.get("width", 0))
    height = abs(element.get("height", 0))
    return Rect(
        x=element.get("x", 0),
        y=element.get("y", 0),
        width=width,
        height=height,
        id=element.get("id"),
    )


def _contains(container: Rect, inner: Rect, margin: float = 0.0) -> bool:
    return (
        inner.left >= container.left + margin
        and inner.right <= container.right - margin
        and inner.top >= container.top + margin
        and inner.bottom <= container.bottom - margin
    )


def _covers_most(container: Rect, inner: Rect, threshold: float = 0.95) -> bool:
    if inner.width <= 0 or inner.height <= 0:
        return False
    return (container.intersection_area(inner) / (inner.width * inner.height)) >= threshold


def _rect_area(rect: Rect) -> float:
    return rect.width * rect.height


def _measure_text_element(element: dict) -> TextMeasurement | None:
    if element.get("type") != "text":
        return None
    font_family = int(element.get("fontFamily", 3))
    font_size = int(element.get("fontSize", 16))
    line_height = float(element.get("lineHeight", DEFAULT_LINE_HEIGHT))
    return measure_text_block(
        element.get("text", ""),
        font_family,
        font_size,
        line_height=line_height,
        padding_x=0,
        padding_y=0,
        exact=True,
    )


def _text_fragments(element: dict) -> list[TextFragment]:
    if element.get("type") != "text" or element.get("isDeleted"):
        return []

    element_id = element.get("id")
    if not isinstance(element_id, str):
        return []

    measurement = _measure_text_element(element)
    if measurement is None:
        return []

    text = _normalize_text(element.get("text", ""))
    lines = text.split("\n") if text else [""]
    font_family = int(element.get("fontFamily", 3))
    font_size = int(element.get("fontSize", 16))
    line_height = float(element.get("lineHeight", DEFAULT_LINE_HEIGHT))
    text_align = element.get("textAlign", "left")
    x = float(element.get("x", 0))
    y = float(element.get("y", 0))
    available_width = float(abs(element.get("width", measurement.text_width)) or measurement.text_width)
    current_y = y

    fragments: list[TextFragment] = []
    for index, line in enumerate(lines):
        line_measure = measure_text_block(
            line,
            font_family,
            font_size,
            line_height=line_height,
            padding_x=0,
            padding_y=0,
            exact=True,
        )
        line_width = float(line_measure.text_width)
        if text_align == "center":
            line_x = x + max(0.0, (available_width - line_width) / 2)
        elif text_align == "right":
            line_x = x + max(0.0, available_width - line_width)
        else:
            line_x = x

        fragments.append(
            TextFragment(
                text_id=element_id,
                rect=Rect(
                    x=line_x,
                    y=current_y,
                    width=line_width,
                    height=float(measurement.line_height),
                    id=f"{element_id}#line{index}",
                ),
                line_index=index,
            )
        )
        current_y += float(measurement.line_height)

    return fragments


def _line_rects(element: dict, *, padding: float = 2.0) -> list[Rect]:
    if element.get("type") != "line" or element.get("isDeleted"):
        return []

    points = _arrow_points(element)
    if len(points) < 2:
        return []

    stroke = max(float(element.get("strokeWidth", 1) or 1), 1.0)
    half = (stroke / 2.0) + padding
    line_id = element.get("id")
    rects: list[Rect] = []
    for index, (start, end) in enumerate(zip(points, points[1:])):
        if start == end:
            continue
        left = min(start.x, end.x)
        right = max(start.x, end.x)
        top = min(start.y, end.y)
        bottom = max(start.y, end.y)
        if start.x == end.x:
            rect = Rect(
                x=left - half,
                y=top - padding,
                width=stroke + (padding * 2),
                height=(bottom - top) + (padding * 2),
                id=f"{line_id}#seg{index}",
            )
        elif start.y == end.y:
            rect = Rect(
                x=left - padding,
                y=top - half,
                width=(right - left) + (padding * 2),
                height=stroke + (padding * 2),
                id=f"{line_id}#seg{index}",
            )
        else:
            rect = Rect(
                x=left - half,
                y=top - half,
                width=(right - left) + (half * 2),
                height=(bottom - top) + (half * 2),
                id=f"{line_id}#seg{index}",
            )
        rects.append(rect)
    return rects


def _significant_horizontal_line_in_container(element: dict, container: Rect) -> tuple[str, Rect] | None:
    if element.get("type") != "line" or element.get("isDeleted"):
        return None
    line_id = element.get("id")
    if not isinstance(line_id, str):
        return None

    points = _arrow_points(element)
    if len(points) != 2:
        return None
    start, end = points
    if start.y != end.y:
        return None

    rects = _line_rects(element, padding=1.0)
    if not rects:
        return None
    rect = rects[0]
    line_width = abs(end.x - start.x)
    min_width = min(max(container.width * 0.45, 48.0), container.width - 8.0)
    if line_width < min_width:
        return None
    if not _contains(container.expanded(2.0), rect, margin=0):
        return None
    if not (container.top + 8.0 < rect.top and rect.bottom < container.bottom - 8.0):
        return None
    return line_id, rect


def _infer_text_ownership(
    elements: Sequence[dict],
    text_elements: dict[str, dict],
) -> tuple[dict[str, str], dict[str, InferredContainer]]:
    containers: dict[str, InferredContainer] = {}
    for element in elements:
        element_id = element.get("id")
        if not isinstance(element_id, str):
            continue
        rect = _element_rect(element)
        if rect is None:
            continue
        if element.get("type") not in {"rectangle", "ellipse", "diamond"}:
            continue
        containers[element_id] = InferredContainer(container_id=element_id, rect=rect)

    text_owner: dict[str, str] = {}
    for text_id, element in text_elements.items():
        explicit_owner = element.get("containerId")
        if isinstance(explicit_owner, str) and explicit_owner in containers:
            text_owner[text_id] = explicit_owner
            containers[explicit_owner].owned_text_ids.add(text_id)
            continue

        block_rect = _element_rect(element)
        if block_rect is None:
            continue

        candidate_ids = [
            container_id
            for container_id, container in containers.items()
            if _contains(container.rect, block_rect, margin=0) or _covers_most(container.rect, block_rect, threshold=0.90)
        ]
        if not candidate_ids:
            continue

        owner_id = min(candidate_ids, key=lambda container_id: _rect_area(containers[container_id].rect))
        text_owner[text_id] = owner_id
        containers[owner_id].owned_text_ids.add(text_id)

    for container in containers.values():
        candidates: list[tuple[float, float, str, Rect]] = []
        for element in elements:
            divider = _significant_horizontal_line_in_container(element, container.rect)
            if divider is None:
                continue
            divider_id, divider_rect = divider
            candidates.append((divider_rect.width, divider_rect.top, divider_id, divider_rect))
        if candidates:
            _, _, divider_id, divider_rect = sorted(candidates, key=lambda item: (-item[0], item[1]))[0]
            container.divider_id = divider_id
            container.divider_rect = divider_rect

    return text_owner, containers


def _arrow_points(element: dict) -> list[Point]:
    x = element.get("x", 0)
    y = element.get("y", 0)
    return [Point(x + px, y + py) for px, py in element.get("points", [])]


def _binding_element_id(binding: object) -> str | None:
    if not isinstance(binding, dict):
        return None
    element_id = binding.get("elementId")
    return element_id if isinstance(element_id, str) else None


def _point_within_expanded_rect(point: Point, rect: Rect, margin: float = 6.0) -> bool:
    expanded = rect.expanded(margin)
    return (
        expanded.left <= point.x <= expanded.right
        and expanded.top <= point.y <= expanded.bottom
    )


def analyze_excalidraw(
    elements: Sequence[dict],
    *,
    padding_x: int = DEFAULT_PADDING_X,
    padding_y: int = DEFAULT_PADDING_Y,
    overlap_area_threshold: float = 4.0,
) -> dict[str, list[dict]]:
    by_id = {element.get("id"): element for element in elements}
    text_elements = {
        element.get("id"): element
        for element in elements
        if element.get("type") == "text" and not element.get("isDeleted") and isinstance(element.get("id"), str)
    }
    text_owner, inferred_containers = _infer_text_ownership(elements, text_elements)
    text_overflows: list[dict] = []

    for element in elements:
        if element.get("type") != "text":
            continue
        container_id = element.get("containerId")
        if not container_id or container_id not in by_id:
            continue

        container = by_id[container_id]
        container_rect = _element_rect(container)
        measurement = _measure_text_element(element)
        if container_rect is None or measurement is None:
            continue

        inner_width = container_rect.width - (padding_x * 2)
        inner_height = container_rect.height - (padding_y * 2)
        if measurement.text_width > inner_width or measurement.text_height > inner_height:
            text_overflows.append(
                {
                    "textId": element.get("id"),
                    "containerId": container_id,
                    "textWidth": measurement.text_width,
                    "textHeight": measurement.text_height,
                    "availableWidth": inner_width,
                    "availableHeight": inner_height,
                    "text": element.get("text", ""),
                }
            )

    overlap_candidates: list[tuple[Rect, str]] = []
    for element in elements:
        rect = _element_rect(element)
        if rect is None:
            continue
        if element.get("type") == "text" and (
            element.get("containerId") or element.get("id") in text_owner
        ):
            continue
        overlap_candidates.append((rect, element.get("type")))

    overlaps: list[dict] = []
    for index, (left, left_type) in enumerate(overlap_candidates):
        for right, right_type in overlap_candidates[index + 1:]:
            # Intentional containment is allowed for region backgrounds, cards, and free-floating labels.
            if _contains(right, left, margin=0) or _contains(left, right, margin=0):
                continue
            if left_type == "text" and right_type != "text" and _covers_most(right, left):
                continue
            if right_type == "text" and left_type != "text" and _covers_most(left, right):
                continue
            area = left.intersection_area(right)
            if area >= overlap_area_threshold:
                overlaps.append(
                    {
                        "leftId": left.id,
                        "rightId": right.id,
                        "area": round(area, 2),
                    }
                )

    text_fragments = [fragment for element in text_elements.values() for fragment in _text_fragments(element)]
    text_collision_map: dict[tuple[str, str, str], dict] = {}
    zone_issue_map: dict[tuple[str, str, str], dict] = {}

    def record_text_collision(*, text_id: str, target_id: str, issue: str, area: float, detail: str) -> None:
        key = (text_id, target_id, issue)
        entry = text_collision_map.get(key)
        rounded_area = round(area, 2)
        if entry is None or rounded_area > entry["area"]:
            text_collision_map[key] = {
                "textId": text_id,
                "targetId": target_id,
                "issue": issue,
                "area": rounded_area,
                "detail": detail,
            }

    def record_zone_issue(*, text_id: str, container_id: str, issue: str, area: float, detail: str) -> None:
        key = (text_id, container_id, issue)
        entry = zone_issue_map.get(key)
        rounded_area = round(area, 2)
        if entry is None or rounded_area > entry["area"]:
            zone_issue_map[key] = {
                "textId": text_id,
                "containerId": container_id,
                "issue": issue,
                "area": rounded_area,
                "detail": detail,
            }

    text_block_rects = {
        text_id: rect
        for text_id, element in text_elements.items()
        if (rect := _element_rect(element)) is not None
    }

    for container_id, container in inferred_containers.items():
        if not container.owned_text_ids:
            continue
        divider_rect = container.divider_rect
        if divider_rect is None:
            continue
        divider_band = divider_rect.expanded(2.0)
        title_ids: list[str] = []
        body_ids: list[str] = []
        for text_id in container.owned_text_ids:
            block_rect = text_block_rects.get(text_id)
            if block_rect is None:
                continue
            overlap_area = block_rect.intersection_area(divider_band)
            if overlap_area >= overlap_area_threshold:
                record_zone_issue(
                    text_id=text_id,
                    container_id=container_id,
                    issue="text_crosses_divider",
                    area=overlap_area,
                    detail=(
                        f"Text '{text_id}' crosses divider '{container.divider_id}' "
                        f"inside container '{container_id}'."
                    ),
                )
                continue
            if block_rect.bottom <= divider_band.top:
                title_ids.append(text_id)
            elif block_rect.top >= divider_band.bottom:
                body_ids.append(text_id)
            else:
                record_zone_issue(
                    text_id=text_id,
                    container_id=container_id,
                    issue="text_crosses_divider",
                    area=max(overlap_area_threshold, overlap_area),
                    detail=(
                        f"Text '{text_id}' straddles divider '{container.divider_id}' "
                        f"inside container '{container_id}'."
                    ),
                )

        for title_id in title_ids:
            title_rect = text_block_rects.get(title_id)
            if title_rect is None:
                continue
            for body_id in body_ids:
                body_rect = text_block_rects.get(body_id)
                if body_rect is None:
                    continue
                area = title_rect.intersection_area(body_rect)
                if area >= overlap_area_threshold:
                    record_zone_issue(
                        text_id=title_id,
                        container_id=container_id,
                        issue="title_over_body",
                        area=area,
                        detail=(
                            f"Title text '{title_id}' overlaps body text '{body_id}' "
                            f"inside container '{container_id}'."
                        ),
                    )

    for index, left in enumerate(text_fragments):
        left_element = text_elements.get(left.text_id, {})
        left_container_id = text_owner.get(left.text_id)
        if left_container_id is None:
            explicit_container_id = left_element.get("containerId")
            if isinstance(explicit_container_id, str):
                left_container_id = explicit_container_id
        left_block_rect = _element_rect(left_element) if left_element else None
        for right in text_fragments[index + 1:]:
            if left.text_id == right.text_id:
                continue
            area = left.rect.intersection_area(right.rect)
            if area < overlap_area_threshold:
                continue
            left_id, right_id = sorted((left.text_id, right.text_id))
            record_text_collision(
                text_id=left_id,
                target_id=right_id,
                issue="text_over_text",
                area=area,
                detail=f"Text '{left_id}' overlaps text '{right_id}'.",
            )

        for element in elements:
            if element.get("isDeleted"):
                continue
            element_id = element.get("id")
            if not isinstance(element_id, str) or element_id == left.text_id:
                continue
            if element.get("type") == "text":
                continue
            if element_id == left_container_id and element.get("type") in {"rectangle", "ellipse", "diamond"}:
                continue

            obstacle_rects: list[Rect] = []
            if element.get("type") == "line":
                obstacle_rects = [
                    rect
                    for rect in _line_rects(element)
                    if rect.width <= 500 and rect.height <= 500
                ]
            else:
                rect = _element_rect(element)
                if rect is not None:
                    if left_block_rect is not None and _contains(rect, left_block_rect, margin=0):
                        continue
                    if left_block_rect is not None and _covers_most(rect, left_block_rect):
                        continue
                    if _contains(rect, left.rect, margin=0):
                        continue
                    obstacle_rects = [rect]

            for obstacle_rect in obstacle_rects:
                area = left.rect.intersection_area(obstacle_rect)
                if area < overlap_area_threshold:
                    continue
                record_text_collision(
                    text_id=left.text_id,
                    target_id=element_id,
                    issue="text_over_element",
                    area=area,
                    detail=f"Text '{left.text_id}' overlaps element '{element_id}'.",
                )

    text_collisions = sorted(
        text_collision_map.values(),
        key=lambda item: (item["textId"], item["targetId"], item["issue"]),
    )
    zone_issues = sorted(
        zone_issue_map.values(),
        key=lambda item: (item["containerId"], item["textId"], item["issue"]),
    )

    rect_by_id = {rect.id: rect for rect, _ in overlap_candidates if rect.id}
    rect_type_by_id = {rect.id: kind for rect, kind in overlap_candidates if rect.id}
    text_rects = [fragment.rect for fragment in text_fragments]
    arrow_issues: list[dict] = []

    for element in elements:
        if element.get("type") != "arrow" or element.get("isDeleted"):
            continue

        arrow_id = element.get("id")
        points = _arrow_points(element)
        if len(points) < 2:
            arrow_issues.append(
                {
                    "arrowId": arrow_id,
                    "issue": "too_few_points",
                    "detail": "Arrow must contain at least two absolute points.",
                }
            )
            continue

        start_binding_id = _binding_element_id(element.get("startBinding"))
        end_binding_id = _binding_element_id(element.get("endBinding"))
        if start_binding_id is None:
            arrow_issues.append(
                {
                    "arrowId": arrow_id,
                    "issue": "missing_start_binding",
                    "detail": "Arrow is not bound to a source element.",
                }
            )
        if end_binding_id is None:
            arrow_issues.append(
                {
                    "arrowId": arrow_id,
                    "issue": "missing_end_binding",
                    "detail": "Arrow is not bound to a destination element.",
                }
            )

        if start_binding_id in rect_by_id and not _point_within_expanded_rect(points[0], rect_by_id[start_binding_id]):
            arrow_issues.append(
                {
                    "arrowId": arrow_id,
                    "issue": "start_point_misses_bound_element",
                    "detail": f"Arrow start point does not land on bound element '{start_binding_id}'.",
                }
            )
        if end_binding_id in rect_by_id and not _point_within_expanded_rect(points[-1], rect_by_id[end_binding_id]):
            arrow_issues.append(
                {
                    "arrowId": arrow_id,
                    "issue": "end_point_misses_bound_element",
                    "detail": f"Arrow end point does not land on bound element '{end_binding_id}'.",
                }
            )

        bound_ids = {binding_id for binding_id in (start_binding_id, end_binding_id) if binding_id}
        obstacle_rects = [
            rect
            for rect_id, rect in rect_by_id.items()
            if rect_id not in bound_ids and rect_type_by_id.get(rect_id) != "text"
        ]
        for start, end in zip(points, points[1:]):
            if start == end:
                continue
            if start.x != end.x and start.y != end.y:
                arrow_issues.append(
                    {
                        "arrowId": arrow_id,
                        "issue": "diagonal_segment",
                        "detail": "Arrow contains a diagonal segment; prefer orthogonal routing for architecture diagrams.",
                    }
                )
                continue
            for rect in text_rects:
                if _segment_intersects_rect(start, end, rect):
                    arrow_issues.append(
                        {
                            "arrowId": arrow_id,
                            "issue": "crosses_text",
                            "detail": f"Arrow segment crosses text element '{rect.id}'.",
                        }
                    )
            for rect in obstacle_rects:
                if _point_within_expanded_rect(start, rect, margin=0) and _point_within_expanded_rect(end, rect, margin=0):
                    continue
                if _segment_intersects_rect(start, end, rect):
                    arrow_issues.append(
                        {
                            "arrowId": arrow_id,
                            "issue": "crosses_element",
                            "detail": f"Arrow segment crosses unrelated element '{rect.id}'.",
                        }
                    )

    return {
        "text_overflows": text_overflows,
        "text_collisions": text_collisions,
        "zone_issues": zone_issues,
        "overlaps": overlaps,
        "arrow_issues": arrow_issues,
    }
