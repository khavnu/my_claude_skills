---
name: wmusi-media-notification-bal
description: Media3 custom notification buttons can't open an activity on Android 13+ (BAL blocked); how WMusi handles it
metadata:
  type: reference
---
Verified 2026-10-05 on emulator-5554 (API 36): a session custom action tapped in the SystemUI media
controls reaches `onCustomCommand` in the service; `startActivity` there logs "Background activity
launch blocked! ... BAL_BLOCK" (check: `adb logcat -d | grep "Background activity"`). So the Sing
button is hidden on API 33+ (`NotificationButtonsState.canOpenAppFromButton`); below 13
`WMusiNotificationProvider` gives it a direct activity PendingIntent. The session activity
(card tap) works fine. Media3 1.11 sources: download `media3-session-1.11.1-sources.jar` from
dl.google.com/android/maven2 (it isn't in the gradle cache).
