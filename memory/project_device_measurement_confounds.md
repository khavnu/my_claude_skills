---
name: project-device-measurement-confounds
description: "Realme measuring traps found 2026-10-06 — dumpsys meminfo sampling causes playback stalls; the feed's per-segment timing log is how to find lyrics bottlenecks"
metadata:
  node_type: memory
  type: project
  originSessionId: f3d6b4db-0990-4904-8a79-1c1052bbf9b2
  modified: 2026-10-06T06:11:29.798Z
---

1. **`dumpsys meminfo <app>` every 15 s causes 0.1 s playback stalls** (buffering=true mid-song).
   2026-10-06, lyrics-speed K10: 2 of 4 runs with the PSS sampler (`scratchpad/pss_sampler.sh`) had
   extra stalls; the same build without it: 0 extra in 2 runs, and K8/K9 (no sampler) 0 in 9 runs.
   Verify: `grep -c 'buffering=true' a2_logs/k10_r*.log` vs `k10nopss_*`. **How to apply:** measure
   RAM and stalls in SEPARATE runs; never blame code for stalls seen in a sampled run.

2. **Lyrics bottleneck hunting: read the feed split before guessing.** App log line
   `whisper: fed until X ms (read a, whisper b, aligner c ms)` (StreamRecognitionFeed) next to
   `whisper: decoded until` shows feed cost vs recognizer cost per 15 s segment. It found the
   resampler costing ~6 s twice per segment (fixed K9, polyphase PcmConverter). Related:
   [[project-tiny-model-thread-overhead]] (same lesson: time the stage alone first),
   [[project-device-ab-control-line]].

3. **Incremental Kotlin builds can hide a broken test source set** (2026-10-07): an anonymous
   `object : LyricsRepository` in `ObserveStreamLyricsUseCaseTest` stopped compiling when the interface
   gained methods (P4/P2), yet `compileDebugUnitTestKotlin` and the filtered test runs stayed green for
   several changes; only a later edit to a dependent file surfaced it. **How to apply:** after changing
   an INTERFACE, build the test source sets with `--rerun-tasks` once before reporting green.
