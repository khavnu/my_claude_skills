---
name: pattern-fp16-mask-nan-on-silence
description: Mask model float16 (tier quantize) trả NaN ở frame im lặng tuyệt đối → segment Failed im lặng → mix phát từ ~10s; worker lib nuốt lỗi không log
metadata:
  type: pattern
---

> **ĐÃ SỬA 2026-09-29 (lib):** `finiteWeight()` trong `SpectrogramStemSeparator.applyPatchMask` (NaN → 1/n) + `Log.w` cho segment Failed (tag `StreamSeparationSession`, đặt sau guard isActive). ĐỪNG đề xuất nâng ε lúc export: lib đo ε=1e-4 lệch 233× so với fp32 vì 3% bin nhạc thật nằm dưới ngưỡng. Lần sync sau phải giữ 2 thay đổi này.

2026-09-29, sau sync lib mask model. Triệu chứng: Separate → Result → Play mix bắt đầu ở ~9.8s (= đầu
segment 1). Chỉ xảy ra với file có đầu bài im lặng tuyệt đối (mẫu = 0), cả A20s lẫn Pixel 9. Không phụ
thuộc máy hay "lượt tách thứ hai" (đã đoán sai 2 lần như vậy).

**Nguyên nhân (đã verify):** `2stems/4stems.tflite` tier quantize (float16) cho mask = NaN ở frame có
|STFT| = 0; tier original (fp32) thì không. Gần như chắc là ε = 1e-10 của Spleeter bị làm tròn về 0 khi
xuống fp16 (`convert_masks_to_tflite.py:66-72`). NaN → `WavPcmEncoder.toPcm16` ném `Cannot round NaN`
→ segment Failed → walk bỏ qua. Mọi segment có đoạn im lặng tuyệt đối đều hỏng, không riêng segment 0.

**Vì sao mất thời gian:** `StreamSeparationSession.kt:109-112` bắt Exception thành `Failed` KHÔNG log.
Dấu hiệu duy nhất trong logcat: có `SpectrogramStemSeparator ... separate(N frames)` nhưng không có
`separateSegment[i] -> 2 stems` theo sau.

**Cách kiểm trong 10 giây:** chạy `.tflite` bằng `tf.lite.Interpreter` trên máy dev với patch có frame toàn 0.
Script và báo cáo gửi lib: `docs/features/lib-sync-2026-09-28/lib-report-2026-09-29.md`.
File tái hiện trên A20s: `/storage/emulated/0/Music/AnhNhoEmNguoiYeuCu-MinhVuongM4U-14484975.mp3`,
`DungAiNhacVeCoAy-PhamAnhQuan-7564963.mp3`.

Bẫy khi thêm log chẩn đoán ở catch: đặt TRƯỚC guard `if (isActive)` sẽ in cả các "failed" giả do preempt
(SpleeterSeparationCancelledException) và do thư mục session bị xoá (FileNotFoundException), mà kết quả
của chúng vốn đã bị bỏ đi.

Liên quan: [[reference-lib-knowledge-in-repo]], [[pattern-quiet-is-not-silent]]
