---
name: wmusi-sheet-window-test-pitfalls
description: "Testing WMusi sheets/side panels (dialog windows) on device — font-scale override does not reach them, squeezed Column hides overflow, Samsung M20 (API 28) storage/rotation quirks"
metadata:
  node_type: memory
  type: project
  originSessionId: 596b63b5-5189-490f-ab6e-b397252bd4aa
  modified: 2026-11-11T07:15:15.547Z
---

Verified 2026-11-11 on Samsung SM-M205G (serial 3201f501bd0a1633, API 28, notch), the user's own phone.

- `DeviceConfigurationOverride.FontScale` / a `LocalDensity` override in a UI test does NOT reach a sheet or side panel: the Dialog's own ComposeView provides `LocalDensity` again from its context. The WMusiSidePanel/ModalBottomSheet content stays at the device font scale. To test large text, set `adb shell settings put system font_scale X` (restore to 1.0 afterwards).
- A non-scrolling `Column` with a max height SQUEEZES its last children (down to 0 height) instead of letting them overflow. A "last row bottom <= panel bottom" bounds check then passes even when the text is cut. Assert the row's height or look at a screenshot.
- API 28 `WindowManager.LayoutParams.toString` prints cutout mode 1 (SHORT_EDGES) as `always`, and Compose's ALWAYS (3) as `unknown(3)`. Do not read `always` in `dumpsys window windows` as "unchanged".
- The M20 has only ~1–2 GB free and the debug APK is ~500 MB (bundled Whisper models). Every reinstall (gradle connected run included) fails with INSTALL_FAILED_INSUFFICIENT_STORAGE unless you `adb uninstall com.wife.recommend.music` (+ `.test`) first. `pm trim-caches 4G` freed ~0.9 GB (user OK'd cleanup).
- M20 rotation: `accelerometer_rotation` resets to 1 after `am start`. Set it to 0 again, then `user_rotation`. The user's default is accelerometer_rotation=1, so restore it at the end.
- The user uses the M20 at the same time (My Files was open mid-run → "No compose hierarchies found"). Check `dumpsys window | grep mCurrentFocus` before each run, and stop if another app is in front.
- The skill's API<30 "sheet floats after the keyboard hides" row did NOT reproduce in WMusi on the M20 (0/5: New playlist sheet, keyboard up in landscape → rotate to portrait → BACK). The fix was reverted. Don't re-add it without a repro.

Related: [[wmusi-device-verify]], [[wmusi-min-api-pitfalls]]
