---
name: locale-default-reset-by-ads
description: "Locale.getDefault() drifts back to the system locale after an interstitial (WebView) and on config changes; format numbers with AppLanguage.current(), not Locale.getDefault()."
metadata:
  node_type: memory
  type: project
  originSessionId: 3eb82f20-c3e8-4cda-8e47-e6cee19550cd
  modified: 2026-11-09T03:54:36.680Z
---

Ticket 2096 (2026-11-09): with the app language set to Arabic in Settings, closing an AdMob interstitial on Huawei INE-LX2r (API 28) turned the Home list durations from `٠١:٥٣` to `01:53` and the ad label to English: the ad's WebView put the system locale back into `Locale.getDefault()` without any `onConfigurationChanged`. Android's ResourcesManager does the same on every process configuration change. Activities only re-apply the language in `attachBaseContext` (LocaleManager).

Fix in place: `utils/AppLanguage` (written by `LocaleManager.updateResources` / `applyDefaultLocale`) is the default locale of the time formatters (`toDisplayTime`, `convertToReadableTime`, `MiscUtils.convertToReadableTime`, `ProgressState`); `MusicApplication` re-applies the default in `onCreate`, `onConfigurationChanged` and on every activity resume (`AppLanguageOnResume`).

**Why:** the drift is timing-dependent (needs an interstitial), so it looks like a device-specific bug; the API 36 emulator shows Latin digits for `ar` anyway, so only an older device (Huawei) shows the Arabic-Indic digits at all.

**How to apply:** any new locale-sensitive formatting (numbers, dates) → pass `AppLanguage.current()` (or `currentAppLocale()` in Compose), never rely on `Locale.getDefault()`. Verify on Huawei: app language Arabic, Home list, open the player until an interstitial shows (frequency-capped, ~15 s between tries), close it, re-read `tv_item_song_duration` via uiautomator.
