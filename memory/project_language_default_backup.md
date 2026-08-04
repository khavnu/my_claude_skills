---
name: project-language-default-backup
description: "Bug \"Settings language không default về ngôn ngữ hệ thống trên fresh install\" — root cause là Auto Backup, quyết định KHÔNG fix"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1df9c8ca-4ee5-431a-b501-8b70d3550106
---

Bug QA report (Pixel 4XL, Android 13, device để ngôn ngữ non-English): cài app từ Play Store → Settings → language KHÔNG default về ngôn ngữ hệ thống (expected: System).

**Root cause (đã verify code):** Android Auto Backup restore Proto DataStore `app_preferences.pb`. Màn Settings/SelectLanguage đọc "ngôn ngữ đang chọn" từ field `language_key` (default `""` = follow system; `SelectLanguageViewModel.kt:50`, `SettingsScreen.kt:147`). Chỗ DUY NHẤT ghi `language_key` là user chủ động chọn (`SelectLanguageViewModel.applyLanguage()`), không có code ghi lúc startup. Vậy fresh install mà ra non-empty = file `files/datastore/app_preferences.pb` bị restore từ lần cài trước (đã chọn English).

**Vì sao chỉ bản Play Store dính:** debug build cùng `applicationId` nhưng khác signing key → Backup Manager không restore (restore gate theo signature). Chỉ release-signed + account từng cài mới bị. → "lúc có lúc không" do backup cũ còn/mất trên cloud.

**Backup rules hiện tại đều trống** (`res/xml/backup_rules.xml`, `data_extraction_rules.xml`) → default backup toàn bộ internal storage kể cả datastore.

**Quyết định (2026-07-30): KHÔNG fix.** Đây là hành vi đúng thiết kế của Auto Backup, chỉ lệch kỳ vọng QA.

**Cách verify / test cho QA (không phải fix ship được):**
- `adb shell settings put secure backup_auto_restore 0` rồi gỡ/cài lại → chặn restore-on-install.
- `adb shell bmgr wipe com.google.android.gms/.backup.BackupTransportService com.tmedilab.sounditor.music.audio.editor` → xóa backup cũ của package.

**Nếu sau này muốn fix:** tách `language_key` ra DataStore file riêng (vd `language_preference.pb`) + exclude riêng file đó trong 2 rule XML (`<exclude domain="file" path="datastore/..."/>`) để giữ backup presets; HOẶC exclude thẳng `app_preferences.pb` (đơn giản, mất backup toàn bộ settings). Lưu ý thêm: Android 13+ còn backup per-app locale ở tầng framework (`AppCompatDelegate.setApplicationLocales`) độc lập với DataStore — cần verify tránh lệch "UI English nhưng Settings = System".
