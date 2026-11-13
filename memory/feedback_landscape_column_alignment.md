---
name: feedback-landscape-column-alignment
description: "Landscape tool screens — left file card top must line up with the right column's first element (heading), never vertically centred; Play result bar is the 76px one at y284"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 87fb5981-5bf1-470a-9072-56ede1d33a2e
  modified: 2026-10-13T09:43:14.657Z
---

On 2026-10-13 the user reviewed the landscape Figma frames and asked that the left audio card in "6. Converter" sit flush to the top, level with the "Output Format" heading on the right ("nó phải ngang với text Output format"). Applied to every tool frame on page `3.Landscape` (Volume/Speed 84, Convert/Channel/Compress 92, EQ 84).

**Why:** a vertically centred card floats differently per screen depending on how tall the right column is; top alignment keeps the two columns reading as one grid.
**How to apply:**
- Landscape two-column tool screens: both columns start at the same top; in Compose use `Arrangement.Top` (not `Center`) for the left column holding the file card.
- Play result bar in landscape frames is the 76px variant at y 284 (unified the same day; the 88px variant at y 272 is gone).
- Overflowing right columns are clipped "(scrollable)" frames ending at the bar top → `verticalScroll` in code.
Related: [[feedback-landscape-keep-portrait]].
