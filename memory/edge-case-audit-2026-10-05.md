---
name: edge-case-audit-2026-10-05
description: "Whole-app Android edge-case audit (9 categories, 4 read-only agents) on 2026-10-05 at commit 2e28bdf — open gaps list, none fixed yet"
metadata:
  node_type: memory
  type: project
  originSessionId: 1375ffce-5fdb-40cc-b1aa-ac55e5d9cb0c
  modified: 2026-10-05T03:47:24.069Z
---

Audit on 2026-10-05 at `2e28bdf` (branch `fixbugs`) with the `edge-cases` skill. Nothing fixed; user has not chosen what to fix. Re-check a finding by opening the cited file before acting — line numbers drift.

Self-verified by reading the code:
- H: process death on the onboarding result overlay → Welcome again. `rememberNavBackStack` restores `[OnboardingKey]` (`feature/root/RootRoute.kt:72`), and `OnboardingViewModel` never reads `onboardingDone` (its init only collects the time format).
- M: re-granting notifications after the day's last slot cancels tomorrow's alarm. `DefaultReminderSyncer.start()` combines a list computed at midnight (`ComputeUpcomingRemindersUseCase` recomputes only on slot/sound/day change) with the permission state; GRANTED re-emits it, every entry is past → `cancelAll`.

Agent-traced, not re-checked by me:
- M: `fallbackToDestructiveMigration` still on at DB v2 with `allowBackup=false` → a downgrade or a v3 without a migration wipes history. Afterwards Home has no cups (only onboarding seeds them).
- M: going to another app (HC permission, mail, Play) counts as an app open → rate sheet over Settings.
- M: the 12/24h setting and the HC row go stale in split screen (refresh only in `onResume`).
- M: rate-sheet Feedback with no mail app does nothing but saves "No thanks".
- M: HC imports older than `start_date` are left out of History averages but shown in the week strip.
- M: a11y: wheel picker has no semantics; the onboarding Back button has no label; the result overlay does not block TalkBack or touches.
- M: onboarding answers are lost on process death (no saved state).
- Low: sound previews overlap or leak (`AndroidSoundPreview`); preview ignores silent mode; no `ActivityNotFoundException` guard when opening the channel settings; fixed-height Settings header clips at 200% font; "1 times a day" (no plurals); `forceDarkAllowed` not set.
- Revoking exact alarms leaves no alarm until the app is next opened (PLAUSIBLE, no broadcast).

Related: [[reminder-alarm-lateness-deferred]] [[health-connect-feature]] [[rtl-deferred]]
