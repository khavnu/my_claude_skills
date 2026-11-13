---
name: pattern-ffmpeg-wrapper-color-range
description: "ffmpeg-wrapper VideoCompressor drops colour range: full-range (yuvj420p/pc) source comes out yuv420p untagged → darker, more contrast (#480); native bug, app can't fix"
metadata:
  node_type: memory
  type: project
  originSessionId: 4c307939-5ce3-4bb7-9648-f0eb7c5763c4
  modified: 2026-10-28T08:51:03.321Z
---

Verified 2026-10-28 (ticket #480, ffmpeg-wrapper with FFmpeg 8.0.1).

**Symptom:** compressed video looks darker / higher contrast than the source in the same player.

**Cause:** source `yuvj420p, color_range=pc` → lib output `yuv420p, color_range=unknown`. Sample values are unchanged (signalstats YMIN 0 / YMAX ~241–245 on both), only the flag is lost, so players read it as limited range. `libffmpeg_jni.so` builds its own filter graph: the buffer source args string `video_size=%dx%d:pix_fmt=%d:time_base=%d/%d:pixel_aspect=%d/%d` has no `range=`/`colorspace=`, then it appends `%s,format=%s`. Desktop ffmpeg 6.1.1 with the same args keeps `yuvj420p, pc`, so don't use desktop ffmpeg as a stand-in for the lib.

**How to check in 10s:** `ffprobe -v error -select_streams v -show_entries stream=pix_fmt,color_range -of csv=p=0 <file>` on source vs output. Find strings in the native lib with `strings jni/arm64-v8a/libffmpeg_jni.so | grep format=` after unzipping the aar.

**How to apply:** this needs a lib fix (pass range/colorspace to buffersrc + copy color props to the encoder). Bug report + files: `/home/khapv/Tmp/claude/andorid_music_editor/video-compress/color-range-bug/`. Same "native execute is not fftools" limitation as [[pattern-ffmpeg-wrapper-video-vfr]].

**Update 2026-10-29:** lib "ffmpeg-wrapper-release (4).aar" adds the fix in native (`scale=in_range=full:out_range=tv`, log line `video src colour: range=...`) but ships WITHOUT libx264 in all 4 ABIs → compress fails at once with `encoder 'libx264' not found` (seen on the emulator). Not adopted; app/libs kept the old aar. Before swapping any new aar, check per ABI: `strings jni/<abi>/libavcodec.so | grep -c libx264` (old aar = 3 and its configure line has `--enable-gpl --enable-libx264`; aar (4) = 0). Corrected 2026-10-29: an earlier version of this note said `grep -c x264_encoder_open`, which prints 0 for both aars.
