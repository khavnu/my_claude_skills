---
name: feedback-minimal-change-first
description: "QC ticket fixes — đưa bản gọn nhất (ít file, dùng lại y nguyên pattern có sẵn) làm lựa chọn đầu; user rollback khi diff lan sang navigation/shared component dù họ đã gật đề xuất"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 50677524-b6cb-43a8-81cf-c447d243ebd0
  modified: 2026-10-26T09:34:45.013Z
---

Ticket #453 (2026-10-26): user OK đề xuất của mình (sheet + OK mở lại system picker + đổi title Video to audio), mình làm 8 file +69/−28 (callback mới qua MusicEditorNavigation, 2 flow cũ VideoToAudio, type `UnusableVideo`, param `title` cho sheet dùng chung). User: "rollback lại nhé, tôi thấy sao thay đổi nhiều thế nhỉ?" → chốt "làm giống hệt như Video to audio" = 4 file +12/−17 (commit `e01a8d05`).

**Why:** với ticket QC trên nhánh release, user ưu tiên diff nhỏ, dễ review, ít rủi ro hơn là làm đủ 100% chữ trong ticket. Gật đầu với "đề xuất" không có nghĩa là chấp nhận mọi hệ quả lan rộng mà đề xuất kéo theo.

**How to apply:**
- Khi đánh giá ticket, nêu kèm **ước lượng số file/khu vực bị đụng** cho mỗi hướng (vd "đụng navigation + 2 flow cũ").
- Luôn có một lựa chọn "giống hệt màn X đang có" nếu codebase đã có pattern tương tự, và đặt nó lên đầu khi ticket nằm trên nhánh release.
- Phần ticket không làm được trong bản gọn → nói rõ là chưa làm, không âm thầm bỏ.
Liên quan [[feedback-landscape-commit-message]].
