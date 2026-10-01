---
name: reminder-alarm-lateness-deferred
description: Inexact reminder alarm can fire hours late; fix deferred on 2026-09-30 until a tester reports it; preferred design = silent checkpoint alarms
metadata:
  node_type: memory
  type: project
  originSessionId: 27ccde43-719f-4759-8157-77c6314d8ec6
  modified: 2026-09-30T09:59:36.248Z
---

`AndroidReminderScheduler` arms one `setAndAllowWhileIdle` alarm for the next slot. The OS window is 75% of the distance to the trigger: measured on API 27, alarm 1h11m away had `window=+53m44s` (`dumpsys alarm`). A 07:00 alarm armed at 22:00 may fire ~13:45.

**Why:** user decided on 2026-09-30 to leave it until a tester reports late reminders. `00-decisions.md:29` forbids SCHEDULE_EXACT_ALARM, so any fix must stay inexact unless the user overrides that decision.
**How to apply:** if a tester reports late reminders, the design already explained to and understood by the user is silent checkpoint alarms: `checkpoint = now + remaining / 1.75`, which never overshoots the target even at 75% lateness. Re-arm on each checkpoint; arm the real alarm once remaining ≤ ~12 min. Caveats: the Doze allow-while-idle quota (~9 min) adds lateness; a checkpoint landing at or after the target must post the notification. Alternatives offered: exact alarm when the user has granted it (changes the decision), or `setWindow` (breaks in Doze). The related review finding "a sync drops a due-but-late reminder" (single alarm overwritten) is still open too.
