---
name: project-tiny-model-thread-overhead
description: Tiny models (Silero VAD) on Pixel 9 run 100x SLOWER with 4 threads than 1 — measure threads per model, never inherit the big model's count
metadata:
  type: project
---

2026-09-29, lyrics spike: whisper.cpp's integrated Silero VAD took 82.2 s with 4 threads vs 0.74 s
with 1 thread on the same 205 s file, Pixel 9 (verify: `whisper-vad-speech-segments -t 1` vs `-t 4`
via adb, see `docs/lyrics-recognition-spike.md`). Per-chunk graphs are tiny, so thread sync on
big.LITTLE dominates. On desktop x86 the same VAD is 0.44 s — **the problem does not show on
desktop**, only on device.

I first misattributed the 80 s to "Silero is slow" from a subtraction (total − encode − decode) and
proposed replacing it with YAMNet; only a direct timing of the component found the real cause.

**How to apply:** when a pipeline stage looks unreasonably slow on device, time that stage alone
with threads=1 before proposing a replacement. whisper.cpp hardcodes VAD `n_thread = 4` in
`whisper_vad_default_context_params`; the app must build its own VAD context. Related:
[[project-lyrics-recognition]].
