---
name: wmusi-widget-emulator
description: How to put the WMusi home-screen widget on the emulator and kill the process like LMK, verified 2026-10-06
metadata:
  type: reference
---

Verified 2026-10-06 on emulator-5554 (Pixel launcher, API 36), scripted with `uiautomator dump` + `input tap`:
1. HOME, long-press empty area (`input swipe 540 1500 540 1500 1200`) → tap "Widgets" → tap "Search" → `input text WMusi` → tap the "WMusi" result row → tap the preview → tap "Add". Then press BACK once to leave the resize frame, otherwise taps on the widget do nothing.
2. `:app:connectedDebugAndroidTest` uninstalls the app → onboarding + audio permission again after `installDebug` (Skip → Allow access → Allow).
3. Kill like LMK (no onDestroy): `adb shell run-as com.wife.recommend.music kill <pid>` (`am kill` does nothing while the media service holds the process).
Widget code: `app/src/main/java/com/wife/recommend/music/widget/`; push path `audio/.../service/surface/PlaybackSurfaces.kt`.
