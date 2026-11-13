---
name: project-soft-input-unspecified-repicks-pan
description: "A window added with no adjust mode re-picks adjustPan on every visibility change (rotation) and overrides a screen's adjustResize — MainActivity now sets the mode in onCreate (ticket 2112)."
metadata:
  node_type: memory
  type: project
  originSessionId: 043a86db-918e-4a0d-9fdc-1525c32e6db3
  modified: 2026-11-12T01:08:36.895Z
---

Ticket 2112 (2026-11-12), fixed in `53f562858`: Huawei nova 3i API 28, edit lyrics in landscape: dragging the cursor slid the whole window under the status bar (adjustPan behaviour) although the screen's chrome is AdjustResize.

Mechanism (read in `~/Android/Sdk/sources/android-24|35/android/view/ViewRootImpl.java`, setLayoutParams + performTraversals): `mSoftInputMode` is captured only when the window is ADDED. If its adjust bits were UNSPECIFIED then, every traversal with `mFirst || mViewVisibilityChanged` re-picks RESIZE (a shown View scroll container) or PAN, and writes it over whatever the app set later. Compose has no View scroll container -> PAN. setSoftInputMode with adjust UNSPECIFIED later keeps the previous adjust ("Don't lose the mode we last auto-computed").

How it was proved: client `window.attributes.softInputMode` stayed 0x10 while the server side (`adb shell dumpsys window windows`, the `ty=1` LoadingActivity window, `sim=#20` on API 27 / `sim={adjust=pan}` on API 35) showed PAN. The visual slide did NOT reproduce on the API 27 emulator (the app's imePadding keeps the cursor above the keyboard); the server mode is the evidence.

**Why:** "the soft input mode is wrong after a rotation / coming back" on old Android looks like a destination-chrome bug; it is this framework rule.

**How to apply:** MainActivity sets `SoftInput.Unspecified.windowMode()` (= ADJUST_PAN, what the system picked anyway) before its window is added, and Unspecified destinations write ADJUST_PAN explicitly, never 0. A new Activity/host that switches modes per screen needs the same. Check with dumpsys `sim=`, not `window.attributes`.
