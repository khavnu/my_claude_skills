---
name: pattern-envelope-approximation-for-live-mix
description: "Vẽ waveform cho bản trộn chưa thành file: mảng RMS riêng từng stem, cộng CÔNG SUẤT lúc vẽ + gain cố định 2.0 — không phải peak, không cộng biên độ"
metadata: 
  node_type: memory
  type: project
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-18T08:44:48.922Z
---

Bản trộn của màn Separation result không tồn tại thành file cho tới lúc Save (player ghép live), nên
không có gì để đọc mẫu. Giải pháp (2026-09-16): **xấp xỉ bằng envelope**, không trộn thật.

**Mảng riêng từng stem, KHÔNG phải một mảng tổng.** Đây là chỗ dễ sai nhất — một mảng tổng đã cộng
sẵn thì lúc user untick hoặc kéo volume không tách ngược ra được phần của stem đó. Chi phí giữ riêng
là 4 × 500 × 4 byte = 8 KB, không đáng để tối ưu.

## Công thức: RMS + cộng công suất + gain cố định

```
displayed[j] = min(1, sqrt(Σ (rms[stem][j] × volume[stem])²) × 2.0)   // chỉ stem đang tick
```

Ba chi tiết, cả ba đều là kết quả sửa sau khi nhìn màn hình thật:

1. **RMS, không phải peak.** Một ô (slot) phủ ~0.5 giây ≈ 22.000 frame. Mẫu to nhất trong nửa giây
   nhạc gần như luôn xấp xỉ mẫu to nhất cả bài → envelope peak đã phẳng và cao ngay với MỘT stem,
   chưa cần cộng 4 cái.
2. **Cộng công suất, không cộng biên độ.** Cộng biên độ vẽ ra khối đặc full height cả bài
   (`0.5+0.6+0.4+0.5 = 2.0` → clamp 1.0 ở gần như mọi ô).
3. **Gain 2.0 cố định** để dùng hết chiều cao khung (RMS nhạc thường ~0.2 → vẽ thật chỉ chiếm 1/5).

## Dự đoán sai đã ghi nhận (đừng lặp)

**"Khớp công thức `StemMixer` là điều kiện sống còn" — SAI.** Mixer làm `left += weight * sample`
cho các mẫu ở CÙNG MỘT THỜI ĐIỂM. Một ô ở đây tóm tắt 22.000 thời điểm, và 4 stem đạt cực đại ở
những thời điểm khác nhau bên trong ô đó. Cộng 4 bản tóm tắt là chặn trên lỏng tới mức vô dụng.
Cộng công suất mới đúng mô hình, vì tách stem chính là việc làm các stem KHÔNG tương quan — tín hiệu
không chung dạng sóng thì công suất cộng còn biên độ không. Bài học: công thức đúng cho MẪU không tự
động đúng cho THỐNG KÊ CỬA SỔ của mẫu.

**Từ chối gain cố định chỉ vì thử một giá trị — SAI.** Bác bỏ dựa trên x2.5 (clip 58% ô), trong khi
x2.0 clip 0%. Đo: 4 bài master khác nhau (1 lofi + 3 loud), ở x2.0 median height 0.34..0.84, clip 0%
cả 4; x2.2 clip 21% một bài; x2.5 clip 58%.

**Chuẩn hoá theo từng bài (chia cho ô to nhất) — đã build rồi BỎ.** Cho ra chiều cao gần như y hệt
(0.34..0.79) nhưng có một bộ phận động: số chia là ô to nhất ĐO ĐƯỢC TỚI LÚC ĐÓ, mà tách thì đo dần
từng chunk → hình vẽ co lại 22-65% khi đoạn to hơn tới. Gain cố định không có bộ phận đó. Câu hỏi
của user lộ ra lỗi này: *"RMS của full-mix ở volume 1 là lấy từ chunk 1 đấy à"*.

## Những phần còn đúng nguyên

**Đo từng chunk khi nó Ready, không đợi xong.** `SegmentProgress` đã có `startUs`/`endUs` +
`totalDurationUs` → map thẳng sang dải ô. Ô chưa chunk nào chạm đọc 0 và vẽ phẳng, nên sóng mọc dần
theo tiến độ tách. Tích luỹ đặt ở `@Singleton` trên application scope, không ở ViewModel: run sống
lâu hơn màn hình, rời result rồi quay lại không phải đọc lại từ đầu.

**Đọc WAV thẳng bằng `short`, đừng dùng `getWaveformData`.** File segment do chính lib ghi nên format
biết chắc (16-bit PCM, little-endian, `WavPcmEncoder`). Một run có tới 480 file; `getWaveformData` là
blocking JNI không cancel được — thủ phạm ticket #273 — nên gọi hàng trăm lần là hàng trăm cơ hội
wedge, và không bỏ dở được khi user rời màn. Tự đọc thì cancel ở mỗi buffer, và không allocate
FloatArray mỗi frame như `WavPcmDecoder`.

**Ô 0 mơ hồ nên phải kèm mask.** `0` nghĩa là "chưa tách tới" HAY "chỗ này im lặng" — hai thứ phải vẽ
khác nhau (nét đứt vs đường phẳng thật). `BlendEnvelope` giữ `perStem` + `measuredSlots` đi CÙNG NHAU
trong một object, không phát thành 2 flow, để UI không ghép envelope mới với mask cũ trong một frame.
Vùng chưa đo KHÔNG chỉ là phần đuôi: seek làm engine tách segment được seek tới trước, nên lỗ có thể
nằm giữa bài → phải mask theo ô, không dùng tỉ lệ tiến độ.

**Vẫn thiên cao, vẫn chấp nhận:** cộng công suất là chính xác chỉ với tín hiệu hoàn toàn không tương
quan, tách stem chỉ tiệm cận chứ không đạt. Phương án đo thật là trộn thật, mà `StemMixer` mất 99
giây cho 4 stem của file 15'53".

Liên quan: [[project_separation_open_items]], [[pattern_blocking_jni_timeout_detached]],
[[reference_waveform_data_not_normalized]], [[pattern_save_pipeline_bottleneck]]
