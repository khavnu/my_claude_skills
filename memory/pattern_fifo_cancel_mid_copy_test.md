---
name: pattern-fifo-cancel-mid-copy-test
description: "Deterministic device test for \"cancel during a file copy leaves no MediaStore row\" — use Os.mkfifo as the temp file; plain queries hide pending rows so count with QUERY_ARG_MATCH_PENDING"
metadata:
  node_type: memory
  type: project
  originSessionId: f8af6503-0c14-4b8d-b9c4-880554cd647d
  modified: 2026-10-15T09:27:45.443Z
---

To test that cancelling a save mid-copy rolls back MediaStore, don't race with `delay()`. Use a FIFO as the source file: `Os.mkfifo(cacheFile.path, 384 /*0600*/)` works from an androidTest in the app cache dir (Pixel 9, Android 17). Then:

1. Launch the insert on `Dispatchers.IO`.
2. Open `FileOutputStream(fifo)`, which blocks until the copy opens it. Write one chunk.
3. Cancel the job, write one more chunk so the blocked `read()` returns, then close.
4. The copy loop's `ensureActive()` then throws.

**Trap:** a pending row (`IS_PENDING=1`) is invisible to a normal query and to `exists()`. An assert of "0 rows" would pass even if the rollback were missing. Count with a `Bundle` that puts `MediaStore.QUERY_ARG_MATCH_PENDING = MATCH_INCLUDE` (API 30+), and delete test rows the same way in `@After`.

Verified 2026-10-15: `app/src/androidTest/.../data/mediastore/MediaStoreVideoOutputDataSourceTest.kt` passes, and removing the `resolver.delete(uri…)` rollback makes it fail with `expected:<0> but was:<1>`.

**Why:** `InputStream.copyTo` never checks for cancellation. A large video copy therefore needs a chunked loop with `ensureActive()`, and that loop has to be tested on a real MediaStore.

**How to apply:** for any new MediaStore writer (audio or video), reuse this test shape. After running it, reinstall the app and re-grant permissions (see [[reference-device-shot-helpers]] trap 7).
