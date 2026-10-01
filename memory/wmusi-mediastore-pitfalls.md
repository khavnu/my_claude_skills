---
name: wmusi-mediastore-pitfalls
description: Verified MediaStore behaviors on API 36 emulator that broke Library tests (pending files, hidden files, dot renames, permission)
metadata:
  type: reference
---

Verified 2026-10-01 on emulator Pixel_9 API 36 (`adb shell content query --uri content://media/external/file --projection _display_name:is_pending:title:owner_package_name`):

- Files written straight into /sdcard by `adb push` or shell `cp` get a row with **is_pending=1**, title = file name, no tags. The shell (owner) sees the row, **every other app sees nothing**. So a shell query is NOT proof the app can see a file. Only a scan resolves it: `MediaScannerConnection.scanFile(ctx, arrayOf(<dir>))` from the app (API 30+: recursive for a directory) or `adb shell content call --uri content://media --method scan_volume --arg external_primary`.
- Files/dirs whose name starts with "." never reach the Audio table (only Files). Inserting DISPLAY_NAME ".x.mp3" via MediaStore is renamed to "_.x.mp3".
- Files inserted under `Ringtones/` get `is_ringtone=1` from MediaProvider itself.
- MediaStore deletes our inserted files but leaves their folders; clean `run_*` folders with shell `rm -rf`.
- A library test APK's own inserted files are visible without READ_MEDIA_AUDIO — tests that only read own files do not prove permission handling.

Fixture/test patterns: data/src/androidTest/.../MediaStoreFixture.kt, LibraryRepositoryDeviceTest.kt. See also [[wmusi-device-verify]].
- Deleting a MediaStore row that no longer exists throws `SecurityException: ... has no access to content://media/...` instead of returning 0. Check existence with a collection query (`_ID = ?`) first (MediaStoreFileDeleter.exists).
- `startIntentSender` for createDeleteRequest from a test/process with no activity silently shows nothing (background activity start). Launch it from an Activity (ConfirmationHostActivity in data androidTest) and click "Allow" with UiAutomator `By.text(Pattern.compile("(?i)allow"))`.
- Logcat cuts a line at ~4000 chars: log counts or the interesting subset, never a whole 5,000-row list.
- Perf fixture: `tools/library-fixture/generate.sh <count>` (5,000 ≈ 41 s, 20,000 ≈ 3 min, needs ~250 MB free on the emulator); measured by data `LibraryPerformanceTest` (`-e fixtureSize 20000`).
