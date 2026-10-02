# Building a design in Figma via MCP (use_figma)

Load the `figma:figma-use` skill before any `use_figma` call. This file adds the
file structure and the traps that cost real retries.

## File structure
- Pages numbered: `1. Read me · 2. Foundations · 3. Components · 4. <Area> · … · N. Flows`.
- Screens named `<page>.<group>.<n> Title` (e.g. `4.3.2 Albums`), each group a
  Section, one row per group. Components keep clean names (`Button`, not
  `3.2.1 Button`) — the number goes on the card label only, because component
  names surface in instances, Assets and code mapping.
- Read me page: where tokens live, how to change the look, component rules,
  layout conventions, product rules, requirements, changelog.
- Flows page: one node per screen group, numbered; solid = navigate, dashed =
  overlay, accent color = the product's signature path.

## Build order
1. Variables: `Color` collection with M3 role names + `setVariableCodeSyntax('ANDROID', 'MaterialTheme.colorScheme.x')`; `Dimension` (space/*, radius/*). Explicit scopes on every variable.
2. Text styles (named roles), effect styles (glow, elevation), paint styles for gradients (variables can't bind gradient stops — one style = one place to edit).
3. Icon components (one per glyph) → atoms → molecules → screen parts. Every stateful control as a variant set with ALL states.
4. Screens from instances only. Take one screenshot per composition, fix, re-shoot.
5. Run the review gate from SKILL.md before reporting.

## Traps (each cost a failed call)
| Symptom | Cause | Fix |
|---|---|---|
| Bound fill renders black on an instance sublayer | Base paint color was `{0,0,0}`; render uses it | Build the base paint from `Object.values(v.valuesByMode)[0]`, then bind |
| Paint opacity silently 1 | `setBoundVariableForPaint` dropped `opacity` even when it was in the base paint (2026-10-01, scrim/dim layers) | Use node `opacity` for translucent bound fills; verify by reading `fills[0].opacity` back |
| Text shows an empty box | Plus Jakarta Sans has no ⇄ ⏱ (and most emoji: ♥ renders as a red emoji) | Write words or use an Icon component; scan new copy with `/[⇄⏱]/` before shipping |
| Edited the wrong note/pill | `section.findOne(n=>n.name==='superseded note')` returns the first match, not the one above your frame | Pick by geometry (same x, directly above) or keep the created id |
| Frames left their Section after a multi-frame screenshot | `figma.group(nodes, page)` → `ungroup` reparents the frames to the group's parent (the page) | Group inside the frames' own section (`figma.group(nodes, section)`), or screenshot each frame; after any group/ungroup, list page-level frames and move them back |
| Theme/brand variants without duplicating frames | — | Add modes to the Color collection and `frame.setExplicitVariableModeForCollection(collection, modeId)`; tiles can each carry their own mode |
| Component collapses to 10 px | `resize()` after `primaryAxisSizingMode='AUTO'` resets to FIXED | Resize first, then set AUTO |
| "Cannot override size in an instance" | `rescale()`/`resize()`/`x` on a nested instance layer | Rescale the outer instance; model values (slider level) as a variant axis |
| Rescaled instance has huge corners | Rescale multiplies bound radius | Make a Size variant per size instead of scaling |
| Swapped variant lost its text/icon | `setProperties({State})` resets overrides | Re-set TEXT/INSTANCE_SWAP props after every variant swap |
| Cloned variant ignores properties | `clone()` drops `componentPropertyReferences` | Relink after cloning |
| INSTANCE_SWAP link reset all icons | Linking resets nested instances to the default | Re-apply per-variant swaps and fills after linking |
| Icon replaced by text | Icons are TEXT (ligature glyph); `findOne(TEXT)` hit it | Exclude `name==='glyph'`, target by layer name |
| Glow still visible after removing style | `setEffectStyleIdAsync('')` keeps raw effect | Also set `effects = []` |
| Instance text edit ignored | Text is property-linked | `instance.setProperties({[key]: value})` |
| `FILL` rejected | Set before appendChild | Append to auto-layout parent first, then FILL |
| Slider fill overflows at 100% | Sibling widened, track shrank | Recompute fill from `track.width` |
| Word-wipe gradient wrong on 2 lines | Gradient spans the whole text box | Keep wipe lines single-line; per-line progress in code |
| Bulk swap changed unrelated buttons (top-bar icons became "play") | `findAll` by component set matched every IconButton in the frame | Scope by parent layer name (`panel`, `compact row`) before bulk `setProperties` |
| Figma "text" matched when you meant a label | Same as icons: TEXT layers include glyphs | Filter by layer name, never by type alone |
| Script half-applied? | Failed scripts roll back | Re-read canvas only if `safeToRetryWithoutCanvasRead` is false |
| Helper rows/columns show white boxes on a dark screen | `figma.createAutoLayout()` frames get a default white fill | Set `fills = []` right after creating every structural auto-layout frame |
| Spacer made with an empty `createAutoLayout()` adds a 100px gap | An auto-layout frame with no children keeps its 100×100 default | Use `itemSpacing`/padding, or a plain frame `resize(1, N)` |
| `getStyleByIdAsync(id)` returns null | Style ids read via `node.fillStyleId` / style lists end in a trailing `,` (`S:abc…,`) | Look styles up by name from `getLocal*StylesAsync()` |
| `remove: node … does not exist` while removing instances | `findAll(INSTANCE)` also returns instances nested inside the ones you remove first | Remove only `children.filter(...)`, never a deep `findAll` result |
| Screenshot URL returns a 74-byte 404 JSON | `get_screenshot` URLs had expired by the time curl ran (2026-10-01) | Download right after the call, or judge from `node.screenshot()` inline |

## Realistic images (covers, avatars, photos)
- Generate your own abstract images (PIL) instead of copyrighted art; vary hue
  and brightness on purpose.
- `upload_assets(count=N, currentPageId)` → POST each file as multipart
  (`-F "file=@x.jpg;type=image/jpeg"`) → response gives `imageHash` and the node
  it placed. Apply elsewhere with `node.fills = [{type:'IMAGE', imageHash, scaleMode:'FILL'}]`
  (works as an instance override); hide the placeholder icon child.
- Map image → content key (song/album title) so the same item shows the same
  image on every screen; leave a few placeholders to show "missing art".
- `figma.createImageAsync` is not supported in use_figma — use upload_assets.
- `figma.createImage(bytes)` works, but an image not attached to a node in the
  SAME call is dropped — a hash reused in a later call renders blank. For
  thumbnails of another page's frame: `get_screenshot` → download →
  `upload_assets(nodeIds=[target])`.
- Split a screen across pages (e.g. a tab with many states) → leave a pointer
  card with a thumbnail where readers will look for it.

## Screenshots
`get_screenshot` returns a URL → `curl -sL -o x.png URL`, then Read it. For
several frames: `figma.group([...])` → `screenshot()` → `ungroup` inside one call.
