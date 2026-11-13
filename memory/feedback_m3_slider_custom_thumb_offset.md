---
name: m3-slider-custom-thumb-offset
description: Material3 Slider with a custom thumb smaller than 16dp draws it above the track centre; use PlayerSliderThumb or a >=16dp tall slot.
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3eb82f20-c3e8-4cda-8e47-e6cee19550cd
  modified: 2026-11-05T10:31:58.104Z
---

Material3 `Slider` (1.4.0 here) measures with `requiredSizeIn(minHeight = TrackHeight)` (16dp) and wraps the thumb in `Box(layoutId THUMB).wrapContentWidth()`: centred horizontally only. The track is centred vertically. A custom thumb shorter than 16dp therefore sits at the top: a 12dp circle was 2dp (~4.5px) above a 4dp track (ticket 2085, fixed 244c1de78).

**Why:** QC sees it at once on the Large Player; the source of the layout is `Slider.kt` lines ~870-950 in the material3 sources jar under ~/.gradle/caches.

**How to apply:** for any custom Slider thumb, reuse `feature/player/PlayerSlider.kt` (`PlayerSliderThumb`: 12dp circle centred in a 24dp slot) or give the thumb a slot at least 16dp tall with the shape centred. `PlayerSliderTest` (androidTest) compares thumb vs track centres with `useUnmergedTree = true` (Slider merges its children's semantics).
