---
name: pattern-fgs-stop-before-startforeground
description: stopService() ngay sau startForegroundService() giết app — phải route lệnh dừng qua chính service
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-09T09:28:02.278Z
---

`stopService()` gọi quá gần `startForegroundService()` (trước khi `onStartCommand` kịp chạy) khiến
lời hứa `startForeground()` không bao giờ được giữ → platform ném
`RemoteServiceException$ForegroundServiceDidNotStartInTimeException` và **giết process**.

Đo được 2026-09-09 trên Pixel 9 / Android 16: khoảng cách chỉ **3ms** giữa
`Background started FGS: Allowed` và `Bringing down service while still waiting for start foreground`.
Không phải timeout 5s — chỉ cần stop tới trước `onStartCommand`.

**Why:** người dùng bấm Start rồi Cancel liên tiếp là gặp ngay. Không có cách nào chặn ở phía caller
vì `onStartCommand` chạy bất đồng bộ.

**How to apply:**
- Lệnh dừng gửi bằng `context.startService(intent.setAction(ACTION_STOP_SELF))`, **không** dùng
  `stopService()`.
- `onStartCommand` gọi `startForeground()` **đầu tiên trên mọi nhánh**, kể cả nhánh dừng ngay,
  rồi mới `stopSelf()`.
- Bọc `startService` trong try/catch `IllegalStateException`: app ở background mà service chưa chạy
  thì không được phép start — nhưng lúc đó cũng không có notification nào cần gỡ.

Tham chiếu: `data/separation/SeparationForegroundService.kt`, `AndroidSeparationRunHost.kt`,
test khoá hành vi `androidTest/.../SeparationForegroundHostTest.kt`.

Liên quan: [[project_audio_separation]].
