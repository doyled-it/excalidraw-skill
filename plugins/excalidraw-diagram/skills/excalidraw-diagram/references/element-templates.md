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
