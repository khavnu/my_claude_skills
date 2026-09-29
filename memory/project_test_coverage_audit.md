---
name: project_test_coverage_audit
description: "Audit độ phủ test toàn repo: :presence:yamnet 0→8, repository :app 0→12; và một defect mergeStems chưa sửa"
metadata:
  type: project
---

Đã audit độ phủ test mọi module (2026-09-07). Tổng: `:core` 109, `:playback` 36, `:presence:core` 12,
`:presence:yamnet` **8 (trước 0)**, `:app` **154 (trước 142)**.

**Cách audit — quan trọng:** đối chiếu tên class với tên FILE test là **SAI** (báo `WavPcmEncoder`
chưa test trong khi test của nó tên `WavPcmEncoderLimitTest`). Phải kiểm tra **class có được test nào
tham chiếu tới không**.

**`:presence:yamnet` từng không có dòng test nào** — lỗ hổng đáng nhất. `YamnetConfig` khai nhãn
AudioSet dạng chuỗi; `PresenceScorer` có `require()` nhưng chỉ nổ **lúc khởi tạo trên máy thật**.
Không gì đối chiếu với CSV đang ship → typo vẫn build/cài được và cho **số 0 vĩnh viễn** cho stem đó.
8 test JVM thuần đọc thẳng `yamnet_class_map.csv` biến chuyện đó thành lỗi build; pin luôn ngưỡng
(vocals 0.085 / drums 0.006), `Speech` không tính là hát, chỉ 2 stem đo được mới khai, sampleRate 16k.
Lưu ý parse CSV phải tôn trọng dấu nháy (`"Child speech, kid speaking"`) — split ',' thô sẽ cắt cụt
đúng những tên đó và test vẫn xanh.

**`DefaultStemSplitterRepository` 0→12.** Chỗ đáng nhất: `IllegalArgumentException` có chữ "cancel"
trong message → `Cancelled`, không phải `InferenceFailed` (TFLite ném đúng kiểu đó khi
`setCancelled(true)` ngắt `Invoke`; message là tín hiệu duy nhất). Test cả hai chiều của nhánh đó.

**DEFECT ĐÃ SỬA (2026-09-07, user yêu cầu):** `mergeStems` chỉ catch `IllegalStateException`, nhưng
`StemMixer.merge` có `require(sources.isNotEmpty())` → ném `IllegalArgumentException` → list rỗng
**crash**. Fix bằng cách **validate input ở boundary** (`if (weights.isEmpty()) return Failure`), KHÔNG
nới catch — nới catch sẽ nuốt luôn lỗi lập trình từ sâu trong mixer. Có test + mutation-verified.
`StemMixer` chỉ có đúng 2 đường ném: dòng 39 `require` (IAE, đã guard) và dòng 50 `check` (ISE, đã
catch sẵn).

**Hai bẫy setup:**
- `TemporaryFolder.root` đọc trong **field initialiser** → "the temporary folder has not yet been
  created". Phải dựng trong `@Before`.
- `StemSplitEngine` có **2 overload `separate`** (Uri và PCM) → MockK không suy được từ `any()` trần.
  Phải ghi kiểu tường minh: `any<Uri>()`, `any<File>()`, `any<(Float, Float) -> Unit>()`.

**Cố ý để trống:** `OnnxAudioTagger`/`MediaCodecPcmDecoder` (test chúng = test ORT/MediaCodec, không
có seam), `MixDecoder` (chỉ tới được qua `MediaExtractor`), `DefaultTrackPresenceRepository` (34 dòng
delegation), DI/theme/navigation.

Smoke script cho device: `.superpowers/sdd/2026-09-04-stream-chunk-size/bench/smoke.sh` — chạy đủ 4
đường (launch, batch, streaming fill, playback) và báo *cái gì đã xảy ra* chứ không chỉ "không crash".

Ledger: `.superpowers/sdd/2026-09-07-production-test-gaps/`. Liên quan: [[project_playback_tests]].
