---
name: pattern-compose-state-timing-traps
description: "Hai bẫy đọc state sai thời điểm trong Compose — remember khoá theo giá trị đang nhảy, và callback đọc tham số composable trong cùng frame"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 31f6884d-949a-493f-a58e-eb1b5204efd7
  modified: 2026-09-14T08:24:12.285Z
---

Hai lỗi cùng họ, đều **không lộ ra khi test trường hợp thường**, chỉ lộ khi giá trị nguồn đang thay đổi.

**Why:** cả hai đều gặp thật ngày 2026-09-14 khi làm sheet speed và sleep timer.

## 1. `remember(key)` khoá theo giá trị đang chạy

```kotlin
// SAI — initialDurationMs là đồng hồ đếm ngược, nhảy mỗi giây
var durationMs by remember(initialDurationMs) { mutableLongStateOf(initialDurationMs) }
```

Mỗi giây khoá đổi → `remember` dựng lại → xoá sạch thứ người dùng vừa xoay. Sheet vốn được tạo mới mỗi lần mở, nên **bỏ khoá** là đúng ngữ nghĩa:

```kotlin
var durationMs by remember { mutableLongStateOf(initialDurationMs) }
```

Ghi ràng buộc vào `@param` chứ không chỉ comment trong thân hàm — nhìn code thì "keyed remember" trông *đúng hơn*, người sau rất dễ thêm khoá lại cho sạch.

Cùng bẫy với cờ chọn mặt sheet: `remember { mutableStateOf(remainingMs == null) }` phải không khoá.

## 2. Callback đọc tham số composable trong cùng một frame

```kotlin
// SAI — `speed` bị bắt lúc compose
onValueChangeFinished = { onSpeedChangeFinished(speed) }
```

Với một cú **tap**, `onValueChange(1.6)` rồi `onValueChangeFinished()` chạy liền nhau trong một frame, **trước** khi recomposition kịp giao `speed` mới → callback thứ hai gửi lại giá trị cũ và ghi đè.

Kéo thả thì không lộ vì cú kéo dài ~500ms, recomposition kịp chen vào. **Chỉ test bằng kéo là lọt.**

Sửa ở API: component tự trả giá trị cuối.

```kotlin
onValueChangeFinished: (Float) -> Unit   // thay vì () -> Unit
```

## Cách phát hiện

Cả hai chỉ lộ khi **nguồn đang chạy**. Test bằng tap lẫn kéo, và test khi đã có sẵn một giá trị đang biến thiên — không chỉ từ trạng thái tĩnh ban đầu.

Xem thêm [[pattern_compose_state_capture_in_coroutine]].
