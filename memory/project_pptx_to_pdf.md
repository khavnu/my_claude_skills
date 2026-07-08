---
name: Office to PDF Feature
description: Trạng thái feature office-to-pdf native (pptx/ppt/docx/doc → pdf) trên branch khapv/convert_remastered
type: project
originSessionId: c80b66f5-f64e-476f-ab9b-7c3a79ff12dc
---
Feature convert Office files (PPTX/PPT/DOCX/DOC) → PDF native (không dùng WebView/LibreOffice).

**Why:** Background conversion không cần Activity context.

**Files chính:**
- `office_reader/.../pdf/SlideToPdfConverter.kt` — PPTX+PPT via XSLF/HSLF, reflection bypass java.awt.*, ~1500 lines
- `office_reader/.../pdf/WordToPdfConverter.kt` — DOCX+DOC via XWPF/HWPF Canvas, ~1930 lines
- `office_reader/.../pdf/OfficeToPdfConverter.kt` — dispatcher theo extension
- `data/.../DefaultFileProcessingRepository.kt` — convertOfficeToPdf() đã wire
- `data/.../DefaultConvertRepository.kt` — convertOfficeToPdf() đã wire

**Status (2026-05-12):**
- DOCX: working well — rich text, tables, images, inline styles
- PPTX/PPT: working — shapes, images, bullet lists
- DOC: working — rich text (bold/italic/color/fontSize), inline images (với đúng scaling factor), all content visible. Layout multi-column chưa support (HWPF không expose đủ thông tin để reconstruct)
- Chưa commit. Branch: `khapv/convert_remastered`

**DOC layout limitation:**
`legacy_Pet resume.doc` có 2-column layout (image trái, text phải) mà HWPF không parse được:
- `dxaAbs/dyaAbs/dxaWidth = 0` cho tất cả paragraphs (không có paragraph frames)
- `officeDrawingsMain.officeDrawings` empty (không có floating shapes)
- Layout mechanism chưa xác định được qua HWPF API

**How to apply:** Khi làm việc với DOC, xem `project_hwpf_learnings.md` trước.
