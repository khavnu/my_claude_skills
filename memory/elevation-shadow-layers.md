---
name: elevation-shadow-layers
description: QA #10 root cause — Modifier.shadow (elevation) shrinks inside offscreen layers (Nav3 crossfade, stretch overscroll) on REAL devices only; emulator does not reproduce
metadata:
  type: project
---

QA #10 (2026-10-06, Pixel Tablet landscape): Home ring circle + "Today's records" card shadow "spreads then shrinks" on More tips / scroll.

Verified root cause: both use elevation shadows (`HomeHeader.kt` CircleFace `.shadow(9.dp, CircleShape)`, `IntakeTimelineList.kt` `.shadow(CardShadow)`). While the content sits in an offscreen layer the spot shadow almost vanishes and snaps back after:
- Nav3 `NavDisplay` (`RootRoute.kt`, no transitionSpec → default crossfade = graphicsLayer alpha < 1). Pixel 9 landscape, animator scale 10, lossless `screencap`: shadow sum under the circle 732 at rest vs 237 at alpha 0.96 (Home layer isolated as (frame − (1−α)·MoreTips)/α).
- Android 12+ stretch overscroll on the records LazyColumn: card shadow turns into a thin hard edge while pulled.
- The Pixel Tablet / Pixel 9 EMULATORS render it correctly (profile/alpha constant) → always check shadow/layer bugs on a real device.

FIXED 2026-10-06 (uncommitted): `core/ui/ElevationShadow.kt` `Modifier.elevationShadow(elevation, shape)` = ambient dropShadow (r=elev, α .11) + key dropShadow (r=1.6·elev, y=0.5·elev, α .22); Pixel 9: shadow at transition start 99% of rest (was 32%). Landscape card shadow is uniformly lighter than the old position-dependent one (portrait matched).

**Why:** emulator gave a false "cannot reproduce" for 30 min.
**How to apply:** for any shadow/alpha/RenderEffect glitch, measure on the Pixel 9 with `animator_duration_scale 10` + rapid `screencap` (restore the scale after). See [[linux-device-testing]].
