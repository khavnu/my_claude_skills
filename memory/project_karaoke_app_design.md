---
name: project-karaoke-app-design
description: New offline karaoke/music-player app (separate from Music Editor) — agreed v1 scope and Figma file being built
metadata:
  node_type: memory
  type: project
  originSessionId: e3b246ca-7bf8-422f-be96-0174aa57b767
  modified: 2026-09-29T10:27:23.458Z
---

User is designing a NEW app (not this repo): offline music player with karaoke as a feature. Figma target: https://www.figma.com/design/oxFsDJWcj57DCjSlM8dTc5/my_idea (pages Foundations/Components/Player/Sing/Flows; variables "Color" + "Dimension", 17 text styles Plus Jakarta Sans, glow effect styles — created 2026-09-29).

Agreed v1 (2026-09-29):
- Full player: Home · Library (Songs/Albums/Artists/Folders/Playlists) · Search · Now Playing · Queue · Favorites/Recent/Most played · Playlists · Equalizer · Sleep timer · Edit tag (no ringtone cutter) · widget/notification. Bottom nav 3 tabs: Home · Library · Settings. No Karaoke tab.
- Now Playing has 2 tabs: Song · Sing. Sing = streamed lyrics with word-level color wipe + 2 stem sliders (Vocal/Beat) + Key/Tempo chips. "Singing" is just lowering Vocal volume — no mode switch, playback stays seamless.
- Settings › Lyrics & Sing: size M/L/XL, font (Jakarta/Be Vietnam Pro/Montserrat/Lora), highlight color presets, keep screen on; live preview.
- Style: dark neon (#0B0B14 bg, primary #B14DFF, secondary #FF3D9A, tertiary #22E1FF).
- Deferred: record (needs LAME), voice effects, 4 stems, scoring, ads, premium, landscape, .lrc/tag lyrics.

Status 2026-09-29: full v1 design built — pages Read me (guidelines) · Foundations · Components · Player (~26 frames incl. 5 context menus) · Sing (4 states) · Flows. Next step agreed: user reviews the whole thing, then we discuss. Rules for editing live on the "Read me" page.

**Why:** target setup is phone → karaoke speaker with its own mic, so the speaker does echo/reverb; app needs no RECORD_AUDIO in v1.
**How to apply:** user trims scope aggressively ("để sau") — propose minimal v1, don't pile on advanced ideas; for pure design (Figma) work the user said "làm hết các bước, không cần confirm" — build everything, then review together (overrides the step-by-step rule for design only, not for code).
