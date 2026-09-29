---
name: feedback-compose-fillmaxwidth-propagation
description: Compose layout pitfall found while fixing EditAudioBar — fillMaxWidth on any descendant of a wrap-content Column/Box bubbles up and stretches non-weighted siblings; prefer Row+weight over ConstraintLayout+hardcoded px for evenly-distributed toolbars
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6cbd5958-fb0d-4789-b5ef-c4357246df40
  modified: 2026-08-28T02:08:36.729Z
---

**`Modifier.fillMaxWidth()` on ANY descendant inside a wrap-content `Column`/`Box` makes the whole ancestor report max width** — not just the element it's called on. A `Column` without its own `fillMaxWidth` still sizes itself to `max(children widths)`; if one child (e.g. a badge-zone `Box`) calls `fillMaxWidth()`, that child claims the full incoming constraint, and the `Column`'s reported width becomes that same full width — propagating outward to any non-weighted parent Row slot.

**Why:** in `EditAudioBar` (audio_editor Trim/Copy effects bar), a reusable `ToolItem` composable was called both with `Modifier.weight(1f)` (Volume/Speed/Fade, correctly constrained) and with no weight (Settings, meant to hug its own content). Removing `fillMaxWidth()` from the outer `Column` wasn't enough — an inner `Box(Modifier.fillMaxWidth().height(...))` for the badge zone still forced the whole item to claim the Row's entire remaining width, so Settings rendered full-screen-wide. Real fix: restructure as a `Box` overlay (icon+label `Column` sized to its own content; badge as a sibling `Box` aligned `TopCenter`, not a fillMaxWidth row sharing space with it) — nothing in the tree asks for more than its own content width, so `weight(1f)` (which forces exact min=max width) is the ONLY thing that stretches an item, and non-weighted callers stay content-sized automatically.

**How to apply:** when a shared composable must support both a `weight(1f)` slot and a content-sized (no-weight) call site, audit the ENTIRE subtree for `fillMaxWidth`/`fillMaxSize` — not just the top-level modifier — before claiming the width bug is fixed. Prefer overlay (`Box` with `Alignment.TopCenter`/`align`) over a shared fillMaxWidth row when one element (like a badge) needs to sit above/overlap another without dictating its sibling's width.

**Related layout lesson from the same fix:** prefer a plain `Row` with `weight(1f)` for "N items evenly distributed, one anchored to an edge" toolbars, over `ConstraintLayout` + `createStartBarrier`/`createEndBarrier` + hardcoded px gaps copied from Figma. The barrier approach is fragile (breaks across locales/label lengths, doesn't reserve space for badges correctly — can push a badge to a negative Y offset above the parent's own bounds) and requires re-measuring every gap from Figma metadata by hand. The user explicitly asked for this simpler structure after the ConstraintLayout version kept producing spacing bugs. See [[project-audio-editor-theming-status]] and [[feedback-figma-full-property-audit]].
