---
name: wmusi-emulator-rotation-pitfall
description: Emulator stays landscape for tests after a user_rotation=1 run even when the setting reads 0 — reboot; plus per-class runner + hung gradle pitfalls
metadata:
  node_type: memory
  type: project
  originSessionId: e7439767-dcde-4ea8-b28d-b211a6457f14
  modified: 2026-10-12T01:24:18.461Z
---

Verified 2026-10-12 on emulator-5554 (Pixel_9, API 36):

- After `settings put system user_rotation 1` (landscape test pass), putting it back to 0 — and even
  `cmd window user-rotation lock 0` — did NOT stick: every test activity still rotated to landscape
  (logcat `Display id=0 rotation changed to 1 … userRotation=1`), so a "portrait" run silently ran in
  landscape (DetailScreensTest 11/22 red). Home stays portrait (launcher orientation 5) and hides it.
  Fix that worked: set user_rotation 0 + accelerometer_rotation 0, then `adb reboot`.
  Check: `adb logcat -d | grep "rotation changed"` while a test runs.
  → Run the portrait pass BEFORE the landscape pass; reboot after a landscape pass.
- `timeout 600 ./gradlew connectedDebugAndroidTest` hung 2.5 days (machine sleep) holding
  /tmp/wmusi-emulator.lock; use `timeout -s KILL` and kill the BUSY gradle daemon (`./gradlew --status`).
- One full `connectedDebugAndroidTest` in landscape hung with no results at all → run per class
  (scratchpad runner `f2-per-class.sh` pattern: flock per class, copy XML, summary line).
- `until ! pgrep -f "<pattern>"` loops never end: pgrep matches the loop's own bash -c command line.

Related: [[wmusi-device-verify]], [[wmusi-adb-shell-loop-pitfalls]].
