---
name: project-ffmpeg-aar-vs-source-decision
description: green_ba_music_player đã chuyển sang dùng ffmpeg-wrapper.aar; cần api scope + -Xskip-metadata-version-check ở 2 module vì aar là Kotlin 2.2 còn project ở 2.0.21.
metadata: 
  node_type: memory
  type: project
  originSessionId: 55aa03b8-b28b-4a32-b415-9485a3510679
  modified: 2026-09-03T03:03:05.479Z
---

Ngày 2026-09-03, `green_ba_music_player` **đã chuyển sang dùng `ffmpeg-wrapper.aar`** (bỏ 18 file source `com/ffmpeg/wrapper/*.kt` và 24 file `.so` trong `audio_editor/src/main/jniLibs/`). Aar nằm ở `audio_editor/libs/ffmpeg-wrapper.aar`, copy từ `/home/khapv/Work/music_editor/andorid_music_editor/app/libs/` (md5 `58886346afd4033e99a1a5a7c25f960c`, 7.5 MB, thay cho 14.3 MB `.so`).

Aar build bằng **Kotlin 2.2 (metadata 2.2.0)**, bytecode Java 17, minSdk 24, compileSdk 35. Project **đã nâng lên Kotlin 2.2.21** nên đọc metadata này tự nhiên, không cần `-Xskip-metadata-version-check` (flag đó từng phải dùng khi còn ở Kotlin 2.0.21 — nay đã gỡ). Còn lại 2 thứ bắt buộc:

1. `api(files("libs/ffmpeg-wrapper.aar"))` trong `:audio_editor` — **không được dùng `implementation`**, và điều này độc lập hoàn toàn với version Kotlin. `com.ffmpeg.wrapper.AudioProcessor` là Hilt binding key (`AudioEditorModule.provideAudioProcessor`, và constructor của `FfmpegAudioProcessorDataSource` + `WaveformExtractor`), mà Hilt component generate ở `:app` → `:app` phải resolve được type. Dùng `implementation` sẽ chết ở `:app:hiltJavaCompile` với `ComponentProcessingStep was unable to process ... AudioProcessor could not be resolved`.
2. `<uses-sdk tools:overrideLibrary="com.ffmpeg.wrapper" />` trong `audio_editor/src/main/AndroidManifest.xml` (kèm khai `xmlns:tools`) — aar khai minSdk 24, app ở 23.

**Why:** Nếu sau này phải quay về Kotlin 2.0.x, cần thêm lại `-Xskip-metadata-version-check` ở **cả** `:audio_editor` lẫn `:app` — thiếu ở `:app` sẽ chết `:app:kspLiteDebugKotlin`. Không có flag thì lỗi là `binary version of its metadata is 2.2.0, expected version is 2.0.0`, kèm **internal compiler error** của K2 trong `FirIncompatibleClassExpressionChecker`.

Lưu ý khi viết comment trong AndroidManifest: chuỗi `--` (ví dụ `readelf --dyn-syms`) làm hỏng XML comment, manifest merger fail với `Error parsing AndroidManifest.xml`.

**How to apply:** Đã verify bằng APK thật (`aapt dump badging` + unzip), không phải suy đoán: `sdkVersion:'23'`, `native-code` đủ 4 ABI, 6 `.so` ffmpeg × 4 ABI, 18/18 class `Lcom/ffmpeg/wrapper/*;` có trong dex. Khi đổi aar mới phải chạy lại đúng bộ kiểm tra này — local AAR trong library module hỏng kiểu im lặng, compile xanh nhưng `UnsatisfiedLinkError` lúc runtime.

Đường sạch lâu dài (chưa làm): build lại aar bằng Kotlin 2.0.21/jvmTarget 11 từ project nguồn `/home/khapv/Downloads/android/ffmpeg-wrapper/` (compileSdk 35, minSdk 24, jvmTarget 17, cần NDK r28c cho CMake) — sẽ bỏ được cả 3 workaround trên.

Liên quan: [[project-kotlin-version-pinned-by-androidx-hilt]], [[project_ffmpeg_module_setup]], [[project_audio_editor_reference_repo]]
