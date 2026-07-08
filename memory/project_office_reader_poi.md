---
name: office_reader POI Patched JARs — Non-obvious Fixes
description: Critical non-obvious decisions in the office_reader module related to Apache POI on Android
type: project
originSessionId: ac81b197-a1c1-4cfe-b509-90c11f3a43d3
---
Two runtime crashes were fixed by patching the POI JARs. These are not obvious from reading the code.

**Fix 1 — VerifyError on XLSX open (commons-io)**
`UnsynchronizedByteArrayInputStream$Builder` had a covariant return type chain (`Builder → AbstractOriginSupplier → AbstractStreamBuilder`). Android ART rejects this when `AbstractStreamBuilder` is absent from the classpath. Fixed by replacing the class with a standalone stub that extends `ByteArrayInputStream` directly — no abstract chain.
File: `office_reader/libs/commons-io-2.15.0-patched.jar`

**Why:** ART verifies the entire class hierarchy at load time, not lazily like JVM. Even if Builder is never called, loading the class fails.

**How to apply:** If `VerifyError` appears for any class in the patched JARs, check for broken abstract superclass chains — the fix is always a standalone stub, not patching the chain.

---

**Fix 2 — OutOfMemoryError on large XLSX (XSSFWorkbook → SAX streaming)**
`XSSFWorkbook` (DOM) loads all sheets simultaneously. With 15+ sheets × 60+ columns, millions of `XSSFCell` objects are created → OOM on 256 MB heap.

Fixed by rewriting `ExcelToPdfConverter` to use `OPCPackage.open() + XSSFReader + SAX DefaultHandler`. Each sheet is parsed one at a time into a lightweight `SheetModel`.

**Why:** DOM approach is fine for small files but fails at scale. SAX keeps memory constant regardless of workbook size.

**How to apply:** Always use the SAX path for XLSX in `ExcelToPdfConverter`. Never revert to `XSSFWorkbook` for conversion.
