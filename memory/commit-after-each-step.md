---
name: commit-after-each-step
description: "WMusi — commit after every verified step and push per milestone (hooks for commit/push removed by the user 2026-10-02; destructive-op guard kept)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e7439767-dcde-4ea8-b28d-b211a6457f14
  modified: 2026-10-02T10:19:44.804Z
---

**Current rule (2026-10-02, latest):** the user asked me to remove the PreToolUse hook's commit and push blocks. Quote: "bạn gỡ các hook về chặn commit và push cho tôi nhé, tôi sẽ báo bạn bổ sung lại khi cần". Done: the hook in `~/.claude/settings.json` now blocks only destructive local ops (`reset --hard`, `checkout .`, `restore .`, `clean -f`, `branch -D`). The backup from before the change is in this session's scratchpad (`settings.before-unhook.json`). The standing WMusi instruction from 2026-09-30/10-01 applies again: commit after each verified step, push at the end of each milestone, and never force-push.

**Why:** the user wants commits to flow again. A short-lived `/collab` flag rule (CLAUDE.md rule 6, flag `~/.claude/collab-active`) had been blocking every commit in WMusi.

**How to apply:**
- One commit per completed and verified step. Add the attribution trailer and keep `.idea/` out.
- When the user says to restore the hooks, put the old block back from the backup and stop committing on my own.
- If a parallel task is mid-edit in the same tree, commit a snapshot without touching the tree: `git add -A -- . ':!.idea'`, then `git write-tree` (save the sha), and later `git commit-tree <tree> -p HEAD -m ...` followed by `git update-ref HEAD <commit>`.
- New Gradle module: add its `/build` `.gitignore` before the first add. 450+ build files slipped in once.
- A parallel design session commits docs in this repo. Leave its commits out of review ranges, and never rewrite them after a push.
