---
name: project-no-db-migrations
description: WMusi is unreleased — schema changes need no Room migration; bump the version and reinstall
metadata:
  type: project
---

The user said on 2026-10-05: "không cần migrate DB, nếu DB thay đổi thì cứ xóa app cài lại là được".

**Why:** the app has not shipped, so no user data needs to survive a schema change. Writing and testing Migration classes is wasted effort.

**How to apply:**
- On a Room schema change, bump the version. Use a destructive fallback if the database builder needs one; do not write `Migration` classes or migration tests.
- Tell the user to reinstall, or uninstall first on the emulator.
- Revisit before the first release. At that point a real migration path (or a schema reset) is needed for existing installs. The existing library.db `MIGRATION_1_2` predates this rule.
