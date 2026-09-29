---
name: dont-guess-unreadable-requirements
description: "Khi không đọc được nguồn yêu cầu (ticket cần login), phải lấy cho được nguồn — không dựng multiple-choice để đoán"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d938a362-5347-4eea-b290-64c4315c3b0a
  modified: 2026-09-14T01:46:14.300Z
---

Khi nguồn yêu cầu không đọc được (ticket sau login, Figma chưa có quyền, screenshot chưa gửi):
**đòi cho được nguồn** — xin credential, xin đường dẫn ảnh, xin user paste nội dung. Không được
dựng `AskUserQuestion` với các option do mình tự suy ra từ codebase rồi implement theo option user
bấm.

**Why:** đã xảy ra ở ticket 936. Không đọc được ticket, mình grep codebase thấy `btn_create_done.xml`
rồi đưa 3 option đều xoay quanh "nút Done màn Create". User bấm 1 option → mình sửa nút Done.
Ticket thật lại là *tăng width nút Scan/Create ở màn History empty cho bằng nút Done*. Nút Done chỉ
là **mốc so sánh**, không phải target. Câu hỏi trắc nghiệm trông như đang clarify, nhưng thực chất
đã khoá sẵn khung sai — user bấm trong khung đó thì câu trả lời cũng sai theo, và cái sai được
"đóng dấu xác nhận" nên khó phát hiện hơn là nếu mình hỏi mở.

**How to apply:** không đọc được nguồn → nói thẳng là không đọc được và hỏi mở ("paste nội dung
ticket / gửi đường dẫn screenshot / cho mình tài khoản"). Chỉ dùng multiple-choice khi đã đọc
nguồn và cái mơ hồ chỉ còn là con số hay lựa chọn implementation. Câu tiếng Việt kiểu "tăng chiều
rộng **bằng** button X" nhiều khả năng nghĩa là "cho bằng với X" (X là mốc), không phải "sửa X".

Liên quan: [[tohsoft-codebase-tickets]]
