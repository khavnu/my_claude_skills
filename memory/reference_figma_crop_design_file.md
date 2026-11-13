---
name: reference-figma-crop-design-file
description: "Figma file cZfjGdrG5lmxtuoWRwwR6D (MusicPlayer) — UCrop replacement design; SF Pro is listed but unusable there, use Inter; bound translucent paints need explicit color."
metadata:
  node_type: memory
  type: reference
  originSessionId: d769ac83-42d0-49ee-81b3-e5debe426f39
  modified: 2026-10-21T08:04:08.893Z
---

Figma `cZfjGdrG5lmxtuoWRwwR6D` page "Image Crop" (2026-10-21): section `01` = UCrop screenshots + feature inventory, section `02` (node 4:25) = new CropImage design, local variable collection `crop`.

Pitfalls verified in that file via use_figma:
- `listAvailableFontsAsync` lists "SF Pro" but text nodes report `hasMissingFont: true` and `setProperties` on instances throws "font that isn't available" → use Inter (SF Pro Display, the app font, is not available either).
- A paint bound with `setBoundVariableForPaint` kept `color` white and rendered white when translucent → set `color` to the variable's real value too. Instances created before a main-component fill change kept an opacity-1 override → reset `inst.fills = inst.mainComponent.fills`.

Related: [[project-audio-editor-theming-status]]
