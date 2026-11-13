---
name: pattern-r8-merges-media3-transformer-logsessionid
description: Release-only — R8 horizontal class merging breaks Media3 Transformer below API 31 (NoClassDefFoundError LogSessionId); keep androidx.media3.transformer.** from merging; how to diagnose a release-only failure without Timber
metadata:
  type: project
---

Found 2026-10-29 on branch feature/compress_video_media3 (AGP 8.13.2, Media3 1.9.3, minSdk 24).

**Symptom:** debug build compresses fine; release build on Android 8.1 (API 27) fails every Media3 compress ~10 ms after `TransformerInternal: Init` (`Worker result FAILURE`, no crash, nothing else logged because Timber is only planted in debug). Android 16 release works.

**Cause:** R8 horizontal class merging folded `DefaultAssetLoaderFactory` (then, after pinning it, `ExoPlayerAssetLoader$Factory`) into unrelated classes (TooltipPopup, AndroidAutofill). The merged `LogSessionId` field (API 31 class) becomes Object + `check-cast LogSessionId` → `NoClassDefFoundError: Failed resolution of: Landroid/media/metrics/LogSessionId` below API 31. Media3's consumer rules don't prevent it.

**Fix:** `app/proguard-rules.pro`: `-keep,allowobfuscation,allowshrinking class androidx.media3.transformer.**` (pinning single classes only moves the merge). Verify in `build/outputs/mapping/release/mapping.txt` that every `androidx.media3.transformer.X ->` has its own line, then run a real compress on the API 27 AVD with the release APK.

**Diagnosing a release-only failure fast:** temporarily add `Timber.plant(Timber.DebugTree())` right after `super.onCreate()` in `MusicEditorApplication` (restore after), assembleRelease (needs `-Dorg.gradle.jvmargs="-Xmx6g"` when emulators run, default 2 GB heap GC-thrashes), read the stack, map class names by grepping `-> <obf>:` in mapping.txt and the line ranges under it (no retrace tool in this SDK). Release APK is release-signed: it can't `install -r` over debug, and on the user's Pixel 9 it would replace their comparison build — emulators only unless asked.

Related: [[project-media3-transformer-compress-spike]], [[pattern-ffmpeg-wrapper-hardware-encoder]].
