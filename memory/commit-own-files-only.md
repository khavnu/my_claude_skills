---
name: commit-own-files-only
description: "WMusi checkout is shared with a parallel session — never `git commit -a`/`add -A`/`-u`/`.`; stage explicit paths and check `git diff --cached --stat`"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 678bed06-f868-4b70-8a61-2c5ea66a1a94
  modified: 2026-10-05T07:23:09.603Z
---

Never use `git commit -am`, `git add -A`, `git add -u` or `git add .` in WMusi. Stage only the files this session edited (`git add docs/design/x.md`), then run `git diff --cached --stat` and confirm it lists only those files before committing.

**Why:** 2026-10-05 a design-only session committed with `git commit -qam` five times. Commits c346139, 1bab1e5, c507e1f, 5966f01 and b17b279 pulled in another session's half-finished code (wmusi-09's agents, up to 38 files). b17b279 was pushed and does not compile. wmusi-09 reported it and asked for explicit paths only.

**How to apply:** this applies whenever another WMusi session may be live (`ListAgents` shows `wmusi-*`), which is normal here. Relates to [[commit-after-each-step]] (its snapshot recipe with `git add -A` is only for this session's own tree, and only when no other session shares it).

2026-10-07 pitfall (my own): staging "everything in git status except .idea" after a subagent finished swept an unrelated in-progress edit (docs/features/karaoke/lyrics_improve_idea.md, a typo "Sihông") into widget commit 6295d32; reviewer caught it. Fixed by restoring the old blob in the index only (`git update-index --cacheinfo 100644,$(git rev-parse <c>^:<f>),<f>` + commit), working copy untouched. Rule: stage ONLY the files the agent's report lists (or that live under the task's own packages), never the whole status.
