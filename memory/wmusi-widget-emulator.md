---
name: wmusi-widget-emulator
description: "How to put the WMusi home-screen widget on the emulator and kill the process like LMK, verified 2026-10-06"
metadata:
  node_type: memory
  type: reference
  originSessionId: 0214ff0b-00b4-4d3c-917b-046af069925c
  modified: 2026-10-08T19:40:27.813Z
---

Verified 2026-10-06 on emulator-5554 (Pixel launcher, API 36), scripted with `uiautomator dump` + `input tap`:
1. HOME, long-press empty area (`input swipe 540 1500 540 1500 1200`) → tap "Widgets" → tap "Search" → `input text WMusi` → tap the "WMusi" result row → tap the preview → tap "Add". Then press BACK once to leave the resize frame, otherwise taps on the widget do nothing.
2. `:app:connectedDebugAndroidTest` uninstalls the app → onboarding + audio permission again after `installDebug` (Skip → Allow access → Allow). If the Widgets picker shows no WMusi entry at all, the app got uninstalled by an earlier connectedAndroidTest run and was never reinstalled — `adb install app-debug.apk` first.
3. Kill like LMK (no onDestroy): `adb shell run-as com.wife.recommend.music kill <pid>` (`am kill` does nothing while the media service holds the process).
Widget code: `app/src/main/java/com/wife/recommend/music/widget/`; push path `audio/.../service/surface/PlaybackSurfaces.kt`.

Verified 2026-10-09 on emulator-5558 (Nexus launcher, Pixel_2 AVD, API 27): long-press empty area →
menu is "WALLPAPERS / WIDGETS / HOME SETTINGS" (tap "WIDGETS", not "Widgets" as a submenu item).
**No search box on this launcher** — the picker is one long alphabetical list of every app's
widgets; scroll down (swipe up repeatedly) to "WMusi" between "Settings" and "YouTube". Long-press
the chosen size's preview to start the drag, lift to drop anywhere on the home screen — this opens
WMusi's own Customize screen (background/theme/Sing-button/opacity) with an "Add to home screen"
button, unlike the Pixel launcher's inline resize-frame flow above.
