---
name: project-kotlin-version-pinned-by-androidx-hilt
description: Kotlin 2.2 trên green_ba_music_player cần force room-compiler-processing 2.8.4 lên kapt classpath; androidx.hilt 1.3.0 và Dagger 2.59+ đều có trần AGP riêng.
metadata: 
  node_type: memory
  type: project
  originSessionId: 55aa03b8-b28b-4a32-b415-9485a3510679
  modified: 2026-09-03T03:02:40.080Z
---

Nâng `green_ba_music_player` lên **Kotlin 2.2.21 mà vẫn giữ AGP 8.11.1 / compileSdk 36** là làm được. Chốt ngày 2026-09-03, đã verify bằng APK thật.

Ba ràng buộc phải xử lý cùng lúc:

**1. `androidx.hilt:hilt-compiler` 1.3.0 kéo XProcessing 2.6.0, không đọc được metadata Kotlin 2.2.** Triệu chứng: `:app:kaptLiteDebugKotlin` chết với `error: Unable to read Kotlin metadata due to unsupported metadata kind: null` trên stub của `ReloadWidgetsWorker`, `SyncMediaWorker`, `Dispatcher`.

Fix — force reader lên, **không** bump androidx.hilt lên 1.4.0 (bản đó đòi AGP 9.1.0 + compileSdk 37, và kéo `androidx.lifecycle:*-compose-android:2.11.0` cũng đòi 37):

```kotlin
// app/build.gradle.kts
configurations.matching { it.name.startsWith("kapt") }.configureEach {
    resolutionStrategy.force("androidx.room:room-compiler-processing:2.8.4")
}
```

Đã verify không phải fix giả: `ReloadWidgetsWorker_AssistedFactory`, `_AssistedFactory_Impl`, `_HiltModule`, `_Factory` đều có mặt trong dex cho cả 2 worker. `./gradlew :app:dependencies --configuration kaptLiteDebug` cho thấy `room-compiler-processing:2.6.0 -> 2.8.4`.

**2. Dagger/Hilt trần ở 2.58 khi còn AGP 8.x.** Từ **2.59 trở lên bắt buộc AGP 9.0.0** — Hilt Gradle Plugin fail ngay lúc apply: `The Hilt Android Gradle plugin is only compatible with Android Gradle plugin (AGP) version 9.0.0 or higher`. Dagger 2.58 chạy tốt với AGP 8.11.1.

**3. Kotlin 2.2 kéo theo KSP2**, nên bắt buộc: Room ≥ 2.7 (dùng 2.8.4 — 2.6.1 không chạy KSP2), và Glide phải chuyển từ `ksp(glide.ksp)` sang `kapt(glide.compiler)` vì processor KSP của Glide chưa sẵn sàng KSP2 (bumptech/glide#5500). `:video` khai Glide processor nhưng không có `@GlideModule` nào — gỡ hẳn.

**Why:** Đã thử và loại trừ được giả thuyết "Dagger là thủ phạm" — bump Dagger 2.57.2 → 2.58 không làm lỗi biến mất, chứng tỏ reader hỏng nằm ở androidx.hilt chứ không phải XProcessing shaded trong Dagger.

**How to apply:** Đừng gỡ `@HiltWorker` để né vấn đề này — từng cân nhắc refactor 2 worker sang Dagger `@AssistedInject` + `WorkerFactory` tự viết, nhưng force XProcessing rẻ hơn nhiều và đã chứng minh chạy được.

Liên quan: [[project-room-schemalocation-must-go-through-ksp]], [[project-ffmpeg-aar-vs-source-decision]]
