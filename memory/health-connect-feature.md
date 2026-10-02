---
name: health-connect-feature
description: Health Connect sync (commit fda4635, 2026-10-02): user decisions, review minors still open, and a test gotcha hit while building it
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
