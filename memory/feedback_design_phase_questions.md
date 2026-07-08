---
name: Design Phase — Câu hỏi kỹ thuật trước khi viết plan
description: Trước khi commit vào plan, tôi phải tự đặt câu hỏi về API lạ và layout/CSS constraints — không để implementation discovery thay thế design thinking
type: feedback
originSessionId: 9b5e7455-32a8-4ddb-afbf-b018e3b89366
---
Trước khi viết plan cho bất kỳ feature nào, tôi phải chủ động đặt câu hỏi kỹ thuật và verify assumptions — không assume "đơn giản là đủ".

**Why:** Feature print office file: plan đề xuất `connectToPrinterAndPrint()` 4 dòng dùng viewer WebView trực tiếp. Thực tế viewer WebView có scroll-snap CSS (`height:100vh`, `overflow:auto`) → Chrome print adapter chỉ capture 1 viewport → 1/1 pages. Câu hỏi này tôi có đủ context để đặt ra ở design phase nhưng đã không làm — dẫn đến plan sai và phải fix trong implementation.

**How to apply:**

**1. Với API lạ/ít dùng** (WebView printing, PrintManager, MediaProjection, v.v.):
- Đọc doc + đọc code thực tế trước khi viết plan
- Đặt câu hỏi: *"API này có constraints gì không rõ ràng từ tên gọi?"*
- Nếu không chắc → spike 20-30 dòng code để validate assumption trước khi commit vào design

**2. Với WebView / rendering:**
- Luôn hỏi: *"WebView này có scroll container, overflow clipping, hay CSS transform nào ảnh hưởng đến print/screenshot/export không?"*
- Đọc stylesheet hoặc HTML template của viewer trước khi đề xuất dùng nó cho print/export

**3. Với UI component mới:**
- Tìm xem codebase đã có component tương tự chưa trước khi propose tạo mới
- `LoadingDialog` đã tồn tại — `PrintPreparingOverlay` không cần tạo

**4. Với async/lifecycle:**
- Hỏi: *"Điều gì xảy ra nếu user cancel, background app, hoặc navigate away trong khi operation đang chạy?"*
- Design cancellation path ngay từ đầu, không để đến lúc test mới nghĩ

**5. Với dialog/loading UX:**
- Hỏi: *"Dialog cần visible trong bao lâu? Dismiss condition có phụ thuộc vào async step nào không?"*
- `printRequested && !isParseComplete` là sai vì bỏ qua giai đoạn async sau parse
