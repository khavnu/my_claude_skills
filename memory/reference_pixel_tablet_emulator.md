---
name: pixel-tablet-emulator
description: "Pixel_Tablet AVD for landscape/tablet checks: needs 8GB RAM (else Lite mode), /data nearly full (uninstall app before install), wm size/density to emulate a Galaxy Fold inner screen."
metadata:
  type: reference
---

Verified 2026-11-10 (ticket 2103):
- Start with `-memory 6144`+ (the user runs it with 8GB): with default RAM the app goes Lite mode and hides the detail cover and its toggle (same as [[reference_emulator_screenshot_capture]] for Pixel_9).
- `/data` has only ~460MB free (other projects' apps are installed there, leave them): `installDebug` over an existing install fails `INSTALL_FAILED_INSUFFICIENT_STORAGE`; `adb uninstall com.amapps.media.music` first. `connectedDebugAndroidTest` also uninstalls the app (data lost).
- Galaxy Z Fold inner screen: `adb shell wm size 2176x1812 && adb shell wm density 431` → `sw673dp w808dp h673dp` (check with `dumpsys activity activities | grep -m1 -oE "sw[0-9]+dp w[0-9]+dp h[0-9]+dp"`); always `wm size reset` + `wm density reset` after.
- Real size: 2560x1600 @320 → 1280x800dp landscape, sw800.
- (2026-11-12) `config.ini` already says `disk.dataPartition.size=20G` but `/data` is 5.8G: the emulator only applies the size when it creates userdata (`-wipe-data`, loses everything), and the image is `user` (no root, no online resize). Freed space instead: removed `/data/local/tmp/music_editor_*.apk`, the two `com.tmedilab.*.test` packages and `com.tmedilab.sounditor.music.audio.editor` (user allowed uninstalling apps); `drink.water2` kept. `pm trim-caches` frees nothing here. An install that fails prints only on the last line: check `pm list packages | grep amapps`, not the exit code.

