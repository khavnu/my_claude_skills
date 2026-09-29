---
name: pattern-unload-model-native-heap
description: Engine đã chạy giữ 1.8-2.7GB native heap mà onTrimMemory không đòi lại được — phải gọi unloadModel() khi run xong
metadata:
  type: project
---

Sau bản lib 2026-09-11 (`audio_stem_split/docs/MIGRATION-2026-09-11.md`):

**`unloadModel()` là bắt buộc, không phải tối ưu.** Một engine đã separate giữ arena TFLite
1.8-2.7GB native heap. Lib đã đo: MỌI mức `onTrimMemory` — kể cả `COMPLETE` (gửi ngay trước khi
Android giết process) — trả về **0 byte**. Triệu chứng khi vượt: app chết **không exception, không
tombstone**, chỉ `Process <pkg> has died: fg TOP`, và hệ thống giết launcher/keyboard/Chrome trước.

Đã wire trong app: `SeparationSessionController` tự gọi khi run kết thúc (mọi segment Ready, hoặc
error), một lần mỗi run qua `modelUnloaded` AtomicBoolean. Đo thật trên Pixel 9: native heap
**2021MB → 321MB**. Segment `Failed` KHÔNG tính là kết thúc — player có thể retry và cần model.

Ba động từ khác nhau: `cancel()` dừng việc, `unloadModel()` trả bộ nhớ (engine vẫn dùng được, reload
~1s), `release()` kết thúc engine (terminal).

**Vendor drift:** repo này patch `core/build.gradle.kts` để bỏ `native_fft_experiment` (cần NDK).
rsync từ project gốc sẽ ghi đè — phải áp lại, và nhớ xoá `five_stem/quantize/src/main/assets`
(126MB) + `core/src/androidTest/.../dsp/` mà rsync kéo theo.

Liên quan: [[pattern_stem_presence_two_measurements]], [[project_audio_separation]]
