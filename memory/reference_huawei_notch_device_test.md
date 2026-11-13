---
name: reference-huawei-notch-device-test
description: "Huawei Nova 3i (INE-LX2r, API 28, notch) landscape device test — serial, dp size, flaky adb, rotation lock resets, helper commands."
metadata:
  node_type: memory
  type: reference
  originSessionId: 3eb82f20-c3e8-4cda-8e47-e6cee19550cd
  modified: 2026-11-03T07:34:41.688Z
---

Verified 2026-11-03 during the landscape side-panel audit.

- Serial `K3VDU19124000916`, Android 9 / API 28, 1080x2340 @480dpi → landscape window 780x360dp (shorter than Pixel 9's 411). Notch 90px (30dp) on the top edge (`dumpsys window displays | grep Cutout`).
- adb drops right after connecting (lsusb still shows 12d1:107e): user must set USB mode to File transfer (MTP) and re-enable USB debugging.
- Rotation: `settings put system accelerometer_rotation 0` + `user_rotation 1` (notch on the left) or `3` (notch on the right = the side panel's side). Launching the app resets `user_rotation` to 0 → re-apply after every `am start`.
- The navigation bar is on the right in landscape and is drawn over the side panel. Closing a panel used to leave it stuck (view flags 0x3712 but WM still 0x3710 = no traversal pushed them); fixed 2026-11-03 in `FullScreenActivity.hideNavigationBar` (requestLayout on API < 30 when the flags change). Check: `dumpsys window windows` → NavigationBar `isVisible=false` and the LoadingActivity window `mSystemUiVisibility=0x..12`. See [[reference-emulator-screenshot-capture]] for the general capture recipe.
- adb drops every few commands: push a script and run it ON the device (`adb shell "nohup sh /sdcard/x.sh >/dev/null 2>&1 &"`, it writes screencaps / dumpsys / `logcat -d -s TAG` to /sdcard and a DONE file), then poll and `adb pull`. Release builds can be installed over (`install -r`, keystore in the repo), but the user prefers debug builds (see [[feedback-debug-builds-on-devices]]). Temporary `android.util.Log` survives R8 (no -assumenosideeffects).
- The bug only showed on the first sheet after force-stop + launch + rotate; repeated open/close alternates stuck / fine (the next sheet's traversal pushes the old flags), so always test from a fresh launch.
- uiautomator bounds clip at x=2129 in landscape (nav bar area), so tap by screenshot coordinates (x1.17 from the 2000px preview), not by dumped bounds near the right edge.
- In-app language: Settings → Ngôn ngữ (a screen, not a sheet), tick then the ✓ at top-end (its a11y bounds read [0,0][0,0]).
