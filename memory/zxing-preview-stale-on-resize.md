---
name: zxing-preview-stale-on-resize
description: Camera preview của zxing-android-embedded trong repo này hỏng nếu container bị resize sau khi preview đã chạy
metadata: 
  node_type: memory
  type: project
  originSessionId: f9ed9259-f23c-46d8-897d-14f4e50e1db0
  modified: 2026-08-26T03:01:17.170Z
---

Trong `zxing-android-embedded/.../CameraPreview.java`, `calculateFrames()` — nơi tính `framingRect` và `surfaceRect` — chỉ có **một** call site: bên trong `previewSized()`, tức chỉ chạy khi camera trả về preview size lần đầu. `onLayout()` chỉ gọi `containerSized()`, mà hàm này lại bị chặn bởi `if (displayConfiguration == null)` nên cũng không cấu hình lại.

Hệ quả: mọi thay đổi kích thước container camera **sau khi** preview khởi tạo đều để lại `surfaceRect`/`framingRect` cũ → dải màu trống ở đáy + khung ngắm lệch. App dùng `zxing_use_texture_view="false"` (SurfaceView + `FitCenterStrategy`), nên `surfaceView.layout(surfaceRect...)` giữ nguyên vị trí cũ, càng lộ rõ.

`reLayout()` (public) KHÔNG cứu được — nó chỉ gọi lại `onLayout()`. Cách duy nhất ép tính lại là `pause()/resume()`, đổi lại camera restart nháy đen 200-500ms.

**Why:** bất kỳ thay đổi layout nào ảnh hưởng chiều cao `viewPager` trong `home_activity.xml` đều chạm vào bug này. Banner ads load/unload hiện vẫn resize ViewPager (hành vi có sẵn, được bù bằng `updateLayoutControlPosition()`).

**How to apply:** khi cần thêm/bớt view ở đáy HomeActivity, cho camera full-screen sẵn rồi overlay view lên trên, đừng để nó chia chiều cao với camera. Xem [[bottom-bar-anchor-pattern]].
