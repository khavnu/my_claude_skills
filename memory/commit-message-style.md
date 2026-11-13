---
name: commit-message-style
description: QA ticket commits in this repo are subject-only "[Touch: N] Component: Verb ..." with no body and no Co-Authored-By
metadata:
  type: feedback
---

QA ticket fixes are committed as a single subject line: `[Touch: <ticket>] <Component>: <Verb> <thing>` (several tickets: `[Touch: 34, 35]`). No body, no Co-Authored-By line.

**Why:** on 2026-10-15 the user rewrote my three commits (which had bodies + Co-Authored-By) into this form on branch `fix_bugs/fix_32` (12dd05f, 6980c4d, f2cd0b1).
**How to apply:** use this form for every ticket commit here; put explanations in the chat or ticket reply instead of the commit body.
