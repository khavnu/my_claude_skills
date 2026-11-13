---
name: splash-root-subcompose-hang
description: Root BoxWithConstraints/SubcomposeLayout around the app hangs a landscape cold start behind the splash (Pixel 9 API 37)
metadata:
  type: project
---

2026-10-15: the first version of the API < 30 rotation fix (9d36c18, later squashed into 308f27a without it) wrapped `ProvideWindowLayout` in a root `BoxWithConstraints`. Landscape cold start on the Pixel 9 (API 37) then stayed on the splash forever: 0 frames rendered, process idle. The splash (`setKeepOnScreenCondition { !isFirstScreenReady }`, MainActivity) waits for Home's first data, which is signalled from composition; with the app subcomposed inside a measure pass, the startup rotation waits for a draw the splash blocks, no measure runs, nothing composes. Portrait cold start was fine, so the bug looked device/orientation-specific.

**Why:** anything that moves app composition into layout (BoxWithConstraints, SubcomposeLayout at the root) can deadlock with the splash hold.
**How to apply:** read window size in composition (`currentWindowDpSize()` expect/actual in core/ui; API < 30 uses LocalConfiguration, see [[linux-device-testing]]). After touching root composition or the splash, cold-start in landscape: `adb shell wm user-rotation lock 1; am force-stop; monkey -p com.tmedilab.drink.water2 1`, then `dumpsys gfxinfo com.tmedilab.drink.water2 | grep "Total frames"` must be > 0.
