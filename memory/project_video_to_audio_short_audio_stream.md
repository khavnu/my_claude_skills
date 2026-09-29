---
name: project_video_to_audio_short_audio_stream
description: Ticket
metadata: 
  node_type: memory
  type: project
  originSessionId: f55fafc1-85e9-4fac-bf70-774937a5c89a
---

Ticket #270 "[V1.0-QC] Video to Audio - Sai duration + lỗi khi chọn End Time ở cuối file" là **báo nhầm của tester**, trùng ticket **#215** (đã fix + Closed ở V1.0.7).

**Nguyên nhân kỹ thuật (đã verify bằng ffprobe trên file AZ Recorder thật):**
Video quay bằng AZ Screen Recorder có audio stream **vào trễ ~0.25s** (leading empty edit / elst: `media time -1`). Nên:
- Container/video-track duration (MediaMetadataRetriever → `videoDurationMs`) = VD 10.077s
- Audio **media** duration (ffmpeg `getInfo`/`getAudioDurationMs` → `extractedAudioDurationMs`) = 9.822s — **ngắn hơn**
- Extract (cả `extractAudioOriginal` copy lẫn `extractAudioCustom` re-encode) đều cho ra file = audio media duration (~9.82s, drop 0.25s silence đầu)

**Vì sao KHÔNG phải bug:**
- Play Result hiển thị 9.822s (audio thật) thay vì 10.077s (video) là **đúng** — không thể trích xuất audio không tồn tại.
- Thông báo "không tìm thấy audio trong phần đã chọn" (`no_audio_stream_found_in_selected_section`) khi kéo selection vào vùng đuôi không có audio = **behavior chủ đích từ fix #215** ("nếu selection không có audio → hiển thị thông báo").

**Quyết định:** KHÔNG đụng code. Option "cap crop bound theo audio duration" chỉ là thay đổi UX, không cần.

**Pitfall khi điều tra:** dễ đoán nhầm "audio kết thúc sớm" — thực tế audio **bắt đầu trễ** (offset đầu). Audio END ≈ video END (10.074 ≈ 10.077) nên nhìn tưởng dài bằng nhau, nhưng tổng audio (9.822) < video (10.077).

Code liên quan: `LocalVideoMetadataDataSource` (tính `audioStreamDurationMs` cho cờ `hasAudio`), `VideoToAudioEditorViewModel.ensureExtracted` (`getAudioDurationMs`, check `==0L` → error), `AudioEditorRepositoryImpl.extractVideoToAudio` (2-pass extract + split). ffmpeg wrapper là AAR black-box (`libs/ffmpeg-wrapper.aar`). Liên quan họ "đuôi file lỗi" với [[pattern nếu có]] nhưng #263 chỉ vá tầng playback ExoPreviewPlayer, khác tầng.
