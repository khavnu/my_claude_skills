---
name: wmusi-adb-shell-loop-pitfalls
description: "adb shell quoting loss across multiple argv + while-read loops dying after 1 iteration when adb eats the loop's stdin"
metadata:
  node_type: memory
  type: reference
  originSessionId: 6d9d149d-71c2-4e42-bad0-a58e67974707
  modified: 2026-10-08T06:57:22.385Z
---

Verified 2026-10-08 on emulator-5558 (Pixel_2, API 27) while seeding `/sdcard/Music/` for QA:

- `adb shell cmd arg1 arg2 "quoted value"` passed as **separate local bash argv** gets rejoined
  by adb into one remote command-line string, and that rejoin drops a layer of quoting — single
  quotes meant for the remote shell vanish (content provider `--where "col='val'"` arrived as
  `col=val`, SQL error), and literal parens in a filename cause a remote `syntax error: unexpected '('`.
  Fix: build the entire remote command as **one local string** (e.g. `adb shell "am broadcast ... -d 'file:///sdcard/Music/$f'"`)
  so adb has only one argv to forward verbatim.
- `while IFS= read -r f; do adb shell ...; done < filelist.txt` silently stops after the **first**
  line — `adb shell` reads from stdin by default, and since the loop's stdin is the same fd `read`
  is consuming from, the first `adb shell` call drains the rest of the file. Fix: redirect the adb
  call's stdin away (`adb shell ... </dev/null`) or read the list on a dedicated fd
  (`done 3< filelist.txt` + `read -r f <&3`).
- `ACTION_MEDIA_SCANNER_SCAN_FILE` broadcasts still work on API 27 (unlike `content call --method
  scan_volume`, API 30+ only) — one broadcast per file, confirmed via `MediaScannerReceiver` logcat
  lines; 39/40 pushed files indexed after fixing the two bugs above.
- The Pixel_2 (API 27, 2 GB RAM) AVD crashed (qemu process died, state lost) under combined load of
  5 concurrent devices (3 emulators + 2 physical). Relaunch: `emulator -avd Pixel_2 -port 5558
  -no-snapshot-save -no-boot-anim` (boots from the `default_boot` snapshot in a few seconds, but any
  app/data installed since that snapshot is gone — reinstall + reseed).

Related: [[wmusi-mediastore-pitfalls]] (API 36 version of pending-file/scan gotchas).
