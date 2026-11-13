---
name: reference-device-rotation-testing
description: "Driving the real Pixel 9 for landscape checks — adb path, forcing rotation on Android 17, forcing permanently-denied permission, testing orientation branches in Compose tests"
metadata:
  node_type: memory
  type: reference
  originSessionId: 87fb5981-5bf1-470a-9072-56ede1d33a2e
  modified: 2026-10-13T04:41:29.903Z
---

Verified 2026-10-13 on Pixel 9 (Android 17, serial 47231FEAQ001B9) while building landscape for the permission screen.

- `adb` is NOT on PATH: use `export PATH=$PATH:$HOME/Android/Sdk/platform-tools` (sdk.dir in `local.properties`). A silent `adb devices 2>/dev/null` looks like "no device" — it's actually "command not found".
- Force rotation: `adb shell cmd window user-rotation lock 1` (landscape) / `lock 0` (portrait); restore with `adb shell cmd window user-rotation free`. `settings put system user_rotation` gets reset on Android 17 — don't use it.
- (2026-10-13) The display only rotates while an app that allows landscape is in front. The Pixel launcher is portrait-only, so `lock 1` while it's in front keeps `mRotation=0`. Launch the app FIRST, then lock, and wait until `dumpsys window displays | grep -oE "mRotation=[0-9]"` prints `mRotation=1` before taking the screencap.
- `connectedDebugAndroidTest` uninstalls the app when it finishes, which drops the audio permission. Run `pm grant <pkg> android.permission.READ_MEDIA_AUDIO` again before checking on the device.
- Verify rotation took: `adb shell dumpsys window | grep mRotation=` → `ROTATION_90`; app no longer locked → `mCurrentAppOrientation=SCREEN_ORIENTATION_UNSPECIFIED`.
- Permanently-denied audio permission (to show "How to allow access?"): `adb shell pm set-permission-flags <pkg> android.permission.READ_MEDIA_AUDIO user-fixed`, then tap Grant once. Undo with `clear-permission-flags`.
- (2026-10-13) Since the portrait lock was removed, androidTest activities follow the sensor. With the phone lying on its side and auto-rotate on, the test window was 2424×1080, so the LazyColumn never composed the lower items and correct code still failed its tests. Fix: put `ui/util/PortraitRotationRule` (androidTest, `uiAutomation.setRotation(ROTATION_FREEZE_0)`) at `@get:Rule(order = 0)`, before the compose rule. Debug by calling `composeRule.onRoot().printToLog("TAG")` and reading the root bounds from logcat.
- In Compose UI tests, test the landscape branch without rotating: provide `LocalConfiguration` with `orientation = ORIENTATION_LANDSCAPE` via `CompositionLocalProvider`. Note: content inside a `Dialog` gets its own real LocalConfiguration — read orientation outside the dialog.
- androidTest names here are camelCase_underscore, not backtick-with-spaces (minSdk 23 DEX).

Feature-specific pitfalls (SidePanel tap fall-through, zero-width Spacer in tests, rememberSaveable on rotation) live in the plan: `docs/superpowers/plans/2026-10-13-landscape-implementation.md` → "Kết quả thực hiện Task 1, 2, 4".

**Chia đôi màn hình trên Pixel 9 (Android 17, 2026-10-28):** máy đặt nằm + xoay tự động bật → vào split là xoay 90° (thành chia trái/phải). `settings put system accelerometer_rotation 0` KHÔNG giữ được (`cmd window user-rotation` vẫn báo `free`); phải `cmd window user-rotation lock 0` SAU KHI đã vào split, mỗi lần dựng split lại. Trả lại: `cmd window user-rotation free` + `settings put system accelerometer_rotation 1`.

**Giả lập tablet (2026-10-28, #482/#483):** AVD `Pixel_Tablet` chỉ còn ~400MB trên /data → `INSTALL_FAILED_INSUFFICIENT_STORAGE` với APK 80MB (`pm trim-caches` không giúp; trong đó có 186MB nhạc test + app project khác, đừng tự xoá). Cách nhanh: trên AVD Pixel 9 chạy `adb shell wm size 2560x1600 && adb shell wm density 320` (đúng Pixel Tablet, smallestScreenWidthDp 800 → `rememberIsTablet()` true), chụp xong `wm size reset && wm density reset` TRƯỚC khi chạy connected test.
