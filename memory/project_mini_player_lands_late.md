---
name: project-mini-player-lands-late
description: "The mini player of a newly opened screen appears one frame late, so anything centred above it jumps up by half its height (ticket 2110); top-align instead."
metadata:
  node_type: memory
  type: project
  originSessionId: 043a86db-918e-4a0d-9fdc-1525c32e6db3
  modified: 2026-11-11T10:24:10.447Z
---

Ticket 2110 (2026-11-11), fixed in `c1541417b`: opening an empty playlist, the centred "No music found" + "Add song" block jumped ~82px (~31dp) up once.

Cause: `rememberMiniPlayerVisible()` reads a per-destination `MiniControlViewModel` (`hiltViewModel()`), whose `queueSizeState` starts at 0 and `uiState.playingSong` at null (song loaded async from Room). The first frame of a new screen has no mini player; the next one adds it and the content area shrinks. Lists are top-aligned, so only centred content shows it.

**Why:** the same jump will come back on any new screen that centres a block in the area above the mini player.

**How to apply:** top-align such blocks under the toolbar (portrait 120dp, landscape 24dp with children centred in a 120dp top band — see `rememberCenteredInTopBand` in `DetailSongListContent.kt`). The user chose this over fixing the ViewModel. The root fix, if ever needed app-wide: a mini-visibility StateFlow whose initial value comes synchronously from `PlaybackStateProvider` (queue non-empty + valid song id). Prove a jump with screenrecord + per-frame position, see [[flicker-frame-capture]].
