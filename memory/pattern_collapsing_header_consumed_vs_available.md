---
name: pattern_collapsing_header_consumed_vs_available
description: "Collapsing header (overlay + contentPadding) hở gap khi list ngắn — fix bằng collapse theo consumed, reveal theo available"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1f10aee8-ed76-4f9a-8dde-0232560746c8
---

Enter-always collapsing header dạng **overlay Box + `LazyColumn(contentPadding=top=headerHeight)`** (file `ui/component/CollapsingHeaderList.kt`): khi list "vừa fit" (scroll-range `R` nhỏ hơn header height `H`), header trượt hết `H` nhưng list chỉ scroll được `R` → hở khoảng trống trắng ở đỉnh. Đây là bug tickets #158 và #239 (cùng lớp lỗi).

**Đừng dùng guard `canScrollForward || canScrollBackward`**: cờ nhị phân này bị chính `contentPadding` làm nhiễu (đo trên `H + items` chứ không phải `items`) và `canScrollBackward` true ngay khi list nhích 1px → chỉ bắt được case list hoàn toàn không scroll được, lọt case "vừa fit".

**Fix đúng — tách 2 kênh trong `NestedScrollConnection`:**
- Reveal (vuốt xuống, `available.y > 0`) → `onPreScroll` dùng `available.y` → header hiện lại tức thì (enter-always).
- Collapse (vuốt lên, `consumed.y < 0`) → `onPostScroll` dùng `consumed.y` (khoảng list THỰC SỰ scroll) → list ngắn consume ~0 → header đứng yên → không bao giờ hở gap.

Invariant giữ luôn đúng: `|headerOffset| ≤ list_scroll`. Không cần đo `layoutInfo`.

**Test:** tách quyết định thành pure fn `nextHeaderOffset(current, availableY, consumedY, headerHeightPx)` (branch: availableY>0 → reveal; consumedY<0 → collapse; else 0; clamp `[-H,0]`) rồi JVM unit test — deterministic, khỏi emulator. Phần callback nào gọi hàm nào = delegation, skip UI test.

Trade-off còn lại: enter-always vẫn cho header overlap mép item đầu vài frame khi vuốt xuống lúc list đang scrolled — cố hữu của pattern, không phải gap.
