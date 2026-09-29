---
name: pattern-timer-end-instant-not-countdown
description: "Hẹn giờ phải lưu mốc kết thúc và đọc lại đồng hồ mỗi tick, không trừ dần qua delay — delay ngưng cùng process khi máy vào Doze"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 31f6884d-949a-493f-a58e-eb1b5204efd7
  modified: 2026-09-14T08:24:33.035Z
---

```kotlin
// SAI — trừ dần
var remaining = durationMs
while (remaining > 0) { delay(TICK); remaining -= TICK }

// ĐÚNG — lưu mốc, đọc lại đồng hồ
val endTime = System.currentTimeMillis() + durationMs
var remaining = endTime - System.currentTimeMillis()
while (remaining > 0) { delay(min(remaining, TICK)); remaining = endTime - System.currentTimeMillis() }
```

**Why:** `delay` bị treo cùng process khi máy vào Doze. Bản trừ dần tỉnh dậy vẫn tưởng còn nguyên từng ấy phút — hẹn 15 phút có thể kêu sau 40 phút. Đọc lại đồng hồ tường thì tỉnh dậy là đúng ngay. Phát hiện ngày 2026-09-14 khi đối chiếu với `green_ba_music_player` (`MusicService.countDownEndTime`).

**How to apply:**

- Expose **mốc kết thúc**, không expose thời gian còn lại. Người dùng nó tự tick theo nhịp họ cần, và mỗi bên tự đọc lại đồng hồ.
- Tầng hiển thị tick riêng trong `viewModelScope` (`CountdownTimerHelper`): không ai xem thì không đếm. Tầng nghiệp vụ chỉ cần bắn đúng một lần lúc hết giờ.
- Canh trước khi hành động: `if (player.isPlaying) player.pause()`.
- Để test được đồng hồ tường, tiêm `currentTimeMs: () -> Long = System::currentTimeMillis` rồi thay bằng `testScheduler.currentTime`. **Phải có test đẩy đồng hồ nhảy vượt mốc trong khi thời gian ảo đứng yên** — đó chính là kịch bản Doze.

Liên quan: [[project_playback_service_same_process]].
