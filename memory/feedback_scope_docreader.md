---
name: DocReader scope restriction
description: Only modify DocReader.kt and directly related files; avoid touching other working files
type: feedback
---

Only change files directly related to the current task (e.g. DocReader.kt). Do not touch files for other formats (DocxReader, PptxReader, XlsxReader, PptReader, XlsReader, OfficeView, etc.) unless explicitly asked.

**Why:** Other features are working correctly. Unrelated changes risk breaking them.

**How to apply:** Before editing any file outside DocReader.kt, confirm with the user first.
