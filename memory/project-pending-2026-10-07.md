---
name: project-pending-2026-10-07
description: Queue of agreed-but-not-started work when the user paused on 2026-10-07 (pick up here next session)
metadata:
  type: project
---

RESUME NOTE (updated 2026-10-08 09:05, 5h limit at 90%, resets 12:50, one-shot resume cron 12:55): done since — wave 5 pushed (5eb790c); Undo→queue slot committed cd92156 NOT pushed; review said NO (3 Important): (1) restoreRemoved scans all 8 removedBatches → stale entries from earlier deletes come back (duplicate / wrong current) — tie Undo to its own removal, prune batches when a song is listed again; (2) setQueue/clear/restore must reset removedBatches + pendingRestoreSongIds (Undo after a new queue hijacks playback); (3) controller must wait until ALL songIds are listed (Room 500-row chunks) — first{containsAll}, fallback to last emission on timeout. Minors: pending ids forever, unbounded batch size, imports order. Fix = one Opus fix round on cd92156 (implementer notes: scratchpad/undoq-report.md), then re-review, build in _review, push; skills: shared protocol written at ~/.claude/skills/_shared/usage-limit-protocol.md and linked from orchestra/long-feature/collab; statusline now writes ~/.claude/usage-latest-{K,D}.json (five_hour/seven_day used % + resets_at); orchestra heartbeat OFF (user: they will say when sessions are needed). Still to do: user-approved skill tweaks (usage-limit as own skill, CLAUDE.md execution-mode table, orchestra 'worker uses other skills' rules, heartbeat hourly + only with workers) — pending user OK on the token-saving version.

User paused after design-audit wave 5 (2026-10-07). Agreed next, in order:
1. Wave 5 was STOPPED mid-way by the user's pause (2026-10-07): ~60 files modified, UNCOMMITTED in the working tree (Now Playing/queue badge, Settings, Licenses, crop, Equalizer preset sheet, Search snackbar, name sheet, VM comment cleanup; it was rewriting a sheet + settings screen at stop). Next session: inspect `git status`/`git diff`, either resume the wave (prompt items A1–A6, B7–B14 in the conversation) or finish what's there; compile all source sets before anything else — the tree may not build. Then review + push.
2. Now Playing Delete → Undo puts the song back in its queue slot; if it was current, current again, resume position + play state (decision recorded in docs/design/audit-2026-10-07-decisions.md).
3. Install origin/main on the Pixel 9 (only when the user asks).
4. Run docs/common_bugs.md groups A–I on emulator-5554 in waves, fix findings (section 0 decisions done: docs/common_bugs-wmusi-decisions.md).
Open user questions: queued song deleted from disk when last → wrap to first?; Huawei pin pending-config; Home tip floating; Delete album semantics (Trash vs permanent, 4.15.22); Theme "Image" needs real photos.
Design-session asks are listed at the bottom of docs/design/audit-2026-10-07-decisions.md.

**Why:** the user asked to stop and rest; this is the agreed backlog so nothing is re-proposed or lost.
**How to apply:** start from item 1; re-check git log first — items may already be done.

**2026-10-08 13:xx:** Undo queue-slot DONE — cd92156 + review fixes cec5dd0 pushed (3 Important + minors; WMusiPlayerTest compiled, not run on device). Next: orchestra wave 1 (T-3 qa-playback, T-4 qa-ux) once the user says to open sessions.
