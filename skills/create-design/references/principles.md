# Visual & UX Principles — reference

Synthesized from: Refactoring UI (Wathan & Schoger), Thinking with Type (Lupton),
Interaction of Color (Albers), Grid Systems (Müller-Brockmann), The Design of
Everyday Things (Norman), Laws of UX (Yablonski), Material 3 + M3 Expressive,
Apple HIG, WCAG 2.2, APCA. Numbers are defaults — deviate on purpose, never by accident.

## Contents
1. Layout & grid · 2. Spacing · 3. Hierarchy & attention · 4. Proportion
5. Typography · 6. Color · 7. Components & states · 8. Icons & imagery
9. Platform · 10. UX laws · 11. Screen states & writing · 12. Motion

---

## 1. Layout & grid
- Mobile: 4 columns, side margins 16–24, gutter 16. Tablet 8 cols, web 12.
- Left-align anything longer than one line; center only short, isolated items
  (titles, empty states, dialogs).
- One alignment edge per block. Misalignments of 1–4 px read as "sloppy" even
  when nobody can say why.
- Symmetry = calm/formal; asymmetry = energy. Balance by visual weight
  (size × contrast × saturation), not by element count.

## 2. Spacing
- Scale: 4, 8, 12, 16, 24, 32, 40, 48, 64. Never pick an off-scale number.
- Padding = inside a container; margin/gap = between containers.
- **Proximity rule:** space inside a group < space between groups, by ~1.5–2×
  (e.g. 8 inside, 16 between items, 24–32 between sections). A header must sit
  closer to its own content than to the section above.
- Start with too much whitespace, then remove. Crowding is the #1 amateur tell.

## 3. Hierarchy & attention
- Six tools: size, weight, color, contrast, position, whitespace.
- **Exactly one primary focal point per screen**, at most one secondary. If
  three things "pop", nothing does (Von Restorff only works on the odd one out).
- Emphasize by de-emphasizing the rest (lighter weight, lower contrast, smaller),
  not only by enlarging the hero.
- Pre-attentive order: luminance contrast > size > motion > hue. Warm saturated
  hues advance, cool ones recede. A hue matching its backdrop disappears
  (pink text on a pink glow).
- Scan patterns: F for text-heavy lists, Z for sparse landing/hero layouts,
  center-weighted for media/players.
- Size hierarchy: primary control ≈ 1.5–1.67× secondary controls
  (e.g. 72–80 vs 48). 1.33× reads as "same level".
- **Verify with the blur test** (`scripts/blur_test.py`) — never by intuition.

## 4. Proportion
- Golden ratio 1.618 is a *tool*, not a law — preference studies replicate
  weakly. Use it to check big splits: primary content ≥ ~62% of height,
  controls ≤ ~38%; focal element near the 38.2% line (the optical center sits
  slightly above the geometric center).
- Rule of thirds for focal placement; modular scales (1.2 minor third, 1.25
  major third, 1.333 fourth, 1.5 fifth) for type and spacing progressions.

## 5. Typography
- 1–2 families. Android default Roboto, iOS SF; Vietnamese-safe choices: Be
  Vietnam Pro, Inter, Plus Jakarta Sans, Montserrat, Lora.
- Scale with named roles (Display/Headline/Title/Body/Label), e.g. 12/14/16/20/24/32
  or a modular ratio. 2–3 weights per screen.
- Line-height: body 1.4–1.6, headings ~1.2, **Vietnamese display text ≥1.3**
  so stacked marks (Ử, Ỗ, ệ) don't clip. Line length 50–75 characters.
- Letter-spacing: slightly negative for large display, slightly positive for
  small uppercase labels.
- **Tabular figures (`tnum`)** for any number that changes in place (timers,
  seek times, percentages) — proportional digits make them jitter.
- Truncate with "…" on one line, or wrap; never clip mid-glyph.

## 6. Color
- Work in HSL/HCT, not raw hex. Build: primary, secondary, a 9–10-step
  neutral ramp, 9–10 tones per hue (50→900), semantic success/warning/error/info.
- **60-30-10**: 60% base/neutral, 30% secondary surfaces, ≤10% accent.
- Harmony: complementary (tension), analogous (calm), triadic/split-complementary
  (vivid but balanced). One accent hue owns "act here".
- Contrast minimums, **both must pass** (`scripts/contrast.py`):
  - WCAG 2: text ≥ 4.5:1, large text (≥18.66px bold / 24px) & icons ≥ 3:1.
  - APCA Lc (better for dark mode): body 75–90, other content ≥ 60,
    large/bold ≥ 45, non-text ≥ 30.
- **White text on saturated mid-tone fills usually fails** (measured: #FFF on
  #B14DFF 3.9:1, on #FF3D9A 3.3:1, on #FF5470 3.1:1).
  **WCAG and APCA disagree on mid-tones:** dark text on #B14DFF passes WCAG
  (5.0) but fails APCA (Lc 38); white passes APCA (71) but fails WCAG. When the
  two disagree, change the **fill tone**, not the text: #9A3BE8 (5.0 / 79),
  #D81F7A (4.8 / 77), #D93A4E (4.5 / 75) pass both with white.
- M3 tonal roles (HCT, tones 0–100): dark scheme primary = T80, onPrimary = T20,
  primaryContainer = T30, onPrimaryContainer = T90. Light scheme mirrors
  (primary T40, onPrimary T100). Picking tones, not hexes, keeps pairs legible.
- Never grey text on a colored background — use a lighter/darker tint of that
  background's own hue (Refactoring UI).
- Dark mode: base dark grey (not pure black); elevation = lighter surface;
  **desaturate** text/icon accents (tone ~80); saturated neon only for large
  fills and glows — saturated small text vibrates and fails contrast.
- Never rely on color alone for state: pair with icon, shape, fill or text.
- Glow/bloom is an accent too: counts toward the 10%.

## 6b. Design tokens — structure and rules
Tokens carry the rules; a hex without a rule gets misused.
- **Two layers:** `Palette/<hue>/<tone>` primitives (tonal ramps, hidden from
  pickers, scopes `[]`) → `Color/<role>` semantic roles aliased to a tone.
  Layers bind roles only, never primitives or raw hex.
- **Ramps by tone** (CIE L*, `scripts/tonal_palette.py`): same tone = same
  lightness across hues, so pairs are predictable. Add a **low-chroma ramp** for
  containers so selected states stay tonal instead of reading as accents.
- **Dark-scheme mapping (M3):** accent T80 · on-accent T20 · container T30
  (low chroma) · on-container T90 · surfaces neutral T4/6/10/12/17/22 ·
  onSurface T90 · onSurfaceVariant NV80 · outline NV60 · outlineVariant NV30.
- **One role = one meaning.** Never reuse `onPrimary` as "white on the brand
  gradient". Brand fills get their own roles (`brand/fillStart|fillEnd|danger`)
  and their own on-role (`brand/onFill`). Mixing meanings breaks the moment a
  developer maps roles to a theme (every default button turns white-on-pastel).
- **Every role's description states:** what it is for, its only partner(s), the
  contrast it guarantees (measured), and what it must never be used for.
- **Required roles:** surfaces + on-surface, primary/secondary/tertiary families,
  error, success, warning, info (each with on-, container, on-container),
  outline (must pass 3:1) vs outlineVariant (decorative), scrim.
- **Surface steps must be perceptible** (neighbouring steps ≥ ~1.1:1).
- Gradients can't bind variables: keep paint-style stops equal to the brand roles
  and say so in the style description.
- Document tokens on a board that shows each pair with **live WCAG/APCA badges**
  computed from the resolved values — the board is the test.

## 7. Components & states
| Group | Components |
|---|---|
| Action | Button (primary/secondary/tonal/text/danger), icon button, FAB |
| Input | Text field, dropdown, checkbox, radio, switch, slider, date picker |
| Navigation | Tab/nav bar, top bar, drawer, segmented control, breadcrumb |
| Display | Card, list item, avatar, badge, chip, divider |
| Feedback | Snackbar/toast, dialog, bottom sheet, progress, skeleton |

- Every interactive component: default, pressed, disabled, selected, error,
  focus. Toggles/cycles: **every state** (Off/On, Off/All/One, Play/Pause/Loading).
- Touch target ≥ 48×48 dp (Android) / 44×44 pt (iOS); WCAG floor 24×24.
- Dialog buttons: 2 choices → equal-width pair, neutral tonal negative left,
  primary/danger right; 3 choices → stacked full width.
- Irreversible actions: confirm dialog naming the item and the loss.
  Reversible: act + Undo snackbar. Prefer Trash over permanent delete.

## 8. Icons & imagery
- One set (Material Symbols, SF Symbols, Phosphor, Lucide), one stroke weight,
  one grid (20 or 24), outline XOR filled — filled only for "on/selected".
- Label any icon whose meaning isn't universal.
- Images: fixed aspect ratios (1:1, 4:3, 16:9), consistent radius, placeholder
  + error fallback. Export SVG for icons; PNG @1x/@2x/@3x for raster.
- **One thumbnail shape per grid/row.** Circles only for people (avatars);
  content art is a rounded square. A deliberate exception must carry meaning
  and be documented (e.g. a music mini player's circular "spinning record").
  Sample data must be coherent too: tracks of an album share its cover. A dark image on a dark background loses its
  edge and reads as a different shape — give thumbnails a faint inside stroke.
- **Content-derived color:** media screens may tint backdrops from the artwork
  (dominant hue at a dark tone, low chroma), but text/controls stay on semantic
  roles so contrast never depends on the image. Model it as `dynamic/*` tokens
  whose description says "runtime value, example shown" + a fallback.

## 9. Platform
- Android M3: top app bar, navigation bar/rail, elevation by tonal surface,
  dynamic color, edge-to-edge with insets, 360×800 base frame.
- iOS HIG: safe areas (notch, Dynamic Island, home bar), large titles, tab bar,
  swipe-back, Dynamic Type, 390×844 base frame.
- Check smallest (320 wide) and large (412+) widths; text +40% for localization.
- M3 Expressive (2025–26): spring motion, shape morphing, emphasized type,
  button groups, toolbars, wavy progress. Research: key actions found ~4× faster —
  but breaking familiar patterns hurts. Fresh + familiar.

## 10. UX laws (the ones that change decisions)
- **Fitts** — frequent actions big and in the thumb zone (bottom half).
- **Hick / Choice overload** — group long menus; surface the top 3 actions.
  An overflow (⋮) menu never repeats an action that already has a visible
  button on the same screen — duplicates add choices without adding capability.
- **Jakob** — copy conventions users already know (Spotify/YouTube patterns).
- **Miller / Chunking** — group into 3–7 chunks.
- **Doherty (<400 ms)** — respond instantly; if work takes longer, show progress
  and something useful meanwhile.
- **Peak–End** — design the best moment and the ending of each flow explicitly.
- **Goal-gradient** — show progress toward completion.
- **Tesler** — complexity moves, it doesn't vanish; absorb it in the app.
- **Aesthetic-usability** — polish buys forgiveness, not usability.
- **Serial position** — first and last items are remembered: put key actions there.

## 11. Screen states & writing
- Every data screen: empty, loading (skeleton > spinner), error, success,
  offline, permission denied. A screen without them is unfinished.
- Buttons say the outcome ("Save changes", "Delete 12 songs"), not "OK".
- Errors say what happened + what to do. Waits > 1 s say what keeps working.

## 12. Motion
- 150–300 ms for most UI; ease-out (decelerate) to enter, ease-in to exit;
  M3 Expressive prefers springs (spatial for movement, effects for color/opacity).
- Motion must explain (where it came from/went), never decorate.
- Respect "remove animations": replace movement with instant state change.
