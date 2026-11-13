---
name: feedback-incremental-ui-first
description: "Màn hình mới đi đúng 3 phase theo thứ tự: UI + Preview → ViewModel + UiState → business logic (repository). Plan cũng phải xếp task theo thứ tự này"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 53ec8f3f-3839-4e45-8e29-8bf52f9cb8ed
  modified: 2026-10-15T01:57:32.503Z
---

Làm từng bước nhỏ, hoàn thành xong báo lại user trước khi làm tiếp. Không làm dồn tất cả một lúc.

Với màn hình mới, thứ tự bắt buộc gồm 3 phase:
1. **UI + @Preview với fake data.** Screen/component, user duyệt preview.
2. **ViewModel + UiState.** Nối Route ↔ VM; state UI-only (chọn mục, mở/đóng sheet, dialog) chạy được, chưa gọi repository.
3. **Business logic.** Repository, data source, fake repo, permission, fetch/scan, đọc metadata.

**Why:** Feedback loop ngắn; UI đổi lớn không kéo theo sửa data layer. 2026-10-15 (plan Compress video): tôi xếp domain model + `VideoProcessingRepository`/fake + đọc metadata (Task 1–3) TRƯỚC UI. User hỏi lại "sao không làm UI trước → preview ổn → gắn VM + UiState → gắn logic business".

**How to apply:** Thứ tự phase (nav → UI → VM → repository) và flow commit của chế độ "tự động làm" nay nằm ở global CLAUDE.md Workflow Rule #9 (thêm 2026-10-15). Đọc từ đó; memory này chỉ giữ lý do vì sao rule ra đời.
