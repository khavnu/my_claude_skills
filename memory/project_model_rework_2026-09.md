---
name: project_model_rework_2026-09
description: 2026-09-25 cả 6 tier model đổi sang average-mask + bỏ 1 output (suy bằng phép trừ) + chunk 524.288; quantize = float16 chứ không còn int8; AAR 37 builtin
metadata:
  type: project
---

Ship 2026-09-25. Cả **6 tier** model đã re-export. Đừng đề xuất lại ba thứ này, và đừng ngạc nhiên
khi thấy `OUTPUT_TENSORS` ít hơn số stem.

**Ba thay đổi, đo trên Pixel 9:**
- `mask_extension="average"` — dải trên 11.025 Hz trước đây bị **xoá sạch**, nay giữ đủ (residual
  99,99% → 0,00%). Tự nó **tốn** ~7% thời gian.
- Bỏ một output khỏi model, suy lại bằng `nguồn − Σ stem khác`. **Chính xác tuyệt đối** (1,00 LSB,
  SNR 92,3 dB) *vì* mask cộng lại bằng 1 — nên nó **phụ thuộc** vào `average`. Suy stem:
  `accompaniment` cho 2-stem, `other` cho 4/5-stem.
- Chunk 1.323.000 → **524.288** = đúng một patch của model. Thêm **một mẫu** vào 1.048.576 mất
  +712 ms và +271 MB, vì nó ép thêm một patch.

Kết quả: 2-Stem Original −27,4% thời gian / −56,0% RAM; 4-Stem Original −23,2% / −51,4%;
4-Stem Quantized −15,7% / −43,5%. Model trong APK 721,3 → 649,1 MB.

**Tier `quantize` nay là float16, KHÔNG phải int8.** Dynamic-range int8 bất khả thi: kernel
`TRANSPOSE_CONV` của TFLite 2.14 từ chối hybrid (`weights->type != input->type`), mà decoder U-Net
toàn TRANSPOSE_CONV. Nghi do lệch converter TF 2.21 vs runtime TF 2.14 — chưa kiểm chứng.

**AAR: 37 builtin** (thêm `DEQUANTIZE` cho float16). Rebuild lần 2 chỉ mất vài chục phút vì host
tooling LLVM/MLIR đã ở trong cache Bazel; scope gồm **10 model** nên rollback là copy file.

**How to apply:**
- `OUTPUT_TENSORS` giờ là **tập con** của stem engine trả về. Luôn dùng `*Config.ALL_STEM_KEYS` làm
  `stemKeys`; dùng `OUTPUT_TENSORS.map { it.key }` sẽ compile sạch, chạy không lỗi, **thiếu 1 stem**.
- Tên tensor bị đánh số lại **mỗi lần convert**; tên sai không throw mà đổi stem cho nhau. Verify
  bằng tương quan với bản cũ (đường chéo >0,9, ngoài đường chéo <0,2).
- Có **12** provider trong DI chứ không phải 6 — `StreamStemSplitEngine` dựng separator riêng, phải
  truyền `remainderStemKey` cho cả nó. Xem [[project_streaming_phase2_shipped]].
- Đo hiệu năng: **in số chunk** trong mỗi lượt. Một lần đo hỏng vì file override
  `tmp_chunk_frames.txt` còn sót trên máy làm baseline đã có sẵn chunk mới (−1,8% thay vì −15,7%).
  Instrumentation đọc trạng thái từ thiết bị sống lâu hơn thí nghiệm sinh ra nó.
- `pkill -f "<pattern>"` khớp cả shell đang chạy nó nếu pattern nằm trong dòng lệnh — đã tự giết
  mình 2 lần (exit 144). Lọc theo PID và bỏ qua `$$`.
- Tải file lớn: nhiều `curl` chạy chồng lên cùng một file làm archive hỏng mà kích thước trông
  *lớn hơn* `content-length`. Dọn theo PID rồi tải đúng một tiến trình.

- **Streaming đã verify** (bài 5:09, 20/20 segment, Σstem vs nguồn 0,00000%) nhưng **chưa được căn
  patch**: segment = 749.700 frame = 1,43 patch → đệm lên 2. Một patch trọn = 11,89s, nằm giữa 10s
  (đã loại) và 15s (đang dùng) — ứng viên đáng đo, xem [[project_stream_chunk_10s]].
- **So audio khi input là mp3 phải bù lag trước.** ffmpeg và MediaCodec xử lý encoder delay khác
  nhau: đo ra **184% residual**, bù 529 mẫu (12,00 ms) thì về 0,00000%. Input WAV thì lag = 0 nên
  bẫy không lộ. Nhớ lọc `.trashed-*` khi glob thư mục export.

Chi tiết đầy đủ: `docs/PERFORMANCE-EXPERIMENTS.md`.
