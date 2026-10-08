---
name: project-realme-cpu-saturated
description: Realme C55 (Helio G88, 2 big A75 + 6 little A55) is CPU-saturated during streaming+lyrics — more threads/smaller windows only steal from separation; check thread math before proposing
metadata:
  type: project
---

2026-10-06, lyrics-speed: on the Realme C55, separation alone costs 5.1 s per 15 s chunk
(SeparatorFp16 A/B, `docs/features/lyrics-speed/checklist.md` S1) but 8-10 s in the app while lyrics
run beside it. Every "more parallelism" idea after K8 lost: wav2vec2 6 threads (K11) left lyrics
unchanged and slowed separation 25-30 s; smaller Whisper windows (R5) made the final 70 s later.
What DID help was cutting work: wav2vec2 verification instead of Whisper transcription (K), the
resampler done 23x cheaper (K9), dotprod build + q8_0 Whisper (R1/R2).

**How to apply:** before proposing a thread/priority/window tweak on this phone, add up the threads
(separation 6 + wav2vec2 4 + Whisper 4 on 8 cores, only 2 of them big) — the answer is almost always
"reduce total work instead". XNNPACK (fp32 and fp16) is slower than TFLite's own kernels here too.
Related: [[project-tiny-model-thread-overhead]], [[project-device-measurement-confounds]].
