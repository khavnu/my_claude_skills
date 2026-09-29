---
name: project_chunk_join_seek_bug
description: "Stream chunk join 'không liền mạch' = MediaExtractor.seekTo trả PTS TỔNG HỢP, segment lệch tới 260ms; đã thay bằng SourcePcmCache decode tuần tự — đừng quay lại decode từng segment"
metadata:
  type: project
---

Fix 2026-09-08, user xác nhận bằng tai + đo với ground truth.

**Đừng bao giờ quay lại decode từng segment bằng `MediaExtractor.seekTo`.** PTS sau seek là số
**tổng hợp từ chính yêu cầu**, không đo từ dữ liệu: mọi segment báo `lead=44100` chính xác, trong khi
audio thật nằm rải từ **−259,6ms đến +129,8ms** so với vị trí đáng lẽ (dao động 389ms). Dấu hiệu nhận
biết: frame MP3 44.1kHz = 26122,449µs nên mốc seek 14.000.000µs KHÔNG THỂ rơi đúng biên frame — một
đáp số tròn trịa chính là bằng chứng nó bịa. Segment 0 (không cần seek) là cái duy nhất đúng +0,0ms.

Đã thay bằng `SourcePcmCache`: decode **một lần tuần tự từ 0** ra file PCM không header, segment đọc
theo offset frame. Frame N = frame N theo cấu trúc. Sau fix: **+0,0ms cả 15 mối nối**, r=0,986-1,000.

**Fill chạy NỀN, không fill trước** — decode 227s mất 27,7s trên máy; fill trước sẽ cộng hết vào
time-to-first-audio. `readRange` treo tới khi đủ frame; segment 0 chỉ cần 16s đầu (~2s).

**Bug thứ hai cùng đợt:** `separateFramesToStems` cache tail là 93ms CUỐI của chính segment thay vì
93ms SAU khi nó kết thúc → ~93ms phát 2 lần. 3 test crossfade cũ vẫn xanh suốt vì fake trả **một hằng
số cho cả lát cắt** — làm cửa sổ đúng và cửa sổ sai giống hệt nhau về số.

**How to apply:**
- Fake trong test phải mã hoá được **vị trí nguồn** (kênh trái) lẫn **lần gọi** (kênh phải), nếu không
  nó không phân biệt được lỗi lệch thời gian.
- `SourcePcmCache` nhận nguồn frame qua tham số (không hardcode MediaCodec) → test được trên JVM.
  Hai bug của chính nó do test bắt, máy không bắt: (1) `StateFlow.first { … || flowKhác.value }`
  không đánh giá lại khi chỉ flow kia đổi → segment cuối treo; phải `combine`. (2) `throw` lại lỗi
  trong `launch` trên scope không có `CoroutineExceptionHandler` → **crash cả process** trên Android.
- **ĐỪNG sửa lệch timing bằng seek.** Một cú seek nhóm làm cả 4 player dừng rồi khởi động lại lần lượt
  = im lặng thật; thử re-sync cưỡng bức thì nó tự kích hoạt 8 lần, drift leo lên 528ms. Đã rollback.
- **Lệch khởi động giữa các player: đã đo 29 mẫu, KHÔNG phải 45ms cố định.** Hai cụm: 2-9ms (12 mẫu)
  và 33-49ms (16 mẫu), đuôi 79ms và 239ms. **Stem nào dẫn là NGẪU NHIÊN** (đã thấy vocals, drums,
  bass) — nên giả thuyết "vòng lặp `applyPlayWhenReady` tuần tự gây ra" là SAI: nó khớp độ lớn nhưng
  không khớp thứ tự. Media3 không có primitive khởi động đồng bộ; mỗi ExoPlayer bắt đầu khi AudioTrack
  của nó sẵn sàng. Một khi phát rồi thì cố định (2 stem lệch 43ms cùng tiến đúng 2003ms/2s).
- **`DRIFT_THRESHOLD_MS` 80 → 150** (cả hai player). 80 nằm đúng chỗ tệ nhất: đủ cao để bỏ qua ca 40ms
  thường gặp, đủ thấp để cái đuôi kích hoạt → thỉnh thoảng seek → gap thật. 150 không bao giờ nổ trong
  dải 2-49ms, vẫn bắt loại 239ms.
- Phần dư 36-79ms **chưa sửa và không sửa được ở cú start**. Cách duy nhất không tốn gap là nudge bằng
  tốc độ (cho player chậm chạy nhanh 1-2% vài giây). Chưa làm vì KDoc `setPlaybackSpeed` ghi Sonic
  re-prime khi đổi tham số và tự nó làm lệch — phải đo ngân sách sai số của chính cách bù trước.

Playbook đo đạc đã viết thành `audio_stem_split/docs/DIAGNOSING-AUDIO-BUGS.md` (đi theo lib).
Xem thêm [[project_fade_merge_export]], [[project_playback_test_flakiness]].
