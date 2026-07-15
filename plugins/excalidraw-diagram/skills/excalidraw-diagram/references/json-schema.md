# Excalidraw JSON Schema

## Element Types

| Type | Use For |
| --- | --- |
| `rectangle` | Processes, actions, components |
| `ellipse` | Entry/exit points, external systems |
| `diamond` | Decisions, conditionals |
| `arrow` | Connections between shapes |
| `text` | Labels inside shapes |
| `line` | Non-arrow connections |
| `frame` | Grouping containers |

## Common Properties

All elements share these:

| Property | Type | Description |
| --- | --- | --- |
| `id` | string | Unique identifier |
| `type` | string | Element type |
| `x`, `y` | number | Position in pixels |
| `width`, `height` | number | Size in pixels |
| `strokeColor` | string | Border color (hex) |
| `backgroundColor` | string | Fill color (hex or `"transparent"`) |
| `fillStyle` | string | `"solid"`, `"hachure"`, `"cross-hatch"` |
| `strokeWidth` | number | 1, 2, or 4 |
| `strokeStyle` | string | `"solid"`, `"dashed"`, `"dotted"` |
| `roughness` | number | 0 (smooth), 1 (default), 2 (rough) |
| `opacity` | number | 0-100 |
| `seed` | number | Random seed for roughness |
| `groupIds` | string[] | Shared group membership; elements with a common id move together. Nested groups append ids outer-last. Group panels with their contents (see SKILL.md → Grouping). |

## Text-Specific Properties

| Property | Description |
| --- | --- |
| `text` | The natural, unwrapped string. Do not insert `\n` to force wrapping — size the box and let text reflow (SKILL.md → Text Sizing and Wrapping) |
| `originalText` | Same natural string as `text`; the app re-wraps bound text to the box width on open |
| `width`/`height` | Derive from measured text (`measure_text_bounds.py` → `reqWidth`/`reqHeight`), not guessed |
| `fontSize` | Size in pixels (16-20 recommended) |
| `fontFamily` | 1 = Virgil/hand-drawn (NEVER use), 2 = Helvetica (titles/labels), 3 = monospace (code/identifiers) |
| `textAlign` | `"left"`, `"center"`, `"right"` |
| `verticalAlign` | `"top"`, `"middle"`, `"bottom"` |
| `containerId` | ID of parent shape |

## Arrow-Specific Properties

| Property | Description |
| --- | --- |
| `points` | Array of `[x, y]` coordinates |
| `startBinding` | Connection to start shape |
| `endBinding` | Connection to end shape |
| `startArrowhead` | `null`, `"arrow"`, `"bar"`, `"dot"`, `"triangle"` |
| `endArrowhead` | `null`, `"arrow"`, `"bar"`, `"dot"`, `"triangle"` |

## Binding Format

```json
{
  "elementId": "shapeId",
  "focus": 0,
  "gap": 2
}
```

## Rectangle Roundness

Add this for rounded corners:

```json
"roundness": { "type": 3 }
```
