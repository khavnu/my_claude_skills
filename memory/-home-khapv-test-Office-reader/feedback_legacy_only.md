---
name: Legacy-only work rule
description: Only touch legacy readers — never modify working modern format code
type: feedback
---

Chỉ làm việc với legacy readers (`reader/legacy/DocReader.kt`, `XlsReader.kt`, `PptReader.kt`).

**Why:** Modern format handling (.docx, .xlsx, .pptx) via JsRenderer + bridge.js đã hoạt động tốt và ổn định. User không muốn risk break những thứ đang chạy.

**How to apply:** Khi fix/improve legacy formats, không được đụng vào:
- `JsRenderer.kt`
- `bridge.js` / `office.css`
- `DocxReader.kt`, `XlsxReader.kt`, `PptxReader.kt`
- `OfficeView.kt` (trừ khi bắt buộc do legacy routing)
- Bất kỳ logic nào của modern format
