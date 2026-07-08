---
name: feedback-figma-apply-output
description: "After every Figma-based code change, produce a structured diff table of style/color changes per section"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 53ec8f3f-3839-4e45-8e29-8bf52f9cb8ed
---

Sau mỗi lần apply thay đổi từ Figma, luôn output một bảng diff có cấu trúc — một block per section — trước khi báo compile result.

**Why:** Giúp user spot lỗi bằng cách scan bảng, không cần mở file trong IDE. Rẻ hơn một correction loop.

**How to apply:**
Format:
```
SectionName
  field      : old style → new style  |  old color → new color
  field      : (unchanged)            |  old color → new color
```
- Liệt kê mọi Text/Icon trong scope (cả changed lẫn verified unchanged)
- Không list section ngoài scope của task
- Post table TRƯỚC compile result
