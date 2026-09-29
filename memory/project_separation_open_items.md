---
name: project-separation-open-items
description: "7 việc đã biết là chưa xong của feature separation — user hoãn có chủ đích, đừng phát hiện lại rồi sửa vội"
metadata: 
  node_type: memory
  type: project
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-16T11:02:22.368Z
---

Chốt ngày 2026-09-10, user đã ghi nhận và hoãn lại (KHÔNG phải bug phát sinh, đừng "phát hiện" lại
rồi sửa vội):

**1. ĐÃ GIẢI QUYẾT (2026-09-11).** `MemoryAfterLibraryUpdateTest` tag file 73 phút có hát trên máy
(`/sdcard/Music/MusicEditor/AudioMerge/Merge_20260824_083734.mp3`) → `Vocals=0.8345`,
`undetectedStems=[]`, và test assert Vocals KHÔNG bị báo absent. Test tự skip nếu máy không có file
đó, nên vẫn nên đưa một clip có hát vào androidTest/res/raw để CI chạy được.

**2. Cảnh báo drums/bass đến muộn.** `stemLevels` của lib chỉ có khi ≥50% segment tách xong
(`MIN_MEASURED_FRACTION`), nên với file dài card cảnh báo xuất hiện giữa chừng. Cảnh báo vocals đến
sớm (tagger đọc mix, vài giây). Đúng thiết kế lib; muốn cả ba cùng lúc thì phải bàn lại.

Liên quan: [[pattern_stem_presence_two_measurements]], [[project_audio_separation]]

**3. ĐÃ XỬ LÍ (2026-09-11). Cache stem không được dọn khi rời feature.**
Đo thật trước khi sửa: tách file 73 phút / 4 stems để lại **4.017 MB**, chỉ bị xoá khi lần tách SAU
bắt đầu (`clearPreviousInstanceDirs` trong `buildEngine`).

Đã thêm `clearWorkspace()` xuyên các tầng, gọi trong `SeparationSessionController.shutdown()`
**sau** `release()` (xoá thư mục engine đang mở sẽ làm run ghi vào hư vô). Khoá bằng
`ClearWorkspaceOnLeavingTest` (4 test, gồm cả hai chiều: stop/cancel KHÔNG được xoá) và
`WorkspaceIsClearedOnLeavingTest` trên máy thật — 6201 KB → 0.

Công thức dung lượng (đã kiểm chứng, xem `SeparationStorage.kt`):
`độ dài(giây) × 176,4 KB × (số stem + 1)` — ~53 MB mỗi phút audio ở 4 stems.

Hai chỗ nên dọn: khi rời feature (`shutdown()`) và khi cancel. **Cẩn thận:** `save()` stitch từ chính
những file này, nên không được dọn khi user mới chỉ rời màn result sang màn lưu.

Liên quan: [[pattern_unload_model_native_heap]]

**4. `ToolDestinationHint(showsSeparationLimits: Boolean)` cần refactor (2026-09-11, user hoãn).**
Cờ Boolean bắt một component dùng chung phải biết "separation" là gì. User đề xuất đúng hướng:
truyền **label + list các hint** vào để `LimitsHint` hiển thị, khi đó component không cần biết tool
nào và tái dùng được cho mọi giới hạn.

`LimitsHint(label, tooltipTitle, tooltipBullets)` vốn đã tổng quát sẵn — chỉ có chỗ gọi là cứng.
Hiện `limitationDurationMs()`/`limitationSizeBytes()` đều trả `NO_LIMIT` nên hint không hiện icon,
vì vậy chưa gấp.

**5b. ĐÃ ĐO LẠI (2026-09-15) — bảng seed viết lại, vẫn còn thiên cao ~33% ở nhánh 2-stem.**
`SeparationPace.kt` giờ có HAI bảng độc lập, `TWO_STEM_FRACTION` đã xoá: tỉ lệ 2/4 stem là 0.47
trên Pixel 9 nhưng 0.94 trên Realme, vì Pixel nghẽn ở inference (decode 68s) còn Realme nghẽn ở
decode (278s) — không hằng số nào nằm đúng giữa hai máy đó.

Nhưng chính ngày đo bảng, chạy lại cùng file cùng máy ra số THẤP hơn bảng: 4-stem **279 / 298 / 301**
(bảng ghi 343), 2-stem **121** (bảng ghi 161). Dải dao động thật trên một máy là ±10%, và bảng cố ý
lấy đầu cao ("overshoot costs patience, undershoot costs trust"). Riêng 2-stem lệch 33% thì hơi
nhiều. KHÔNG gấp: `blendPace()` thay seed bằng số thật ngay sau lần chạy đầu.

**5c. ETA chưa gồm thời gian Save (2026-09-15, user quyết KHÔNG gộp).**
ETA màn config = thời gian TÁCH. Save tốn thêm ~48s (4 stem, file 15'53", MP3) và nằm ngoài lời hứa.

Đã cân nhắc gộp và bác, lý do: ETA phải trả lời "bao giờ nghe được", không phải "bao giờ có file" —
hai mốc cách nhau một khoảng do chính người dùng quyết (preview/edit bao lâu tuỳ họ). Gộp vào sẽ sai
với người preview trước khi Save (nghe được sớm hơn con số hứa), sai với người chỉ save 1 stem
(~12s), và sai với người bật Mix (encode 1 lần).

Preview KHÔNG rút ngắn Save: 48s đó là stitch + encode trên file full-length, chạy sau khi tách xong.
Preview chỉ dời chỗ chờ (từ spinner sang nghe thử), không giảm tổng.

Chỗ thật sự lệch kỳ vọng là **dialog Save dùng chung một dòng chữ cho cả hai stage** — bấm Save sớm
sẽ thấy "Saving stems…" suốt mấy phút trong khi đang chờ TÁCH. User đã quyết giữ nguyên, không đổi
chữ, không hiện thời gian.

**5. Seed pace thiên CAO ~58%, cần đo lại (2026-09-11, ĐÃ XỬ LÍ ở mục 5b).**
Sau khi sửa `ENGINE_PARALLELISM` 1→2 (xem [[pattern-short-file-hides-serialization]]), mọi seed trong
`SeparationPace.kt` (376 / 607 / 949 / 3144) thành lỗi thời — chúng đo khi decode còn chặn inference.

Đo thật Pixel 9, file 15'53" 2-stem: **161 ms/audio-sec** (trước fix 208). Màn hình hứa 4.0 phút cho
việc mất 2.6 phút.

Muốn sửa tận gốc phải **đo 4-stem thật** bằng file ≥10 phút, KHÔNG suy ngược bằng phép chia — hệ số
`TWO_STEM_FRACTION = 0.58` cũng đo trong điều kiện cũ nên cũng đáng ngờ. Suy ngược chỉ để tham khảo:
pace ngắn hạn 2-stem Pixel 9 ~138 thay vì 218 → bậc 10 GB có thể ~238 thay vì 376.

Ba bậc RAM còn lại (7/5/0 GB) cần cắm lại Z Flip 3 / Realme RMX3710 / Samsung M20. `blendPace()` tự
chỉnh sau lần chạy đầu trên máy thật, nên chỉ lần đầu người dùng thấy số thổi phồng — không gấp.

**6. Hai việc nhỏ đã nêu, chưa đụng (2026-09-11).**
- `pureDecodeTime=49875ms` cho 953s audio ≈ **19x realtime**, chậm hơn mức thường của MediaCodec MP3.
  Giờ decode chạy song song nên không chặn ai, nhưng trên máy yếu có thể tụt sau playhead.
- Log `SeparationTiming` đang ở `Timber.i` nên sẽ nằm lại trong bản release. Giữ để chẩn đoán ngoài
  thực địa hay hạ xuống `d` — chưa quyết.

**7. ĐÃ GIẢI QUYẾT (2026-09-16) — waveform giờ vẽ đúng bản trộn.**
Cách làm: **envelope xấp xỉ**, không trộn thật. Mỗi stem giữ một mảng 500 peak
(`ENVELOPE_POINT_COUNT`, khớp `WAVEFORM_SAMPLE_COUNT` của mọi màn khác), đo từng chunk ngay khi nó
Ready, rồi cộng theo volume lúc vẽ — xem [[pattern_envelope_approximation_for_live_mix]].

Cả 3 cái giá lúc hoãn đều tránh được: (a) không phải đợi tách xong, sóng mọc dần từ trái, ô chưa đo
đọc 0; (b) tick/volume chỉ cộng lại 500 số, không đụng file; (c) khớp `StemMixer` vì nó cộng tuyến
tính `left += weight * sample` rồi clamp — đúng phép `blendEnvelopes` làm.

**Còn chưa đúng:** fade in/out không phản ánh vào hình (blend chỉ tính `volume`, chưa tính `fade`).
Và `MixPreviewState.isLoadingWaveform` giờ là cờ chết, luôn `false` — đã nêu, user chưa quyết dọn.

