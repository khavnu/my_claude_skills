---
name: feedback-compose-responsive-sizing-decision
description: "Decision framework for choosing fixed dp vs wrap-content vs weight(1f) among siblings in a Row/Column, including nested-weight blocks — taught by user after the EditAudioBar sizing bugs"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6cbd5958-fb0d-4789-b5ef-c4357246df40
  modified: 2026-08-28T02:32:02.934Z
---

Before sizing any sibling in a `Row`/`Column`, ask: **if one sibling's size changes (longer localized text, a badge appearing/disappearing), should the others resize to compensate so the total still matches the container?**

| Relationship between siblings | Sizing |
|---|---|
| Size is a fixed design-system token (icon 24dp, divider 1dp, avatar 44dp) — independent of sibling content | Fixed `dp` |
| Independent, sizes to its own content, doesn't compete for space with anyone | Wrap content (no modifier) |
| Truly peer siblings, competing for one finite space, must split fairly | `weight(1f)` on **all** of them |
| N fixed-size elements (icon/button/divider) + **exactly one** element that must absorb whatever space is left | `weight(1f)` **only on that one**; the rest stay fixed/wrap |
| 3 groups where the MIDDLE one must sit at the row's true geometric center, regardless of how the two edge groups' content lengths compare | **Equal `weight(1f)` (fill=true) on BOTH edge groups**, middle group plain/wrap-content. Forces both flanks to the same width no matter their content, so the fixed middle child between them lands exactly on center — proven: if flank widths are R/2 each (R = leftover space, split 1:1), middle's own center = R/2 + middleWidth/2 = rowWidth/2 always. |
| 3 groups where the middle one should sit in whatever gap is left, but exact geometric centering doesn't matter — only "don't let one side hog 100% of the slack" | `Arrangement.SpaceBetween` on the parent, no weight on any group (or `weight(1f, fill=false)` on an edge group that also needs to ellipsize). **Not equivalent to the row above** — SpaceBetween only makes the two *gaps* equal; if the two edge groups' actual content widths differ, the middle group visually drifts off true-center toward whichever edge used less of its space. |

**Nested weight is common and not a special case** — a block of "peer" items competing with each other can itself be the "space-absorbing" element at the outer level, competing against fixed siblings (divider, an icon-only button). Example from `EditAudioBar` (audio_editor effects bar):

```
Row                                           ← outer level: "flexible block" vs "fixed elements"
├── Row(weight 1f)  "Volume/Speed/Fade block"  ← absorbs all leftover space
│   ├── ToolItem(weight 1f)  Volume            ← inner level: 3 true peers, split evenly
│   ├── ToolItem(weight 1f)  Speed
│   └── ToolItem(weight 1f)  Fade
├── Spacer(34dp) + Divider(1dp) + Spacer(34dp) ← fixed, design token size
└── ToolItem  Settings                         ← wrap content, doesn't compete with anyone
```

Divider/Settings are NOT peers of the 3-item block (different role, fixed size) — only the block itself gets `weight(1f)` at the outer level. The "Settings item rendered full-width" bug happened because Settings had briefly been treated as if peer-level weight logic applied to it, when it actually belongs to the fixed/wrap group at the outer level. See [[feedback-compose-fillmaxwidth-propagation]] for the related implementation pitfall (fillMaxWidth on a descendant silently making a wrap-content parent claim full width, independent of this sizing-decision question).

**Second real miss, same session — went through THREE attempts:**
1. Diagnosed `EditorTopBar` (Back+Title / Undo+Redo / Save) as "N fixed + 1 flexible" (Title absorbs all leftover space) → wrong: pushed Undo/Redo flush against Save.
2. "Fixed" it with `Arrangement.SpaceBetween` (equal-gap centering) → still wrong per the user: only guarantees equal *gaps*, not true geometric centering — drifts off-center whenever Title's and Save's content widths differ (the exact locale-dependent case this whole bug was about).
3. **Correct, user-specified fix:** equal `weight(1f)` on both the Back+Title Row and the Save Box (Undo/Redo plain, with 12dp horizontal padding as a min-gap safety net, not a centering mechanism) — see the two rows added above for the proof and the distinction from SpaceBetween.

**Root lesson:** the original (pre-any-edit) code already had this exact equal-weight-flanks structure — the very first "fix" (attempt 1) dismantled a structurally-correct layout because the real visible symptom (empty space between a short title and the Undo icon) was *expected, correct behavior* of equal-weight flanks with asymmetric content, not a bug. Before touching a multi-group Row's sizing: (a) identify which of the two centering patterns above is actually wanted (ask, don't guess — per [[feedback-ask-when-uncertain]]), and (b) check whether the *existing* structure already implements it correctly before assuming a fix is needed.
