"""Reusable deterministic layout helpers for Excalidraw generators.

This is intentionally domain-agnostic. Project generators can build their own
specs on top of these primitives without carrying custom layout code in-repo.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable

from geometry import Point, Rect, fit_text_to_box, measure_text_block, orthogonal_route


DEFAULT_APP_STATE = {
    "currentItemFillStyle": "solid",
    "currentItemStrokeWidth": 2,
    "currentItemStrokeStyle": "solid",
    "currentItemRoughness": 0,
    "currentItemOpacity": 100,
    "currentItemFontFamily": 3,
    "currentItemFontSize": 16,
    "currentItemTextAlign": "left",
    "currentItemRoundness": "round",
}


@dataclass(frozen=True)
class BoxSpec:
    box_id: str
    title: str
    body: str
    x: float
    y: float
    width: float
    height: float
    stroke: str
    fill: str
    text: str
    font_size: int = 15
    title_font_size: int = 18
    align: str = "left"


def stable_int(value: str) -> int:
    return int(hashlib.md5(value.encode("utf-8")).hexdigest()[:8], 16)


def excalidraw_document(
    elements: list[dict],
    *,
    view_background_color: str,
    stroke_color: str,
    fill_color: str,
) -> dict:
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            **DEFAULT_APP_STATE,
            "viewBackgroundColor": view_background_color,
            "currentItemStrokeColor": stroke_color,
            "currentItemBackgroundColor": fill_color,
        },
        "files": {},
    }


def text_dims(text: str, font_size: int, padding_x: int = 0, padding_y: int = 0) -> tuple[int, int]:
    measurement = measure_text_block(
        text,
        font_family=3,
        font_size=font_size,
        padding_x=padding_x,
        padding_y=padding_y,
    )
    return measurement.text_width + padding_x * 2, measurement.text_height + padding_y * 2


def make_text(
    text_id: str,
    x: float,
    y: float,
    text: str,
    font_size: int,
    color: str,
    *,
    align: str = "left",
) -> dict:
    width, height = text_dims(text, font_size)
    return {
        "id": text_id,
        "type": "text",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "text": text,
        "originalText": text,
        "fontSize": font_size,
        "fontFamily": 3,
        "textAlign": align,
        "verticalAlign": "top",
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "angle": 0,
        "seed": stable_int(text_id),
        "version": 1,
        "versionNonce": stable_int(f"{text_id}:nonce"),
        "isDeleted": False,
        "groupIds": [],
        "boundElements": None,
        "link": None,
        "locked": False,
        "lineHeight": 1.25,
    }


def make_rect(
    rect_id: str,
    x: float,
    y: float,
    width: float,
    height: float,
    stroke: str,
    fill: str,
    *,
    dashed: bool = False,
    roundness: int = 3,
    stroke_width: int = 2,
) -> dict:
    return {
        "id": rect_id,
        "type": "rectangle",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "strokeColor": stroke,
        "backgroundColor": fill,
        "fillStyle": "solid",
        "strokeWidth": stroke_width,
        "strokeStyle": "dashed" if dashed else "solid",
        "roughness": 0,
        "opacity": 100,
        "angle": 0,
        "seed": stable_int(rect_id),
        "version": 1,
        "versionNonce": stable_int(f"{rect_id}:nonce"),
        "isDeleted": False,
        "groupIds": [],
        "boundElements": [],
        "link": None,
        "locked": False,
        "roundness": {"type": roundness} if roundness else None,
    }


def add_canvas_background(elements: list[dict], bg_id: str, width: float, height: float, color: str) -> None:
    elements.append(
        {
            "id": bg_id,
            "type": "rectangle",
            "x": 0,
            "y": 0,
            "width": width,
            "height": height,
            "strokeColor": "transparent",
            "backgroundColor": color,
            "fillStyle": "solid",
            "strokeWidth": 0,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "angle": 0,
            "seed": stable_int(bg_id),
            "version": 1,
            "versionNonce": stable_int(f"{bg_id}:nonce"),
            "isDeleted": False,
            "groupIds": [],
            "boundElements": None,
            "link": None,
            "locked": True,
            "roundness": None,
        }
    )


def add_section(
    elements: list[dict],
    section_id: str,
    title: str,
    x: float,
    y: float,
    width: float,
    *,
    stroke: str,
    label_fill: str,
    label_text: str,
) -> None:
    label_width, label_height = text_dims(title, 15, padding_x=12, padding_y=8)
    elements.append(
        {
            "id": f"{section_id}_line",
            "type": "line",
            "x": x,
            "y": y,
            "width": width,
            "height": 0,
            "strokeColor": stroke,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "dashed",
            "roughness": 0,
            "opacity": 100,
            "angle": 0,
            "seed": stable_int(f"{section_id}_line"),
            "version": 1,
            "versionNonce": stable_int(f"{section_id}_line_nonce"),
            "isDeleted": False,
            "groupIds": [],
            "boundElements": None,
            "link": None,
            "locked": False,
            "points": [[0, 0], [width, 0]],
        }
    )
    elements.append(make_rect(f"{section_id}_label_bg", x + 18, y - label_height / 2, label_width, label_height, stroke, label_fill, roundness=2))
    elements.append(make_text(f"{section_id}_label", x + 30, y - (text_dims(title, 15)[1] / 2), title, 15, label_text))


def add_box(elements: list[dict], spec: BoxSpec) -> Rect:
    title_fit = fit_text_to_box(
        spec.title,
        font_family=3,
        font_size=spec.title_font_size,
        max_width=int(spec.width - 28),
        max_height=64,
        min_font_size=max(12, spec.title_font_size - 4),
    )
    _, title_height = text_dims(title_fit.text, title_fit.font_size)
    title_y = spec.y + 16
    divider_y = title_y + title_height + 12
    body_y = divider_y + 14
    body_max_height = int(spec.height - (body_y - spec.y) - 16)
    body_fit = fit_text_to_box(
        spec.body,
        font_family=3,
        font_size=spec.font_size,
        max_width=int(spec.width - 28),
        max_height=max(48, body_max_height),
        min_font_size=10,
    )
    _, body_height = text_dims(body_fit.text, body_fit.font_size)
    box_height = max(spec.height, (body_y - spec.y) + body_height + 16)

    elements.append(make_rect(spec.box_id, spec.x, spec.y, spec.width, box_height, spec.stroke, spec.fill))
    elements.append(make_text(f"{spec.box_id}_title", spec.x + 16, title_y, title_fit.text, title_fit.font_size, spec.text))
    elements.append(
        {
            "id": f"{spec.box_id}_divider",
            "type": "line",
            "x": spec.x + 14,
            "y": divider_y,
            "width": spec.width - 28,
            "height": 0,
            "strokeColor": spec.stroke,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "angle": 0,
            "seed": stable_int(f"{spec.box_id}_divider"),
            "version": 1,
            "versionNonce": stable_int(f"{spec.box_id}_divider_nonce"),
            "isDeleted": False,
            "groupIds": [],
            "boundElements": None,
            "link": None,
            "locked": False,
            "points": [[0, 0], [spec.width - 28, 0]],
        }
    )
    elements.append(make_text(f"{spec.box_id}_body", spec.x + 16, body_y, body_fit.text, body_fit.font_size, spec.text, align=spec.align))
    return Rect(spec.x, spec.y, spec.width, box_height, id=spec.box_id)


def add_code_panel(
    elements: list[dict],
    panel_id: str,
    title: str,
    body: str,
    x: float,
    y: float,
    width: float,
    *,
    stroke: str,
    fill: str,
    text: str,
) -> Rect:
    title_fit = fit_text_to_box(title, font_family=3, font_size=15, max_width=int(width - 28), max_height=40, min_font_size=13)
    body_fit = fit_text_to_box(body, font_family=3, font_size=13, max_width=int(width - 28), max_height=280, min_font_size=12)
    _, title_h = text_dims(title_fit.text, title_fit.font_size)
    _, body_h = text_dims(body_fit.text, body_fit.font_size)
    height = 26 + title_h + 16 + body_h + 16
    elements.append(make_rect(panel_id, x, y, width, height, stroke, fill, roundness=2))
    elements.append(make_text(f"{panel_id}_title", x + 16, y + 14, title_fit.text, title_fit.font_size, text))
    elements.append(make_text(f"{panel_id}_body", x + 16, y + 40, body_fit.text, body_fit.font_size, text))
    return Rect(x, y, width, height, id=panel_id)


def _binding_focus(rect: Rect, side: str, point: Point) -> float:
    if side in {"left", "right"}:
        span = max(rect.height, 1)
        raw = ((point.y - rect.top) / span) * 2 - 1
    elif side in {"top", "bottom"}:
        span = max(rect.width, 1)
        raw = ((point.x - rect.left) / span) * 2 - 1
    else:
        raise ValueError(side)
    return round(max(-1.0, min(1.0, raw)), 3)


def _binding_for_edge(rect: Rect | None, side: str | None, point: Point, gap: float) -> dict | None:
    if rect is None or side is None or rect.id is None:
        return None
    return {
        "elementId": rect.id,
        "focus": _binding_focus(rect, side, point),
        "gap": gap,
    }


def make_arrow(
    arrow_id: str,
    route: list[Point],
    color: str,
    *,
    start_rect: Rect | None = None,
    start_side: str | None = None,
    end_rect: Rect | None = None,
    end_side: str | None = None,
    start_gap: float = 2,
    end_gap: float = 2,
) -> list[dict]:
    min_x = min(point.x for point in route)
    min_y = min(point.y for point in route)
    points = [[point.x - min_x, point.y - min_y] for point in route]
    max_x = max(point[0] for point in points)
    max_y = max(point[1] for point in points)
    start_binding = _binding_for_edge(start_rect, start_side, route[0], start_gap)
    end_binding = _binding_for_edge(end_rect, end_side, route[-1], end_gap)
    return [{
        "id": arrow_id,
        "type": "arrow",
        "x": min_x,
        "y": min_y,
        "width": max_x,
        "height": max_y,
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 0,
        "opacity": 100,
        "angle": 0,
        "seed": stable_int(arrow_id),
        "version": 1,
        "versionNonce": stable_int(f"{arrow_id}:nonce"),
        "isDeleted": False,
        "groupIds": [],
        "boundElements": [],
        "link": None,
        "locked": False,
        "points": points,
        "startBinding": start_binding,
        "endBinding": end_binding,
        "startArrowhead": None,
        "endArrowhead": "arrow",
        "lastCommittedPoint": points[-1],
        "elbowed": True,
    }]


def edge_point(rect: Rect, side: str, offset: float = 0) -> Point:
    if side == "left":
        return Point(rect.left, rect.top + rect.height / 2 + offset)
    if side == "right":
        return Point(rect.right, rect.top + rect.height / 2 + offset)
    if side == "top":
        return Point(rect.left + rect.width / 2 + offset, rect.top)
    if side == "bottom":
        return Point(rect.left + rect.width / 2 + offset, rect.bottom)
    raise ValueError(side)


def _segment_intersects_rect(start: Point, end: Point, rect: Rect) -> bool:
    if start.x == end.x:
        x = start.x
        return rect.left < x < rect.right and not (
            max(start.y, end.y) <= rect.top or min(start.y, end.y) >= rect.bottom
        )
    if start.y == end.y:
        y = start.y
        return rect.top < y < rect.bottom and not (
            max(start.x, end.x) <= rect.left or min(start.x, end.x) >= rect.right
        )
    raise ValueError("Only orthogonal segments are supported")


def _path_clear(points: list[Point], obstacles: Iterable[Rect], padding: float) -> bool:
    expanded = [rect.expanded(padding) for rect in obstacles]
    for start, end in zip(points, points[1:]):
        if start == end:
            continue
        for rect in expanded:
            if _segment_intersects_rect(start, end, rect):
                return False
    return True


def route_between(
    start_rect: Rect,
    start_side: str,
    end_rect: Rect,
    end_side: str,
    *,
    start_offset: float = 0,
    end_offset: float = 0,
    obstacles: Iterable[Rect],
    padding: float = 18,
) -> list[Point]:
    start = edge_point(start_rect, start_side, start_offset)
    end = edge_point(end_rect, end_side, end_offset)
    filtered = [rect for rect in obstacles if rect.id not in {start_rect.id, end_rect.id}]
    if start.x == end.x or start.y == end.y:
        return orthogonal_route(start, end, obstacles=filtered, padding=padding)

    lane_x_values = sorted({
        start.x,
        end.x,
        (start.x + end.x) / 2,
        *[rect.left - padding for rect in filtered],
        *[rect.right + padding for rect in filtered],
    })
    lane_y_values = sorted({
        start.y,
        end.y,
        (start.y + end.y) / 2,
        *[rect.top - padding for rect in filtered],
        *[rect.bottom + padding for rect in filtered],
    })
    candidates = [[start, Point(end.x, start.y), end], [start, Point(start.x, end.y), end]]
    candidates.extend([start, Point(lx, start.y), Point(lx, end.y), end] for lx in lane_x_values)
    candidates.extend([start, Point(start.x, ly), Point(end.x, ly), end] for ly in lane_y_values)
    valid = [route for route in candidates if _path_clear(route, filtered, padding)]
    if valid:
        return min(valid, key=lambda route: sum(abs(a.x - b.x) + abs(a.y - b.y) for a, b in zip(route, route[1:])))
    return [start, Point(start.x, end.y), end]
