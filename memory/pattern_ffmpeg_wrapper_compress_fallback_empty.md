---
name: pattern-ffmpeg-wrapper-compress-fallback-empty
description: Lib ≤(6) VideoCompressor trả Success + file 0 byte khi re-encode to hơn nguồn và stream-copy fallback fail (WMV2→mp4); (7) giữ bản re-encode; app có guard file rỗng
metadata:
  node_type: memory
  type: project
  originSessionId: d6752420-e93a-4f84-ba77-d391c305b1bf
  modified: 2026-11-02T07:10:13.384Z
---

Ticket #499 (2026-11-02): Compress video file WMV2 (`codec_wmv2.avi`) → "Lưu thành công" nhưng 00:00 | 0 KB.

Chuỗi: lib giờ DECODE được WMV2 (trước kia Pixel 9 báo -1128613112 decoder not found → UnsupportedVideoCodec, nay không còn). Re-encode ra 391 KB ≥ nguồn 308 KB → `VideoCompressor` (lib) "keeping the original (stream copy)" → `-c:v copy` WMV2 vào mp4 fail -22 → lib (6) vẫn trả Success, file rỗng. Lib (7) (`ffmpeg-wrapper-release (7).aar`, áp 2026-11-02) log "stream copy not usable ...; keeping the re-encoded output" → file hợp lệ.

**Why:** chỉ nhánh FFmpeg dính (máy có hardware AVC encoder, API ≥ 28). Emulator dùng c2.android → nhánh Media3, Media3 bỏ 2 track và báo "Asset loader error" đúng, nên emulator mặc định KHÔNG tái hiện được.

**How to apply:**
- Tái hiện nhánh FFmpeg trên emulator: tạm sửa `MediaCodecCompressEngineDataSource.compressEngine()` thành `CompressEngine.Ffmpeg` (màu magenta kệ), nhớ `git checkout` file đó trước khi commit.
- App có guard `DefaultVideoProcessingRepository.withEmptyOutputAsFailure` (Success + sizeOf==0 → ProcessingFailed) cho cả 3 tool video; thấy toast "Couldn't process the video" là guard bắt được lib báo sai.
- So 2 bản AAR: unzip → `javap -c -p -cp cls com.ffmpeg.wrapper.VideoCompressor`, diff các dòng `// Method|String` (bản 7 thêm File.renameTo).
- Sau khi thay AAR, build có thể fail KSP `WorkerAssistedFactory ... Invalid return type: T` — chạy lại là xanh (cache tăng dần).

Liên quan: [[pattern-ffmpeg-wrapper-hardware-encoder]], [[pattern-ffmpeg-wrapper-video-vfr]].
