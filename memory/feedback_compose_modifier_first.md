---
name: feedback-compose-modifier-first
description: modifier phải là tham số đầu tiên trong mọi @Composable function — cả definition lẫn call site
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2ae4ca50-9343-47d6-a053-e3ab557d399f
---

`modifier` phải là tham số đầu tiên trong mọi `@Composable` function, cả ở definition lẫn call site.

**Why:** Đây là convention của project (đã ghi trong global CLAUDE.md). User đã nhắc khi tôi để `modifier` ở cuối trong `NumberEditField`.

**How to apply:** Khi viết bất kỳ `@Composable` function nào — public hay private — luôn đặt `modifier: Modifier = Modifier` ở vị trí đầu tiên. Tại call site dùng named argument, cũng đặt `modifier = ...` lên đầu.
