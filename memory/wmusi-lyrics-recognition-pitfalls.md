---
name: wmusi-lyrics-recognition-pitfalls
description: "Lyrics recognition (lib 0.3.1 pipeline) pitfalls verified 2026-10-20 — runTest backgroundScope + advanceUntilIdle, unscoped @Inject repos duplicating Whisper runs, emulator e2e recipe"
metadata:
  node_type: memory
  type: project
  originSessionId: a262b834-fb52-4207-97e1-f64b8d6db760
  modified: 2026-10-20T03:58:21.649Z
---

Verified 2026-10-20 while wiring `:lyrics:pipeline` (checklist `docs/features/lyrics-recognition/checklist.md`):

- **`advanceUntilIdle()` does not run `backgroundScope` work** (background tasks don't keep the scheduler busy) → a test launching collectors in `backgroundScope` saw nothing. Use `runCurrent()`. Cost ~20 min (`LibLyricsRepositoryRecognitionTest`).
- **An `@Inject` class bound with `@Binds` but without `@Singleton` is one instance per injection** — `LibLyricsRepository` had per-instance shared runs, so Now Playing + Sing ran Whisper twice and the Sing tab sat on "Listening" ~1 min. Seen only on the emulator: logcat `-s Lyrics:I` showed `run mode …` twice. Any engine class with per-process state needs `@Singleton`.
- **Emulator e2e recipe**: tagless copy of a corpus song (`ffmpeg -map_metadata -1`, new title) pushed to `/sdcard/Music/…` + `MEDIA_SCANNER_SCAN_FILE`; navigate with `uiautomator dump` (script `/home/khapv/Tmp/claude/WMusi/lyrics-recognition/open_probe.sh`, `ui.sh`); kill mid-run with `run-as com.wife.recommend.music kill -9 <pid>`. Numbers on emulator-5554: first line ~13 s after the Sing tab, 215 s song final in 49 s, resume shows kept lines in < 10 ms.
- Library device tests (`:sing:engine` androidTest) get the models via the `wmusi.lyrics.models` convention plugin (device-test assets). A clip pushed to `Android/data/<test pkg>/files` is wiped when the full connected run reinstalls the test APK → assumption-skip reported as failure.

Related: [[project-karaoke]], [[wmusi-device-verify]].
- **Next-song e2e (verified 2026-10-21)**: S7 + `recognizeAhead` run only while a Sing *session* is open — "Original" leaves it closed, tap **Guide** (572,1555) after `open_probe.sh`. Probe songs are ~3.5 min: a song ending auto-advances and looks like a "next-song run" that is really the current one — read `file=` vs separation `separateSegment[0]` times. Reinstall (`installDebug`) before an e2e: the emulator keeps the APK of the last connected run, and a stale build cost one full round here.
- **Non-vi plain lyrics are NOT left to Whisper (verified 2026-10-26, emulator, lib 0.3.3):** with only the bundled vi wav2vec2, English USLT plain lyrics ran `WhisperStopsEarly, aligner lyrics.emissions` and ended `timing=ForcedAlignment (confidence 0.01)` — the vi model aligns Latin-script lyrics, and well (3 JamendoLyrics en songs: p50 48 ms, 91 % ≤ 0.5 s). public_api.md's "ngôn ngữ khác về Whisper" is wrong for this case. NeMo multi pushed to `getExternalFilesDir/models/lyrics` (read since LyricsRecognition passes `modelDirectories`) → `AlignmentModelVerifies`, Whisper hears 0 lines, p50 133 ms (80 ms frames) but 96 % ≤ 0.5 s. Recipe + scorer: `/home/khapv/Tmp/claude/WMusi/nemo-en/` (`open_song.sh <tag>`, `score.py <run_dir>` vs `lyrics-corpus/sung/jamendolyrics/annotations/lines`); probe mp3s = tagless + USLT, title "NeMo probe enN" so LRCLIB misses. `pm clear` between conditions (stored lyrics are keyed by uri/size/mtime).
