---
name: project-lyrics-recognition
description: Lyrics recognition (vocals stem → timestamped text) requirements agreed 2026-09-29 — multilingual, offline, line start+end, few-seconds tolerance; spike-first
metadata:
  type: project
---

2026-09-29 user decided to pursue lyrics recognition (ASR on the separated vocals stem). This is a
DIFFERENT feature from [[project-karaoke-idea-explored]] (which rejected ASR for karaoke, where the
user supplies text). Here there is no text — transcription is the actual goal.

Agreed requirements: multilingual; offline only; output one line per sung phrase with start AND
end time; a few seconds of timestamp error is acceptable (so Whisper segment timestamps suffice —
no DTW/token timestamps needed).

Grounded constraints found in-repo (verify before relying):
- Energy VAD on the vocals stem does NOT work: Spleeter masks sum to 1, vocals stem is never
  silent — `audio_stem_split/core/.../StemLevel.kt` `UNDETECTABLE_STEMS`. Use YAMNet per-frame
  scores on the mix instead; `PresenceScorer.score()` currently collapses frames by MAX, and its
  `absentBelowScore` thresholds are track-level, not reusable per frame.
- New native libs must pass 16 KB page-size alignment (reason GPU delegate was removed, see
  [[project_prior_removals]]).

Spike DONE 2026-09-29 (desktop) — report `docs/lyrics-recognition-spike.md`, scripts
`docs/lyrics_spike/`. Headlines: separation is required (raw mix → hallucination); large-v3-turbo
hallucinates whole 30 s windows ("Ghiền Mì Gõ") on 5/7 tracks — don't propose it; genre matters
more than model size (ballad OK, rap/EDM garbage); `-mc 0` mandatory; VAD not enough, needs a
post-filter. Spike traps: `~/Music` is ~all Vietnamese, "HappyNewYearBeatInstrumental" HAS vocals
(not a negative control); desktop separation needs the TF 2.16 Flex venv at
`~/.claude/jobs/95bd196e/tmp/quantize_spike/venv_oracle`; build whisper.cpp with SDK cmake
`~/Android/Sdk/cmake/3.22.1/bin/cmake` (no system cmake). Pixel 9 measured 2026-09-29 (table in the spike doc): small+greedy+VAD 194 s for a 205 s track,
medium 444 s / 843 MB. CORRECTED same day: the ~80 s was VAD THREAD OVERHEAD (4 threads), not Silero — with VAD on 1 thread small+greedy = 81.7 s, see [[project-tiny-model-thread-overhead]]. YAMNet-as-VAD (AUC 0.58-0.77) and `-ac` (slower, loses lines) both rejected with numbers. On-device traps: `pkill -f` with
a pattern that appears in your own command kills your own shell (exit 144); `-np` suppresses
whisper's timing lines; `/system/bin/time -v` exists on device (labels "Real time (s)",
"Max RSS (KiB)"); two devices attached → always `adb -s`.

Original plan: recommended a desktop spike first (whisper.cpp vs ORT, base vs small, ± YAMNet VAD;
measure WER/CER per language incl. Vietnamese, line-timestamp error, line merge/split rate).
Vietnamese sung ASR expected weak (tones overwritten by melody) — likely "draft to edit" quality.

Round 3 (2026-09-29, concurrent run on Pixel 9): separation 32 s alone / 43 s concurrent for a
192 s track; ASR 173 → 213 (concurrent) → 248 s (alone again) — thermal drift (BIG 85 °C) swamps
contention, single-run numbers are ±40% once the phone is warm. ASR is the entire critical path.
Device traps: this Pixel reports AC (not USB) power over the cable, so `svc power stayon usb` does
nothing — use `stayon true`; the user may unlock the wrong device when two are attached — check
`isKeyguardShowing` per serial before retrying.
