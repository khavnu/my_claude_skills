---
name: reference-samsung-m20-device-test
description: "Samsung M20 (SM-M205G, API 28, 1080x2340) device test quirks — serial, flaky uiautomator dump, banner taps, API 27 emulator does not reproduce Samsung inset bugs."
metadata:
  node_type: memory
  type: reference
  originSessionId: 043a86db-918e-4a0d-9fdc-1525c32e6db3
  modified: 2026-11-11T05:06:10.886Z
---

Verified 2026-11-11 on ticket 2107 (sheet floating after keyboard + rotate).

- Serial `3201f501bd0a1633`; another session's emulator is often attached too, so always `adb -s <serial>`. `adb devices` shows nothing until USB debugging is on (lsusb still lists it as MTP).
- `uiautomator dump` fails intermittently, mostly while the keyboard is up or in landscape: retry up to 4x, and fall back to a screenshot.
- The test banner sits at the bottom (y≈2130-2340): a tap that misses a sheet row opens Samsung Internet. Check that the target exists before tapping it.
- Rotation with auto-rotate off: `settings put system user_rotation 1|0`.
- Samsung API 28 inset bugs (missing onApplyWindowInsets after the IME hides) do NOT reproduce on the Pixel_2 API 27 emulator: go to the device first. Same script, 4/5 runs stuck before the fix. See [[compose-sheet-window-pitfalls]] skill row.
- If a Gradle build gets interrupted: "Could not read entry ... executionHistory.bin" → `./gradlew --stop; rm -rf .gradle/9.6.1/executionHistory`.
