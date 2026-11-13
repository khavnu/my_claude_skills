---
name: pattern-open-folder-intent-by-api
description: ACTION_VIEW on a directory document URI crashes the system Files app below Android 10 (getRootId in launch metrics); use the root URI there. Also the API<29 FULL_SCREEN_KIND thumbnail bug.
metadata:
  type: project
---

**Open folder:** `ACTION_VIEW` + `DocumentsContract.buildDocumentUri("com.android.externalstorage.documents", "primary:Movies/…")` + `Document.MIME_TYPE_DIR`.
- Works on API 36 (emulator) and 37 (Pixel 9).
- On API 27 it **crashes `com.android.documentsui`**: `Metrics.sanitizeRoot` → `DocumentsContract.getRootId` throws `Invalid URI`. The crash is in the other app, so our try/catch cannot stop it.
- Fix in `ui/util/VideoShareIntents.kt`: below Q, open `buildRootUri(…, "primary")` with `Root.MIME_TYPE_ITEM`. It lands on the storage root, without crashing.
- Verified on 2026-10-16 with `am start` and the in-app button on the `Pixel_2` AVD (API 27). API 28–35 are untested; no images are installed for them.

**Thumbnail (pre-existing; FIXED 2026-10-16 in commit 188aec49 "Shared: Fix blank video thumbnails below Android 10"):**
- On API < 29, `data/coil/VideoThumbnailFetcher.loadLegacy` upgrades a small MINI thumbnail to `FULL_SCREEN_KIND`.
- Video does not support that kind: `IllegalArgumentException: Unsupported kind: 2`. Coil then fails and the thumbnail is blank.
- Reproduced with a Coil probe on API 27: MINI was 512x288, so the upgrade path ran.
- Fix: fall back to a `MediaMetadataRetriever` frame, and keep the small MINI if that fails too.
- Regression test: `androidTest/.../data/coil/VideoThumbnailFetcherTest` (API ≤ 28 only, fixture `assets/video_320x240.mp4`). Its `@Before` must poll until the public dir is writable: on API 27 a runtime `pm grant` remounts storage asynchronously, and the first write otherwise fails with EACCES.

**API 27 AVD traps:**
- DocumentsUI hides internal storage until "More options → Show internal storage" is turned on.
- The Tools search field takes focus, and Gboard swipe-typing turns `input swipe` into text such as "by by".
- `input text` with no IME drops letters ("Compress" → "Cmrss").
- `keyevent 111` leaves the app.
- What worked: `ime disable` both IMEs, then swipe; re-enable them afterwards.

**Why:** Open folder had only been tested on Android 10+. API 24–28 devices would have shown "Files has stopped".
