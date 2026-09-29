---
name: project-playback-service-same-process
description: "PlaybackService chạy chung process với app; foreground service giữ luôn các @Singleton sống — đo được, đừng suy đoán lại"
metadata: 
  node_type: memory
  type: project
  originSessionId: 31f6884d-949a-493f-a58e-eb1b5204efd7
  modified: 2026-09-14T08:24:54.113Z
---

Đo ngày 2026-09-14 bằng `dumpsys activity services`:

```
pid cua app   : 29859
PlaybackService
  processName = com.tmedilab.sounditor.music.audio.editor
  app         = ProcessRecord{... 29859: ...}      ← cùng pid
  isForeground= true
manifest      : KHONG co android:process nao
```

**Hệ quả:**

- Foreground service giữ **cả process** sống, nên mọi `@Singleton` (`DefaultPlaybackController`, `PlaybackSpectrumRepository`…) sống theo. `adb shell am kill` **không** giết được khi đang phát — pid không đổi.
- Service và singleton nói chuyện trực tiếp qua Hilt, không cần binder/IPC. Mẫu đang dùng: service ghi vào một `@Singleton` coordinator, UI đọc ra (`PlaybackSpectrumRepository`, `SleepTimerCoordinator`).
- `onTaskRemoved` chỉ `stopSelf()` khi **không** đang phát. Đang phát thì vuốt khỏi recents service vẫn sống.
- Controller sống **lâu hơn** service: service chết khi pause + task removed, còn controller sống tới khi process chết.

**Cách kiểm khi cần lại:**

```bash
adb shell dumpsys activity services <pkg> | grep -E "processName|app=|isForeground"
adb shell pidof <pkg>
```

Không dựng lại được kịch bản service-bị-huỷ bằng adb: `am stopservice` bị bind lại ngay nếu UI đang mở, `am kill` bị FGS chặn, vuốt recents bằng `input swipe` không ăn. Phải thử tay.

Liên quan: [[pattern_timer_end_instant_not_countdown]], [[pattern_fgs_stop_before_startforeground]].
