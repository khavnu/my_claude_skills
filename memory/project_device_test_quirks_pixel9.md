---
name: project-device-test-quirks-pixel9
description: "Pixel 9 (API 37) device-test quirks for this app — connectedAndroidTest uninstalls the app, can report success on failed install; am kill blocked by music service."
metadata:
  node_type: memory
  type: project
  originSessionId: d769ac83-42d0-49ee-81b3-e5debe426f39
  modified: 2026-10-21T11:01:56.971Z
---

Verified 2026-10-21 during the CropImage work (Pixel 9 serial 47231FEAQ001B9, API 37):
- `connectedDebugAndroidTest` uninstalls the app at the end → any installed build (incl. a release smoke build) and its data are gone; do device walks BEFORE connected tests.
- Gradle can print BUILD SUCCESSFUL even when the test APK install failed → read counts from `app/build/outputs/androidTest-results/connected/debug/*.xml`.
- `adb shell am kill com.amapps.media.music` does nothing while music plays (foreground service); simulate process death with `adb shell run-as com.amapps.media.music kill -9 <pid>`.
- Compose UI tests on API 37 need espresso ≥ 3.7.0 (fixed in commit "Shared: Bump espresso to 3.7.0").
- Lite mode (≤ 3 GB RAM) hides the crop entry points; the only API < 28 AVD here (Pixel_2, API 27, 32-bit) can't reach them from the UI.
- A subagent's `git stash` / `stash pop` silently dropped a staged `git rm` (90 ucrop files stayed tracked) → after any deletion commit check `git ls-files <dir> | wc -l`.
- (2026-10-22) The Pixel 9 is SHARED with another project's session (~/AndroidStudioProjects/WMusi, package com.wife.recommend.music) that runs connected tests under `flock /tmp/wmusi-pixel9.lock`. Wrap every adb/install/connected command of ours in `timeout N flock /tmp/wmusi-pixel9.lock ...`, otherwise screenshots catch their test Activity (verify: `ps aux | grep wmusi-pixel9.lock`).
- (2026-10-22) `-Pandroid.testInstrumentationRunnerArguments.class=A,B` ran only class A (3 tests instead of 9): run one class per invocation and read the counts from the result XML.
- (2026-10-22) Connected tests CANNOT run on this Pixel 9 while app widgets are placed: the widget update broadcast reaches the test process and `TestMusicApplication` (no Hilt component) crashes in `BaseWidget.widgetUpdater` — and Gradle still uninstalls the app, wiping the user's widget placements and data (happened once, landscape work). Run connected tests on the emulator only; ask before any connected run on a real device.
- (2026-10-23) Rotating the REAL Pixel 9 for landscape checks: `cmd window user-rotation lock 0|1` works (device default is auto-rotate, `accelerometer_rotation`=1); restore after with `cmd window user-rotation free` + `settings put system accelerometer_rotation 1`. An app-open / interstitial ad forces portrait and the display stays ROTATION_0 after it closes; re-lock before the next capture. Back on a Main tab opens the quit sheet, a second Back leaves the app.
