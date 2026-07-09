# Excalidraw Diagram Skill — Renderer Setup

`SKILL.md` in this directory is the design workflow. This file covers the optional
**renderer**, used only for visual validation. The `.excalidraw` file is always the
deliverable; a PNG is never written next to it unless the user explicitly asks.

All commands below run from **this skill's `references/` directory**, wherever the skill
is installed (e.g. `~/.claude/skills/excalidraw-diagram/references`,
`~/.codex/skills/excalidraw-diagram/references`, or a cloned checkout). Substitute
`<skill>` with that path.

## Files

- `SKILL.md`: design workflow and generation rules
- `references/color-palette.md`: palette and evidence-artifact styling
- `references/element-templates.md`: common Excalidraw JSON element templates
- `references/json-schema.md`: compact schema reference
- `references/render_template.html`: browser-side SVG renderer
- `references/render_excalidraw.py`: Playwright renderer
- `references/measure_text_bounds.py`: Playwright text-measurement helper
- `references/geometry.py`: deterministic sizing, layout, routing, and preflight helpers
- `references/preflight_excalidraw.py`: geometry preflight checker for overflow and overlap
- `references/pyproject.toml` / `uv.lock`: Python dependency declaration

## Renderer setup

```bash
cd <skill>/references
uv sync
uv run playwright install chromium
```

Notes:
- `uv` must be available (https://docs.astral.sh/uv/).
- These steps need network access to download Python packages and Chromium.
- The renderer should use Playwright-managed Chromium. Avoid wiring it to the full
  `Google Chrome.app` binary; that can crash in some macOS sandboxed/headless
  environments before the page loads.

## Offline rendering

By default, `references/render_template.html` imports `@excalidraw/excalidraw` from
`https://esm.sh/`.

For restricted-network or fully offline use, place a local ESM bundle at:

`<skill>/references/vendor/excalidraw-bundle.mjs`

The template prefers that local bundle first and only falls back to the CDN if the
local file is missing.

If rendering fails with a module-load error, either add the local vendor bundle or
allow network access to `https://esm.sh/`.

## Deterministic sizing

Measure text bounds instead of guessing them:

```bash
cd <skill>/references
uv run python measure_text_bounds.py --text "Process" --font-family 3 --font-size 16
```

For multiline text:

```bash
cd <skill>/references
printf 'hello\nworld\n' | uv run python measure_text_bounds.py --stdin --font-family 3 --font-size 16
```

It uses Playwright and the local browser environment to measure text, then returns JSON
with both raw text size and padded container size.

For geometry-first generation, also use:

```bash
cd <skill>/references
uv run python preflight_excalidraw.py ../example.excalidraw --fail-on-issues
```

Generation scripts can import `references/geometry.py` to wrap text, size containers from
measured text, route orthogonal arrows around rectangles, and run mechanical preflight
checks before the render loop. By default, use those helpers from an inline command or a
temporary script rather than checking a one-off generator into the user's repo.
