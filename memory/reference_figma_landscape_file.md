---
name: reference-figma-landscape-file
description: "Figma file BxnEuwKr28L6L8G9FmNnph (Music_player_landscape) — portrait baseline, foundations, landscape designs L01–L21; page/node map and build pitfalls."
metadata:
  node_type: memory
  type: reference
  originSessionId: e0371a35-47d3-4e75-a5d0-74465e79f887
  modified: 2026-10-22T09:44:02.713Z
---

Created 2026-10-22. Pages: `0:1` "00 · Portrait baseline (reference)" (59 screenshots in sections A–F), `2:2` "01 · Foundations" (variable collection "Theme · PhotoTheme.1", 9 Inter text styles, 23 `icon/*` components, 10 components: StatusBar/GestureBar/Banner/SongRow/MiniPlayer/SearchField/Button Primary+Outline/panel MenuItem+Header), `2:3` "02 · Landscape" (L01–L21 at 923×411 + README node `11:1191` with rules and decisions D1–D4).

Decisions 2026-10-22 (user): no banner in landscape for now; Player keeps 3-tab pager, each tab has its own landscape layout (L05 Song `12:1191`, L06 Queue `12:1281`, L07 Lyrics `12:1394`); video player and tablet/foldable deferred to a later phase. Widget config/picker designed 2026-10-23 after upstream moved widget config to Compose: L22 picker `20:1261` (1000,7050), L23 config Photo tab `20:1448`, L23b Playlist/Color `20:1547` (y=7750); components on Foundations: `widget/Transport` 18:10, `widget/PickerTile` 18:22 (Selected bool), `widget/Preview · Minimal/Compact/Mini/Playlist` 19:68/19:82/19:105/19:121. Code not done yet: 12 config activities still `screenOrientation=portrait`.

Pitfalls hit while building (use_figma):
- `createAutoLayout()` then `resize(w, 10)` fixes the height at 10 and clips → set `primaryAxisSizingMode="AUTO"` after resize, `clipsContent=false`.
- Icon container frames with `layoutMode` hug their 24dp icon → set both axis sizing modes FIXED before `resize`.
- Video player sheets (2026-10-23): L24 menu `34:1530`, L24b speed `34:1646`, L24c add to playlist `34:1747`, L24d queue `34:1828` (y=9072/9772); background component `player/VideoPlayer · landscape` 33:57; new icons icon/floatingWindow 34:1922, icon/mirror 34:1925, icon/delete 34:1928.
- A menu row whose nested icon instance was set `visible=false` no longer lists that child in `children`: replace the instance instead of trying to unhide it.
- A paint bound to a color variable keeps the VARIABLE's alpha: an `opacity` set on it is overwritten (white@40% rendered solid white). For translucent white use an unbound `{type:'SOLID',color:white,opacity}`.
- Editor 2026-10-23 (user): L14 Trim — Play result bar (PlayResultPreview, #232534) always full width at the bottom; L14b `26:1476` — ResultWaveformBottomSheet stays a bottom sheet in landscape, FULL WIDTH (user: "bottom sheet fill width" → sheetMaxWidth = Dp.Unspecified), not a side panel. Copy: L14c `29:1496`, L14d result sheet `29:1732` (y=8432).
- An instance's `children` is empty until it is appended to a parent: append first, then hide/override children (found via `findOne` by name).
- `icon/checkbox` is an empty square outline, not a check mark; use an SVG check (`createNodeFromSvg`).
- Widget config frames: launch a config activity directly with `am start -n com.amapps.media.music/.feature.widgets.widget_config.WidgetCompactConfigActivity --ei appWidgetId 999` (any id) to capture it.
- `surface/cover` equals `surface/dialog` (#3A3C47): a cover inside a panel is invisible; use `surface/secondary`.

Related: [[reference-emulator-screenshot-capture]], [[reference-figma-crop-design-file]]
