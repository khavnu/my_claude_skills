---
name: linux-device-testing
description: On the Linux workstation adb/emulator paths differ from CLAUDE.md (Mac); how to drive + kill the app for device checks
metadata:
  node_type: memory
  type: reference
  originSessionId: 27ccde43-719f-4759-8157-77c6314d8ec6
  modified: 2026-09-30T08:47:18.846Z
---

Verified 2026-09-30 on the Linux box (CLAUDE.md paths are macOS-only):
- `adb` is not on PATH → `~/Android/Sdk/platform-tools/adb`; emulator `~/Android/Sdk/emulator/emulator`; Gradle works with system JDK 21 (no JAVA_HOME needed).
- 2026-10-01: user asked to test on the physical Pixel 9 only; the emulators are busy with their other tasks. Do not install on or drive `emulator-*` unless the user says so.
- AVDs here: `Pixel_9` (API 36, sdk_gphone64_x86_64, production image — no root) and a user-made Pixel 2 API 27 (Google Play image → `adb root` refused). Both show up as `emulator-5554`, so check `getprop ro.build.version.sdk` before assuming which one.
- Physical Pixel 9 `47231FEAQ001B9` (API 37, same 1080x2424 as the AVD, same tap coordinates): user approved it for this app on 2026-10-01 (pm clear, clock/zone/app-locale changes, restore afterwards). It is also used by another project's instrumentation tests (`com.audioseparation.lyrics.whisper.test` took the foreground on 2026-09-30), so check the top activity is free before driving it, and ask again if unsure.
- Per-app locale without touching the user's system language: `cmd locale set-app-locales com.tmedilab.drink.water2 --locales ar` (reset with no `--locales`) — good for RTL checks. Startup flicker: `screenrecord --time-limit 4` while launching, then `ffmpeg -vf fps=10,...,tile=` contact sheet.
- Process-death repro: `am kill` does NOT kill the app; use `adb shell run-as com.tmedilab.drink.water2 kill <pid>` (debug build), then relaunch.
- Non-exported ReminderAlarmReceiver can't be broadcast from shell; fire a reminder by adding a slot 2–3 min ahead in Reminder schedule and polling `dumpsys notification`.
- Change device clock without root: `adb shell cmd alarm set-time <epochMs>` works (sends TIME_SET); `cmd time_detector suggest_manual_time` is refused for shell. First `cmd time_detector set_auto_detection_enabled false`, and set it back to `true` afterwards to restore real time.
- Change zone: `adb shell cmd alarm set-timezone America/New_York` (restore `Asia/Ho_Chi_Minh`). Read the armed reminder: `dumpsys alarm | grep -oE "type 0 origWhen [0-9]+ [^}]*com.tmedilab.drink.water2"` — API 36 prints `origWhen <ms>` and has no "Pending alarm batches" header; API 27 prints `when <ms>`.
- UI driving: `uiautomator dump` + grep text/bounds; onboarding = LET'S GO then NEXT ×4 (then wait ~5 s for save).
