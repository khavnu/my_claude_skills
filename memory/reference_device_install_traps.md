---
name: reference_device_install_traps
description: Cài APK lên AVD Pixel_Tablet (đầy /data) và Pixel 9 thật (đang chạy bản ký release) — cách cài không phải gỡ app
metadata:
  node_type: memory
  type: reference
  originSessionId: 91545e97-7bcf-4812-8776-aaf369eaf48e
  modified: 2026-10-30T02:21:21.010Z
---

Verified 2026-10-30 (ticket #482):

- **AVD `Pixel_Tablet` đầy `/data`: thủ phạm là Play Store tự update ~25 app hệ thống vào `/data/app`** (Maps, YouTube, Chrome, GSA, Photos…), không phải file test (`/sdcard` chỉ ~190MB).
  Dọn 2026-10-30: `cmd package uninstall-system-updates <pkg>` cho 20 app không dùng khi test (giữ gms, vending, webview, inputmethod.latin) → 96% → 54%, trống 2.6GB.
  Play sẽ update lại theo thời gian — đầy lại thì lặp lại lệnh này (liệt kê: `pm list packages -f -s | grep /data/app`).
- Mẹo tạm khi còn đầy (`~/Android/Sdk/emulator/emulator -avd Pixel_Tablet`): `/data` còn ~350MB → `install` báo
  "Requested internal only, but not enough space" (ngưỡng low-storage, không phải hết chỗ thật). `pm trim-caches` không giúp.
  Cách: `settings put global sys_storage_threshold_percentage 1` + `sys_storage_threshold_max_bytes 50000000` → install →
  `settings delete global` cả 2 key (mặc định là null).
- **Xoay Pixel_Tablet sang portrait**: hướng tự nhiên là landscape; phải `settings put system accelerometer_rotation 0` +
  `user_rotation 1` + `cmd window user-rotation lock 1`, kiểm bằng `dumpsys window displays | grep cur=` ra `1600x2560`.
- **Pixel 9 thật (47231FEAQ001B9)**: app đang là bản ký release → debug báo `INSTALL_FAILED_UPDATE_INCOMPATIBLE`.
  `assembleRelease` (không có keystore.properties thì ký bằng `musiceditor.jks` test dùng chung) cài đè `-r` được, giữ data.
  Kiểm tra cài thật chưa bằng `dumpsys package <pkg> | grep lastUpdateTime` — `install ... | tail -1` có thể nuốt mất lỗi.

Liên quan: [[reference_device_rotation_testing]], [[feedback_connected_test_multi_device]].

- **Xoay Pixel 9 thật (2026-10-30)**: `cmd window user-rotation lock 1` KHÔNG ăn (vẫn `cur=1080x2424`); phải `cmd window user-rotation -d 0 lock 1`. Trả lại: `-d 0 free` + `user_rotation 0` + `accelerometer_rotation 1`.
