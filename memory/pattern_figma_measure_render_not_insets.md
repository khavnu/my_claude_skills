---
name: pattern-figma-measure-render-not-insets
description: "Kích thước icon/shape từ Figma MCP phải đo trên ảnh render 1:1, không lần ngược các lớp inset % lồng nhau"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 31f6884d-949a-493f-a58e-eb1b5204efd7
  modified: 2026-09-14T02:20:53.198Z
---

`get_design_context` trả React+Tailwind với `inset-[8.33%]`, `aspect-[22/22]`, `left-1/2` lồng
nhiều tầng. Lần ngược chuỗi % đó ra dp **sai hệ số tỉ lệ** — các tầng không cùng gốc toạ độ, và
`aspect-[22/22]` là kích thước node gốc trong Figma chứ không phải kích thước lúc đặt vào layout.

**Why:** Ngày 2026-09-14, dựng `SpeedRingIcon` (utility row của Large Player) tôi suy ra
r=7.5dp / stroke=1.67dp / chữ 8sp từ các lớp `inset`. User bảo check lại. Đo pixel trên ảnh render
1:1 ra **r=9dp / stroke=2dp / chữ 10sp** — tôi đã nhân dư một hệ số 0.8333, vòng tròn nhỏ hơn thiết
kế 17%. Tỉ lệ thật giữa SVG và dp là **1:1**.

**How to apply:**

1. Tải screenshot frame ở đúng kích thước gốc → `1px = 1dp`:
   `get_screenshot(maxDimension = original_width)` rồi `wget`. `maxDimension` chỉ **giới hạn**,
   không phóng to — xin số lớn hơn kích thước gốc vẫn trả về đúng native size.
2. Đo bằng cường độ pixel, không dùng ngưỡng nhị phân. Stroke phủ **trọn** pixel nào thì mép nằm
   ở biên pixel đó:
   ```python
   # nền #0F132E ≈ 26; ink ≈ 239
   # 2:239 3:239 4:26  →  mép ngoài tại x=2.0, stroke dày đúng 2.0
   ```
   Ngưỡng `sum(rgb) > N` nuốt mất pixel antialias và làm lệch 1px mỗi bên.
3. Suy font size từ cap height bằng một text **đã biết cỡ** trong cùng ảnh:
   `ratio = cap_height_px / known_sp` (Noto Sans ra đúng 0.714) → `size = cap_height / ratio`.
4. Crop để đo chữ bên trong shape phải tránh mép trong của shape — nếu không sẽ đo nhầm vành.

Chỉ dùng `inset` % để biết **thứ tự lớp và hướng layout**, còn con số thì lấy từ ảnh render.
Xem thêm [[feedback_visual_reading]] và [[feedback_figma_apply_output]].
