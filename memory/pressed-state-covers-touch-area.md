---
name: pressed-state-covers-touch-area
description: User wants a control's pressed/ripple area to match its whole touch area, and spacing done by item size, not gaps
metadata:
  type: feedback
---

When enlarging a tappable item (QA #59, 2026-10-30), the user wanted the spacing done by making each item taller
(click area) instead of gaps between items, AND the ripple/pressed box to grow with it — a ripple that only hugs
icon+label while the touch area is bigger was called out as "chưa tăng". Result: `MainTabItem` clips + ripples the
whole item (commit a3a6612).

**Why:** the visible pressed state is how the user (and QA) judge the touch area; a mismatch looks like the change was not made.
**How to apply:** when changing touch targets, make the indication fill the same bounds, and show both in the device screenshot.
