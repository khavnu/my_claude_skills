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

The checks only stop a design from being bad. Being *remembered* takes a
deliberate signature moment and a real choice between directions. Without them,
"most popular" research converges on the market average. Convention for
structure, one bold idea per feature where it matters.

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
   **Classify every decision before designing it:**
   - *Structural* (sort, menus, settings, forms, list rows, dialogs): follow the
     convention. Familiar beats clever; skip steps 1a–1b.
   - *Expressive* (the app's main screens, heroes, feature screens people come
     for, e.g. Now Playing, Equalizer, Sing, onboarding, empty states): run 1a–1b.
   Popularity research only gives the **floor** (what users expect). For an
   expressive decision also look for the **ceiling** (award winners,
   `references/research-sources.md`), and ask: *"What does every top app do the
   same way?"* That shared habit is the cheapest place to stand out.
1a. **Signature moment** (expressive only): name the one moment in the feature
   where the app shows its personality, and write it into the brief. It is the
   *peak* of Peak–End (`principles.md` §10): the moment people remember and
   describe to others. One per feature. Examples: the band curve morphing
   between presets, the knob glow pulsing with the bass, lyrics lighting up word
   by word. Techniques: `references/creative.md`.
1b. **Diverge before converging** (expressive only): draw 3 low-detail
   thumbnails (grey boxes + the one idea, 10–15 min each, never polished):
   - **Safe:** the convention the floor research found.
   - **Stretch:** the convention + one signature twist.
   - **Bold:** break one assumption on purpose (shape, layout, input method,
     metaphor). Name the assumption it breaks.
   Put them side by side with one line each: what it gains, what it risks. Let
   the user pick, or mix them, *before* any detailed work. Never polish all three.
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
   **The signature moment gets motion, not prose:** at least one animated frame
   (load `figma:figma-use-motion`) or a keyframe strip (start · peak · end, with
   duration + easing/spring on each step). A note saying "it glows and pulses"
   is not a hand-off: developers cannot build from it.
5. **Render, run the Review Gate** on every changed screen, fix, re-render.

Load when needed: `references/principles.md` (hierarchy, color, type, layout,
UX laws, motion) · `references/creative.md` (signature moments, divergence
techniques, guardrails) · `references/specs.md` (standard sizes) ·
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
| 8 | Distinctiveness (expressive screens only) | Place the screen next to the same screen from 3 top competitors with logos and names hidden. List the elements only this app has (signature moment, shape, metaphor, motion). ≥1 = pass, 0 = fail. Structural screens: write "n/a, structural" | |

**Full gate vs. delta gate.** A *new* or *redesigned* screen gets all rows. An
*edited* screen (rows added, a button moved, copy changed) gets only the rows
the edit can affect. List the skipped rows with one reason each, e.g. "1 ✓
new grip 12.2:1 · 2–4 skipped: layout unchanged · 5 ✓ token-bound · 6 ✓ drag
state drawn". Silently shortening the full gate is the failure this rule
replaces. When it is unclear which rows an edit touches, run the full gate.

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
| Expressive screen designed from "what's most popular" alone → the market average | Floor + ceiling research, a signature moment, 3 thumbnails (Safe / Stretch / Bold) before detail |
| Creativity spent on a structural screen (a "fun" sort sheet, a clever settings list) | Structural = convention. Spend the novelty budget on the signature moment |
| Signature moment handed off as a sentence ("pulses with the beat") | Motion frame or keyframe strip with timings |
| Bold idea shipped without its fallback (reduced motion, disabled state, small screen, other theme modes) | The creative layer passes the same gate as everything else (`creative.md` › Guardrails) |
