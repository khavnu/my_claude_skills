---
name: pattern-separate-process-needs-more-than-manifest
description: Thêm android:process cho service KHÔNG chuyển việc nặng sang process đó — Hilt dựng @Singleton thứ hai và mọi thứ đọc state rỗng
metadata: 
  node_type: memory
  type: project
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-16T09:08:57.277Z
---

Thử ngày 2026-09-16 vì migration note của lib xếp "run separation in its own process" là việc đáng
giá nhất. Cách rẻ nhất — thêm `android:process=":separation"` cho `SeparationForegroundService` —
**không những vô ích mà còn làm hỏng notification**.

Đo sau khi thêm, lúc đang tách:

```
process chính (UI)    TOTAL 1.88 GB   Native Heap 1.36 GB   ← arena vẫn ở đây
process :separation   TOTAL  148 MB   Native Heap   14 MB   ← rỗng
```

Log `separateSegment[...]` mang **pid của process UI**, không phải process con.

**Why:** service không chạy việc tách — nó chỉ giữ process priority và vẽ notification. Việc tách
sống trên `applicationScope` của `SeparationSessionController`, một `@Singleton`. Hilt tạo
`@Singleton` **riêng cho từng process**, nên service ở process mới inject một controller thứ hai,
rỗng: session vĩnh viễn `Idle` → `dropWhile { it is Idle }` không bao giờ cho qua → `collect` không
chạy → notification kẹt không cập nhật %, và nút Cancel gọi `stop()` trên controller không liên quan
đến run thật.

**How to apply:** muốn đạt điều note mô tả (biến cú chết im lặng thành lỗi bắt được) thì phải chuyển
**engine + controller** sang process con, cộng AIDL/Messenger vì `StateFlow` không vượt ranh giới
process, `SeparationSnapshot` phải Parcelable, và playback vẫn phải ở process UI (Media3 cần Activity
TOP — xem [[pattern-audio-focus-needs-top-activity]]). Vài ngày làm việc, không phải một dòng
manifest. Đừng thử lại đường tắt.

Liên quan: [[project-separation-device-limits]], [[project-playback-service-same-process]]
