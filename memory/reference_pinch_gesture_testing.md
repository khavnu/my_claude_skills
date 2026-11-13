---
name: reference-pinch-gesture-testing
description: Two-finger gestures (pinch zoom) cannot be injected through adb on these devices; drive them from an androidTest instead.
metadata:
  node_type: memory
  type: reference
  originSessionId: 3eb82f20-c3e8-4cda-8e47-e6cee19550cd
  modified: 2026-11-06T02:14:05.944Z
---

Tried 2026-11-06 (ticket 2081, video pinch zoom), all dead ends:
- `adb shell input` has no multitouch.
- `sendevent /dev/input/event2` on the Pixel_9 AVD: "Permission denied" (google_apis image, no root).
- Emulator console `adb emu event send EV_ABS:ABS_MT_SLOT:0 ...` accepts the events (sync code must be `EV_SYN:0:0`, `SYN_REPORT` is rejected), but the app never saw a pinch.
- Pixel 9: no root, no console.
- The emulator's software decoder also garbled the test video (colour stripes) after a while.

What works: an androidTest that inflates the real view (`R.layout.layout_video_player_surface`) in `ActivityScenario.launch(ComponentActivity::class.java)` and dispatches multi-pointer `MotionEvent.obtain(...)` sequences (DOWN, POINTER_DOWN, MOVEs, POINTER_UP, UP). See `app/src/androidTest/.../feature/video/CustomPlayerViewZoomTest.kt`; it ran on the emulator and on the Pixel 9. For a full-app check, ask the user to do the pinch by hand and then capture with screencap.
