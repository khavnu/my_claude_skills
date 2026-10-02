---
name: competitor-apps-survey
description: How competing drink-water apps on the Pixel 9 schedule reminders and sync with health apps (surveyed 2026-10-02)
metadata:
  node_type: memory
  type: reference
  originSessionId: 1375ffce-5fdb-40cc-b1aa-ac55e5d9cb0c
  modified: 2026-10-02T03:00:58.129Z
---

Surveyed 2026-10-02 on Pixel 9 `47231FEAQ001B9` (API 37) via `dumpsys package` / `dumpsys alarm` / UI driving. Re-check with `adb shell dumpsys alarm | grep -A3 <pkg>`.

- Health: only WaterMinder (`com.funnmedia.waterminder`) uses Health Connect — READ/WRITE_HYDRATION; one HydrationRecord per drink (start = end time), deleting the drink deletes the record. It also offers Fitbit (OAuth WebView) and Samsung Health. Water Time (`com.mobilecreatures.drinkwater`) uses legacy Google Fit. Others: none.
- WaterMinder Health Connect states (from a jadx decompile of v5.10.10, `HealthConnectActivity`, `ze4.HCAllowPermissionView`, `vf4.HCInstallPromptDialog`). The Settings row is always shown. `getSdkStatus` 3 (available) or 2 (update required) shows the ALLOW screen; ALLOW on status 2 opens a dialog with "Health Connect app is either not installed or needs to be updated. Install or update Health Connect from the play store." and buttons Cancel / Install (`https://play.google.com/store/apps/details?id=com.google.android.apps.healthdata`). The status is re-checked in onResume. Status 1 (unavailable) renders an empty screen.
- Reminders: all 7 declare SCHEDULE_EXACT_ALARM, and 4 of them ask the user for it (WaterMinder, Watercat, klstudios, highsecure); none forces it. WaterMinder asks during onboarding and arms one exact alarm per slot for about 24h (`window=0 exactAllowReason=permission`).
  - Water Time: USE_EXACT_ALARM, 10 alarms armed ahead (`flags=0x5`).
  - ascendik: forces a battery-optimisation exemption before reminders can be switched on, which makes its alarms exact (`exactAllowReason=allow-listed`).
  - watertracker: inexact `flags=0x20` (window about 1h) plus a WorkManager backup job.
- Watercat (water.drink.reminder.tracker): asks for exact alarm later, through a "may not arrive on time" banner with a FIX button; `0x5`, about 2 days armed ahead.
- klstudios: one onboarding screen for exact alarm, notifications and full-screen intent; can be skipped (with a warning); without exact alarm, `0x20` window 45m.
- highsecure: bottom sheet with an X during onboarding that opens the global "Alarms & reminders" list; `setAlarmClock` (`0x3`), 8 rolling alarms.
- None of the 3 above has health sync. The full write-up is the user's doc "Drink water apps — Health & Reminder survey": https://claude.ai/code/artifact/184c371c-308a-4c60-9bd2-d18a72c55338

Related: [[reminder-alarm-lateness-deferred]]
