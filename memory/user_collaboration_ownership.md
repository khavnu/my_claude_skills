---
name: user-collaboration-ownership
description: "User occasionally doubts their own technical contribution when delegating all code-typing to Claude — ground reassurance in concrete evidence, not generic flattery"
metadata: 
  node_type: memory
  type: user
  originSessionId: 4779c242-c814-40eb-a9fe-1458df90f3f9
  modified: 2026-08-22T10:30:52.927Z
---

User (senior Android engineer) delegates ~100% of code typing/implementation to Claude in this
project, but personally makes the real engineering judgment calls — architecture decisions,
catching risks, verifying claims before accepting them. On 2026-08-22, user expressed self-doubt
("giống monkey coder" — feeling like a mindless copy-paste coder) about this workflow, worried
that heavy delegation to AI means their actual skill is low.

**Why**: The worry comes from conflating "who types the code" with "who understands/decides".
Concrete evidence from that session, not flattery: user originated the Stem Mixer feature spec
themselves (N synced ExoPlayer preview, slider, merge button — a real design, not a vague ask);
pushed back to verify causality ("2 progress song song là tránh được OOM bạn nhỉ?") instead of
accepting my explanation at face value; and independently approved re-architecting `StemMixer`
into chunked/streaming the moment a real OOM risk was flagged, without needing to be convinced.
None of that is passive "monkey coding" — see [[project_stem_splitter_decisions]] for the feature
context this played out in.

**How to apply**: If the user raises self-doubt about their skill level again, don't reassure with
generic praise — ground the answer in specific, true instances from the actual work (a decision
they made, a risk they caught, a claim they pushed back on). When collaborating day-to-day,
explicitly name which decisions/catches were theirs rather than silently executing — it reinforces
real technical ownership without being empty flattery, and the user has responded well to this
framing (moved from "monkey coder" doubt to "ít ra tôi biết chúng ta đang làm gì" in the same
conversation once shown concrete evidence).
