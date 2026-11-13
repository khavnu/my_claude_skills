---
name: reference-zflip3-device-test
description: "Samsung Z Flip 3 (SM-F711B, API 35, 1080x2640, 3.0x) device test quirks — two displays break screencap, cover display in dumpsys, USB drops when folding."
metadata:
  node_type: memory
  type: reference
  originSessionId: 043a86db-918e-4a0d-9fdc-1525c32e6db3
  modified: 2026-11-11T09:04:59.934Z
---

Verified 2026-11-11 (ticket 2111, floating window).

- Serial `R5CT42E8HCJ`. Main screen 1080x2640, density 480 (3.0x): 594px = 198dp, so dp minimums (e.g. the floating controls' 200dp) bite here first.
- Two displays: plain `adb exec-out screencap -p` writes an unreadable file. Get the main id with `adb shell dumpsys SurfaceFlinger --display-id` (first line, "HWC display 0") and use `screencap -p -d <id>`.
- `dumpsys window displays | grep cur=` can return the COVER display (512x260) first; do not derive tap coordinates from it — find views with uiautomator bounds instead.
- The USB link dropped once right after authorizing; re-plug with the phone unfolded, File transfer mode.
- Floating window overlay is NOT in uiautomator dumps: read its frame from `dumpsys window windows | grep APPLICATION_OVERLAY` (`mAttrs={(x,y)(wxh)`), as on the Realme.
