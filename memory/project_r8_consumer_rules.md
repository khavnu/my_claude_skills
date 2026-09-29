---
name: project_r8_consumer_rules
description: R8 từng làm app crash SIGABRT vì AAR ONNX Runtime không ship keep rule cho JNI; đã vá bằng consumer-rules.pro trong chính module library
metadata: 
  node_type: memory
  type: project
  originSessionId: e0e87c8a-7800-4c48-8018-92b52653531d
  modified: 2026-09-07T07:48:02.500Z
---

`:audio_stem_split:onnx_runtime` và `:audio_stem_split:native_build:custom` giờ đều có
`consumer-rules.pro` + `consumerProguardFiles(...)`. `app/build.gradle.kts` để
`isMinifyEnabled = true` cho release, đã verify chạy được end-to-end (2026-09-07).

**Why:** AAR `onnxruntime-android` 1.29.0 chỉ ship keep rule cho mấy class **telemetry** — đọc thẳng
từ `proguard.txt` của nó. Tầng native của ORT tra class Java **theo TÊN** qua JNI, nên R8 đổi tên
`OrtSession$Result` → `b.g`, `OrtException` → `b.d`, xoá 89 class → **SIGABRT**
(`JNI DETECTED ERROR: java_class == null in call to GetMethodID`), không phải exception bắt được.
AAR TFLite build bằng Bazel trong `libs/` cũng MẤT rule `@UsedByReflection` mà artifact Maven gốc có
— hiện chỉ còn tới R8 nhờ `select-tf-ops.aar` tình cờ mang bản y hệt.

**How to apply:**
- Keep rule phải nằm trong **module library** (consumer rules đi theo module), KHÔNG phải trong
  `:app/proguard-rules.pro` — nếu không thì repo này chạy được còn mọi tích hợp sau đều gãy.
- **Build R8 xanh không chứng minh gì.** Cả hai lỗi đều compile/đóng gói/cài/mở app bình thường; chỉ
  lộ khi thật sự chạy model.
- **Timber KHÔNG được plant ở release** (`AudioSeparationApplication` chỉ plant khi `BuildConfig.DEBUG`)
  → mọi diagnostic qua Timber vô hình đúng ở build có bug. `Log.d` của engine thì còn.
- R8 **không giảm size đáng kể**: 976MB debug → 961MB release. APK này là model chứ không phải code.
  Bài toán size là Play Asset Delivery, chưa động tới.

**Bẫy đo đạc:** đừng đọc "có đang phát không" từ `uiautomator dump` — tôi đã 2 lần đọc ra
"position stuck 00:00" và suýt báo sai là R8 làm hỏng playback. Nguồn đúng là
`adb shell dumpsys audio | grep AudioPlaybackConfiguration` → `state:started` (nhớ pid nằm ở dạng
`u/pid:<uid>/<pid>` nên grep `"/$PID "`).

**Nguồn artifact giờ nằm TRONG repo**: `audio_stem_split/docs/readme-vi.html` (trước chỉ ở
scratchpad và đã bị xoá mất một lần — khôi phục được nhờ WebFetch lưu raw HTML kèm summary, rồi bóc
wrapper doctype/head/frame-runtime của publish pipeline). Sửa artifact = sửa file đó rồi publish lại
cùng URL.

Ledger: `.superpowers/sdd/2026-09-07-r8-release-build/`. Liên quan:
[[project_stream_chunk_10s]], [[project_streaming_phase2_shipped]].
