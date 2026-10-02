---
name: subagent-model-policy
description: WMusi — user OK'd using higher model/effort for subagents when a task needs it (2026-10-02); which tier for which role
metadata:
  type: feedback
---

2026-10-02 the user said: "Ok bạn, áp dụng Model, effort cao hơn cho các task nếu cần nhé" (after I proposed the split below).

**Why:** in the visualizer milestone, Sonnet implementers needed a full fix round on concurrency/IO work (Task 4 decoder + cache: 3 Important findings), while UI/port tasks were fine on Sonnet. A fix round costs ~7–15 min + a re-review; the model price difference is cheaper than that.

**How to apply:**
- Implementer on **Opus** for tasks heavy on concurrency, playback/service lifecycle, MediaCodec/IO, Flow cancellation, or anything a fix round would be expensive to redo (e.g. Now Playing ↔ player wiring, sleep timer).
- Implementer on **Sonnet** for UI, ports, mechanical changes.
- Reviewer on Sonnet; scoped re-review of a small diff (< ~300 lines) on **Haiku**, Sonnet if the fix has subtle logic.
- Final whole-branch review on Opus (it caught the Back-pops-wrong-entry crash in the detail milestone).
- Controller stays on the session model; `/fast` is the user's toggle, not mine.
