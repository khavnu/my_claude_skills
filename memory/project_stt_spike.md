---
name: project-stt-spike
description: On-device Android SpeechRecognizer (vi-VN) — failed as a Whisper replacement (spike 2026-10-19); SHIPPED 2026-10-20 in 0.3.0 only as the K-verified background upgrade (OnDeviceTranscriber + verifyUpgrade)
metadata:
  type: project
---

Spike for WMusi (WMUSI-21 → AUDIOSEPARATION-22/25). Full numbers + rerun command: `docs/features/lyrics-stt-spike/report.md`.
Headline: WER with diacritics Whisper q8_0 0.648 vs STT 0.577; both gates failed (≥0.15 better on 4/14, mode K accepts 6/14);
speed: CORRECTED 2026-10-20 — the "exactly real time" conclusion was WRONG (only 1× and unpaced were tried); the engine
decodes ~3× real time on a Pixel 9 and silently DROPS faster input (1/2/3× same words, 5× −1/3, 10× −2/3); 0.3.1 feeds at 3×.
VozNote "fast" (7 min in 36 s) = the same loss (181/650 words). Lesson: sweep a rate before declaring a limit;
LOAD matters too (2026-10-20, AUDIOSEPARATION-30/WMUSI-26): WMusi's stored vocals gave 53 lines/coverage 1.00 at 1/2/3× on
an idle Pixel 9 (`SttUpgradeDeviceTest.speedSweepOnPushedPieces`) but 43/0.73 at 3× while the app was PLAYING — the engine
runs in a system process and loses CPU. WMusi uses speed = 1.0; lib default stays 3×; mode K never accepted an STT text worse than Whisper's.
2026-10-20 (corrected from "open decision"): user chose the verified background upgrade; shipped in 0.3.0 —
`OnDeviceTranscriber` + `LyricsPipeline.verifyUpgrade` + `LyricsSource.Transcribed` (AUDIOSEPARATION-26). E2E Pixel 9:
Khi Em Ngủ Say accepted (verify 79 s), rap rejected (52 s). An enum source missing from a SOURCE_ORDER list sorts FIRST
(indexOf = -1) — CandidateRanking and PureLyricsFinder both had to be fixed when Transcribed was added.

**Why:** next session may re-propose "use Android STT as the first pass" — the two failed quality gates (remix/rap losses,
K accepts only 6/14) are what kill that, not speed.

**How to apply:** before suggesting STT again, read the report; anything new must beat those numbers or measure a phone we
could not (no Realme/Samsung run yet). Temporary module `audio_stem_split/lyrics/stt_spike` kept until WMusi confirms the wiring.
Related: [[project-karaoke-idea-explored]], [[project-lyrics-sources]].
