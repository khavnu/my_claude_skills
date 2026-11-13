---
name: reference-emulator-screenshot-capture
description: "Capturing app screens on the Pixel_9 AVD — adb path, RAM ≥6GB or the app hides Theme/EQ (Lite mode), sheets/ads that interrupt navigation."
metadata:
  node_type: memory
  type: reference
  originSessionId: e0371a35-47d3-4e75-a5d0-74465e79f887
  modified: 2026-10-22T09:43:57.373Z
---

Verified 2026-10-22 while capturing the portrait baseline for landscape work ([[reference-figma-landscape-file]]).

- `adb` is not on PATH: `~/Android/Sdk/platform-tools/adb`. AVDs: `Pixel_9` (API 36, 411×923dp), `Pixel_Tablet`, `Pixel_9_2GB`, `Pixel_2`.
- Start with `emulator -avd Pixel_9 -memory 6144`. With `-memory 4096` the app is in **Lite mode** (`common/DeviceConfig.kt`: totalMem GB ≤ 3) → drawer hides "Change theme" and Equalizer. Check: `adb shell cat /proc/meminfo | head -1`.
- `adb shell dumpsys deviceidle whitelist +com.amapps.media.music` stops the "Avoid abnormally stopped music" sheet on every launch.
- Opening Player / Trim from a list shows an interstitial (test ad); the dismiss button has content-desc "Close". Back on Home opens ConfirmQuit with a native ad; tapping a banner opens Chrome.
- uiautomator text matching works for Vietnamese titles via a Python parser of `/sdcard/ui.xml` (grep missed them); tap by content-desc where possible.
- Screenshots go to `/home/khapv/Tmp/claude/green_ba_music_player/landscape/portrait_baseline/` (59 files).
- Portrait no-regression check = `scripts/portrait-guard/guard.py` (README there). Captures are only comparable in the SAME app data state: `connectedAndroidTest` uninstalls the app (EQ off, queue, "NEW" video badge reset) and a recipe like `video_home` flips the badge. To compare two builds, `install -r -d` the base APK (build it in a `git worktree` at the base commit), capture, install the new APK, capture, compare — verified 2026-10-22.
- Landscape on the emulator: `adb shell cmd window user-rotation lock 1` (`settings put system user_rotation` alone gets overridden). An interstitial / UMP consent activity forces portrait and the lock can come back portrait: re-run the lock before screenshots and check `dumpsys window displays | grep mRotation`.

- `adb shell monkey -p <pkg> 1` can inject a rotation event that turns `accelerometer_rotation` back to 1 → the emulator follows its (landscape) sensor and portrait captures come out 2424x1080. Launch with `am start -n com.amapps.media.music/.feature.loading.LoadingActivity` (guard.py fixed in acaf5e171, verified 2026-10-23: setting stayed 0, guard OK). Check: `adb shell settings get system accelerometer_rotation`.
- After `connectedAndroidTest` uninstalls the app, the next launch shows the media permission dialog and the UMP consent: `pm grant` READ_MEDIA_AUDIO/VIDEO/IMAGES + POST_NOTIFICATIONS, then tap "Consent" once (online) before running the guard.
- If the emulator window was rotated by hand, its accelerometer stays sideways (`adb emu sensor get acceleration` → `9.81:0:0`) and every newly started activity — the connectedAndroidTest ComponentActivity included — comes up at ROTATION_90 even with auto-rotate off: portrait compose tests then measure a 2424x1080 root and fail. Reset with `adb emu sensor set acceleration 0:9.81:0` (verified 2026-10-23).
- Widget config / editor portrait no-regression: build the base APK in a temp `git worktree`, `install -r -d` base → capture → new → capture, compare with PIL (status bar cropped); same app data both times.
- UMP consent dialog: the "Consent" button is a `content-desc`, not a `text` (grepping `text="Consent"` misses it and every later step fails silently). It comes back after any reinstall / `pm clear` while online.
- Empty-library states (no music): Folders → Hidden folders → Add folder → tick the 4 music folders (AudioTrim, Music, WMusiAutoLyrics, WMusiSamples) → ✓. Check with a Folders-tab dump that `AudioTrim` is gone before capturing. Undo with `adb shell pm clear com.amapps.media.music` (emulator only). Verified 2026-10-23.
- Adding test songs (e.g. one per letter for the A–Z bar): the scan drops short/small files (`MediaDataSource.isValidSong`: `fileSizeLimitInKb`, `durationLimitInSecond`), so 3 s mp3s never show. `ffmpeg -f lavfi -i "sine=frequency=440:duration=60" -c:a libmp3lame -b:a 128k -metadata title="Alpha Test Song" ...`, push to `/sdcard/Music/AZTest/`, `am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/Music/AZTest/<f>` per file, force-stop + relaunch → 357 → 383 songs (verified 2026-10-26). Remove with `adb shell rm -rf /sdcard/Music/AZTest`.
- (2026-11-11, ticket 2108) The Pixel_2 AVD (API 27, x86 32-bit) tops out at ~3.1 GB whatever `-memory` says → always Lite mode → no Equalizer anywhere (drawer, player menu). Use Pixel_9 (`-memory 6144`) for EQ / theme work. EQ path there: drawer → Equalizer → "Use the equalizer of the app" → turn on + OK → ⋮ (top right, tap ~1031,215) → Reverb.
- (2026-11-11, ticket 2113) Lyrics style sheet: the Lyrics tab's style button (`img_text_style_edit`) exists only when the song HAS lyrics. Without lyrics: Lyrics tab → "Enter lyrics" → `tv_adjust_style` opens the same `AdjustLyricTextStyleSheet`.
