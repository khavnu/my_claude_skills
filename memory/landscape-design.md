---
name: landscape-design
description: "Landscape support work (branch update/landscapde_mode) — Figma file with portrait baseline + landscape proposal, decisions pending"
metadata:
  node_type: memory
  type: project
  originSessionId: 17a72152-9a13-41b8-8200-102b196fdaf3
  modified: 2026-10-05T09:21:27.345Z
---

2026-10-05: user wants landscape support (app was portrait-locked via `android:screenOrientation="portrait"` in androidApp manifest; configChanges already include orientation so rotation does not recreate the Activity).

- Figma: https://www.figma.com/design/BJPpT75bsmDF54or09evw6/Drink_water_reminder — pages: Foundations (vars bound to MaterialTheme/LocalAppColors), Assets & Components (81 assets from composeResources + static Lottie frames), 4. Portrait (27 screens rebuilt from code), 5. Landscape (proposal), 6. Landscape audit (device captures + findings).
- Running under skill `long-feature`: checklist `docs/features/landscape/checklist.md` (read it first each session). Q1–Q6 answered 2026-10-05 (rail, WindowSizeClass, tablet later, onboarding 2 panes). Scope = UI only, portrait visuals unchanged; golden PNGs live OUTSIDE the repo (`~/Work/drink_water/golden-landscape/`); no iOS testing.
- 2026-10-05 status: groups A, B, C done — user committed them as 514c402 "Update landscape mode support" (2026-10-06; tablet change + golden robustness still uncommitted on top); checklist evidence per item. Goldens: 35 states × portrait/landscape in `~/Work/drink_water/golden-landscape/{portrait,landscape}`, run `golden.sh verify` / `SET=landscape golden.sh verify`. 2026-10-06: tablet in landscape now also uses the landscape layout (width ≥ 840 and wider than tall; field renamed `isLandscapeLayout`), checked on the Pixel Tablet emulator (`emulator-5556`, user-started). Open: implementation deviates from Figma on onboarding (header centred top) and Edit intake (kept vertical); Figma page 5 not updated.
- Pitfalls found: `AppBottomSheet` `fillMaxWidth` defeated M3's 640 dp sheet max width; Crop-centred portrait Lottie hides its waves in landscape; keyboard up + rotation made the tab pager drift (fixed by resyncing on `pagerState.currentPage`).
- (Superseded) Proposal awaiting user decisions Q1–Q6 (on the Landscape page note): NavigationRail when height is compact, two panes for Home/History/onboarding, centred 600 dp column for lists, sheets max 640 dp with horizontal content.
- 2026-10-05 (corrected): the portrait lock is now removed for good in the uncommitted C1 change (earlier note said it was reverted after the audit).

- 2026-10-06 Figma sync of page 4 Portrait DONE (all frames vs Pixel 9 goldens, ≤1 dp): method = Figma screenshot (412x924, status bar 66) vs golden `portrait/*.png` scaled 1080→412 and pasted at y=66; compare ink row-bands per x-column (numpy). Not synced on purpose: Calculating / Result 1 (Lottie mid-frame vs golden end frame). 36 PNG icons on page 3 traced to vectors (vtracer, colour-quantised); multi-colour art stays raster. Page 5 Landscape still the old proposal.
- 2026-10-06 page 5 Landscape rebuilt to match Pixel 9 landscape goldens (≤2 dp): 5.1 tabs, 5.2 child screens, 5.3 onboarding (10, incl. new Bedtime + Result 3/4), 5.4 sheets (11). Old proposal frames + "Approach & open questions" deleted (user OK). Tablet (user chose "all screens", 1280×800, no cutout, rail x 0–80, gesture handle 220×4 at y 782): sections 5.5–5.8 (tabs 3, child 3, onboarding 10, sheets 11) DONE 2026-10-06. Tablet goldens predate QA #1/#2/#4 (title +12, content +6, 48 dp period buttons): tablet frames follow current code, not those goldens. Tablet sheets = phone-landscape sheets at x 320, y +356, height +32. Goldens: `golden-landscape/tablet-land/`. History chart is rebuilt procedurally from HistoryChart.kt formulas (box 40/10, 31 slots + 1 empty, gap 2, vertical scale s).
- Code facts found while syncing (verified in code): sheet OK/Cancel footer is 44 dp + 8 dp bottom (`PopupSheet.FooterBottom`); list rows carry their own 0.5 dp hairline (row pitch 70.5 / 60.5); NumberWheelPicker rows 44 dp 20/23 sp, time wheel 36 dp.

**Why:** design must be agreed before any code (user: "chúng ta sẽ trao đổi cách làm cho hợp lí nhất").
**How to apply:** next session reads the checklist, then only the open items (user review of landscape, N5 tablet, Figma sync, commit) remain; device checks per [[linux-device-testing]].
