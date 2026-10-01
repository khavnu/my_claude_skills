---
name: create-design
description: Use when designing, building, restyling, reviewing or handing off UI — app screens, mockups, design systems, components or Figma files — and before calling any design done, ready, or passing it to developers.
---

# Create Design

## Overview
Design quality is decided by measurement on the **rendered** screen, not by
intent. Agents know the principles; what they skip is checking them — they
confirm the screen list is complete, then ship white text on neon buttons, a
focal point nobody sees, five competing accents. This skill makes the checks
part of the output.

## Workflow
1. **Brief:** each screen's purpose, user, *conditions of use* (distance, one
   hand, dark room, glance vs. read), platform, version scope. Ask when unsure.
   **Taste-dependent picks the user will see** (preset images, visualizer or
   chart styles, theme/color presets, fonts, EQ or timer presets, icon
   metaphors): research what is most viewed / starred / rated *before*
   choosing, time-boxed ~15–20 min, and write source + date + numbers (+
   licence for reused content) into the repo docs. Skip it for anything a rule
   already decides (contrast, touch target, platform guideline, tech limit)
   and for trivial picks. Sources that work: `references/research-sources.md`.
   **Structural UX conventions** no rule settles yet (menu/action order,
   grouping, navigation structure, settings layout): check the platform
   guidelines (Material 3, Apple HIG) and NN/g, then how the most-used apps in
   the category do it. Write the convention down (in this skill or the repo
   docs) so every later screen follows the same one.
2. **Foundations** as tokens: tonal primitives → semantic roles (one meaning each,
   with pairs, guaranteed contrast and "never" rules in every description), type
   scale, spacing and radius scales. See `principles.md` §6b.
3. **Components** with every state (default, pressed, disabled, selected, error,
   focus; every state of a toggle/cycle). **Any image slot** (thumbnail, cover,
   avatar, logo, product photo, map tile…) needs two cases: *with image* and
   *no image* (missing, still loading or failed). List every entity type that
   shows an image (songs, albums, users, products, shops, places…) and give
   **each one its own fallback** (glyph, initials, shape) so types stay
   distinguishable. Never reuse one generic placeholder for all of them.
4. **Screens** from components, named `<page>.<group>.<n>`, grouped by feature.
5. **Render, run the Review Gate** on every changed screen, fix, re-render.

Load when needed: `references/principles.md` (hierarchy, color, type, layout,
UX laws, motion) · `references/specs.md` (standard sizes) ·
`references/figma-workflow.md` (Figma MCP structure + API traps) ·
`scripts/tonal_palette.py` (tone ramps from brand seeds) ·
`references/research-sources.md` (popularity research without API keys).

## Review Gate — REQUIRED in every done / hand-off / progress report
One table per screen. Each row: a **measured value + how it was measured**.
"Looks fine" is not a value.

| # | Check | Pass rule | Measured |
|---|---|---|---|
| 1 | Contrast of every text/icon pair on its *real* backdrop (glow, image, gradient end) | WCAG ≥4.5 text, ≥3 large/icon **and** APCA \|Lc\| ≥60 content, ≥75 body — `python3 scripts/contrast.py FG BG` | |
| 2 | Focal point | Blur test: most salient element = the reason the screen exists — `python3 scripts/blur_test.py out.png screen.png` | |
| 3 | Accent budget | 1 primary accent (gradient/glow/brand fill), ≤1 secondary | |
| 4 | Proportion | Main content ≥~62% height when it is the point; primary control ≈1.5× secondary | |
| 5 | Consistency & tokens | Every color bound to a semantic role (no raw hex, no primitive); each role used only with its pair; on-scale sizes; same-row controls share height+radius; nested radius = outer − padding | |
| 6 | States | Empty, loading, error, permission/offline, long text, each toggle state; every image slot with image **and** without, a fallback for each entity type | |
| 7 | Conditions of use | The brief's condition checked numerically (legible at distance, thumb reach…) | |

**A failing row blocks "done".** Fix it, or report it as an open blocker with its
number. Never downgrade a measured fail to "acceptable" yourself — the user decides.
**An unmeasured row is a FAIL**, not a deferral: measure it now from what you
have (pixels in the screenshot, dp at 160 dpi, visual angle = size ÷ distance),
or state exactly which input is missing.

## Quick reference
- De-emphasize the rest instead of enlarging the hero. One primary action per screen.
- Saturated mid-tone fill: white text fails WCAG, dark text fails APCA → **darken
  the fill** (e.g. #B14DFF→#9A3BE8: WCAG 5.0, APCA 79), don't swap text color.
- Dark mode: dark-grey base, desaturated tone ~80 for text/icons, neon only on large fills.
- A hue on a same-hue backdrop vanishes (pink wipe on pink glow).
- Tabular figures for changing numbers; Vietnamese display line-height ≥1.3.
- Golden ratio checks big splits; it is not a formula.
- **Menus / action lists** (Material 3, Apple HIG, NN/g): most-used first;
  related actions grouped, groups separated by dividers; one fixed group order
  shared by every menu in the app. Typical order: primary/signature action →
  play/open → add/save → go to → edit/share/other → **destructive last**, in
  its own divided group, red, ideally only one. A new action goes into its
  group, never just appended at the bottom. Rows ≥48dp tall.
- Design with realistic content before judging: real-looking images in varied
  colors, long names, missing images. Placeholders hide color competition.

## Common mistakes
| Mistake | Fix |
|---|---|
| Contrast checked against the token, not the glow/image under the text | Sample the rendered pixel |
| Sampling the dimmed line instead of the one that matters | Measure the focal element first |
| Gate run on one screen, twelve shipped | Every changed screen |
| Known fail shipped as a footnote | It is a blocker until the user accepts it |
| Delete/Remove in the middle of a menu, or a new action appended at the end | Re-sort into the shared group order; destructive group always last |
| New menu row cloned from an accented row (signature/primary) and kept its color | Clone a neutral row; check every new row's color against its neighbours |
| Only the main entity type got a no-image fallback; the others show blank or borrow its placeholder | A no-image variant for every entity type that shows an image, placed next to its with-image case |
