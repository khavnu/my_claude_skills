---
name: wmusi-figma-bulk-transform-pitfalls
description: "Plugin-API traps hit while bulk-cloning ~400 WMusi frames into landscape (layoutMode switch, removed nodes, findAncestor, wrap grids, blur_test args)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ad3962cc-8c87-4a93-b911-940ac3a0a811
  modified: 2026-10-07T06:26:01.045Z
---

Verified 2026-10-07 while building page `8. Landscape & tablet` (393:11080) in Figma `my_idea`.

- Switching an auto-layout frame's `layoutMode` (VERTICAL→HORIZONTAL) silently turns children's FILL/HUG into FIXED at the old cross size (texts became 352×320, body became HUG 1888 wide). After any switch, re-set `layoutSizingHorizontal/Vertical` on the frame and every child.
- `node.findAncestor` does not exist in use_figma (TypeError) — walk `parent` by hand.
- Removing a node that is still in a cached `findAll` array makes the next `.name` read throw "node does not exist" mid-script; the script is NOT atomic, earlier edits stay. Filter with `!n.removed` after removals.
- Wrap grids (`layoutWrap = 'WRAP'`) cannot take FILL children: set a FIXED cell width = (width − pads − gap·(cols−1)) / cols and clone cells; never trim a wrap grid to one row.
- WMusi frames are `content` auto-layout columns with named blocks (`top bar`, `LibraryTabs`, `count row`, `header`, `sheet`, `scrim`, `MiniPlayer`, `BottomNav`), so layout transforms can key on names — check names with a frequency audit first.
- `create-design/scripts/blur_test.py OUT IN...` — output path comes FIRST.

**Why:** each cost a failed run or a silent broken batch that only showed up in screenshots.
**How to apply:** any future bulk Figma rewrite in this file (new orientation, new size class, re-theme). Related: [[wmusi-figma-file]].

Added 2026-10-09 (section 4.26):
- "Scrolled" state of a list frame: insert a no-layout clipping frame (`list viewport`, FILL×FILL) where the first list item was, put an auto-layout `list content` column inside it, move the items in (set them FIXED width first), then `inner.y = -offset`. Auto-layout padding cannot be negative.
- A TEXT inserted into a top bar row with `layoutSizingVertical = 'FILL'` stays top-aligned even with counterAxisAlignItems CENTER — set it to `HUG`.

Added 2026-10-12 (sections 4.27/4.28, 5.6 continued) — found twice, cost a rebuild each time:
- Grabbing "first TEXT found" via `findOne(n=>n.type==='TEXT')` or `node.getStyledTextSegments(...)[0]` from an arbitrary existing frame can return an ICON's internal "glyph" text (Material Symbols font) instead of a real label — renders as garbled/icon-like glyphs when you then set `.characters` to normal words. Always source `fontName`/`fontSize` from a node you've verified renders as plain text (e.g. `61:559` "Mix" label, `35:427` song title) — never from the first TEXT match inside an arbitrary clone. When picking a specific label among an instance's children (e.g. a button's "label" vs its "icon"), use **direct children** (`row.children.find(c=>c.type==='TEXT')`), not recursive `findOne`, which walks into nested instances and returns the icon's glyph text first.
- Row overflow is not only a font-200% concern: sum `child.width + itemSpacing×(n-1) + padding` vs the parent's width for any new multi-item auto-layout row, even at 100% font/normal strings — a 2-action row already overflowed 360dp by 20dp here, silently clipped (no `…`, just gone) since the frame had `clipsContent=true`.
- `layoutPositioning = 'ABSOLUTE'` only valid when the parent is itself auto-layout (`layoutMode !== 'NONE'`); a plain `figma.createFrame()` child already free-positions via x/y, setting ABSOLUTE there throws.
- A `Button`/component instance often carries a leftover default "icon" child from whatever it was last edited as (e.g. a mic icon). It cannot be `.remove()`d (instance structural children refuse removal) — set `.visible = false` instead.
- Contrary to the 2026-10-07 note above ("script is NOT atomic, earlier edits stay"): a thrown error partway through a script here rolled back the WHOLE script's mutations every time it happened this session (verified by re-querying right after). Don't assume either way — re-read the canvas after any error before deciding what to redo.
