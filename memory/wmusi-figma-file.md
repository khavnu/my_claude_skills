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
- 3:3 4. Player — sections 4.1 Onboarding … 4.17 Screen sizes
- 3:4 5. Sing — 5.1 Preparing … 5.5 Localization checks
- 3:5 6. Flows — navigation map (updated 2026-10-01 with 4.15/4.16, Genres, sleep timer)
- 167:8308 7. Archive — replaced originals with their amber Superseded notes; never build from them
- 393:11080 8. Landscape & tablet — L (800×360) + T (1280×800) twin of every page 4/5 frame (added 2026-10-07); rules = Read me card 10, checklist docs/features/landscape/checklist.md

Section `4.15 Update 1/10/2026` = node `106:2195` (added 2026-10-01): 37 frames — missing states/fixes, Library toolbar (4.15.26–33), sort order + Trash multi-select (4.15.34–37); mapping item → frame is in `docs/design/missing-designs.md` (bottom table). Replaced originals moved to page 7. Archive (2026-10-01); sections 4.2 / 4.3 / 4.7 / 4.9 open with a card pointing to the current frames — read that card first.

Section `4.17 Screen sizes` = node `177:6062` (320 / 600 dp). Section `4.16 Theme` = node `126:3746` (2026-10-01); spec + image credits in `docs/design/theme.md`. Theme accents are Color-collection modes (Dark · Midnight, Plum, Ocean, Teal, Forest, Wine) applied with `setExplicitVariableModeForCollection`.

Icons are Material Symbols Rounded TEXT glyphs inside `Icon/<name>` components (child named `glyph`): a new icon = clone `Icon/folder` (4:53) and change the glyph characters. To get a drawable (the `core/designsystem/res/drawable/ic_*.xml` "Exported from Figma component" files): `use_figma` read-only `await node.exportAsync({format:'SVG_STRING', svgOutlineText:true})` on the `Icon/<name>` component, path rounded to 3 decimals, fill white (done for format_list_numbered 324:168, swap_vert 325:10248 on 2026-10-06).

Tokens are read from the variables API, not the Read me text: the Read me lyric sizes (28/22) are stale; the real text styles are 40/52 and 26/34. How to list pages / read tokens: skill `figma-reader` Step 1.5.

Section `4.2 Home` = `41:1227` (verified 2026-10-05 via get_metadata of page 3:3 — the page dump is ~900 KB, grep it from the saved tool-result file): 4.2.2 `64:2265` · 4.2.4 `267:8164` · 4.2.5 `267:8256` · 4.2.7 Recently played `172:5663` · 4.2.8 Favorites `172:5800` · 4.2.9 Favorites empty `172:5937` · 4.2.10 Home v1 grid `264:7571` · 4.2.11 Most played `266:7632` (note `266:8075`: 90-day window, 30 s / half rule, ⋮ Reset play counts) · 4.2.12 Recently added `266:7787` (note `266:8077`) · 4.2.13 Ready to sing `266:7937` (note `266:8079`) · 4.2.14 no history `267:8054`. `267:10946` is a 4.16 theme thumbnail, not a screen.

Section `4.10 Edit` = `41:1235` (verified 2026-10-05 via get_metadata of 3:3): 4.10.2 Change artwork `174:5967` · 4.10.3 Crop artwork (square, "saved as 1000 × 1000") `174:6022` · 4.10.4 cover·Album `198:6347` · 4.10.5 photo·Artist `198:6397` · 4.10.6 cover·Playlist `198:6443` · 4.10.7 cover·Genre `198:6493` · 4.10.8 Crop circle·artist `198:6543` · 4.10.9 Artist no photo `198:7829`. Playlist cover built 2026-10-05 (docs/features/playlist/plan.md R14).

Section `4.18 Song sort in detail · 6/10/2026` = `325:7809` (verified 2026-10-06, built this day): spec + frame ids in `docs/design/detail-sort.md`. `AlbumCard` (`9:54`) has a `Show menu` boolean since 2026-10-06 (⋮ on Library grids) — see `docs/design/item-menus.md`. Detail-frame clones need `getStyledTextSegments` font loading before any text edit (Plus Jakarta Sans variants).

Section `4.19 Equalizer v2 · 6/10/2026` = `343:8316` (built 2026-10-06) supersedes 4.14.1/.2/.3/.8; component `EffectKnob` = `342:274` in 3.2 Actions. Details: `docs/design/equalizer-style-research.md`. Play Store installs/ratings ARE scrapable without a key: plain urllib GET of the details page, regex `\["<n>+",\d+,(\d+)` for exact installs and `"ratingValue"` — contrary to create-design research-sources.md.

Widget: section `4.20 Widget · directions` = `346:8641` (Stretch chosen), `4.21 Widget · Stretch` = `351:8641` (built 2026-10-06); tokens `widget/dark/*`, `widget/light/*`, `dynamic/artworkTone10|90`. Spec: `docs/design/widget.md`.
Widget picker/customize: section `4.22` = `355:8706` (2026-10-06). requestPinAppWidget never opens the config activity and sends nothing on cancel — verified in AppWidgetManager docs.
Section `4.23 Folders · songs at a folder level` = `362:9293` (2026-10-06), answer appended to docs/design/proposals/folders-root-songs.md. figma: node.findOne from a FRAME did not reach TEXT inside a nested INSTANCE (returned null) — recurse over .children manually.
Section `4.24 Multi pick` = `368:9293` (2026-10-06) supersedes 4.13.1/4.13.2; answer in docs/design/proposals/multi-pick.md.
Section `4.25 Folders v2` = `371:10197` (2026-10-06): BROWSE + flat music folders, folder screens, hidden folders; hide deletes song links (user decision). Answer in docs/design/proposals/folder-screen.md.
Now Playing Stretch (sections 4.26 + 4.27 both DELETED from Figma) was DROPPED 2026-10-06: seek bar stays the plain 4.6.1 bar, waveform only as the view-only cover style 4.6.18 (SoundCloud-like, not seekable). Do not re-propose a waveform seek bar or chorus marking.
