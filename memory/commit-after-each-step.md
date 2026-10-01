---
name: commit-after-each-step
description: "WMusi — commit after every verified step; push at the end of each milestone by lifting the push hook temporarily, then restoring it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e7439767-dcde-4ea8-b28d-b211a6457f14
  modified: 2026-10-01T10:23:59.676Z
---

2026-09-30 the user said: "Có kết quả thì bạn commit, chuyển sang các bước tiếp theo, nhớ commit sau mỗi lần làm xong nhé". In this project, commit as soon as a step is done and verified (tests pass, checklist evidence updated), then move on without waiting.

2026-10-01 (updated) the user added: "sau khi xong sẽ commit, gỡ hook push tạm thời và push lên nhé, sau đó revert push hook — Sau đó sẽ chuyển sang task khác, quy trình vẫn như thế (tự động commit, push...)". So at the end of each milestone/task: commit, push, move to the next one — standing instruction, no need to ask again.

**Why:** the global CLAUDE.md forbids auto-commit/push unless the user explicitly asks; the user has asked, as a standing instruction for WMusi.

**How to apply:**
- One commit per completed step, attribution trailer, keep `.idea/` out.
- Push: the PreToolUse Bash hook in `~/.claude/settings.json` blocks any command whose text matches `git\s+(push|reset\s+--hard|…)` — even a grep for the words. To push: remove `push|` from that regex, run the push, then put `push|` back immediately and check the file is identical to before (diff against a copy). Never leave it lifted.
- The same hook's commit branch did not block commits in WMusi (verified 2026-10-01 with `git commit --dry-run`, exit 0).
