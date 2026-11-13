---
name: pattern-ffmpeg-wrapper-hardware-encoder
description: ffmpeg-wrapper hardware (h264_mediacodec) history — 1.0.35 -38, (4)/(5) IDR loss / no video, (6) OK on Huawei but magenta on c2.android and HANG on API 27 sync mode
metadata:
  type: project
---

Measured 2026-10-20 on a Pixel 9 with a temporary androidTest probe (since deleted). The app stayed in the foreground through `ActivityScenario`, so the timings are not skewed by the background cpuset (see [[pattern-background-cpuset-not-throttle]]).

**`hardware = true` does not work in 1.0.35.**
- It maps to `-c:v h264_mediacodec -b:v`, and fails within about 40 ms with code `-38` (ENOSYS).
- The encoder is compiled in: `strings libavcodec.so` shows `--enable-jni --enable-mediacodec`.
- But `nm -D --undefined-only libffmpeg_jni.so` lists no `av_jni_set_java_vm`. FFmpeg's MediaCodec code has no JavaVM, so it returns ENOSYS.
- Lib-side fix: call `av_jni_set_java_vm(vm, NULL)` in `JNI_OnLoad`.

**Software presets, scaled to 720p at a 1.2 Mbps target:**

| Clip | Preset | Time | SSIM |
|---|---|---|---|
| 30 s 720p | ultrafast | 3.1 s | 0.952 |
| 30 s 720p | veryfast (current) | 7.9 s | 0.977 |
| 10 min 1080p | ultrafast | 307 s | 0.919 |
| 10 min 1080p | veryfast | 440 s | 0.939 |

- SSIM on the 10-minute clip is over its first 120 s.
- Output sizes on the 10-minute clip were 103 MB (ultrafast) and 99.6 MB (veryfast).
- On long 1080p sources, decode + scale dominate: ultrafast only saves about 30%.

**How to apply:** re-run this probe when the lib ships a fix. Only app-owned videos are readable without READ_MEDIA_VIDEO (see [[pattern-ffmpeg-wrapper-replace-audio]]).

**Update 2026-10-20, new wrapper (imports `av_jni_set_java_vm`):** `hardware = true` now works and uses `c2.exynos.h264.encoder`, but it is SLOWER. Run back to back, on the 10 min 1080p source → 720p at 1.2 Mbps:

| Encoder | Time | SSIM | Size |
|---|---|---|---|
| hw | 477 s | 0.965 | 100.2 MB |
| sw veryfast | 284 s | 0.939 | 99.6 MB |

- On the 30 s clip: hw 7.6 s vs sw 7.5 s.
- The earlier 440 s veryfast run was the old lib / a warmer phone, so compare only back-to-back runs.
- A force-stop from Android Studio (`Killing … due to from pid`) killed one long run; ask the user not to Run the app during probes.

**Update 2026-10-29, lib "(4)" — and "(5)" (same native .so, only Kotlin fallback + "grew the file" guard) (no libx264 — dropped for GPL, so hardware is the only path):** hardware=true on Huawei Y5 2019 (AMN-LX3, MediaTek; mislabelled "nova 3i" before 2026-10-29) loses the first IDR (packet 0 = SPS/PPS + P slice; first keyframe at ~8 s; 885 packets → 646 decodable frames); on the Android 16 emulator it writes NO video stream yet returns 0. Sizes round to x16 (364x360 → 352x352). Check any HW output with `ffprobe -count_frames -show_entries stream=nb_read_frames` vs packets and the first keyframe pts. Report + files: /home/khapv/Tmp/claude/andorid_music_editor/video-compress/hw-encoder-bugs/

**Update 2026-10-29, lib "(6)" (libffmpeg_jni.so rebuilt, logs `video: encoded N packets`):** Huawei nova 3i (INE-LX2r, Kirin 710): keyframe at 0 s every 2 s, 885/885 frames, colour correct, still 352x352, tag `unknown`. Android 16 emulator (c2.android.avc.encoder): video now present, keyframes OK, but the WHOLE picture is magenta (pixel layout mismatch, encoder `color-format=19` I420). Y5 2019 (MTK OMX encoder) re-tested: IDR loss FIXED (keyframe 0 s, 885/885, colour correct). Pixel_2 AVD Android 8.1 (OMX.google.h264.encoder): HANGS forever — API 27 has no AMediaCodec async callback, wrapper falls back to sync mode and loops on dequeueOutputBuffer with zero output (file stays 48 B; no exit even when OMX dies); only `FFmpeg.cancel()` frees it (~12 s). So any API < 28 device may hang → app needs a timeout/fallback there. Pixel 9 real (Android 17, c2.exynos.h264.encoder, same color-format=19 I420 input as the magenta emulator): OK — magenta is c2.android-only. To test a new aar on the Pixel 9 without touching the user's release build (different signature): git worktree in scratchpad + `debug { applicationIdSuffix = ".lib6" }` + a duplicated `.lib6` client in google-services.json (processDebugGoogleServices rejects unknown packages). Check `vcodec=` in the log to confirm which aar actually ran — the user may switch branches mid-test. Evidence: hw-encoder-bugs/lib6_*.

Driving Pixel_2 AVD (API 27): the Tools search field takes focus on start, so `input swipe` gets eaten as keyboard gesture typing — type `Compress` in the search instead; the picker is old DocumentsUI → overflow "Show internal storage" → "Android SDK built for x86" → Movies. Get a thread dump on a user build without root: `run-as <pkg> kill -3` writes /data/anr (unreadable), so use `adb bugreport` and grep `----- pid <pid>`.

**Pixel 9 real, lib (6), 2026-10-30 (VFR + 4K):** VFR screen recording comes out CFR at the rounded average fps (23.35→23; bursts resampled, statics duplicated, duration kept, content in time). 23.976 → 24 fps, resampled not retimed (frame matching by SSIM: out 639 ≈ src 638) so no A/V drift. 4K sources lose the last 1–2 frames (drain at EOS); 1080 becomes 1072 by a native `crop=trunc(iw/16)*16` (rows cut, not scaled). Other video tools (Remove audio, Add audio replace/mix, Video to Audio) unaffected by (6): they use `-c:v copy`/`-c:a copy`, verified by bitstream md5 on Pixel 9; the only build diff is gpl+libx264. Light caps the short side at 1080 (`VideoCompressOption.kt` `outputShortSidesPx`), so "4K kept at source size → encoder refuses" can't happen from the level cards. How to check timing: dump `frame=pts_time` of src/out, then SSIM the out frame N against src N-2..N+2.
