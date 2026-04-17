---
name: PptReader current status
description: Trạng thái fix PPT rendering — những gì đã xong và còn lại
type: project
---

## Đã fix (session 2026-04-13) — rendering hoạt động tốt

1. **Master placeholder text pollution** — master shapes chỉ render fill color, không render text
2. **`when` block ordering** — `is HSLFAutoShape` trước `is HSLFTextShape`
3. **Background color** — lấy từ `slide.masterSheet?.background`
4. **Dark slide text** — `contrastColor()` tính luminance → set default text color
5. **Locale CSS fix** — tất cả `%.2f` format dùng `Locale.US`
6. **EscherClientAnchorRecord field mapping** — mapping đúng: `flag=top(y1), col1=left(x1), dx1=right(x2), row1=bottom(y2)`. Verified: title.row1 == subtitle.flag (contiguous layout).
7. **Group flattening** — `renderGroup` flatten children ra slide level, không wrap trong positioned div
8. **Text overflow** — `overflow:visible` cho text div (positioned case) để title text không bị clip trong anchor box nhỏ
9. **Vertical alignment** — `getVerticalAlignCss()` đọc `getVerticalAlignment()` từ HSLF → CSS flex alignment (MIDDLE/BOTTOM)
10. **Image positioning/sizing** — fix theo coordinate mapping đúng ở #6
11. **Slide 18 blank (HSLFTable → java.awt crash)** — `slide.getShapes()` throws `NoClassDefFoundError: java.awt.geom.Rectangle2D` trên Android khi slide chứa HSLFTable. Fix: catch block gọi `renderShapesViaEscher()` — đi thẳng vào PPDrawing Escher tree, bỏ qua HSLFTable construction hoàn toàn. User confirm: "Nhìn cũng được rồi đấy".

## Trạng thái hiện tại
- User xác nhận: "Ô, ngon rồi đấy" — rendering PPT hoạt động tốt (session đầu)
- User xác nhận: "Nhìn cũng được rồi đấy" — slide 18 (table/Milestones) fix xong (session 2026-04-13)
- Debug logs đã xóa hết

## Lưu ý kỹ thuật quan trọng
- `getAnchor()` via reflection LUÔN LUÔN FAIL trên Android (InvocationTargetException) → Escher records là primary path thực sự
- EscherChildAnchorRecord: `getDx1/getDy1/getDx2/getDy2` IS correct (x1,y1,x2,y2)
- EscherClientAnchorRecord: `flag/col1/dx1/row1` → top/left/right/bottom (khác với EscherChildAnchorRecord)
