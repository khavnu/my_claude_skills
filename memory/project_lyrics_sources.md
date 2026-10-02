---
name: project-lyrics-sources
description: Lyrics sources feature (embedded/file/LRCLIB/Whisper + verifier/aligner/resolver) — where the measurement corpus lives, how to rerun it, and traps hit building it (2026-10-02)
metadata:
  type: project
---

Checklist: `docs/features/lyrics-sources/checklist.md` (long-feature, approved 2026-10-02; user Q4:
run EVERY source, combine, log — no switches, Whisper always full).

**Corpus is OUTSIDE the repo** (lyrics are copyrighted): `/home/khapv/AndroidStudioProjects/lyrics-corpus/`
— `manifest.json` (21 songs), `lrclib/*.json`, `evidence/<key>/` (vocals16k.wav, whisper.json, vad.txt),
`export/`, `report/`. Rerun (verified 2026-10-02):
`python3 tools/build_evidence.py` (~40 s/song; cached) → `python3 tools/export_evidence.py` →
`LYRICS_CORPUS=<corpus> ./gradlew :audio_stem_split:lyrics:core:testDebugUnitTest --tests "*.CorpusVerificationReport" --rerun-tasks`.
whisper-cli is built in `tools/whisper.cpp` at the vendored commit with the SDK cmake
(`~/Android/Sdk/cmake/3.22.1/bin`, no system cmake).

Traps (each cost a round):
- whisper-cli has NOT got the lib's `VadSpeechCut.toTrackRange` fix: a segment spanning a VAD gap
  starts at the previous line's end. Host evidence is pessimistic there; check
  [[project-lyrics-open-items]] before blaming the lib. Its token offsets are in VAD-compressed time.
- CLI output must go through `HallucinationFilter` + `RepeatedLineGuard` (report does it) or
  "u u u…" loops wreck identity scores.
- LRCLIB `q` searches names only, never lyric text (two exact lyric lines → 0 hits).
- ffmpeg `-metadata lyrics=` writes ID3 TXXX "USLT", not a USLT frame.
- Android JVM unit tests compile against android.jar: no `com.sun.net.httpserver` — use ServerSocket.
- Single-word identity is useless for Vietnamese (another song scored 0.756); word PAIRS separate.
- Word timestamps (group D, 2026-10-02): heuristic token timestamps are the keeper; DTW was tried
  and rejected (needs flash attention off → different text; 200–400 ms late on Đoản Xuân Ca vs
  30–120 ms heuristic). Don't re-propose DTW without new evidence. whisper-cli has flash attention
  ON by default (`-nfa` to turn off).
- Forced alignment spike (J1, 2026-10-02): `PYTHONPATH=tools/pydeps python3 tools/ctc_align_spike.py <hf id> [romanize]`
  (torch/transformers installed with `pip --target tools/pydeps` — no python3-venv on this host).
  dragonSwing/wav2vec2-base-vietnamese (Apache) beat everything: N6 p90 8/10 vs Whisper-align 3/12;
  MMS-300m-FA (CC-BY-NC) worse on vi because it needs tone-stripped text. Numbers: checklist Nhật ký.
- ORT minimal AAR rebuild (2026-10-02) WORKS on this host without sudo: tools unpacked in
  `lyrics-corpus/tools/build-tools/` (cmake 3.31.8 tarball, Temurin JDK 17, pkgconf via `apt download`
  + `dpkg -x`, ninja from the SDK cmake), run `build_ort_aar.sh` there (~40 min, 4 ABIs). One app =
  one libonnxruntime.so → every ORT model must be in `onnx_runtime/custom/required_operators.config`.
- wav2vec2 on device: ORT CPU arena ON = 892 MB RSS, OFF = 356 MB (Wav2Vec2Config.cpuArena=false).

