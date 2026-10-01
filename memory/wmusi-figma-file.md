---
name: wmusi-figma-file
description: WMusi (Karaoke Player) Figma file key, page ids and the 4.15 update section
metadata:
  node_type: memory
  type: reference
  originSessionId: e7439767-dcde-4ea8-b28d-b211a6457f14
  modified: 2026-10-01T04:03:40.018Z
---

Figma file `my_idea`, fileKey `oxFsDJWcj57DCjSlM8dTc5`. Page ids (verified 2026-09-30 via use_figma `figma.root.children`):
- 26:2 1. Read me — design system guide, product rules, changelog
- 0:1 2. Foundations — Color/Dimension/Palette variable collections, text/paint/effect styles
- 3:2 3. Components — sections 3.1 Icons … 3.6 Sing
- 3:3 4. Player — sections 4.1 Onboarding … 4.16 Theme
- 3:4 5. Sing — 5.1 Preparing … 5.5 Localization checks
- 3:5 6. Flows — navigation map

Section `4.15 Update 1/10/2026` = node `106:2195` (added 2026-10-01): 37 frames — missing states/fixes, Library toolbar (4.15.26–33), sort order + Trash multi-select (4.15.34–37); mapping item → frame is in `docs/design/missing-designs.md` (bottom table). Originals replaced by it carry an amber "Superseded" pill above the frame — read 4.15 first when implementing Home/Library/Trash/Song info/Scan/Delete dialogs.

Section `4.16 Theme` = node `126:3746` (2026-10-01); spec + image credits in `docs/design/theme.md`. Theme accents are Color-collection modes (Dark · Midnight, Plum, Ocean, Teal, Forest, Wine) applied with `setExplicitVariableModeForCollection`.

Icons are Material Symbols Rounded TEXT glyphs inside `Icon/<name>` components (child named `glyph`): a new icon = clone `Icon/folder` (4:53) and change the glyph characters.

Tokens are read from the variables API, not the Read me text: the Read me lyric sizes (28/22) are stale; the real text styles are 40/52 and 26/34. How to list pages / read tokens: skill `figma-reader` Step 1.5.
