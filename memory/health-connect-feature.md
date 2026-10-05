---
name: health-connect-feature
description: Health Connect write (fda4635) + read of other apps' drinks (d7b1f89), 2026-10-02: decisions, open minors, test gotcha
metadata:
  type: project
---

Committed as `fda4635` on branch `fixbugs` (2026-10-02). Plan: `~/.claude/plans/2026-10-02-health-connect.md`.

Review minors still open (an opus reviewer flagged them; the user has not asked for fixes):
- M3: `requestWritePermission` returns false when there is no launcher, so the VM shows PERMISSION_DENIED although no screen was shown.
- M4: process death while the permission screen is up → the permission is granted but the sync flag stays off.
- M5: `clientRecordVersion` follows the wall clock and is not persisted; a clock set back can lose an edit.
- M6: `readGranted` treats a transient IPC failure as "not granted".
- M7: redundant `return` in the `startActivity` catch; `finish()` called twice in `HealthPermissionRationaleActivity`.
- M8: import order in `HomeViewModel.kt`, `AppModule.kt` and `ReminderRow.kt`.
- M9: `privacyPolicyUrl = about:blank` blocks the Play release.

Decisions made by the user: Settings "Health Connect" switch row below "Intake goal"; write-only, no backfill (tentative until the iOS `HealthKitManager.swift` source is checked; the source is not on the Linux box); switching off = stop writing, nothing is revoked; no permission prompt on first launch; the iOS flow stays unchanged (the stub returns `NOT_INTEGRATED`, so the row is hidden); privacy policy = `about:blank` placeholder (`AppLinks.privacyPolicyUrl`).

**Why:** the user asked for parity with WaterMinder without touching iOS.
**How to apply:** before commit or release, check that the Play health declaration and a real privacy URL are tracked.

Test gotcha (cost one debug cycle): `TestScope.advanceUntilIdle()` does not run coroutines launched in `backgroundScope`. A class under test that launches on an injected scope must get `this` (the TestScope), or the "nothing happens" tests pass vacuously. Verify by checking that the positive tests fail first.

Related: [[competitor-apps-survey]] [[linux-device-testing]]

Read side, commit `d7b1f89` (plan `~/.claude/plans/2026-10-02-health-connect-read.md`). Other apps' drinks join the intake table (`source_name`, unique `health_record_id`; DB v2 AutoMigration). They count like own drinks, are read-only (the repository refuses edit and delete; the mirror skips them), and are imported on foreground plus right after enabling the switch. The first read covers 30 days; later reads use the Changes API with the token in DataStore; a full re-read drops missing imports. Reading needs READ and WRITE. Source labels resolve via `<queries>` on Health Connect's rationale intents. iOS is untouched: `HealthSync`'s read methods have default bodies (user rule: no iOS changes).
Open review minors (read side):
- M2: the import day uses the device zone, not the record's `startZoneOffset`.
- M3: one transaction per change.
- M4: imports count toward the 15000 ml manual cap (ask the user).
- M6: `readGranted()` has no caller.
- M7: READ is asked again on each off→on after a denial.
- M8: the imported row needs `mergeDescendants` for a11y.
- M10: `room3-patterns.md` still says "keep version 1".
- M11: an intake id can be reused after the migration rebuild.
Open product questions: should imports hide or disappear when the switch is off or READ is lost; how to treat future-dated records.
Device trick: WaterMinder on the Pixel 9 already syncs with Health Connect, so use it as the "other app" (it shows an ad after logging; leave the ad alone).
