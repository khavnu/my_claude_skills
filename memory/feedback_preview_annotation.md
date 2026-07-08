---
name: feedback-preview-annotation
description: Thêm @Preview vào mọi Screen và Composable mới tạo
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 823797c6-5dae-4139-8f17-2a05db3b935b
---

Khi tạo Screen mới hoặc Composable riêng lẻ, phải bổ sung `@Preview` annotation.

**Why:** User muốn có preview để dễ review UI mà không cần chạy app.

**How to apply:** Mọi `@Composable` function mới (Screen, standalone component) đều cần ít nhất một `@Preview`. Nếu có nhiều state (loading/error/empty/content), thêm preview cho từng state quan trọng.
