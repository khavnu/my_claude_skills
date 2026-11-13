---
name: m3-switch-thumb-size
description: M3 1.12.0-alpha03 Switch keeps the 24 dp OFF thumb only if thumbContent has a non-zero intrinsic size; an empty lambda still shrinks it
metadata:
  type: project
---

QA #42 (2026-10-16): `thumbContent = {}` did NOT stop the OFF thumb shrinking to 16 dp. In material3 1.12.0-alpha03 `Switch.kt` ThumbNode.measure, `hasContent` = content maxIntrinsicHeight/Width != 0. Fix in `core/ui/AppSwitch.kt`: `Spacer(Modifier.size(SwitchDefaults.IconSize))` as thumb content.

**Why:** cost a wrong "fixed" claim to the user; my pixel-threshold measurement of the thumb (white > 245) mixed in the light grey track and reported equal sizes.
**How to apply:** verify UI size claims with a cropped side-by-side screenshot read by eye, not a colour-threshold script. Source to re-check: material3-android-1.12.0-alpha03-sources.jar → Switch.kt `hasContent`.
