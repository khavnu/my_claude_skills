---
name: pattern-open-folder-drive-quickview
description: "#462: Open folder → tap video không phát trên Pixel là lỗi DocumentsUI giao QUICK_VIEW cho Drive Projector, Drive thêm ?cpn= vào URI nên mất grant; app không sửa được bằng intent mở thư mục"
metadata:
  type: project
---

Verified 2026-10-30 trên Pixel 9 (Android 17, DocumentsUI 17, Drive 2.26.427.3), tái hiện bằng `adb am start` thuần — không qua app:

- DocumentsUI (`com.google.android.documentsui`) chạm file video → gửi `ACTION_QUICK_VIEW` cho `com.google.android.apps.docs/com.google.android.apps.viewer.ProjectorActivity` (handler QUICK_VIEW duy nhất trên Pixel).
- Drive Projector tự gắn `?cpn=...` vào URI `content://com.android.externalstorage.documents/document/...` → URI khác URI được grant → `SecurityException: Permission Denial ... requires that you obtain access using ACTION_OPEN_DOCUMENT` → ExoPlayer "Source error" → màn đen 0:00/0:00 "Sự cố với tệp".
- "Qua Files phát được" vì QC dùng **Files by Google** (`com.google.android.apps.nbu.files`), có PreviewActivity riêng.
- Realme C55 có nhiều handler nên hiện chooser → không vướng Drive.

Intent đã thử (`cmd package query-activities`):
- `VIEW` + `vnd.android.document/directory`: chỉ DocumentsUI nhận.
- `VIEW` + `vnd.android.document/root`: Files by Google (`.gateway.browse.BrowseGatewayHandler`) + DocumentsUI. Files by Google chỉ nhận root URI (`/root/primary` → mở bộ nhớ trong); truyền URI thư mục thì nó đóng im lặng.
- `OPEN_DOCUMENT` + `EXTRA_INITIAL_URI` = thư mục lưu: mở thẳng đúng thư mục (picker mode), file chọn trả về app.

Liên quan: [[pattern-open-folder-intent-by-api]].

**Hướng B đã làm (2026-10-30, chưa commit lúc ghi):** `VideoSaveSuccessScreen.openFolderOrToast2` + `buildPickVideoInFolderIntent` (VideoShareIntents.kt) — register thẳng trên `activityResultRegistry` (hàm Context không nhận result được), picked URI → `buildVideoOpenIntent`. Verify Pixel 9 bản debug: picker mở đúng VideoCompress → chọn → chooser (Files by Google / Photos) → Photos phát, không Permission Denial. Bẫy test: Back trong picker = lên thư mục cha, phải Back 2-3 lần mới về app. Pixel 9 lúc 13:29 bị cài bản ký khác → release không cài đè được, dùng debug.
