# excalidraw-skill

An agent skill for generating **editable `.excalidraw` diagrams that argue visually** (not rendered images, and not boxes with labels). It ships with a deterministic layout
toolkit (text measurement, container sizing, orthogonal arrow routing, and geometry
preflight) so diagrams come out clean on the first pass instead of after rounds of
coordinate nudging.

Ask for "a diagram of how the AG-UI protocol streams events to a frontend" or "visualize
this ingestion pipeline", and the agent produces an `.excalidraw` file you open directly
in [Excalidraw](https://excalidraw.com) (web app) or the Obsidian Excalidraw plugin.

## What it does

- **Structure carries the argument.** Fan-out for one-to-many, timelines for sequences,
  convergence for aggregation, section boundaries for distinct phases. It runs an
  isomorphism test: *if all the text disappeared, would the layout still communicate the
  idea?*
- **Concrete over generic.** Technical diagrams use real event names, payloads, and API
  calls as evidence artifacts, not placeholder boxes.
- **Deterministic layout, not hand-placed JSON.** Multi-box diagrams are sized from
  measured text and routed with a geometry helper, then run through a mechanical preflight
  (overflow, overlap, clipping, connector sanity) before anything renders.
- **The `.excalidraw` is the deliverable.** A PNG is only ever produced for validation in
  a temp dir, and is **never** written next to the source unless you explicitly ask. A
  co-located PNG just goes stale on the next edit.

## Install

The skill uses the standard `.claude-plugin` marketplace format, so the same repo installs
into any coding agent that understands that format. Pick your tool:

### Claude Code

As a plugin (recommended):

```
/plugin marketplace add doyled-it/excalidraw-skill
/plugin install excalidraw-diagram@doyled-it-diagrams
```

As a bare skill (clone + symlink):

```bash
git clone https://github.com/doyled-it/excalidraw-skill.git
ln -s "$PWD/excalidraw-skill/plugins/excalidraw-diagram/skills/excalidraw-diagram" \
  ~/.claude/skills/excalidraw-diagram
```

### Codex CLI

Codex (0.133.0+) consumes the same marketplace format:

```bash
codex plugin marketplace add doyled-it/excalidraw-skill --ref main
codex plugin add excalidraw-diagram@doyled-it-diagrams
```

To pull updates after the repo changes:

```bash
codex plugin marketplace upgrade doyled-it-diagrams
```

As a bare skill:

```bash
git clone https://github.com/doyled-it/excalidraw-skill.git
ln -s "$PWD/excalidraw-skill/plugins/excalidraw-diagram/skills/excalidraw-diagram" \
  ~/.codex/skills/excalidraw-diagram
```

### Any other agent

Any tool that loads skills from a directory works the same way: symlink (or copy) the
skill directory into wherever that tool discovers skills:

```bash
ln -s "$PWD/excalidraw-skill/plugins/excalidraw-diagram/skills/excalidraw-diagram" \
  <your-tool-skills-dir>/excalidraw-diagram
```

The only files the agent strictly needs are `SKILL.md` and `references/`. The renderer
(below) is optional.

## Optional: the renderer

Diagram generation needs no dependencies. The renderer only exists for **visual
validation** and for **deterministic text measurement**, and it's worth setting up if you
want the agent to sanity-check dense diagrams before handing them over.

```bash
cd plugins/excalidraw-diagram/skills/excalidraw-diagram/references
uv sync
uv run playwright install chromium
```

Requires [`uv`](https://docs.astral.sh/uv/) and (first run) network access to fetch
Chromium and the ESM Excalidraw bundle. For offline/restricted networks, see the
[skill's renderer README](plugins/excalidraw-diagram/skills/excalidraw-diagram/README.md)
for vendoring a local bundle.

## Layout

```
.claude-plugin/
  marketplace.json                       # marketplace "doyled-it-diagrams"
plugins/excalidraw-diagram/
  .claude-plugin/plugin.json             # plugin manifest
  skills/excalidraw-diagram/
    SKILL.md                             # design philosophy, process, gotchas
    README.md                            # renderer setup (optional)
    references/
      color-palette.md                   # palette + evidence-artifact styling
      element-templates.md               # Excalidraw JSON element templates
      json-schema.md                     # compact schema reference
      geometry.py                        # sizing, routing, preflight helpers
      preflight_excalidraw.py            # overflow/overlap checker
      measure_text_bounds.py             # Playwright text measurement
      render_excalidraw.py               # Playwright PNG renderer (validation only)
      render_template.html               # browser-side SVG renderer
      pyproject.toml / uv.lock           # renderer dependencies
```

> **Packaging note:** in a `.claude-plugin` marketplace, each plugin's `source` must point
> at a **subdirectory** (`"./plugins/excalidraw-diagram"`), not the repo root (`"./"`).
> Codex reports "plugin not found in marketplace" for a root-level source. Hence the
> `plugins/<name>/` layout here.

## License

MIT, see [LICENSE](LICENSE).
