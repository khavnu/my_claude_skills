---
name: project_mix_reset_is_policy_not_necessity
description: "resetMixPreview() trên màn Separation result là yêu cầu QA, không phải ràng buộc kỹ thuật — player apply volume/fade live được; comment trong code là biện minh hậu kỳ"
metadata: 
  node_type: memory
  type: project
  originSessionId: 963158e9-c09f-4361-9181-29bce6730c03
  modified: 2026-09-25T02:20:22.462Z
---

Ticket #422 (V1.2) bắt "chỉnh stem → dừng Mix + reset playback về 00:00". Đây là **chính sách QA**,
không phải giới hạn của player:

- `DefaultSeparationPlaybackRepository.previewEdit()` đẩy thẳng `setStemVolume` + `setStemFade`
  xuống player đang chạy, không rebuild stream, không seek.
- `isAudible()` cover cả Mix context (`isMixing` + stem nằm trong `mixedStems`) — tức đúng kịch bản
  của ticket đã được hỗ trợ sẵn.
- `SeparationSessionController.resetMixPreview()` toàn bộ chỉ là `if (current.isMixing) stop()`.
- Volume >100% được preview thật qua limiter khớp với limiter lúc render → preview trung thực bằng
  file Save ra.
- Volume/fade không đổi độ dài track, nên lập luận "vị trí cũ thuộc về bản mix cũ" không đứng được.

**Why:** KDoc của `updateEdit()` viết rất thuyết phục — *"committing one makes it a different piece
of audio — the position it was at belongs to the old one"* — nhưng đó là văn biện minh viết NGƯỢC
lại sau khi đã nhận yêu cầu, không phải lý do thiết kế gốc. Đọc comment đó mà tin sẽ tưởng có ràng
buộc kỹ thuật và không tìm nữa.

**How to apply:** Khi đụng lại vùng mix preview của Separation result, đừng suy ra ràng buộc từ
comment — đọc `previewEdit()` và `resetMixPreview()` trước. Nếu sau này có ticket đòi "giữ phát khi
chỉnh stem" thì chỉ cần gỡ lời gọi `resetMixPreview()` ở `updateEdit()` và `revertStem()`, không
phải sửa gì ở tầng player.

Đã quyết định (25/09/2026) KHÔNG push back với QA — implement theo đúng spec. Xem thêm
[[project_separation_open_items.md]].
