---
name: feedback_ticket_commit_prefix
description: Commits fixing a dev.tohsoft.com ticket start with "[Touch: <id>] " (several ids comma-separated)
metadata:
  type: feedback
---

A commit that fixes a Codebase ticket is titled `[Touch: <id>] <Area>: <change>`, e.g. `[Touch: 2056] TimePickerBottomSheet: remove wheel background`, `[Touch: 2055, 2053] ...` (see `git log --all --format=%s | grep "Touch:"`).

**Why:** the user corrected a proposed message without the prefix (ticket 2059); Codebase links the commit to the ticket through it.
**How to apply:** every commit/commit proposal for a ticket fix; non-ticket work keeps the plain `<Area>: <Verb> ...` form. Related: [[reference_codebase_api_access]].
