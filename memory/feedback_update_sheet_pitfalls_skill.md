---
name: feedback-update-sheet-pitfalls-skill
description: "New, device-verified bottom sheet / side panel / dialog window pitfalls go into the global skill compose-sheet-window-pitfalls in the same session."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3eb82f20-c3e8-4cda-8e47-e6cee19550cd
  modified: 2026-11-04T01:31:15.928Z
---

The global skill `~/.claude/skills/compose-sheet-window-pitfalls/SKILL.md` (shared with ~/.claude-k via symlink) collects window-level pitfalls of Compose sheets/side panels/dialogs (landscape, hidden nav bar, notch, API 28-29, Huawei, long locales). When a new one is found AND verified on a device, add a row (symptom, root cause, fix, how verified) to the matching table in the same session; correct or remove rows that turn out wrong.

**Why:** user, 2026-11-04: "sau đó trong quá trình làm nếu phát hiện gì mới sẽ update thêm" — the skill is meant to carry these lessons to other apps.

**How to apply:** load the skill before sheet/dialog/landscape work; after a fix of this kind is verified, edit the skill before reporting done.
