---
name: project-media3-transformer-compress-spike
description: "Spike 2026-10-29 (branch spike/media3-transformer-compress): Media3 Transformer for Compress video — fixes keyframe/VFR/size issues but NOT #480 colour, and fails on >1080p on low-end decoders"
metadata:
  node_type: memory
  type: project
  originSessionId: 4c307939-5ce3-4bb7-9648-f0eb7c5763c4
  modified: 2026-10-29T03:20:40.898Z
---

Context: ffmpeg-wrapper (4) dropped libx264 (GPL) and its hardware path is broken (see [[pattern-ffmpeg-wrapper-hardware-encoder]]), so Media3 Transformer 1.9.3 was tried as the compressor. Code: `data/media3/Media3VideoCompressor.kt` + probe `androidTest/.../data/media3/Media3CompressProbeTest.kt` (runs only with `-e probe true`; inputs pushed to /data/local/tmp/m3probe, copied into app cache via `uiAutomation.executeShellCommand("cat …")` because the app can't read /data/local/tmp and adb-created Android/data dirs are owned by shell). Run with installDebug + installDebugAndroidTest + `am instrument` (NOT connectedAndroidTest, which uninstalls the app). Outputs/logs: /home/khapv/Tmp/claude/andorid_music_editor/m3spike/.

**Good (emulator Android 16 + Huawei AMN-LX3 Android 9):** first keyframe at 0 and decoded frames = packets everywhere; VFR screen recording keeps 124/124 frames; exact sizes (364x360, no x16 rounding); portrait kept via rotation -90; fast (emulator 2–5 s per clip, Huawei 13.4 s for the 30 s QC clip vs 28 s with the ffmpeg HW path).

**Size:** the default InAppMp4Muxer reserves a ~380–400 KB `free` box (front moov) → small files ~20% over the estimate. `Transformer.Builder.setMuxerFactory(FrameworkMuxer.Factory())` removes it; then output/estimate = 0.79–0.94 (safe side), except the emulator screen recording (1.2–1.5, encoder ignored the low bitrate).

**Bad:**
- #480 colour NOT fixed: full-range QC source comes out stretched on BOTH devices (decoded gray: ≤5 = 5.3–5.6%, ≥250 = 3.2–3.6%, same as the old broken ffmpeg output; source 0.9% / 0%). Tag is fine (pc on emulator, tv on Huawei) — the pixels are already expanded inside the GL pipeline.
- Device decoder limits: Huawei decoders max 1920x1088 (OMX.google) / 2048x1088 (OMX.MTK) → 2560x1440 and 2424x1080 fail with `ERROR_CODE_DECODING_FORMAT_UNSUPPORTED`; decoder fallback can't help. Check limits with `cat /vendor/etc/media_codecs*.xml | grep -A6 'video/avc'`.
- Framework MediaMetadataRetriever can't read FLV (probe skips; app uses FFmpeg fallback for metadata).

**Routing research (2026-10-29, item 1):** `data/media3/VideoDecoderSupport.kt`.
- Decoder prediction = `MediaCodecList(REGULAR_CODECS).findDecoderForFormat(trackFormat)` (+ per-decoder `VideoCapabilities.isSizeSupported`): matched Transformer's real outcome 13/13 (emulator 7/7 all decodable up to 4K; Huawei 2 OK ≤1080p, 4 FAIL >2048 wide — MTK decoder reports max 2048x2048).
- Full-range detection: `MediaExtractor` KEY_COLOR_RANGE reports QC's full-range .mov as LIMITED (2) — wrong. Media3 `MetadataRetriever` (`retrieveTrackGroups()` → `Format.colorInfo.colorRange`) reports FULL (1) — correct, on both devices. Use Media3 for rule (a).
- Huawei logcat buffer is small: long probes lose early lines → `adb logcat -G 8M` first.

**Pixel_2 AVD, Android 8.1 / API 27 (2026-10-29, probe via worktree from spike branch + `git stash apply stash@{0}`):** no hang, 4/4 exports OK in 25 s total (`OMX.google.h264.encoder`); keyframe 0, frames = packets, VFR 124/124 (ExportResult.durationMs says 4810 but container is 5.31 s — ignore that field). **Colour of QC full-range source NOT stretched here**: whole-video displayed gray p5/p50/p95 22/119/228 vs source 21/119/229 (Android 16 emu 6/116/247, Huawei 7/120/247) → the stretch is GPU/driver-dependent, not Media3 itself; the API 27 emulator uses the host GPU so this says nothing about real Android 8 phones. **VideoDecoderSupport is too strict on API 27**: predicted 2560x1440 and 2424x1080 as not decodable (OMX.google caps) yet Transformer decoded both → don't block on the prediction; try the export and map `ERROR_CODE_DECODING_FORMAT_UNSUPPORTED` instead. Output/estimate 0.95–1.04 (VFR 1.15). Files: /home/khapv/Tmp/claude/andorid_music_editor/m3spike/pixel2_api27/. Measure colour with the whole-video script (fps=2, scale in_range=<tag>:out_range=pc, gray percentiles), not one 10 s window.

**Decision 2026-10-29 (user):** ship ffmpeg-wrapper (6) + Media3 combined now (don't wait for a (7)); Media3 covers API < 28 (FFmpeg sync-mode hang) and devices whose default AVC encoder is software c2.android / OMX.google (magenta).
