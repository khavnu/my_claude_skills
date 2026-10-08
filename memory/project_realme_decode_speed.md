---
name: project-realme-decode-speed
description: Realme C55 decodes mp3 to PCM at only 3–5x realtime (not ~37x) — cost of anything that "just decodes the source again"; per-sample conversion is half of it in debug builds
metadata:
  type: project
---

Measured 2026-10-05 (`audio_stem_split/core/src/androidTest/.../stream/SourceDecodeSpeedDeviceTest.kt`, anh_nho_em.mp3 4:38):
- `MediaCodecPcmDecoder.decode` + `SourcePcmCache`: whole song 53–83 s, to 166 s 33–51 s (3.3–5x realtime).
- A bare MediaExtractor+MediaCodec loop that never reads the output buffer: 31–46 s. Reading the buffer +
  converting is the other half (DEBUG build; release never measured). FUSE vs internal storage: no difference.
- Tried and NOT worth it: pipelined input/output loop (no gain); bulk PCM16 path with a 65,536-entry LUT
  (byte-identical, ~15–25% alone, invisible in the app) — both reverted.
- Separate runs drift up to 40% on this phone: compare only interleaved A/B in one run.

**Why:** the stream-resume checklist assumed "decode again ~0.8 s per 30 s" and dropped the source cache;
that made a resume at 50% wait 38 s. Fixed by keeping the cache (`SourcePcmCache.openKept`), user's choice.

**How to apply:** before any design that re-decodes a source (seek, resume, re-separation), budget
~0.25 s of wall clock per second of audio on the Realme, or keep the decoded PCM.
