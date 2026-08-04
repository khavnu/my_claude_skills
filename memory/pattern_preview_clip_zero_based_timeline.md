---
name: pattern_preview_clip_zero_based_timeline
description: ExoPlayer ClippingConfiguration cắt theo timeline 0-based của file đã extract; neo clip start vào source PTS (cropStart) làm preview không play khi start vượt nửa selection
metadata: 
  node_type: memory
  type: project
  originSessionId: 49c44c9b-dec7-4278-a1c7-ecce95ae1501
---

**Bug (Video to Audio):** start > duration/2 thì không play được preview (waveform/result view).

**Root cause:** File temp đã extract chỉ chứa đoạn crop, timeline ExoPlayer thấy là **0-based**, dài `segLen = cropEnd - cropStart`. `preparePreviewPlayer` từng đặt clip `AudioSegment(cropStartMs, cropStartMs + segLen)` cho format MP4 (tưởng file giữ source PTS theo ticket #118). ExoPlayer `ClippingConfiguration.setStartPositionMs` cắt trên `[0, segLen]` → khi `cropStart >= segLen` (⟺ `cropStart >= cropEnd/2`, ≈ `duration/2` khi cropEnd = full) cửa sổ clip nằm ngoài file → clip rỗng → im lặng không play. Dưới ngưỡng thì play nhưng sai vùng (chỉ phần đuôi).

**Fix:** luôn `AudioSegment(0L, durationMs)` bất kể container. File temp đã là đoạn đã cắt → phát nguyên `[0, segLen]`.

**Why:** Ticket #118 (MP4 giữ PTS bắt đầu ở cropStart) chỉ đúng cho file **SAVE**, không áp cho preview clip vốn đọc file temp 0-based.

**How to apply:** Khi clip/seek file đã trích xuất (đã cắt sẵn) bằng ExoPlayer ClippingConfiguration hoặc seekTo — luôn tính theo timeline 0-based của chính file đó, không dùng offset PTS/cropStart của nguồn gốc. Ngưỡng lỗi "quá nửa" là dấu hiệu clip window vượt EOF. Liên quan [[feedback_coroutine_finally_ui_state]].
