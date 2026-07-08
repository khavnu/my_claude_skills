---
name: feedback-top-down-thinking
description: "Xử lí vấn đề top-down: function → pseudo code → implement, không dive thẳng vào code"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 53ec8f3f-3839-4e45-8e29-8bf52f9cb8ed
---

Trước khi implement, sketch top-down:
1. **Function**: cái này serve ai, caller cần gì?
2. **Pseudo code**: các nhánh logic, edge case
3. **Implement**: mới viết code thật

**Why:** Dive thẳng vào implement nhanh với task đơn giản, nhưng với logic nhiều nhánh hoặc abstraction mới thì tốn nhiều round fix hơn là dừng sketch 2 phút trước. Ví dụ từ session:
- `rememberVideoPlayerState`: sketch caller interface trước → thấy ngay abstraction không che được gì → không extract
- `playPreview()`: sketch các nhánh null/non-null trước → không bỏ sót case

**How to apply:** Với mọi function mới hoặc refactor, tự hỏi "caller cần gì từ đây?" trước khi mở file. Nếu answer phức tạp hoặc không chắc → viết pseudo, discuss với user trước.

Liên quan: [[feedback-refactor-value-check]]
