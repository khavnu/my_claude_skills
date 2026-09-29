---
name: bottom-bar-anchor-pattern
description: "HomeActivity dùng view neo vô hình làm mốc căn lề đáy, không đọc chiều cao TabLayout"
metadata: 
  node_type: memory
  type: project
  originSessionId: f9ed9259-f23c-46d8-897d-14f4e50e1db0
  modified: 2026-08-26T03:01:30.195Z
---

`home_activity.xml` có `@+id/view_tabbar_anchor` — một `View` `INVISIBLE`, `alignParentBottom`, cao đúng bằng TabLayout. Mọi tính toán căn theo đáy màn hình đọc từ anchor này qua `HomeActivity.getTabbarHeight()`, KHÔNG đọc `mTabLayout.getHeight()`.

Lý do: TabLayout ẩn/hiện bằng `translationY` + `INVISIBLE` khi user tap vào tab Scan. Nếu các view khác căn theo nó thì chúng xê dịch theo animation. Anchor đứng yên nên `layout_control` của ScanFragment (Photos/Torch/Batch + zoom) và `paddingBottom` của 3 tab kia không bao giờ nhảy.

`fixTabLayoutHeight()` phải set chiều cao cho **cả** TabLayout lẫn anchor. Hàm này cũng không được tạo `new LinearLayout.LayoutParams(...)` — TabLayout là con của `RelativeLayout`, ép kiểu sai sẽ ClassCastException ở measure pass; phải mutate params sẵn có.

**Why:** `INVISIBLE` (không phải background trong suốt) để anchor vẫn được đo/layout nhưng không nhận touch, tránh cản gesture tap-to-toggle của ScanFragment.

**How to apply:** thêm view nào cần bám đáy HomeActivity thì căn theo anchor. Liên quan: [[zxing-preview-stale-on-resize]].
