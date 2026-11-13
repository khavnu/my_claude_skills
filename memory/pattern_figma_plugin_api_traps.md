---
name: pattern-figma-plugin-api-traps
description: "use_figma traps that cost retries: bound paint renders black in instances, resize() kills hug, nested rescale throws, instance resize doesn't reflow children (detach + SCALE), SECTION children use local coordinates"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e3b246ca-7bf8-422f-be96-0174aa57b767
  modified: 2026-10-13T03:41:34.915Z
---

Traps hit on 2026-09-29 building components in Figma file my_idea (see [[project-karaoke-app-design]]):

1. **Bound color paint renders with its raw base color on instance sublayers.** `setBoundVariableForPaint({color:{r:0,g:0,b:0}}, 'color', v)` on a glyph inside an instance → binding shows in `fills[0].boundVariables` but the render is BLACK. Fix: build the base paint from the resolved value `Object.values(v.valuesByMode)[0]`, then bind. Verify by screenshot, not by reading fills.
2. **`resize()` after `primaryAxisSizingMode='AUTO'` silently turns hug into fixed** → vertical components collapse to the height passed to resize (e.g. 10px). Always set AUTO *after* resize.
3. **`rescale()` on an instance nested inside another instance throws** "This property cannot be overridden in an instance: size". Rescale the outer instance instead.
4. **INSTANCE_SWAP property + `componentPropertyReferences={mainComponent}` resets every variant's nested instance to the property default** (and drops fill overrides) — re-apply per-variant swaps/fills afterwards.
6. **Paint opacity is dropped if added after binding** (`{...boundPaint, opacity}` → opacity 1). Put `opacity` in the base paint passed to `setBoundVariableForPaint`, or use node `opacity`.
7. **Layers inside an instance can't be resized or moved** (`x`/`resize` throw or are ignored) → a slider value can't be an instance override; model it as a variant axis (StemSlider `Level=0/15/30/50/75/100`). Swapping variant via `setProperties` resets TEXT/INSTANCE_SWAP overrides — re-set them after; `clone()`d variants lose `componentPropertyReferences` — relink.
8. **Icons in this file are TEXT nodes** (Material Symbols ligature, layer name `glyph`) → `findOne(n => n.type==='TEXT')` hits the icon first and overwrites it. Always exclude `name==='glyph'` or target by layer name.
9. **`setEffectStyleIdAsync('')` detaches but keeps the raw effect** — also set `effects = []` to actually remove glow.
10. **Property-linked text inside an instance ignores `characters =`** (silently) — change it via `instance.setProperties({[key]: value})`.
11. **Widening a sibling inside a slider shrinks the auto-layout track** → fixed-width fill rects overflow at 100%; recompute fills from `track.width` after any width change.
12. (2026-10-13, music editor landscape file) **Resizing an instance doesn't reflow its children** if the component's constraints are fixed. A waveform instance going from 360×200 to 448×120 got its bars cut off and its sections misplaced. To stretch something non-uniformly at 1.0, `detachInstance()`, then set `constraints = {SCALE, SCALE}` on every descendant that isn't inside a nested INSTANCE or BOOLEAN_OPERATION (setting it there throws "cannot be overridden in an instance"), then `resize`. Afterwards, restore the round handles: record the square nodes before the resize and set them back to their original size, centred where they were.
13. (2026-10-13) **Children of a SECTION use LOCAL coordinates**, the same as children of a FRAME. Assuming absolute coordinates pushed 24 of 37 frames outside their sections. Always verify with `absoluteBoundingBox`.
5. **Karaoke wipe via hard-stop text gradient only works on single-line text** — gradient spans the whole box, so wrapped lines all cut at the same x.

**Why:** each cost a failed call + screenshot round-trip.
**How to apply:** reuse the resolved-color `paint()` helper and "resize then AUTO" order in every use_figma script for this file.
