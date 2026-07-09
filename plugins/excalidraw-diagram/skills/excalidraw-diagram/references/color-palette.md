# Excalidraw Diagram Palette

Use this file as the single source of truth for colors.

## Core Colors

- Background: `#FFFFFF`
- Primary stroke: `#1F3A5F`
- Primary fill: `#EAF2FF`
- Secondary stroke: `#2F5D50`
- Secondary fill: `#E8F6F1`
- Accent stroke: `#A64B2A`
- Accent fill: `#FDEEE8`
- Neutral stroke: `#5B6470`
- Neutral fill: `#F4F6F8`

## Text Colors

- Primary text on light fills: `#10233C`
- Secondary text on light fills: `#18352D`
- Accent text on light fills: `#5E2B18`
- Dark surface text: `#F7FAFC`
- Annotation text: `#51606F`
- **Table-cell highlight text (pop): `#DC2626`** — bright, saturated red. Use for "best-in-column" cell text, "matrix-winner" callouts, or any text-level highlight inside a table where the cell stays on a light fill. The muted accent text (#5E2B18) is too close to #10233C to read as a highlight at small sizes.

## Structural Colors

- Section boundary stroke: `#AAB7C4`
- Section label text: `#3C4A59`
- Arrow stroke: `#425466`
- Timeline line: `#697586`
- Marker dot: `#2D4F73`

## Evidence Artifact Colors

- Code snippet background: `#0F172A`
- Code snippet border: `#334155`
- Code keyword text: `#7DD3FC`
- Code string text: `#86EFAC`
- Code emphasis text: `#FDE68A`
- JSON key text: `#93C5FD`
- JSON value text: `#FCA5A5`

## Font Defaults

- **Titles, labels, descriptions:** `fontFamily: 2` (Helvetica) — clean, professional
- **Code, data names, technical identifiers:** `fontFamily: 3` (Cascadia/monospace) — for things like `ContainerTree`, `sections_json`, function names
- **Never use `fontFamily: 1`** (Virgil/hand-drawn) — too cartoony for technical diagrams

## Guidance

- Use the primary palette for the main flow.
- Use the secondary palette for supporting systems or downstream effects.
- Use the accent palette sparingly for warnings, friction points, or transformations.
- Use neutral fills for containers, labels, and low-emphasis groupings.
- Evidence artifacts should read as distinct and denser than the rest of the diagram.
- **For in-table highlights** (e.g., bolded "best in column" values in a findings table), use `#DC2626` for the text color. The muted accent text (`#5E2B18`) is too dark and too close to the primary text color (`#10233C`) to register as a visual highlight at table-cell text sizes (11–13pt) — readers can't pick it out.
