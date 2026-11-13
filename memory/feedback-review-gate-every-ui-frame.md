---
name: feedback-review-gate-every-ui-frame
description: "Run create-design's Review Gate (contrast, focal point, states) on every new UI frame as it's built, not only on polish/final passes"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 527d62c9-e35e-41ee-81ec-f9b0dec21ae6
  modified: 2026-10-12T08:17:09.648Z
---

2026-10-12: built ~40 new Figma frames across 3 requests in one session (5.6 "Your lyrics" editor + Search-online flow, 4.27, 4.28) without running `create-design`'s Review Gate once — no `blur_test.py`, no `contrast.py` — even though several were real new UI, not just spec notes (the Search-lyrics WebView screen, the Import-lyrics sheet, the collapsing-header keyframes). Caught only when re-reading the `design-critique` skill the user pasted for an unrelated opinion ask, not during the work itself.

User, when asked whether to run it retroactively on those ~40 frames: "bước áp dụng review gate để lần sau đi bạn" — explicitly deferred for this batch, not asking for a retroactive pass.

**Why:** treating a request as "mostly spec/documentation" is not a reason to skip the gate — several frames in a "spec" request are still real, judged UI. Catching this after the fact instead of during the build is the failure, not the missed frames themselves.

**How to apply:** next time new Figma UI is built (not just text/rule updates to existing frames), run the Review Gate — at minimum contrast + consistency + states — as each frame is finished, same turn, not deferred to a later polish pass. See `~/.claude/skills/create-design/SKILL.md` Review Gate table and `scripts/contrast.py` / `scripts/blur_test.py`. Related: [[wmusi-figma-bulk-transform-pitfalls]].
