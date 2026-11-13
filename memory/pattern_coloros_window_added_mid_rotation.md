---
name: pattern-coloros-window-added-mid-rotation
description: "ColorOS (Realme C55, Android 15): dialog window added during a rotation while the IME closes is 'shown' in WM but has no SurfaceFlinger layer → invisible sheet that still holds focus/Back; release-only, fixed by delaying AdaptiveSheet container swap 500ms (#472)"
metadata:
  node_type: memory
  type: project
  originSessionId: 50677524-b6cb-43a8-81cf-c447d243ebd0
  modified: 2026-10-27T04:46:25.483Z
---

Ticket #472 (2026-10-27), fixed in commit `07fe226d` (`ui/component/AdaptiveSheet.kt`, `ROTATION_SETTLE_MS = 500`).

**Symptom:** landscape → Save side panel + keyboard open → rotate to portrait → the bottom sheet vanishes, the navigation bar shows over Play result, taps do nothing. Rotating back shows the side panel again.

**What was actually wrong** (each fact verified, with how):
- App side was correct: temporary log showed `sheetState current=Expanded offset=1613`, uiautomator dump had the field + buttons at the sheet's position.
- WindowManager said the dialog window was `isVisible=true HAS_DRAWN` and held focus (`dumpsys window windows`).
- **SurfaceFlinger had no `Layer (<windowId> …)` for it** (`dumpsys SurfaceFlinger | grep -c "Layer (<id> "` → 0; after the fix → 1). That is the real cause: the window was added while ColorOS ran the rotation transition with the IME closing, and never got a surface.
- First Compose frame came ~0.9 s after the sheet was created.

**Traps that cost time:**
- **Debug build does not reproduce** (0/4); release (R8, faster) did (2/2). Diagnose timing bugs on a release build. Release builds install over QA's APK with `adb install -r` (same `musiceditor.jks` key); debug needs an uninstall (data loss).
- Emulator (Android 16, Pixel) never reproduces. Rotating with the keyboard closed never reproduces.
- First hypothesis ("`show()` animation cancelled by insets change") was wrong — the release log disproved it. Check WM vs SurfaceFlinger before blaming Compose state.
- ColorOS blocks `pm grant` (needs a developer option); grant permissions through the UI. The Realme USB connection dropped twice mid-run — check `adb devices` before blaming the app.

**How to apply:** any container that is swapped on rotation (AdaptiveSheet bottom sheet ↔ SidePanel) must not add its new window during the rotation. Verify on a ColorOS device with a release build, loop ≥5 times, and check the dialog layer count in SurfaceFlinger. Related: [[pattern-rotation-resets-remember]], [[reference-device-shot-helpers]].
