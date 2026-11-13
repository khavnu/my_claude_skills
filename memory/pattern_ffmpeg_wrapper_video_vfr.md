---
name: pattern-ffmpeg-wrapper-video-vfr
description: "ffmpeg-wrapper 1.0.35 (FFmpeg 8.0.1) VideoCompressor drops frames on VFR input; native execute ignores -fps_mode/-r/-enc_time_base, so the app cannot work around it"
metadata:
  node_type: memory
  type: project
  originSessionId: f8af6503-0c14-4b8d-b9c4-880554cd647d
  modified: 2026-10-28T09:10:46.923Z
---

ffmpeg-wrapper 1.0.35 (`app/libs/ffmpeg-wrapper.aar`, `FFmpeg.version` = 8.0.1), checked 2026-10-15.

**VFR bug:** with an Android screen recording as input (VFR, tbr 90k, 124 frames / 5.31s), `VideoCompressor.compress` outputs 29 frames / 3.60s, on the Pixel 9 and on the x86_64 emulator alike. Desktop ffmpeg 6.1.1 with the same args keeps 124 frames / 5.31s. The native log shows `non-strictly-monotonic PTS` and `non monotonically increasing dts to muxer … dropped`. CFR test videos compress correctly (1080p→720p, portrait →720x1280, 480p kept).

**Not workable from the app:** `FFmpeg.execute` with extra `-fps_mode passthrough|vfr|cfr -r 30` or `-enc_time_base demux` gave byte-identical output, so the native execute is not full fftools and ignores those flags. It has to be fixed in the lib.

**Why:** found while integrating real Compress video. Camera recordings in low light are often VFR too, so the impact may be wider than screen recordings.

**How to apply:** before investigating "compressed video is shorter/choppy", check whether the source is VFR (`ffprobe -show_entries stream=r_frame_rate,nb_frames`). The bug report + repro probe + files are in `/home/khapv/Tmp/claude/andorid_music_editor/video-compress/vfr-native-bug/`. Wrapper API notes (verified with javap + device logs 2026-10-15):
- `compress` only takes a target HEIGHT (`scale=-2:H`), so portrait sources need `VideoResolution.scaledHeightFor`.
- `FFmpeg.execute` already does `withContext(Dispatchers.IO)`, but it calls blocking `nativeExecute` with NO cancellation hook. A cancelled coroutine keeps encoding unless `FFmpeg.cancel()` (a process-wide flag) is called. `FfmpegVideoProcessorDataSource` forwards cancellation with a watcher; on device, Stop → native `CANCELLED` in ~0.2s.
- Corrected 2026-10-15: an earlier version of this note said "every command must go through FfmpegCommandGate". That shared gate was dropped at the user's request; video is kept independent of the audio data source, and audio still has its own per-instance mutex.
- Speed on Pixel 9: a 9:56 1080p clip at Normal (CRF 28, veryfast, scaled to 720p) took 377s, and 691 MB became 89 MB.
- Updated 2026-10-16: the app now encodes to a target size rather than CRF. With `videoBitrate > 0`, `compress` builds `-c:v libx264 -preset P -b:v N` without `-crf` (checked with `javap -c` on `VideoCompressor.class`). The bitrate comes from `videoBitrateForTargetSize` (`FfmpegVideoProcessorDataSource.kt`), and the minimum is 150 kbps.
- Measured size vs. target on a Pixel 9 (single-pass ABR):
  - 0.96–1.06 on 4K m2ts, 720p m2ts and 720p flv;
  - 1.14 when the minimum bitrate kicks in;
  - about 0.75 on an mkv with subtitles and font attachments, because those streams are dropped from the output.
- In the app, a 720p flv at Normal was estimated at 1.7 MB and came out at 1.7 MB.
- Updated 2026-10-16: there is now a quality floor per output short side: 360p → 400k, 480p → 600k, 720p → 1200k, 1080p → 2000k video. It lives in `planVideoCompress` (`domain/model/VideoCompressOption.kt`).
  - How it was measured: 4 ten-second sources × 4 resolutions × 4 bitrates, encoded on the Pixel 9 with `VideoCompressor` and scored with host ffmpeg `ssim`.
  - Phone footage stays at SSIM ≥ 0.97 at these floors. 360p at 150k was visibly blocky (0.92).
  - Motion graphics with fine dots is the worst case (0.94 at 360p/400k).
  - Comparison sheets are in `/home/khapv/Tmp/claude/andorid_music_editor/video-compress/disabled/`.
- Unsupported codecs, measured on a Pixel 9 on 2026-10-16:
  - `removeAudio` (stream copy into mp4) returns `-22` (AVERROR(EINVAL)) for WMV2, VP8 and FLV1.
  - `compress` returns `-22` for WMV2 and `-1128613112` (AVERROR_DECODER_NOT_FOUND) for FLV1. VP8 compresses fine.
  - Both codes fail within a few ms, before any frame. The app maps them to `AudioOperationError.UnsupportedVideoCodec` (`videoErrorFor` in `FfmpegVideoProcessorDataSource.kt`), which reaches the screen through the work-data code `ENCODE_ERROR_UNSUPPORTED_CODEC` (`data/operation/VideoWorkErrors.kt`) and shows the "cannot be processed" sheet.
  - The wrapper has no video-codec probe (only `getAudioInfo`/`probeAudio`), so this can't be checked when the video is opened.
- Updated 2026-10-28 (#478/#479): desktop ffmpeg 6.1.1 with the lib's args (`-c:v libx264 -preset veryfast -b:v N -c:a aac -b:a 128k`) gives the same SIZE as the lib (2,888,568 vs 2,887,450 B on QC's Video.mov), so size experiments can run on the host (colour range differs, see [[pattern-ffmpeg-wrapper-color-range]]). Output/target measured: 1.01–1.04 for clips of 60 s or more, 1.071 at 30 s, 0.91–0.93 for some 10 s clips. `planVideoCompress` now shows `encodeTargetBytes × 1.04` and judges availability on it; a silent source budgets 0 audio (commit 861dd1bd).
