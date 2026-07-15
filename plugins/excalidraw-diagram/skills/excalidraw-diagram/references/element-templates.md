# Excalidraw Element Templates

Use these as starting points when building `.excalidraw` files. Replace placeholder IDs, positions, text, and palette-driven colors.

## Rectangle

```json
{
  "type": "rectangle",
  "id": "elem1",
  "x": 100,
  "y": 100,
  "width": 180,
  "height": 90,
  "strokeColor": "<stroke from palette>",
  "backgroundColor": "<fill from palette>",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 12345,
  "version": 1,
  "versionNonce": 67890,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [{ "id": "text1", "type": "text" }],
  "link": null,
  "locked": false,
  "roundness": { "type": 3 }
}
```

## Text

`width`/`height` are not free parameters — derive them from measured text (`measure_text_bounds.py` → `reqWidth`/`reqHeight`), and set the parent box to match. `text` and `originalText` hold the same **natural, unwrapped** string; do not insert `\n` to force line breaks (let wrapping decide them). See "Text Sizing and Wrapping" in SKILL.md.

```json
{
  "type": "text",
  "id": "text1",
  "x": 130,
  "y": 132,
  "width": 120,
  "height": 25,
  "text": "Process",
  "originalText": "Process",
  "fontSize": 16,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "<text color from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 11111,
  "version": 1,
  "versionNonce": 22222,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": "elem1",
  "lineHeight": 1.25
}
```

## Arrow

```json
{
  "type": "arrow",
  "id": "arrow1",
  "x": 282,
  "y": 145,
  "width": 118,
  "height": 0,
  "strokeColor": "<arrow color from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 33333,
  "version": 1,
  "versionNonce": 44444,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [118, 0]],
  "startBinding": { "elementId": "elem1", "focus": 0, "gap": 2 },
  "endBinding": { "elementId": "elem2", "focus": 0, "gap": 2 },
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

## Line

```json
{
  "type": "line",
  "id": "line1",
  "x": 100,
  "y": 100,
  "width": 0,
  "height": 200,
  "strokeColor": "<structural line color from palette>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 44444,
  "version": 1,
  "versionNonce": 55555,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [0, 200]]
}
```

## Small Marker Dot

```json
{
  "type": "ellipse",
  "id": "dot1",
  "x": 94,
  "y": 94,
  "width": 12,
  "height": 12,
  "strokeColor": "<marker dot color from palette>",
  "backgroundColor": "<marker dot color from palette>",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 66666,
  "version": 1,
  "versionNonce": 77777,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false
}
```

## Grouped Cluster

A panel and everything inside it share a `groupIds` entry so the whole cluster moves as one unit (and can be ungrouped in-app for manual fixes). Elements sharing a group id are grouped; nested groups append ids outer-last so every descendant carries the outer id.

```json
[
  {
    "type": "rectangle",
    "id": "section",
    "x": 80,
    "y": 80,
    "width": 360,
    "height": 220,
    "groupIds": ["section-cluster"],
    "roughness": 0,
    "boundElements": [{ "id": "section_title", "type": "text" }]
  },
  {
    "type": "text",
    "id": "section_title",
    "x": 96,
    "y": 92,
    "width": 200,
    "height": 25,
    "text": "Ingest",
    "originalText": "Ingest",
    "fontSize": 16,
    "fontFamily": 2,
    "roughness": 0,
    "containerId": "section",
    "groupIds": ["section-cluster"]
  },
  {
    "type": "rectangle",
    "id": "step_parse",
    "x": 110,
    "y": 150,
    "width": 140,
    "height": 60,
    "groupIds": ["section-cluster"],
    "roughness": 0
  }
]
```

Notes:
- The panel (`section`), its bound title, and the inner box (`step_parse`) all carry `"section-cluster"`, so dragging any one moves the whole group.
- For a section nested inside a larger background, the inner elements would read `"groupIds": ["step-subgroup", "section-cluster", "background"]` — innermost first, outermost last.
