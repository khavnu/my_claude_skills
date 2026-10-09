---
name: project-lyrics-device-run-recipe
description: How lyrics-speed device runs and corpus A/B were done (2026-10-07) — b_runs.sh, TEMP manual-lyrics hook, running reports on a backup copy as the "before"
metadata:
  type: project
---

1. **Realme lyrics run**: scratchpad `b_runs.sh` with `TAG=x RUNS="song.mp3:1 ..."` (clean state, waits battery ≤ 37.5 °C,
   drives the UI through `realme_ui.py`, saves `a2_logs/<TAG>_r<round>_<song>.log`; `timeline.py <log>` prints provisional/
   verified/final/ctc times). Scratchpad is lost on reboot — if gone, rebuild from the transcript (search tool_use commands
   for `b_runs.sh`).
2. **Manual lyrics without UI** (P4 is API-only): temporarily add to `DefaultLyricsRepository.observeLyrics` after `val manual = ...`:
   `?: track.displayName?.substringBeforeLast('.')?.let { name -> context.getExternalFilesDir(null)?.resolve("manual_$name.txt") }?.takeIf(File::isFile)?.readText()?.let(ManualLyrics::candidate)`
   marked `// TEMP`, push `manual_<song>.txt` (LRC) to `/sdcard/Android/data/<pkg>/files/`; REMOVE hook + file after
   (`grep -c TEMP` = 0). Pseudo-songs: `lyrics-corpus/fleurs/songs/<lang>/<n>/vocals16k.wav` → mp3, reference.tsv → LRC.
3. **RAM in its own run** (see [[project-device-measurement-confounds]]): sampler logging `dumpsys meminfo` TOTAL PSS +
   `Java Heap:`; the JVM heap limit on the C55 is 512 MB.
4. **Clean "before" for a corpus report**: copy the latest `checkpoints_backup/code_backup_*` to scratchpad, add `gradlew` +
   `gradle/wrapper` + `local.properties`, run the same `--tests` there with `LYRICS_CORPUS` set. Comparing against an old
   report file is NOT a valid before — it may predate other changes (2026-10-07 it did, and looked like a regression).
   `alignment-forced.tsv` column `viterbiMs` is wall time and noisy (±30% between runs): compare the other columns byte for byte.
5. **Picker flake** (2026-10-07): `realme_ui.open_streaming_and_pick` can fail twice on a song that IS in Downloads
   (list long, other files on top); just rerun that one song (`RUNS="song.mp3:2"`) — not an app bug.
6. **New alignment model? check the blank first**: the most frequent argmax token on a FLEURS pseudo-song must be the
   token the lib takes as blank (`<pad>`/`[PAD]`). Vakyansh/fairseq models (and tr) use `<s>` id 0 — see checklist K7.
7. **Scratchpad scripts are gone after a reboot** (2026-10-08 lost b_runs.sh / realme_ui.py / timeline.py). Device drivers now
   live in `lyrics-corpus/tools/device/` (pixel_ui.py: tap by text + `pick` via picker Downloads root; px_run.sh; px_offline.sh
   which always turns airplane mode back off). Keep new device scripts THERE, not in the scratchpad.
8. **The Pixel 9 is the user's own phone**: notifications/heads-ups steal taps (`cmd statusbar collapse` before each tap);
   never `pkill -f` a pattern that is in the same command line (it kills the shell — airplane mode stayed ON once).
9. **"lyrics: final" is not always THE final** (2026-10-08): a run whose final check fails logs `final … chose text=Whisper
   → 0 line(s)` then `run mode <fallback>` and runs again (hidden from the UI via `transcriptionIncomplete`). px_run.sh /
   ab_nemo.sh stop at the FIRST final, so a fallback run is not measured — check for a second `run mode` line before
   reporting a time (wav2vec2 en hit this in the NeMo A/B, runs/ab/ab_en_*_w2v2_*.log).
