---
name: project-ffmpeg-module-setup
description: "How the real :ffmpeg module ended up wired into green_ba_music_player — source Kotlin wrapper + prebuilt .so extracted from the reference project's AAR, minSdk 23 verified safe by symbol inspection."
metadata: 
  node_type: memory
  type: project
  originSessionId: 63051cfc-1237-41ac-8e16-237e84974539
  modified: 2026-08-24T06:31:02.303Z
---

**UPDATE 2026-08-24:** `:ffmpeg` no longer exists as a separate Gradle module — it was merged into a single `:audio_editor` module (along with the former `:common`/`:copy`/`:trim`) on `refactor/audio_editor_modular`. `com.ffmpeg.wrapper.*` and the `cpp/`/`jniLibs/` content described below moved as-is (package and prebuilt `.so`s untouched) to `audio_editor/src/main/java/com/ffmpeg/wrapper/`, `audio_editor/src/main/cpp/`, `audio_editor/src/main/jniLibs/`. The `minSdk = 23` reasoning below still lives as a comment in the merged `audio_editor/build.gradle.kts`. See [[project_ffmpeg_cpp_source_kept]] for why `cpp/` is kept despite never being compiled by Gradle.

The audio_trim port's native FFmpeg seam (`FakeAudioProcessorDataSource` in [[project_audio_trim_module_no_buildlogic]]'s :audio_trim module) was replaced with a real `:ffmpeg` Gradle module at the repo root. Final setup, after several false starts:

**Source:** the Kotlin JNI-bridge wrapper (`com.ffmpeg.wrapper.*` — AudioProcessor.kt, FFmpegNative.kt, etc.) plus native C source (`ffmpeg_jni.c`, `license_verify.c`, `CMakeLists.txt`) came from the user's own standalone build project at `/home/khapv/Downloads/android` (BUILD.md describes a 2-step cross-compile-FFmpeg-then-build-JNI-wrapper flow, set up for the user's own dev machine "towerhanoi" with NDK r28c — not reproducible in a sandbox with no NDK installed).

**Native binaries:** rather than cross-compiling (impossible without NDK/FFmpeg source in-sandbox), the actual `.so` files (`libavcodec/avfilter/avformat/avutil/swresample.so` + the already-compiled `libffmpeg_jni.so`, all 4 ABIs) were extracted directly from the reference project's prebuilt `app/libs/ffmpeg-wrapper.aar` (`unzip` → `classes.jar` + `jni/<abi>/*.so`) and dropped into `ffmpeg/src/main/jniLibs/<abi>/`. This sidesteps two dead ends tried first: (1) consuming the AAR directly in `:audio_trim` — hit a Kotlin 2.2.0-vs-2.0.21 metadata mismatch (see superseded [[project_ffmpeg_wrapper_kotlin_version_conflict]]); (2) trying to compile `ffmpeg_jni.c` via the original module's own `externalNativeBuild { cmake {...} }` — no NDK in this environment, so that block was removed from `ffmpeg/build.gradle.kts` entirely once the prebuilt `.so` made it unnecessary.

**minSdk decision:** the original module (both the Downloads project and the reference AAR) declares `minSdk = 24`, conflicting with this app's `minSdk = 23` (manifest merger error: "uses-sdk:minSdkVersion 23 cannot be smaller than version 24"). Rather than bumping the whole app's minSdk (a product decision — drops Android 6.0 Marshmallow support) or using the risky `tools:overrideLibrary` escape hatch, verified empirically that lowering `:ffmpeg`'s own declared `minSdk` to 23 is safe: ran `nm -D`/`readelf --dyn-syms` on all 5 core .so's + `libffmpeg_jni.so`, and every imported libc/libm/liblog symbol (malloc, pthread_mutex_*, memcpy, lseek64, getauxval, sched_getaffinity, arc4random_buf, ...) has existed in bionic since API ≤21-23 — none of the API-24-exclusive symbols (getentropy, explicit_bzero, posix_spawn, sendmmsg, complex-math casin/cacos) appear anywhere. A genuinely missing symbol fails hard at dlopen/link time, not silently, so absence of any API-24-only import is solid (not just hopeful) evidence. This reasoning is written as a comment directly on `minSdk = 23` in `ffmpeg/build.gradle.kts` — read it there before ever bumping this value back up "to be safe" without re-checking.

**Also needed:** `gradle/libs.versions.toml` was missing a `kotlinx-coroutines-core` alias (only `-guava`/`-test` existed) — added, since the ffmpeg module's own `build.gradle.kts` (copied verbatim from the Downloads project, not touched otherwise) depends on it via a literal Gradle coordinate string, not a catalog reference.

See [[project_audio_trim_module_no_buildlogic]] for how `:audio_trim` itself is wired, and the same file for why this branch has no `:build-logic` convention plugins (this `:ffmpeg` module was hand-wired the same way).
