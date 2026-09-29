---
name: project-room-schemalocation-must-go-through-ksp
description: green_ba_music_player set room.schemaLocation qua annotationProcessorOptions nên KSP không nhận — schema chưa từng được export dù exportSchema=true.
metadata: 
  node_type: memory
  type: project
  originSessionId: 55aa03b8-b28b-4a32-b415-9485a3510679
  modified: 2026-09-03T03:04:56.077Z
---

`app/build.gradle.kts` của `green_ba_music_player` từng set:

```kotlin
defaultConfig {
    javaCompileOptions { annotationProcessorOptions { arguments["room.schemaLocation"] = "$projectDir/schemas" } }
}
```

Room chạy dưới **KSP** (`ksp(libs.room.compiler)`), mà `annotationProcessorOptions` chỉ tới KAPT/javac → option bị bỏ im lặng, build không tự sinh lại schema.

Dấu hiệu nhận biết trong build log: `room.schemaLocation` xuất hiện trong warning `The following options were not recognized by any processor: [...]` của task kapt.

**Đính chính:** file `app/schemas/com.amapps.media.music.data.room.AppDatabase/2.json` **đã có sẵn trong repo** từ commit `33cb94cc7 "Fix Room schema for upgraded toolchain"` — không phải "chưa từng được export". Vấn đề thật là option đi sai kênh nên build **không tự regenerate**, tức lần bump `version` tới sẽ không có gì cập nhật file này.

**Why:** Schema không tự sinh lại thì lần bump `version` tới không có gì để diff/validate, và `room-testing` MigrationTestHelper cũng không bám vào đâu.

**How to apply:** Đặt ở top-level module, không nằm trong `android {}`:

```kotlin
ksp { arg("room.schemaLocation", "$projectDir/schemas") }
```

Sau khi sửa, build sinh ra file **byte-identical** với bản đang có trong HEAD (md5 `9c30a3d11d3a18fd46e74d152859aa75`, version 2, 13 entities, 1 view, identityHash `25809f520fea0668077e02be69cad4df`). Điều này đồng thời chứng minh nâng Room 2.6.1 → 2.8.4 **không đổi schema** nên không cần migration. File không bị gitignore.

`:video` có DB riêng (`VideoDatabase.kt`) nhưng `exportSchema = false` nên không dính.

Liên quan: [[project-kotlin-version-pinned-by-androidx-hilt]]
