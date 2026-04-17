---
name: Office Reader project overview
description: Android library module rendering Office files (docx/xlsx/pptx/doc/xls/ppt) in WebView using JS libraries + POI fallback
type: project
---

Android library `:office_reader` with demo `:app`. Public API: `OfficeView.load(uri, quality)`.

**Architecture (current):**
- Modern formats (DOCX/XLSX/PPTX) → JS libraries in WebView (docx-preview, SheetJS, JSZip+DOMParser fallback)
- Legacy formats (DOC/XLS/PPT) → Apache POI → HTML → WebView
- `JsRenderer.kt` bridges Kotlin ↔ JS via `@JavascriptInterface`
- `bridge.js` contains all render logic for JS path
- `renderer.html` is the single HTML host page in assets

**Key decisions:**
- POI XSLF (PPTX) doesn't work on Android (java.awt dependency) → custom ZIP+XML parser in JS
- docx4j doesn't work on Android (javax.xml.stream) → removed
- PPTX2HTML jQuery plugin was unreliable → removed, always use JSZip fallback
- Viewport width=960 for DOCX so WebView auto-scales pages to fit screen
- PPTX uses native pixel rendering + CSS transform:scale()

**Test files:** `/home/khapv/Desktop/Offfice/` — Brochure.docx, Letter.docx, Resume.docx, Photo album.pptx, Your big idea.pptx

**Why:** User wants to view Office files within Android app without external apps or internet.

**How to apply:** Follow existing JS-in-WebView pattern. All rendering logic in bridge.js. CSS in office.css. No POI for modern formats.
