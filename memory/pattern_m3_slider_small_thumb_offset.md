---
name: pattern-m3-slider-small-thumb-offset
description: Material3 Slider custom thumb smaller than 16dp sits above the track — the thumb slot is stretched to 16dp and top-aligned; fix by a 16dp slot with a centred dot
metadata:
  node_type: memory
  type: feedback
  originSessionId: f8af6503-0c14-4b8d-b9c4-880554cd647d
  modified: 2026-10-15T03:37:03.124Z
---

M3 1.4.0 `Slider` (BOM 2026.03.00): `SliderImpl` applies `requiredSizeIn(minHeight = TrackHeight)` where `TrackHeight = SliderTokens.InactiveTrackHeight` = 16dp. The thumb slot is `Box(Modifier.layoutId(THUMB).wrapContentWidth())`, which wraps width only, so it is stretched to 16dp tall, and its content is placed TopStart. The track, meanwhile, is centred (`trackOffsetY = (sliderHeight - trackHeight) / 2`). A custom thumb < 16dp therefore sits above the track's centre: 12dp thumb → 2dp offset (measured 1.7dp on Pixel 9, 2026-10-15). `AppPlayerSlider` (20dp thumb) is not affected.

**Why:** the user spotted the offset on the Compress video seek bar. `wrapContentHeight()` on the custom thumb did NOT fix it, because the slot Box loosens min constraints when it measures its child.

**How to apply:** for a thumb < 16dp, wrap it in `Box(Modifier.height(16.dp), contentAlignment = Alignment.Center)`. Pin the result with a bounds test that compares the centres of the testTagged thumb and track (`ui/component/video/VideoSeekBarTest.kt`). Source: `material3-android-1.4.0-sources.jar` → `Slider.kt` `SliderImpl` (~line 774). Re-check after an M3 upgrade.
