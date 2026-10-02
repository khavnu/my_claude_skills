---
name: project-lyrics-open-items
description: :audio_stem_split:lyrics finished 2026-09-30 — deliberately open items (A20s, pipeline 30 vs 36 lines, no product UI) so they are not "rediscovered"
metadata:
  type: project
---

`:audio_stem_split:lyrics:core` + `:lyrics:whisper` finished 2026-09-30; every checklist item ticked
or deferred (`docs/features/lyrics/checklist.md`, Nhật ký quyết định has every number). Open on purpose:

- **N10 low-RAM device (Samsung A20s, 2.86 GB) not measured** — user: "A20s chúng ta sẽ improve sau".
  Expect the baseline (non-armv82) .so there; RSS +295–363 MB on top of separation.
- **Pipeline 30 vs 36 lines — RESOLVED 2026-09-30** (was listed open; the overlap-add guess was
  WRONG): recognition alone on the same device-separated stem gives 36, so it is streaming window
  boundaries, mostly line merging (295 vs 307 words). Two real defects found and fixed: a segment
  spanning a VAD-removed gap timed 32 s early (`VadSpeechCut.toTrackRange`), and ~6 words lost at a
  window seam because Silero resets per call (VAD now gets 2 s of `leadingContext`). STILL OPEN:
  Silero also dips inside a sustained sung phrase (1.8 s) — `vadMinSilenceMs = 2000` fixes the seam
  but broke the corpus (lost a verse, cross-line loops), so default stays 100 ms. Numbers:
  checklist Nhật ký. Line COUNT is a bad quality metric here — compare words/coverage per line.
- ~~No product UI~~ — corrected 2026-10-02: the Streaming screen shows lyrics (ticker above
  "Phát tất cả", `DefaultLyricsRepository`, model read in place from app assets). Model delivery for
  product is still the user's decision.
- **HallucinationFilter may drop fast rap** (Em Bé: 953 → 254 words after filtering, 2026-10-02
  host corpus) — not yet split into real hallucination vs rap; not fixed.
- Targets relaxed by the user (not by Claude): N3 (≤ 35 s on a track whose opening the model hears;
  pop exempt), N8 (pipeline ≤ recognition-alone + 45%). N1 accepted at +14–16% for sessions.

Related: [[project-lyrics-recognition]], [[project-whisper-jni-device-traps]].
