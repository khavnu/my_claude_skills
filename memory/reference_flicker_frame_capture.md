---
name: flicker-frame-capture
description: "Prove a one-frame UI flash on a device: adb screenrecord around the action, ffmpeg crop+fps to frames, PIL mean/stddev per frame; baseline by git stash + install."
metadata:
  type: reference
---

Used for ticket 2105 (2026-11-10, Vivo V2201), where a screenshot can't catch a ~70 ms flash:
1. `( adb shell screenrecord --time-limit 6 /sdcard/rn.mp4 & ); sleep 1.5; adb shell input tap <Save>; sleep 6; adb pull /sdcard/rn.mp4`
2. `ffmpeg -v error -i rn.mp4 -vf "fps=15,crop=W:H:X:Y" f/%03d.png` (crop = the view's bounds from uiautomator; recording is at physical px).
3. Per frame `ImageStat.Stat(img.convert("L"))` mean/stddev: the odd frame out is the flash; paste neighbours into a strip PNG to look at it.
4. Baseline: `git stash push -- <files>`, installDebug, `git stash pop`, repeat 1-3.

**Why:** gives a before/after that QC and the user can see, instead of "looked fine to me".
