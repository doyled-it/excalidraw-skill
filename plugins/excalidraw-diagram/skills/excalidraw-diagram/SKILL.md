---
name: excalidraw-diagram
description: Create editable .excalidraw JSON diagram files (not rendered images) that make a visual argument. Use when the user wants to visualize a workflow, architecture, protocol, or concept, asks for an .excalidraw file, or wants a diagram to embed in Obsidian. Prefer over mermaid or ASCII when the user wants an editable canvas, a polished hand-tunable layout, or a diagram that teaches with concrete evidence artifacts (real payloads, API calls, event names) rather than labeled boxes.
---

# Excalidraw Diagram Creator

Generate `.excalidraw` JSON files that argue visually, not just display information.

Setup: if the user asks you to set up or verify the renderer for this skill, see `README.md` in this skill directory.

## Customization

Before generating any diagram, read `references/color-palette.md` and use it as the single source of truth for colors, fills, strokes, text colors, fonts, and evidence artifact styling.

## Core Philosophy

Diagrams should argue, not display.

The structure should carry meaning:
- Fan-out for one-to-many relationships.
- Timelines for ordered sequences.
- Convergence for aggregation or synthesis.
- Section boundaries for distinct responsibilities or phases.

Run this test before committing to a layout:
- Isomorphism test: if all text disappeared, would the structure still communicate the core idea?
- Education test: does the diagram teach something concrete, or does it only label boxes?

## Depth Assessment

Choose the right level first.

Use a simple conceptual diagram when:
- The goal is to explain a mental model.
- Technical specifics are unnecessary.
- The abstraction is the point.

Use a comprehensive technical diagram when:
- The user wants a real architecture, protocol, or integration explained.
- The audience needs to see actual formats, event names, or API calls.
- The diagram should teach, not just summarize.

For technical diagrams, include evidence artifacts.

## Research Mandate

Before drawing technical diagrams:
1. Look up the real spec, docs, or source material.
2. Use actual event names, payloads, method names, and API endpoints.
3. Show how components really connect.
4. Avoid generic placeholders when a concrete example exists.

## Evidence Artifacts

Include at least one of these when the diagram is technical:
- Code snippets for APIs or integration points.
- JSON or data examples for payloads and schemas.
- Event timelines for protocols or workflows.
- UI mockups for concrete outputs.
- Example inputs and outputs.

The point is to show what the system actually looks like.

## Multi-Zoom Architecture

Comprehensive diagrams usually need three zoom levels:
1. Summary flow: the whole pipeline at a glance.
2. Section boundaries: grouped regions by responsibility, phase, or actor.
3. Internal detail: code, payloads, sequences, and examples inside each section.

## Containers vs Free-Floating Text

Default to free-floating text.

Use a container only when:
- It represents a distinct thing.
- Arrows need to bind to it.
- The shape itself carries meaning.
- It visually groups a cluster.

Use free-floating text for titles, labels, annotations, and supporting detail.

## Process

Before generating JSON:
1. Assess whether the diagram should be conceptual or technical.
2. Gather concrete facts if it is technical.
3. Choose a structure whose geometry mirrors the concept.
4. Sketch the spatial hierarchy: summary flow, sections, then detail.
5. For any text element or text-bearing shape whose size matters, measure required bounds with `references/measure_text_bounds.py` instead of guessing.
6. Read `references/element-templates.md` and `references/json-schema.md`.
7. Generate valid `.excalidraw` JSON.

After generating JSON:
1. Validate that the file has `type: "excalidraw"` and a non-empty `elements` array.
2. **Visual inspection — render to PNG only as needed, and never leave the PNG next to the source.**
   - The `.excalidraw` is the deliverable. The user opens it in Excalidraw (web or Obsidian plugin); a `.png` next to it is dead weight and goes stale on the next edit.
   - **Default:** rely on `references/preflight_excalidraw.py` + `references/measure_text_bounds.py` for mechanical checks. These catch overflow, overlap, and clipping when used carefully.
   - **When a render is genuinely needed** (preflight passed but you suspect text-wrap issues, or the user explicitly asked for a preview): render to `/tmp/` only, inspect with the Read tool, then delete the PNG. Do not place a PNG next to the `.excalidraw` source file.
   - **When the user explicitly asks for a PNG deliverable:** render it next to the `.excalidraw` and keep it. That's the only case where a co-located PNG is acceptable.
3. Check EVERY aspect of the rendered image thoroughly (whether the render is in `/tmp/` or, by explicit request, next to the source):
   - Are all labels fully readable? Not clipped, not overlapping lines or other elements?
   - Are arrow labels clearly separated from the arrow line itself? (Labels sitting ON a line are hard to read)
   - Are all arrows visually connected to their source/target boxes?
   - Is spacing consistent? Are elements aligned?
   - Is the overall composition balanced?
4. Fix the JSON and re-render until the diagram looks clean. Common issues:
   - Arrow labels clipped: widen the gap between connected boxes or shorten the label
   - Arrow labels overlapping their line: move the label above or below the line with 10-15px padding
   - Text overflows container: increase container width/height
   - Fonts look cartoony: ensure no `fontFamily: 1` (Virgil) elements remain; use 2 (Helvetica) or 3 (monospace)
   - Floating arrows not connected to boxes: set startBinding/endBinding AND ensure waypoints touch box edges
5. Only commit/deliver after visual inspection confirms the diagram is correct.

## Deterministic Layout

For technical diagrams with multiple boxes, repeated arrow routing, or likely iteration, prefer a generator-plus-validator workflow over hand-placing raw JSON.

Use deterministic layout when:
- The diagram has more than a few containers and connectors.
- The user may revise the diagram multiple times.
- Layout errors would materially reduce trust in the diagram.
- You need a diagram that can be regenerated safely after copy changes.

In deterministic mode:
1. Generate the `.excalidraw` from code or a structured layout spec rather than editing coordinates by hand.
2. Prefer ephemeral generation first: use an inline shell command or a temporary script outside the target repo unless the user explicitly asks for a reusable generator to be checked in.
3. Derive box sizes from measured text or from a conservative fixed-width text model.
4. Route arrows from explicit border anchor points; prefer orthogonal routing for technical architecture diagrams.
5. Bind arrows to shapes with valid `startBinding` and `endBinding` whenever the connector represents a relationship between boxes. Do not ship free-floating arrows for box-to-box architecture flows.
6. Prefer shared lanes for long returns, feedback loops, and fan-in paths instead of one-off elbows that only solve a single collision.
7. Keep IDs stable so regenerated files diff cleanly.
8. Add geometry validation before rendering.

Repository hygiene rule:
- Do not leave one-off diagram generator scripts in the user's repo by default.
- Only create or keep a repo-local generator when the user asks for regeneration support, a maintained spec, or reusable diagram tooling as part of the codebase.
- If a temporary generator is needed, prefer `/tmp` or an inline command and leave the repo with only the requested diagram artifacts unless instructed otherwise.

Use the Python helpers in `references/geometry.py` for exact text measurement, wrapping, container sizing, orthogonal routing, and preflight analysis. Use `references/preflight_excalidraw.py` to fail fast on overflow or overlap before rendering.

Minimum validation rules for deterministic mode:
- Text must fit inside its containing box with padding.
- Text overlap checks must be geometry-based and ownership-aware: derive rendered text bounds using the same font metrics and wrapping model as the renderer, then test those rectangles against foreign shapes, foreign text, and connector lanes.
- Boxes must not overlap.
- Box-to-box arrows must have valid bindings on both ends unless the connector is intentionally free-floating and labeled as such.
- Arrow segments must not cross text blocks.
- Arrow segments must not cut through unrelated boxes.
- Arrow routing must be deliberate; avoid accidental diagonals for architecture diagrams unless the diagonal itself communicates meaning.
- Long connectors should reuse explicit lanes when possible; avoid bespoke elbows that make the same relationship class look inconsistent across the diagram.
- Generation should fail fast on validation errors instead of relying only on visual inspection.

## Text Overlap Geometry

Treat text collision detection as a geometric problem, not a visual guess.

Preferred model:
- Measure rendered text with `references/measure_text_bounds.py` using the actual font family, font size, line height, and intended wrap width.
- Convert each text block into rectangles at the line, word, or label level depending on the precision needed.
- Check those rectangles against:
  - container interior bounds, to detect overflow or clipping
  - other text rectangles, to detect unreadable stacking
  - unrelated shapes, dividers, and panels
  - arrow segments expanded by a small safety padding
- Respect ownership: text overlapping its own containing card is expected, but text crossing outside its owning container or into a foreign element is a real issue.

Default precision:
- Prefer whole-label or per-line rectangles when that is sufficient.
- Escalate to per-word rectangles when dense evidence cards, callouts, or lane labels need finer checks.
- Do not default to per-character boxes unless no renderer-consistent measurement is available.

Why:
- Character-box heuristics ignore kerning, ligatures, real wrap behavior, and line metrics.
- Renderer-consistent text rectangles produce far fewer false positives and catch the failures that matter in live diagrams: clipped labels, labels cut by dividers, and labels intersecting foreign boxes or arrows.

If preflight cannot distinguish owned text from foreign overlap, treat that as a tooling gap and resolve it before trusting a "clean" result.

## Connector Discipline

For technical architecture diagrams, connector quality is part of correctness, not just polish.

Treat these as defaults:
- If two containers are connected conceptually, use a bound arrow attached to both containers.
- Use the helper route points as geometry, not as permission to skip bindings.
- Prefer one or two canonical lane heights or lane columns for feedback paths.
- Minimize bend count. Extra bends need a reason such as obstacle avoidance or lane reuse.
- If a connector is long enough that a reader must trace it visually, label the lane or restructure the layout.

Red flags:
- Arrow starts or ends in whitespace instead of a container edge.
- Similar relationships use visibly different elbow patterns.
- A long return path is routed ad hoc instead of via a shared bus/lane.
- Preflight passes but the connector still requires visual guesswork to follow.

Render-and-inspect is still required, but it should confirm a layout that already passed mechanical checks. Do not treat PNG rendering alone as sufficient validation.

## Deterministic Text Sizing

Do not guess text bounds for labels, cards, payload blocks, or evidence artifacts when those dimensions affect layout.

Use:

```bash
# Run from this skill's references/ directory (wherever the skill is installed)
cd <this-skill-dir>/references
uv run python measure_text_bounds.py --text "Process" --font-family 3 --font-size 16
```

For multiline text, prefer stdin:

```bash
cd <this-skill-dir>/references
printf 'line one\nline two\n' | uv run python measure_text_bounds.py --stdin --font-family 3 --font-size 16
```

The script returns JSON with:
- `textWidth`
- `textHeight`
- `reqWidth`
- `reqHeight`

Use `reqWidth` and `reqHeight` for the containing shape when you want padding included.
Use `textWidth` and `textHeight` for the text element itself.

This is deterministic relative to the local Playwright renderer environment. It is more reliable than heuristic character counting.

## Gotchas

Hard-won failure points specific to Excalidraw JSON. Check these before delivering.

- **Bound arrows need BOTH ends wired AND geometry that touches the edge.** Setting `startBinding`/`endBinding` is not enough — if `points` don't actually reach the box border, the arrow renders detached. Conversely, points touching an edge with no binding will drift when the box moves. You need both.
- **`boundElements` is the reverse link and is easy to forget.** A container holding bound text/arrows must list them in its `boundElements` array; the text/arrow points back via `containerId`/binding. Set only one side and the label floats free or the arrow won't follow the box.
- **`fontFamily` is the most common cause of a bad-looking diagram.** 1 = Virgil (hand-drawn, never use), 2 = Helvetica (titles/labels), 3 = monospace (code/identifiers). A stray `fontFamily: 1` makes the whole diagram look cartoony. Grep the JSON for `"fontFamily": 1` before shipping.
- **`roughness: 0` is mandatory for a clean look.** The Excalidraw default is 1 (sketchy). Technical diagrams want 0 everywhere.
- **Text bounds are renderer-specific, not guessable.** Width from character count is wrong (ignores kerning, wrap, line metrics). Always measure with `measure_text_bounds.py`; preflight overlap results are only trustworthy if measured with the SAME font family/size/wrap as the render.
- **Preflight can pass on a diagram that still reads badly.** Mechanical checks catch overflow/overlap/clipping but not "this arrow needs visual tracing" or inconsistent elbow patterns. A clean preflight is necessary, not sufficient — see Connector Discipline.
- **`originalText` must mirror `text`** on text elements, or edits in the Excalidraw app behave oddly.
- **The renderer's Chromium must be the Playwright-managed one.** Wiring it to the full Google Chrome.app can crash headless on macOS before the page loads (see README).

## Output Expectations

When fulfilling a diagram request:
- Create a `.excalidraw` file. That's the deliverable.
- **Do not render a `.png` next to the source file** unless the user explicitly asked for a PNG. Render to `/tmp/` for visual inspection if mechanical checks aren't enough, then delete it.
- Keep IDs stable and bindings valid.
- Prefer concrete examples over generic labels.
- Use the palette consistently across the diagram.

## References

- `references/color-palette.md`
- `references/element-templates.md`
- `references/json-schema.md`
- `references/render_excalidraw.py`
- `references/geometry.py`
- `references/preflight_excalidraw.py`
- `references/measure_text_bounds.py`
