---
name: Multi-fix interaction check
description: Sau mỗi fix trong danh sách, re-evaluate xem fix đó có làm fix khác trở nên thừa/sai không
type: feedback
originSessionId: 0f37d1c2-b66d-46c3-a846-779b0cc4ba5b
---
Khi apply nhiều fix từ code review, đừng tick từng item theo checklist mà không nhìn lại interaction.

**Why:** Fix `reset()` gọi `cancelDecrypting()` đã đảm bảo job bị cancel khi screen dismiss. Nhưng sau đó vẫn thêm `viewModel.cancelDecrypting()` vào `LoadingDialog.onClick` — redundant vì `onDismiss()` → `onDispose` → `reset()` → `cancelDecrypting()` rồi.

**How to apply:** Sau mỗi fix, dừng lại hỏi: *"Fix này có làm item nào trong danh sách còn lại trở nên obsolete không?"* Nếu có — bỏ item đó, không apply mù.
