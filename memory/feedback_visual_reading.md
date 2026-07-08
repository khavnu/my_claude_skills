---
name: feedback-visual-reading
description: "Claude's visual comprehension of screenshots/Figma is limited — ~80% layout, ~50% detail accuracy"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 53ec8f3f-3839-4e45-8e29-8bf52f9cb8ed
---

Claude đọc screenshot và Figma link chỉ nắm được khoảng 80% bố cục tổng thể và 50% chi tiết cụ thể.

**Why:** Khả năng nhận diện màu sắc chính xác, spacing cụ thể, font size, border radius và các chi tiết pixel-level rất hạn chế từ ảnh.

**How to apply:**
- Khi nhận screenshot/Figma để implement UI: **chủ động hỏi lại** những chi tiết không rõ (spacing, màu cụ thể, font size, border) thay vì tự suy đoán
- Ưu tiên đọc Figma qua tool (get_design_context, get_variable_defs) hơn là nhìn ảnh raw
- Sau khi implement, **báo lại những chỗ đã tự suy đoán** để user review
- Không tự tin 100% khi chỉ dựa vào screenshot — verify với user trước khi hardcode values
