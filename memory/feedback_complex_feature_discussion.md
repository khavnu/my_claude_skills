---
name: feedback-complex-feature-discussion
description: "Với tính năng mới phức tạp, phải trao đổi kĩ với user trước khi implement — không nhảy vào code ngay"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d1dc9b4b-1808-4805-b852-a0bfcaf3ef4a
---

Trước khi implement bất kỳ tính năng mới phức tạp nào, phải trao đổi đầy đủ với user:

**Why:** User muốn được tham gia vào quá trình thiết kế, không chỉ nhận code đã làm sẵn. Brainstorm → clarify intent → propose approaches → agree spec → implement.

**How to apply:**
- Dùng `superpowers:brainstorming` — hỏi từng câu một, không hỏi dồn
- Cần từ user trước khi code: PDF/asset samples thật, Figma design nếu có, clarify scope "cái gì bị bỏ / cái gì giữ lại"
- Spike phần uncertain nhất TRƯỚC (không để đến cuối mới phát hiện blocker)
- Viết spec ra `docs/superpowers/specs/` để agents đọc được — artifact chỉ để user xem, không phải ground truth
- Clarify "không dùng code cũ" → scope khác nhau hoàn toàn nếu replace vs integrate
