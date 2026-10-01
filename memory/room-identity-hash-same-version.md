---
name: room-identity-hash-same-version
description: "Could not save data" on onboarding = Room schema changed while version stayed 1; fallbackToDestructiveMigration does not cover identity-hash mismatch
metadata:
  type: project
---

Verified 2026-09-30 on emulator: installing the pre-T7 build (60af5fb, had `recording` table) then installing over it with the current build → every Room write throws `IllegalStateException: Room cannot verify the data integrity ... Expected identity hash f7cab1d9..., found 2bd836e5...`. `safeWrite` (`data/SafeStorage.kt`) swallows it → `StorageError.WriteFailed` → "Could not save data" on onboarding step 0 (goal write to `daily_goal`).

`fallbackToDestructiveMigration` only fires when the VERSION differs, not on hash mismatch at the same version. So `room3-patterns.md` "keep version = 1, change schema freely" only holds if the tester uninstalls.

**Why:** safeWrite logs nothing, so the message alone points at 15+ write sites; took a full repro to find.
**How to apply:** when "Could not save data" appears after an update, first check `git log -- shared/schemas` for an identityHash change; repro = install old commit via `git worktree`, open app, install current over it. Temporary `println` in `safeWrite` catch shows the cause in logcat (`System.out`).
