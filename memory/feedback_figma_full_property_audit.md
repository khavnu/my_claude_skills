---
name: feedback-figma-full-property-audit
description: "User frustrated by repeated Figma-reading misses — must audit ALL properties of every in-scope node numerically, never eyeball or silently approximate"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6cbd5958-fb0d-4789-b5ef-c4357246df40
  modified: 2026-08-27T09:45:56.880Z
---

During the audio_editor "Generate" redesign the user had to catch, one by one: badge corner shape, divider position (20dp vs measured 45dp), item gap (16 vs 30), sheet background (solid vs gradient), icon colors (guessed from screenshot), untinted Close icons. Final straw: "bạn làm đọc figma kiểu éo gì mà sai nhiều thế".

**Why:** each iteration only verified the properties the user explicitly named; positions/gaps were never computed from `get_metadata` x/width; icon colors were once guessed from the rendered screenshot; approximations ("gom về token") were applied silently to a gradient.

**How to apply:** follow figma-reader v2.4 Step 2.7 — for every node in scope compute gaps from metadata coordinates, check per-corner radii, check gradient vs solid, download SVGs (wget) for icon colors, check tint inheritance on Icons; list every approximation explicitly for user approval; re-run the leaf-node checklist before reporting done, even for one-property iterations. See [[project-audio-editor-theming-status]].
