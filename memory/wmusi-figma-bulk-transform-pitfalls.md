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
