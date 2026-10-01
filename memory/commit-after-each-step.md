---
name: commit-after-each-step
description: In WMusi the user authorized committing after every completed step, without asking again
metadata:
  type: feedback
---

On 2026-09-30 the user said: "Có kết quả thì bạn commit, chuyển sang các bước tiếp theo, nhớ commit sau mỗi lần làm xong nhé". In this project, commit (never push) as soon as a step is done and verified: tests pass, and the checklist evidence is updated. Then move on to the next step without waiting.

**Why:** the global CLAUDE.md forbids auto-commit unless the user explicitly asks. The user has now asked, as a standing instruction for WMusi.

**How to apply:** one commit per completed checklist group or step, with the attribution trailer. Keep IDE files (.idea/) out. Pushing still needs an explicit request.
