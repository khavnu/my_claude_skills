---
name: pattern-ffmpeg-wrapper-replace-audio
description: ffmpeg-wrapper 1.0.35 replaceAudio/replaceAudioRegion behaviour measured on Pixel 9 — both cut the video to a short audio; which audio formats fail and with which code
metadata:
  type: project
---

These results were measured on 2026-10-19 on a Pixel 9, with a temporary androidTest probe calling `FfmpegVideoProcessorDataSource.replaceAudio`. The probe has since been deleted.

- **`replaceAudioRegion(0, videoDur)` does NOT pad with silence.** A 20 s AAC over a 180 s video gives a 20 s output. `replaceAudio` gives the same result. The earlier claim that "regions keep the full length via apad" came from reading bytecode and was never measured. It was wrong, and the comment in `FfmpegVideoProcessorDataSource.replaceAudio` still says it.
- Audio format results, identical for both paths (video with or without its own audio):
  - **OK:** mp3, aac, ac3, opus, amr, rm, mp1, mka.
  - **`-22` / decoder-not-found:** wma, ra, aiff. `videoErrorFor` maps these to `UnsupportedVideoCodec`, so Add audio wrongly shows the "video unusable" dead-end sheet.
  - **`-1094995529` (AVERROR_INVALIDDATA):** midi, gsm, au. These end in the generic error toast.
- **Probe trap:** a probe that reads a video the app does not own fails with `-13` (EACCES), because the app has no READ_MEDIA_VIDEO (see [[project-no-read-media-video]]). Use a video the app saved itself, for example one under `Movies/MusicEditor/...`. Test audio files live in `/storage/emulated/0/A_Supported_inputs/`.

**How to apply:** before relying on lib behaviour for Add audio, measure output durations with `ffprobe` on a pulled file. Do not trust the code comment.

**Update 2026-10-20 (wrapper from ~/Downloads, committed 378caaed):**
- `replaceAudio(..., shortAudioFill = SILENCE, tempDir)` keeps the full length when the video has its own audio. Measured: 180 s video + 17 s AAC gave a 180 s output, silent (-91 dB) after the audio ends.
- ~~A video with NO audio stream is still cut to the audio length~~ — FIXED in the next wrapper drop (2026-10-20, it added a private `probeVideo`). Verified on the emulator: a 6 s silent video + 3 s audio gave a 6 s output, silent after 3 s.
- `AudioMerger.mixTwo(video.mp4, audio, out.m4a, w1, w2, FIRST)` accepts the mp4 directly. The output is as long as the video. Weights are linear amplitude: 0.3 gives -10.3 dB on a stereo source. A MONO original loses about 3 dB more (-13 dB at 0.3), from the mono→stereo upmix.
- The Add audio Mix path is now `mixTwo` → temp m4a → `replaceAudio` (DefaultVideoProcessingRepository.mixIntoVideo).

**Re-measured 2026-10-20 with the 14:26 wrapper (Pixel 9, probe since deleted).**

| Format | `replaceAudio` | `mixTwo` | Error |
|---|---|---|---|
| wma, aiff | **-22** | **OK** | FFmpeg log: `Unsupported channel layout "2 channels"`. The replace command does `-map 1:a:0 -c:a aac` without aformat, while mixTwo normalizes with `aformat=channel_layouts=stereo`. |
| ra | -22 | -22 | — |
| midi, gsm, au | INVALIDDATA (-1094995529) | INVALIDDATA (-1094995529) | — |

- `UNSUPPORTED_AUDIO_EXTENSIONS` in AddAudioViewModel stays as it is.
- Lib-side fix: add `-ac 2` / aformat on the replace path. After that, unblock wma + aiff (+ aif) and re-measure.

**Update 2026-10-20 15:12 wrapper (commit 8ed49f7f, libffmpeg_jni.so only):**
- `replaceAudio` now handles wma and aiff, with or without a video audio stream, and the output has real AAC audio.
- ExoPlayer can't play WMA/AIFF, so their Replace preview is silent. Verified on the Pixel with `dumpsys audio`: only the video's AudioTrack started.
- ~~Kept blocked~~ — corrected 2026-10-20: the user meant "unblock whatever the lib supports". wma/aiff/aif are UNBLOCKED (commit after e9a1cfc8); a silent preview for them is accepted for now.
- ra / midi / gsm / au still fail in the lib.
