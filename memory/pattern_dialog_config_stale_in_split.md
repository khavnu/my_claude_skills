---
name: pattern-dialog-config-stale-in-split
description: Compose dialog/bottom sheet reads its own window's LocalConfiguration, which stays full screen when the app enters split screen with the sheet open — read Activity-level mode via CompositionLocal (ProvideWindowMode)
metadata:
  type: project
---

Verified 2026-10-28 (ticket #473, emulator Pixel_9 API 36): open a bottom sheet full screen, then enter split screen. Inside the sheet `LocalConfiguration.current.screenHeightDp` stayed 923 and `LocalWindowInfo.containerSize` 1080x2424 while `Activity.isInMultiWindowMode` was true → `checkScreenSizeMode()` read inside the dialog returned Portrait, the Split cap never applied, the sheet went under the status bar. A sheet opened *after* entering split was fine, which is why earlier tests missed it.

Fix in repo: `ProvideWindowMode` wraps the app in `MainActivity.setContent`; `checkScreenSizeMode()`/`isInMultiWindowMode()` read `LocalWindowMode` (ui/component/Orientation.kt), fall back to own configuration when no provider (Previews, UI tests overriding LocalConfiguration). Dialogs inherit the CompositionLocal from the parent composition.

Also: `Activity.isInMultiWindowMode()` is a binder IPC on API 24 (`ActivityManagerNative.getDefault().isInMultiWindowMode(mToken)`), a cached field on API 35+ — check `~/Android/Sdk/sources/android-*/android/app/Activity.java`.

How to apply: any per-window decision made inside a Dialog/ModalBottomSheet must come from the Activity composition, not the dialog's LocalConfiguration. Test by opening the sheet BEFORE entering split. Related: [[pattern-rotation-resets-remember]].
