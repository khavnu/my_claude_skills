---
name: widget-upgrade-device-test
description: How to run an app-update test with home-screen widgets on the Pixel 9 (pin via in-app chooser, adb helper, old 2.91/2.88 APKs); widget default-background bug root cause (fixed ce0e7d995).
metadata:
  type: reference
---

Verified 2026-10-22 (widget config Compose port):
- Old builds: 2.88.08 `upgrade/old-2.88.08-litetest-release.apk` (origin/release/2.88, flavor litetestRelease: release key, test ads; `pro` is another package, `lite` has real ads). Old production build: `/home/khapv/Tmp/claude/green_ba_music_player/upgrade/old-2.91-release.apk` (commit be0145f1c, release key, vc 91). New release: `./gradlew :app:assembleRelease` (keystore in repo) then `adb install -r` — same vc 91 is accepted by adb.
- adb helper `/home/khapv/Tmp/claude/green_ba_music_player/tools/dev.py` (tapid / taptext / ids / shot / top via uiautomator resource-ids) and `homeshots.sh <prefix>` (4 home pages + side-by-side image). Run under `flock /tmp/wmusi-pixel9.lock` ([[project-device-test-quirks-pixel9]]).
- Placing widgets without dragging: app drawer → "Tiện ích" → tap a widget → launcher dialog "Thêm vào màn hình chính" → our config Activity opens (started by `PinWidgetBroadcastReceiver` with `startActivity`, so Back does NOT remove a pinned widget; only the launcher-picker drag path uses the result).
- Widgets render content/background only with a current song: play one (mini player `iv_playing_play`), interstitial/app-open ads and the "Tránh nhạc bị dừng" sheet (`HỦY BỎ`) get in the way.
- (fixed 2026-10-22, commit ce0e7d995) Widgets showing the layout's default `android:src` after placing / confirming an unchanged config / an APK update: `RemoteViewsWidgetRenderer.full` ignored `WidgetFrame.background` while `WidgetUpdater.render` skipped the background partial because the frame had it (since 09b1fd288, in 2.91). Pinned by androidTest `RemoteViewsWidgetRendererTest` (applies the real RemoteViews). Lesson: `WidgetUpdaterTest` uses a fake renderer, so renderer-contract bugs only show in a test that applies the real RemoteViews; debug builds log every push (`adb logcat | grep 'WidgetUpdater: push'`).
