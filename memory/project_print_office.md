---
name: Print Office Feature
description: Architecture và các fix quan trọng của feature print DOCX/PPT/XLS từ viewer và file list (branch feature/print)
type: project
originSessionId: 9b5e7455-32a8-4ddb-afbf-b018e3b89366
---
Feature print office files (DOCX/DOC/PPTX/PPT) từ cả file list lẫn viewer.

**Why:** PrintManager cần toàn bộ page HTML trên disk trước khi print — chỉ có `DocumentViewerView` mới parse được, nên không thể print trực tiếp như PDF/image.

---

## Hai luồng print

**Luồng A — từ file list (autoPrint=true):**
`FileActionMenuBottomSheetRoute.PRINT` → `Unit` (delegate lên caller) → caller navigate tới viewer với `autoPrint=true` → viewer parse xong → `connectToPrinterAndPrint()`

**Luồng B — từ trong viewer (autoPrint=false):**
`FileActionBottomSheets.PRINT` → `onPrintClick` → `printRequested=true` → `LaunchedEffect` → `connectToPrinterAndPrint()`

---

## Files chính

| File | Vai trò |
|------|---------|
| `office_reader/.../viewer/host/DocumentViewerView.kt` | `connectToPrinterAndPrint()`, `cancelPrint()`, `printJob: Job?` |
| `office_reader/.../viewer/print/PrintHtmlBuilder.kt` | Build flat paginated HTML (page-break-after:always mỗi trang) |
| `app/.../feature/viewer/office/NewDocxViewerScreen.kt` | `printRequested`, `autoPrint`, `onCancelPrint`, LoadingDialog |
| `app/.../feature/viewer/office/NewSlideViewerScreen.kt` | Same as Docx |
| `app/.../bottom_sheet/action_menu/files/FileActionMenuBottomSheetRoute.kt` | `PRINT` office → `Unit` + delegate |
| `app/.../feature/files/component/FileActionBottomSheets.kt` | `PRINT` → `onPrintClick` (viewer đã open) |

---

## Các fix quan trọng và lý do

### 1. Slide in 1/1 pages
Viewer WebView dùng scroll-snap (`height:100vh`, `overflow:auto`) → Chrome print adapter chỉ capture được 1 viewport.
**Fix:** Build flat HTML qua `PrintHtmlBuilder` (cùng pipeline với exportToPdf), load vào off-screen WebView ẩn (`alpha=0f`), dùng WebView đó cho print adapter.

### 2. Loading dialog dismiss quá sớm
Condition cũ: `printRequested && !isParseComplete` → dialog bị dismiss ngay khi parse xong, trước khi async print prep bắt đầu (document 1925 trang mất nhiều giây build HTML).
**Fix:** `if (printRequested)` — dialog tồn tại suốt toàn bộ print flow.

### 3. onReady timing — dismiss đúng lúc
`onPrintConsumed` (reset `printRequested`) được pass vào `connectToPrinterAndPrint()` như `onReady` param, chỉ được gọi ngay trước `printManager.print()`. Giữ dialog visible trong suốt giai đoạn async HTML build + WebView load.

### 4. Background/foreground
`lifecycle.withResumed {}` — suspend coroutine cho tới khi Activity ở RESUMED state. Tránh `PrintManager.print()` bị gọi khi app đang background (dialog sẽ bị drop silently).

### 5. printWebView leak khi cancel
`try/finally` với `printDispatched: Boolean` — nếu coroutine bị cancel trước khi `printManager.print()` được gọi, `finally` block remove + destroy printWebView.

### 6. TOCTOU crash khi cancel (FileNotFoundException)
User bấm Cancel → `view.close()` → `store.delete()` xóa page files → coroutine vẫn đang chạy trong `PrintHtmlBuilder.build()` trên `Dispatchers.IO` → `file.exists()` trả về true → file bị xóa → `file.readText()` throw `FileNotFoundException` → crash.
**Fix kép:**
- `printJob?.cancel()` trong `close()` trước `store?.delete()` — cancel sớm
- `readPage()` dùng `try-catch IOException` thay vì TOCTOU-unsafe `if (exists())`

### 7. Cancel không thoát viewer khi đang xem
`onCancelPrint` cũ luôn gọi `onBack()`. **Fix:** `if (autoPrint) onBack()` — chỉ navigate back khi mở viewer từ file list.

### 8. Cancel không dừng print coroutine
Dialog Cancel chỉ reset `printRequested` nhưng coroutine vẫn chạy, có thể gọi `PrintManager.print()` sau cancel.
**Fix:** `LoadingDialog.onClick` gọi `documentView?.cancelPrint()` trước `onCancelPrint()`.

---

## Status (2026-06-15)
- DOCX print: working — multi-page đúng số trang, dialog persist đủ lâu
- PPTX/PPT print: working — slide đúng số trang (fix 1/1 pages)
- Cancel: safe — coroutine bị cancel, không crash, viewer/file list navigation đúng
- Branch: `feature/print`
