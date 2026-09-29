---
name: reference-waveform-data-not-normalized
description: AudioProcessor.getWaveformData trả biên độ tuyệt đối (không normalize) — dùng được để phát hiện file im lặng
metadata:
  type: reference
---

`AudioProcessor.getWaveformData(path, count)` (ffmpeg-wrapper.aar) trả biên độ **tuyệt đối**, KHÔNG
peak-normalize. Đo thật trên máy: file WAV toàn zero → peak ≤ 0.001; file nhạc thật → peak > 0.001.

Nhờ vậy `extractWaveformFromPath` dùng được cho "no audio detected" (spec 18.2) mà không cần thêm
model hay decode riêng. Ngưỡng: `SILENCE_PEAK_CEILING = 0.001f` (~-60 dBFS) trong
`domain/model/SilenceDetection.kt`, khoá bằng `SilentFileWaveformTest` (androidTest, tự sinh file
WAV im lặng).

**Đừng dùng `AudioTagger`/YAMNet của lib cho việc này** — nó trả lời câu hỏi khác (stem nào vắng
mặt, phục vụ cảnh báo "No vocals in this audio"): một bản instrumental cũng cho
`undetectedStems = {vocals, drums}`, không phân biệt được với file im lặng.

Liên quan: [[project_audio_separation]], [[reference_lib_knowledge_in_repo]]
