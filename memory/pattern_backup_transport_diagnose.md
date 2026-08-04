---
name: pattern_backup_transport_diagnose
description: "Chẩn đoán \"No data backed up\" / \"Back up now\" không hoạt động — Google transport throttle full-data backup, dùng LocalTransport để test"
metadata: 
  node_type: memory
  type: project
  originSessionId: 18c0fac6-3e8b-43ca-803c-d804a7f390d7
---

Khi test Auto Backup trên máy thật mà bấm **"Back up now" / `bmgr backupnow`** báo **"No data backed up"** hoặc log `Transport rejected package because it wasn't able to process it at the time`:

**Đây KHÔNG phải lỗi app / config / account.** Google cloud transport (`GmsBackupTransport`) **cố ý throttle full-data backup ~1 lần/24h/app** và **không cho ép on-demand**. Reject tức thì (~70ms, chưa upload byte nào). `@pm@ Success` chỉ là key-value metadata của package manager, không phải data app.

**Cách phân biệt nguyên nhân:**
- Reject **tức thì** (chưa upload) → throttle, KHÔNG phải quota. (Quota sẽ upload rồi mới fail.)
- Đổi account mới vẫn reject → loại bỏ quota. (Account cũ full 15GB dùng chung Gmail/Photos/device-backups, ẩn khỏi Drive UI — xem `one.google.com/storage`.)

**Cách test backup/restore ĐÁNG TIN — dùng LocalTransport (không throttle, chạy ngay):**
```bash
ADB=/home/khapv/Android/Sdk/platform-tools/adb   # adb không trong PATH
# 1. Pull APK đang cài (nhớ cả split APKs: base + arm64_v8a + xxxhdpi) để install lại
$ADB shell pm path <pkg>
# 2. Chuyển transport → local
$ADB shell bmgr transport com.android.localtransport/.LocalTransport
# 3. Backup (thấy progress bytes = data thật đang đẩy → Success)
$ADB shell bmgr backupnow <pkg>
# 4. uninstall + install-multiple lại
$ADB uninstall <pkg>; $ADB install-multiple base.apk split_arm64.apk split_xxxhdpi.apk
# 5. Restore KHÔNG tự chạy khi adb install → ép thủ công:
$ADB shell bmgr list sets                 # lấy token (thường = 1)
$ADB shell bmgr restore <token> <pkg>     # cú pháp mới bắt buộc token; restoreFinished: 0 = OK
# 6. TRẢ transport về Google (bắt buộc, tránh ảnh hưởng backup thật của máy)
$ADB shell bmgr transport com.google.android.gms/.backup.BackupTransportService
```

**Verify quota account:** `one.google.com/storage/management` → mục Backups.

Đây là lý do gốc của [[project_language_default_backup]] (Auto Backup restore `app_preferences.pb` giữa 2 máy chung account). Muốn tắt backup thật: `android:allowBackup="false"` (KHÔNG phải bỏ dòng — default vẫn `true`) + **giữ** `android:localeConfig` (đừng xóa nhầm như commit ticket #233 trên branch `improve/disable_backups`).
