---
name: project-whisper-jni-device-traps
description: :lyrics:whisper on-device traps (2026-09-29) — CLI numbers don't transfer to an app process; -mc 0 ≠ no_context; test APK targetSdk dialog; fixtures wiped by connectedAndroidTest
metadata:
  type: project
---

Each of these cost a device round trip while building `:audio_stem_split:lyrics:whisper`
(checklist `docs/features/lyrics/checklist.md`, Nhật ký quyết định has the numbers):

- **whisper-cli timings from `adb shell` do not transfer to an app process.** Same build, same flags:
  CLI 4 threads fine; inside the app 3 threads made decode 196 ms/token vs 22 ms with 1. Default is
  now 2 (`WhisperConfig.DEFAULT_THREADS`). Verify with `WhisperThreadSweepDeviceTest -e threads 1,2,3,4`.
- **`-mc 0` is `n_max_text_ctx = 0`**, not `no_context = true` (`examples/cli/cli.cpp:1237`).
- **`whisper_get_timings()` returns PER-RUN averages and is heap-allocated** — delete it or leak.
- **Encoder is not abortable** in whisper.cpp: `ggml_graph_compute_helper(sched, …)` takes no abort
  callback; the flag is checked only after encode (`src/whisper.cpp` ~2514) → cancel latency ≈ one
  encode (~6–11 s on Pixel 9 at 2 threads).
- **Library test APK targets minSdk by default** → Android shows the "built for older version"
  dialog over the test activity → process stays in cpuset `/foreground` (Pixel 9: CPUs 0-6, no X4).
  Fixed with `testOptions.targetSdk = 36` + `ForegroundRule`. Check: `cat /proc/<pid>/cpuset` = `/top-app`.
- **`connectedAndroidTest` uninstalls the test APK, which wipes `/sdcard/Android/data/<test pkg>/`**
  (the 200 MB model fixtures). Use `ANDROID_SERIAL=… ./gradlew :…:installDebugAndroidTest` + `adb shell am instrument -w -e class …`.
- **logcat ring buffer dropped the FIRST result of long sweeps twice** — `adb logcat -G 16M` first.
- Language auto-detect pinned from a window with 1.3 s of singing → "zh" → 0 lines; only pin with ≥ 8 s speech.

Related: [[project-lyrics-recognition]], [[project-tiny-model-thread-overhead]].
