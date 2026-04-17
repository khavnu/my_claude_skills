---
name: Skip git operations
description: User handles all git commits/pushes manually — never attempt git commit or push
type: feedback
---

Never run git commit, git push, or any git write operations. The user does all git operations themselves.

**Why:** Project hook blocks automated commits anyway; user prefers full control over git history.

**How to apply:** In all subagent prompts and direct work, skip all git steps. Do not include commit commands in subagent task descriptions. Do not ask the user to run commit commands.
