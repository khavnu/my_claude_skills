---
name: project_fade_merge_export
description: Fade từng stem + gộp về MỘT operation merge (N=1 = lưu 1 stem) + export ra Music/AudioSeparation — shipped 2026-09-08; đừng đề xuất lại API saveStem riêng
metadata: 
  node_type: memory
  type: project
  originSessionId: e0e87c8a-7800-4c48-8018-92b52653531d
  modified: 2026-09-08T02:51:49.724Z
---

Shipped 2026-09-08, verify xong trên máy thật cả hai màn hình (Stem Splitter batch + Streaming).

**Một operation duy nhất, đừng thêm cái thứ hai.** `StemMergeRepository.merge(weights,
outputFileName, onProgress)` đứng sau cả nút "Lưu stem" từng dòng lẫn nút "Gộp lại" trên **cả hai**
màn hình. Lưu 1 stem = N=1, lưu mix = N=all. Bản đầu có `mergeStems()` + một `saveStem()` riêng
nhận `Map<String, StemSaveSetting>` → đã **xoá cái thứ hai**: nó chỉ là cái này với list ngắn hơn,
tức hai code path buộc phải đồng ý về weight/fade/encode mãi mãi mà caller không lợi gì. Doc comment
trong repo đã ghi rõ điều này — nếu sau này thấy "cần API lưu 1 stem" thì đó là N=1, không phải API mới.

**Fade:** `gain(t) = clamp(min(t/fadeIn, (duration-t)/fadeOut, 1), 0, 1)`, mặc định 10s/10s, bake vào
sample. `FadeEnvelope` ở `:core` và một **bản copy y hệt** ở `:playback` — `:playback` là module lá
(không `project(...)`) để consumer chỉ muốn phát không bị kéo TFLite theo. Hai bản ghim bằng **MỘT file
golden dùng chung** `audio_stem_split/shared-test-resources/fade-golden.tsv` (gắn vào test source set
mỗi module bằng `resources.srcDir`) — trước đó là hai bảng chép tay và **chúng không ghim gì cả**:
sửa `:core` kèm sửa bảng của `:core` thì cả hai module vẫn xanh.
`fit()` thu nhỏ cặp fade quá dài (giữ tỉ lệ) thay vì để `min()` cắt đỉnh xuống 0.625.
`fadeIn <= 0` phải trả `1f` — `0f/0f` = NaN, `min` lan NaN, sample NaN ghi vào file **không throw**.
Trong `StemMixer` phải dùng frame **tuyệt đối** (`chunkStartFrame + index`), đọc `index` là fade
restart mỗi 30s im lặng.

**Export:** `MediaStoreAudioExportRepository.exportToMusic()` → `Music/AudioSeparation/`. API 29+
không cần permission cho media của chính app; dưới Q trả `ExportUnsupported`. `IS_PENDING` 1→0 quanh
lúc ghi. Báo lỗi **tách rời merge** — file merge vẫn tồn tại dù publish fail.

**How to apply — cách verify audio đã bake đúng:** kéo file từ máy về, so **từng sample** với stem
nguồn chưa fade qua đúng công thức. Kết quả đạt: worst 1 LSB, 0 frame lệch >1 (batch 230s; stream
vocals/drums/mix 4 stem). **Luôn chạy kèm dòng đối chứng**: nếu KHÔNG áp fade thì sai lệch sẽ là
29.408 LSB. Một phép verify không thể fail thì không chứng minh gì.

**Bẫy đã dính, sẽ dính lại:**
- **numpy cộng mảng `int16` trong `int16`** → tràn âm thầm. Lần đo mix đầu báo 24.586 frame lệch,
  worst 65.535 (lật dấu full-scale) trông y hệt wraparound trong encoder — nhưng app clip đúng từ
  đầu, chính phép đo mới sai. Cast float64 TRƯỚC khi cộng, và bật `np.seterr(all='raise')`.
  Nguyên tắc: **phép đo trên máy tố cáo code đã ship + đã test một lỗi cơ bản → nghi phép đo trước.**
- **`uiautomator dump` có HAI kiểu nói dối, đã dính cả hai:**
  1. *Chỉ chứa node đang hiện trên màn hình.* Tưởng save bên stream treo mấy phút; footer "Đã lưu vào
     Music/…" nằm dưới mép.
  2. *Khi UI animate liên tục thì nó FAIL* — `ERROR: could not get idle state` — và **để nguyên
     `/sdcard/w.xml` cũ**, nên script nào không check exit/stderr sẽ đọc snapshot từ vài phút trước.
     Lúc đang phát nhạc thì nhãn vị trí tick 250ms → window không bao giờ idle → dump luôn fail. Đã
     làm tôi tưởng stream playback đứng ở 00:00 (2026-09-08), đúng lại vết xe của
     [[project_r8_consumer_rules]].

  **Đảo ngược lại thì nó là bằng chứng tốt:** dump fail vì "could not get idle state" nghĩa là UI
  đang recompose liên tục, tức nhãn vị trí ĐANG chạy. Nhãn đứng im thì window idle và dump thành công.
  Helper phải `rm` file cũ + raise khi thấy ERROR, đừng đọc thầm. Tín hiệu "có đang phát không" đáng
  tin nhất vẫn là `dumpsys audio | grep -c state:started`.
- **Fade làm hỏng MỌI phép đo "nguồn vs tổng các stem"** (dính 2026-09-24). File export có fade,
  file nguồn thì không, nên `source - Σstems` đo trên nguyên file đọc ra ~20% residual ở **mọi dải
  tần** — trông y hệt lỗi model. Đã kiểm tra lag (=0) và fit gain toàn cục (22,5%→20,1%) rồi mới vẽ
  residual theo từng giây: hình chữ V đối xứng, 90% ở giây 0, 0,13% ở giữa. Plateau phẳng lì 4,32%
  ở khúc giữa chính là `(1 − 1/1.2079)²` → chứng minh hệ số gain vừa fit là do hai đầu fade đẻ ra.
  **Cách đúng: đo trên cửa sổ nằm giữa hai đoạn fade, không hiệu chỉnh gì.** Làm vậy thì Σstems
  khớp nguồn **0,00000%** — khớp với ghi chép "stem Spleeter cộng lại ≈ bản gốc" ở trên.
  Hệ quả thứ hai: **đối chứng không phải "dải này phải bằng 0"** mà là "chạy cả hai bản, các dải
  không bị tác động phải đọc giống nhau". Ngưỡng tuyệt đối đoán trước đã làm một bản fix chạy đúng
  trông như fail.
- `adb` không có trong PATH của shell này → dùng `/home/khapv/Android/Sdk/platform-tools/adb`.
  Trích bounds từ uiautomator bằng bash/grep hay sai; parse bằng python theo từng `<node ...>`.

**Phát hiện chưa sửa (cố ý, ngoài scope):** cộng cả 4 stem ở weight `1f` thì **clip thật** — 24.302 /
10.050.048 frame (0,24%) chạm `coerceIn(-1f,1f)` trên bài 3:47. Không phải bug: stem Spleeter cộng
lại ≈ bản gốc vốn đã master sát full-scale. Khi đưa vào product phải hạ weight mặc định hoặc
peak-normalise. Đã ghi trong Known issues của README.

**Còn nợ:** subset save màn Batch (chọn 2/4 stem) chỉ có unit test, chưa chạy máy — kéo slider qua
adb hỏng 2 lần, và **không dùng Solo thay được** vì `applyStemVolumes` suy ra mute mà không ghi vào
`stemVolumes` — đúng cái `save()` đọc.

Test sau đợt này: `:core` 129, `:playback` 56, `:presence:core` 12, `:presence:yamnet` 8, `:app` 164
— 369, 0 fail. Checkpoint: `checkpoints_backup/code_backup_2026-09-08_094920_merge_model_export`
(xem [[project_checkpoint_convention]]).
