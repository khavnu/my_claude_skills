---
name: reminder-alarm-lateness-deferred
description: Reminder lateness (QA #20/#88): lost-alarm fix 649db13; exact alarms on consent (Watercat banner) built 2026-10-02; Realme still windows exact alarms
metadata:
  node_type: memory
  type: project
  originSessionId: 27ccde43-719f-4759-8157-77c6314d8ec6
  modified: 2026-09-30T09:59:36.248Z
---

`AndroidReminderScheduler` arms one `setAndAllowWhileIdle` alarm for the next slot. The OS window is 75% of the distance to the trigger: measured on API 27, alarm 1h11m away had `window=+53m44s` (`dumpsys alarm`). A 07:00 alarm armed at 22:00 may fire ~13:45. 2026-10-02 on the Pixel 9 (API 37): our 10:30 alarm showed `window=+1h0m flags=0x20`, the same as competitors that use inexact alarms.

**Why:** user decided on 2026-09-30 to leave it until a tester reports late reminders. `00-decisions.md:29` forbids SCHEDULE_EXACT_ALARM, so any fix must stay inexact unless the user overrides that decision.
**How to apply:** if a tester reports late reminders, the design already explained to and understood by the user is silent checkpoint alarms: `checkpoint = now + remaining / 1.75`, which never overshoots the target even at 75% lateness. Re-arm on each checkpoint; arm the real alarm once remaining ≤ ~12 min. Caveats: the Doze allow-while-idle quota (~9 min) adds lateness; a checkpoint landing at or after the target must post the notification. Alternatives offered: exact alarm when the user has granted it (changes the decision), or `setWindow` (breaks in Doze). The related bug "a sync drops a due-but-late reminder" was fixed on 2026-10-02 (`planAlarm` in `platform/PickNextSlot.kt`, FLAG_ONE_SHOT PendingIntent plus the armed reminder in DataStore). Committed as 649db13 on branch fixbugs. Verified on 2026-10-02 on the Realme RMX3710 (`QKOZWW65AIEQP7JJ`, API 35): the PI shows `flags=0x44000000`, and after a delivery or a force-stop the PI is gone. To repro a late alarm: `dumpsys battery unplug` + `am set-standby-bucket <pkg> restricted` holds the alarm about 24h (`policyWhenElapsed app_standby=+23h58m`). Opening the app lifts the bucket to 10, so the held alarm then fires. Run `dumpsys battery reset` afterwards. Also verified on the Pixel 9 (API 37). Correction (2026-10-02): `adb install -r` / an app update does NOT remove the app's alarms or PendingIntents. The old non-one-shot alarm survived and was armed next to the new one, so `cancelLegacyAlarm()` in `AndroidReminderScheduler` cancels it. The user chose to do exact alarms later.

Update 2026-10-02: the user chose the Watercat approach instead of checkpoint alarms. Exact alarms are used when allowed (always below API 31; `SCHEDULE_EXACT_ALARM` from 31 on), and a "Reminders may be late" banner with FIX sits on Reminder schedule (plan `~/.claude/plans/2026-10-02-exact-reminder-alarms.md`; committed as `68f30c2` on `fixbugs`).
Verified facts:
- A revoke stops the app and cancels exact alarms but can keep their FLAG_ONE_SHOT PendingIntent. That is why `ArmedReminder.isExact` exists, and why the grant broadcast calls `onExactConsentGranted()`.
- Pixel 9: exact = `window=0 flags=0x5`.
- Realme/ColorOS: `exactAllowReason=permission flags=0x4` but the window is about 75% of the time left (the user accepted this as an OEM limit). `appops get` there reports "No operations" even when the consent is granted.
Open review minors (the user has not asked for fixes): m2 lint cannot see the API guard behind `exactAlarmsAllowed(sdkInt)`; m3 `InlinedApi` warning in `BootCompletedReceiver`; m4 the banner's FIX button has no TalkBack context and its title is not a heading; m5 the banner shows even when no slot is on (ask the user before gating it); m6 FIX does nothing if both settings intents are missing; m7 style (`var armedExactly` inside `runCatchingPlatform`).
