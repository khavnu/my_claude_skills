---
name: DOCX image wrap distance bug
description: Floated images in docx-preview have no margin gap with surrounding text despite reading correct distL/distR from metadata
type: project
---

docx-preview generates `<div style="float:left">` for anchored images but does NOT apply `distL/distR/distT/distB` from `wp:anchor` as margins.

**What we know:**
- Brochure.docx has `wp:anchor distL=228600 distR=228600` (24px each side)
- docx-preview creates 2 floated divs (1 anchor → 2 DOM elements)
- `applyWrapDistances()` in bridge.js reads anchor metadata and applies margin
- margin-right with `!important` via cssText still doesn't create visual gap
- Suspect: docx-preview sets fixed inline width on floated div → margin-right extends beyond container instead of pushing text away

**Next steps to try:**
1. Inspect full DOM structure of floated div (what children, what inline styles)
2. Try reducing floated div width by distR and adding margin-right
3. Try adding margin directly on `<img>` inside floated div
4. Try wrapping img in a new container with padding

**Why:** User expects image-to-text spacing matching original Word document.

**How to apply:** Fix in bridge.js `applyWrapDistances()` function. Test with Brochure.docx.
