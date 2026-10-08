---
name: rtl-deferred
description: QA #101 (RTL layout broken under Arabic/Hebrew) deferred 2026-10-01; user rejected forcing LTR
metadata:
  type: project
---

Reproduced on 2026-10-01 on Pixel 9 via `cmd locale set-app-locales com.tmedilab.drink.water2 --locales ar`. Bidi reorders the English-only strings (`ml 300/2990`, `ml / day 240`, `!one. Come…`). The time wheel swaps its minute and hour columns. The History chart stays LTR while the week strip mirrors, and the month arrows are unmirrored PNGs.

**Why:** the user said to skip the bug for now and explicitly rejected the "lock layout to LTR" fix (forcing `LayoutDirection.Ltr` or `supportsRtl=false`).
**How to apply:** do not propose locking LTR again. When #101 comes back, plan real RTL support: per-component fixes (wheel column order, auto-mirrored arrows, chart direction, bidi-safe number+unit strings).

**Per-component RTL fixes done (2026-10-07/08, verified on Pixel 9 with `cmd locale set-app-locales <pkg> --locales ar`, reset with no `--locales`):**
- #21 `ChangeCupButton` (DrinkButton.kt): art nudges inside a non-mirrored PNG → `absoluteOffset`, not `offset` (Compose `offset` flips sign under RTL).
- #22 speech-bubble tail `ic_triangle.xml`: `android:autoMirrored="true"` — CMP resources 1.12.1 honours it (`XmlVectorParser.kt:79`). Position via `offset` was already right.
- Rule of thumb: vector that points somewhere → `autoMirrored`; nudge tied to a fixed bitmap → `absoluteOffset`. Still unchecked: `PlanPassthrough` badge offset, `WeightSheet` picker shift, wheel column order, History chart direction, bidi of "ml 300".
