---
name: feedback-user-comments
description: Không xóa comment của user — user giữ comment trong code để dễ đọc lại sau
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fef94919-6dd1-433e-9e63-9742d395519b
---

Không tự ý xóa comment mà user đã viết trong code, kể cả khi comment có vẻ thừa hoặc vi phạm "no-comment" rule.

**Why:** User dùng comment để note lại context cho bản thân khi đọc lại sau. Đây là preference cá nhân, không phải lỗi.

**How to apply:** Chỉ xóa comment khi user explicitly yêu cầu. Nếu thấy comment cần cải thiện thì mention, không tự xóa.
