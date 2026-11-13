---
name: pattern-rotation-resets-remember
description: Xoay màn hình mất state UI dù Activity không recreate — remember nằm trong nhánh portrait/landscape hoặc trong AdaptiveSheet; sửa bằng rememberMovableContent hoặc hoist lên trên AdaptiveSheet
metadata:
  node_type: memory
  type: project
  originSessionId: 50677524-b6cb-43a8-81cf-c447d243ebd0
  modified: 2026-10-27T01:34:18.424Z
---

MainActivity có `configChanges=orientation|screenSize|...` (AndroidManifest.xml:41) nên xoay KHÔNG recreate Activity, ViewModel giữ nguyên. Nhưng QA vẫn báo "xoay mất state" (#464, #465, 2026-10-27) vì:

1. **State `remember` trong composable được gọi ở 2 nhánh `if (checkScreenSizeMode() == ScreenSizeMode.Landscape) … else …` (trước 2026-10-27 là `isLandscapeOrientation()`)** — đổi nhánh = call site mới = `remember` khởi tạo lại. Ví dụ chip preset trong `SpeedAdjustmentSection` (state nội bộ, init theo `speed == 1f`). Sửa: bọc lambda bằng `rememberMovableContent` (`ui/component/MovableContent.kt`) — commit `deabcc31`.
2. **State `remember` bên trong `AdaptiveSheet`** — xoay đổi bottom sheet ↔ SidePanel (2 dialog window khác nhau), content dựng lại. Sửa: hoist state lên trên lời gọi `AdaptiveSheet`, truyền value + callback xuống — commit `710029d5` (TransitionBottomSheet). rememberMovableContent qua 2 dialog window chưa kiểm, đừng dựa vào.

`rememberSaveable` KHÔNG cứu được cả 2 trường hợp (state bị unregister khi composable rời composition).

**How to apply:** ticket "xoay mất trạng thái" → tìm `remember` của state đó, xem nó nằm dưới nhánh orientation hay dưới AdaptiveSheet. Còn nhiều chỗ cùng pattern chưa sửa (vd `SpeedBottomSheet` trong editor dùng SpeedAdjustmentSection bên trong AdaptiveSheet). Verify trên máy: `cmd window user-rotation lock 1` rồi `lock 0`, chụp trước/sau. Liên quan [[reference-device-rotation-testing]].
