---
name: reference-editor-device-test
description: "Trim/Copy (audio editor) device tests — Lite mode hides them on Pixel_2 emulator and Huawei nova 3i; use Realme C55; path, zoom coords, hold-at-edge drags with input motionevent."
metadata:
  node_type: memory
  type: reference
  originSessionId: 043a86db-918e-4a0d-9fdc-1525c32e6db3
  modified: 2026-11-12T02:18:36.397Z
---

Verified 2026-11-12 (ticket 2115).

- Trim / Copy rows are hidden in Lite mode (`HIDDEN_IN_LITE` in `feature/common/dialog/song_action/SongActionRules.kt`; no debug override). Lite on: Pixel_2 AVD (API 27, 4GB) and Huawei nova 3i. Not Lite: Realme C55 (`QKOZWW65AIEQP7JJ`), Z Flip 3.
- Path on Realme portrait: Main > Songs tab > first row's more (1008,581) > swipe the sheet up > "Trim" (~195,1763). Zoom (+) at (187,919); start knob of a fresh song ~ (161,511).
- Landscape: the waveform is only the left column (Realme x≈108..1488 px), so a finger can leave it — that is where off-screen handle bugs show; portrait waveform is full width.
- A drag that holds at an edge (auto-scroll) needs `adb shell input motionevent DOWN x y` / `MOVE` / `sleep` / `UP` (works on API 33); `input swipe` releases at once.
- `:audio_editor` has no test source set; its pure helpers are tested from `app/src/test/.../feature/audio_editor/` (e.g. `WaveformVisibleRangeTest`).
- (2026-11-12, ticket 2116) The Equalizer screen is also missing in Lite (drawer has no "Equalizer" on Pixel_2 AVD / Huawei): EQ checks on Realme or Z Flip.
- Capturing a sub-second animation: Realme C55 refuses `screenrecord` (file in /sdcard, /data/local/tmp or stdout: "Permission denied" / 0 bytes) and `screencap` loops are ~0.6 s apart -> use a temporary `android.util.Log` + `logcat -s TAG`. Z Flip records fine with `screenrecord --display-id <main id> /sdcard/Download/x.mp4` (video stays portrait-framed; crop the landscape band).
- `rememberSaveable` does not restore across a rotation when the screen switches layout branch (portrait Column vs landscape Row): the saved key is positional. Keep such per-item UI state in the ViewModel-held state (EqualizerUiState.shownLevels).
