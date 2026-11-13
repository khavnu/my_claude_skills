---
name: project-frozen-locale-configuration
description: FullScreenActivity wraps the base context with LocaleManager.setLocale (createConfigurationContext), so resources.configuration and Compose LocalConfiguration never see a rotation in an Activity with configChanges (the video player).
metadata:
  type: project
---

`FullScreenActivity.attachBaseContext` → `LocaleManager.setLocale(base)` → `createConfigurationContext(config)`: the context's configuration is frozen at creation. Activities that recreate on rotation (MainActivity, widget config) are fine. `SimpleVideoPlayerActivity` has `configChanges=orientation|screenSize|...`, so inside it `LocalConfiguration.current` / `resources.configuration` keep the creation size after a rotation (logged 2026-10-23: device landscape, Compose read w=411 h=923).

Fixed for the player only in aa52563e2: `liveScreenConfiguration(frozen, reported)` from `onConfigurationChanged` is provided as `LocalConfiguration` around the player's Compose content (`LiveScreenConfigurationTest`). LocaleManager itself untouched (app-wide).

**Correction 2026-11-04 (verified on device):** a sheet drawn by the shell layer of the player (`ShellSheetLayer` in `AdsActivity.setShellContent`, OUTSIDE the live provider) still picks the right presentation after every rotation: side panel in landscape, bottom sheet in portrait — Huawei API 28 and emulator API 36, player created in portrait and in landscape, checked with uiautomator bounds of `design_bottom_sheet` (temporary trigger, reverted). So the root composition's `LocalConfiguration` does follow rotations; what stays frozen is `resources.configuration` (and possibly a nested window's own composition). Do not "fix" code for a frozen configuration without reproducing it first.

**How to apply:** any new Compose code in a configChanges Activity must not trust `LocalConfiguration`/`resources.configuration` unless it sits inside that provider. Symptom: sheets choose the wrong presentation after rotating, sizes computed from the old orientation.

Related: [[reference-emulator-screenshot-capture]]
