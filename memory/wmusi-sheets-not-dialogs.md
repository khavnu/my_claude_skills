---
name: wmusi-sheets-not-dialogs
description: WMusi design rule — confirmations and short inputs are bottom sheets, never centred dialogs (user 2026-10-06)
metadata:
  type: feedback
---

Every confirmation / short input in WMusi is a bottom sheet; only system UI (launcher pin dialog, Android delete/permission prompts) stays a dialog.

**Why:** the user asked for consistency ("thiết kế đồng bộ… dùng bottom sheet thay vì center dialog") after a new design used a centred dialog while 49 other overlays were sheets.

Buttons (user 2026-10-06, "button trong bottomsheet màu khác"): full-width `actions` area at the sheet bottom; 1 = full width, 2 = equal pair Tonal-left, 3 = stacked confirm → Tonal alt → Text Cancel; exactly ONE coloured button (Primary or Danger) per sheet.

**How to apply:** new confirm/input designs start from a sheet (handle, surfaceContainer, top radius 28, left-aligned, 2 choices = equal pair neutral-left). Before calling a design done, check no frame has a node named `dialog`. Full list + rules: `docs/design/sheets-not-dialogs.md`. Related: [[wmusi-figma-file]].
