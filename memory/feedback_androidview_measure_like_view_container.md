---
name: androidview-measure-like-view-container
description: Porting a View screen to Compose with AndroidView inside verticalScroll — measure specs differ from NestedScrollView/FragmentContainerView; ListView with weight collapses to 1 row.
metadata:
  type: feedback
---

Verified 2026-10-22 on the widget config port (`widget_config/components/WidgetPreview.kt`, `WidgetConfigScreen.kt` PreviewCard), before/after screenshots on Pixel 9:
- `AndroidView` maps a root `layout_width="match_parent"` to EXACTLY the slot width; the old `wrap_content` FragmentContainerView gave AT_MOST, so the widget kept its own 320dp. Fix: inflate into a `FrameLayout(context)` wrapper (attachToRoot = true) and hand THAT to AndroidView — same hierarchy as the Fragment container.
- Compose `verticalScroll` measures children with UNSPECIFIED height; the old `NestedScrollView android:fillViewport="true"` re-measured its child EXACTLY, so nested wrap_content views got AT_MOST. A `ListView` with `layout_height=0dp + weight` inside a wrap_content LinearLayout then measures ONE row under UNSPECIFIED. Fix: give the AndroidView a bounded `heightIn(max = ...)`.

**Why:** both bugs look fine in code review and only show on device; took 3 device rounds to find.
**How to apply:** when an AndroidView replaces a Fragment/View inside a scroll container, compare before/after screenshots first, and reproduce the old parent (wrapper FrameLayout + bounded max height) instead of tweaking the inflated root's LayoutParams.
