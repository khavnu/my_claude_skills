---
name: feedback-landscape-keep-portrait
description: "Landscape work must not change the existing portrait UI: every spacing or size tweak goes in the checkScreenSizeMode() == Landscape branch (same rule for the Split branch), and shared components get a portrait test that pins the old values"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 87fb5981-5bf1-470a-9072-56ede1d33a2e
  modified: 2026-10-13T06:53:01.799Z
---

When the user tunes landscape spacing (for example the EmptyView gaps, the bottom gap under Delete in a side panel), the change goes only in the `checkScreenSizeMode() == ScreenSizeMode.Landscape` branch (`isLandscapeOrientation()` was removed 2026-10-27). Portrait keeps its exact old values. The user said this explicitly on 2026-10-13: "chú ý là mọi thứ chúng ta làm không ảnh hưởng đến Portrait UI cũ nhé".

**Why:** shared components (`EmptyView` has 11 callers, plus `AppSortBottomSheet`, `AppNameInputBottomSheet`…) reach many portrait screens. One unconditional tweak silently changes all of them.
**How to apply:** keep the portrait constant next to the landscape one (`PORTRAIT_BUTTON_GAP` / `LANDSCAPE_BUTTON_GAP` in `ui/component/EmptyView.kt`). Add a portrait test that pins the old number (`EmptyViewTest.portrait_keepsTheOriginal40dpGapAboveTheButton`). Take a portrait screenshot on the device before reporting. See also [[feedback-landscape-commit-message]].

Split screen (2026-10-27, #473): the same rule applies to the new `ScreenSizeMode.Split` branch — the user said "Mục tiêu là không được ảnh hưởng đến UI portrait và landscape có sẵn".
