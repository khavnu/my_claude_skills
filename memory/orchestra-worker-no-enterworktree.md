---
name: orchestra-worker-no-enterworktree
description: "An /orchestra worker must not switch into its worktree with EnterWorktree — the isolation blocks writing the session file in main's .claude/orchestra/"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 632e030a-f8cd-4905-909a-47586e011f2e
  modified: 2026-10-05T07:42:02.873Z
---

As an `/orchestra` worker, never call `EnterWorktree` on the task's worktree (even when the user says "chuyển đến folder này"). Stay in the launch dir and work by absolute path: `git -C <worktree>`, `cd <worktree> && ./gradlew …` in one command.

**Why:** verified 2026-10-05 (T-1 trash): after `EnterWorktree(path=WMusi-wt/trash)` the Write to `/home/khapv/AndroidStudioProjects/WMusi/.claude/orchestra/sessions/T-1-trash.md` was refused ("isolated in the worktree … edit the worktree copy"), and compound `git` commands were refused too. Had to ask the user, then `ExitWorktree(keep)`.

**How to apply:** on `/orchestra join`, if the session is not already opened inside the worktree, use the skill's absolute-path mode directly. Related: [[commit-own-files-only]], [[wmusi-device-verify]].
