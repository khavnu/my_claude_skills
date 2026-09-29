---
name: figma-page-listing
description: Figma MCP get_metadata without nodeId lists only the first page; list all pages via use_figma figma.root.children
metadata:
  node_type: memory
  type: reference
  originSessionId: 3fd3973b-4b11-41d6-bb34-5961448e9bbf
  modified: 2026-09-29T10:35:18.310Z
---

Figma MCP `get_metadata` called without `nodeId` returned only 1 page ("Read me") for file `oxFsDJWcj57DCjSlM8dTc5` (my_idea — Karaoke Player design), while the file actually has 6 pages. Verified 2026-09-29.

Reliable listing: `use_figma` (load figma-use skill first) with `return figma.root.children.map(p => ({id: p.id, name: p.name}))`.

Pages at that date: Read me 26:2 · Foundations 0:1 · Components 3:2 · Player 3:3 · Sing 3:4 · Flows 3:5. Player page metadata is ~88k chars — exceeds tool output, filter with `jq -r '.[0].text' | grep '^  <frame'`.
