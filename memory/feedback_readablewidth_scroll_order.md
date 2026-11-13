---
name: readablewidth-scroll-order
description: "In landscape, verticalScroll placed after readableWidth only scrolls the centred column; put the scroll first. Compose UI tests do not catch it, check on a device."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3eb82f20-c3e8-4cda-8e47-e6cee19550cd
  modified: 2026-11-06T02:39:00.012Z
---

`Modifier.readableWidth(layout)` (ui/layout/WindowLayout.kt) narrows a form to a centred 640dp column in landscape. If `.verticalScroll(...)` comes after it, only that column takes the swipe and the empty sides do not scroll (ticket 2083, fixed 50c9182e6 for the scan screens). Write `.fillMaxWidth().verticalScroll(state).readableWidth(layout)`.

**Why:** QC filed it on Scan music/video; the same order still sits (2026-11-06) in ConverterContent.kt:97, SettingsContent.kt:64, SendFeedbackContent.kt:107, SettingAudioFocusContent.kt:59, ChangeCoverScreen.kt:192.

**How to apply:** check this order whenever a landscape form scrolls. Verify on a real device: uiautomator `scrollable="true"` bounds show the scrolling part (Pixel 9 old: x 459..2139 of 2424), then `adb shell input swipe` in the side margin. Two androidTests (a side-margin swipe with performTouchInput, and the hasScrollAction node's boundsInRoot) both PASSED on the broken code, so they prove nothing here.
