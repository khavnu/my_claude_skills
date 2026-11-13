---
name: display-mode-refactor
description: "DisplayMode refactor (Phone/Tablet x Portrait/Landscape): steps 1-2 done 2026-11-10 (f562b64bf, 25e99f220); step 3 (~65 rememberWindowLayout sites) optional, not started."
metadata:
  type: project
---

User agreed (2026-11-10) to a refactor once tickets 2104 and 2105 are done:
- `enum class DisplayMode { PhonePortrait, PhoneLandscape, TabletPortrait, TabletLandscape }` with `isLandscape` / `isTablet`; pure `displayModeOf(widthDp, heightDp, smallestWidthDp)` (unit-tested, tablet = sw >= 600); `@Composable rememberDisplayMode()`; `Configuration.displayMode()` for Service/Activity.
- Step 1: add it + tests, `rememberWindowLayout()` derives from it (no behavior change). Step 2: move tablet checks (`Context.isTablet()`, `emptyTextBesideIcon` + its `TABLET_MIN_WIDTH_DP`, WidgetChooser, WidgetConfig `isTablet`, FloatingVideoPlayService) to it. Step 3 (optional): the ~65 `rememberWindowLayout()` call sites.
- Not for size-based decisions (detail pane = 40% of width, EmptySimpleFitting height fit).

**Why:** the phone-landscape-vs-tablet rule had to be rewritten for 2093 and 2080; the 600 threshold is duplicated.

**How to apply:** check which Configuration each site reads (locale wrapper freezes resources.configuration, see [[project_frozen_locale_configuration]]). Commit per step.


Progress (2026-11-10): step 1 `f562b64bf` (ui/layout/DisplayMode.kt + DisplayModeTest), step 2 `25e99f220` (isTablet, EmptySimple/EmptyState, WidgetChooser, WidgetConfigActivity), checked on Pixel Tablet AVD + Vivo V2201 landscape. Left on purpose: `coverGlyphKeepsOwnColor` (CoverDefaults.kt) keeps its own `>= 600` because it mirrors the `drawable-sw600dp` resource folder.
