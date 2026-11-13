---
name: pattern-exoplayer-needs-seekable-factory
description: Every new ExoPlayer that plays library audio must use seekableMediaSourceFactory, otherwise raw .aac (ADTS) seeks restart at 00:00 silently
metadata:
  type: project
---

Any new `ExoPlayer.Builder` that plays a library audio file needs `.setMediaSourceFactory(seekableMediaSourceFactory(context))` (`playback/SeekableMedia.kt`). The default extractors treat a raw ADTS `.aac` (and an MP3 without an index) as unseekable: `seekTo` silently plays from 00:00 and `duration` stays `C.TIME_UNSET`.

Found 2026-10-16 in the Add audio preview (`ui/component/video/SyncedAudio.kt`). After a seek to 02:36 on Pixel 9, the audio still played from about 00:01 (drift −156 s). The drift check never corrected it, because `duration` was unset. With the factory, drift after the same seek is about −60 ms (constant-bitrate seeking is approximate). Without seeks, drift stayed at ±10 ms over 60 s.

**Why:** emulator tests passed with an `.mp3` and an 8 s video, so the bug only showed with `AAAAC_aac_2.aac` plus a seek on a long video.

**How to apply:** when testing a new player, seek on a `.aac` file (Pixel: `AAAAC_aac_2.aac`, 3:37). To measure drift, temporarily log `currentPosition` of both players every second (see [[reference-device-shot-helpers]]).
