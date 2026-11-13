---
name: feedback-proposal-includes-problem
description: "When proposing or reporting a fix, restate the problem itself (what the user sees, where, when) — never just a code like \"N1\" or \"H3\"."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3eb82f20-c3e8-4cda-8e47-e6cee19550cd
  modified: 2026-11-03T09:40:21.279Z
---

Every fix proposal / "làm tiếp X?" / done-report must carry the problem's content, not only its label: what the user sees, on which screen/sheet, under which conditions (orientation, language, device/API), and the cause in one line if known. Labels like "N1", "H3", "mục 2" may appear, but only next to that description.

**Why:** the user (2026-11-03, landscape side-panel audit) had to scroll back to find what "fix N1" meant; labels coined earlier in a long session are not memorable.

**How to apply:** in option lists and next-step offers write e.g. "N1 — thanh điều hướng Huawei (API 28) kẹt sáng ở cạnh phải sau khi đóng side panel, che Settings/A–Z" instead of "N1". Same for commit-ready summaries.
