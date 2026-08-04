---
name: pattern_nav3_transition_input_gate
description: Navigation3 NavDisplay giữ entry exit hit-test suốt 700ms fade → tap lạc sang màn đang biến mất; chặn bằng NavEntryDecorator đọc LocalNavAnimatedContentScope
metadata: 
  node_type: memory
  type: project
  originSessionId: f4de034b-f8f0-4680-9263-b44c7950769c
---

Navigation3 `NavDisplay` (nav3 1.0.0) dùng default transition `fadeOut` **700ms** (`DEFAULT_TRANSITION_DURATION_MILLISECOND`). Trong suốt cửa sổ đó, entry đang **exit** vẫn được compose + hit-test → tap nhanh ngay sau Back/pop có thể rơi vào control của màn đang biến mất nếu nó trùng vị trí control của màn được reveal (ticket #250: nút Home màn "Saved successfully" trùng vị trí nút Save màn edit → tap Save sau Back nhảy nhầm Home).

**Fix — 1 decorator dùng chung, áp cho MỌI entry:**
- File: `navigation/TransitionInputBlockingDecorator.kt` → `rememberTransitionInputBlockingDecorator<T>()`.
- Đọc `LocalNavAnimatedContentScope.current.transition`; nếu `transition.targetState == EnterExitState.PostExit` (đang exit) → bọc `entry.Content()` trong `Box` + `Modifier.pointerInput` **consume toàn bộ change ở `PointerEventPass.Initial`**.
- Thêm vào `entryDecorators = listOf(...)` của NavDisplay, sau 2 decorator bắt buộc (saveable + viewModelStore).
- Đã áp cho cả 7 NavDisplay (root + 6 nested: edit, video_to_audio, merge, 3 folders tab).

**Key facts (verified từ source jar nav3 1.0.0):**
- `NavEntry.Content()` là hàm public gọi content; `NavEntryDecorator<T> { entry -> ... }` là API tạo decorator (constructor public, `decorate` là trailing lambda).
- Decorator chạy BÊN TRONG AnimatedContent nên `LocalNavAnimatedContentScope` luôn available.
- Robust với z-order: dù màn exit vẽ trên hay dưới, control của nó không nhận tap.

**Why:** transition dài + input không bị chặn = misroute tap; gate input trên entry non-settled khiến chỉ màn incoming/settled nhận touch.

**How to apply:** bất kỳ NavDisplay mới nào → thêm `rememberTransitionInputBlockingDecorator()` vào `entryDecorators`. Khó viết UI test deterministic (phụ thuộc transition-clock nội bộ + `decorate` là `internal`) → QC tay. Liên quan [[feedback_flow_patterns]], [[pattern_compose_flicker_fix]].
