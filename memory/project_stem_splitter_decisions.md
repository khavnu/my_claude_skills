---
name: project-stem-splitter-decisions
description: Quyết định kỹ thuật đã chốt cho feature Stem Splitter (Vocals/Instrumental/Drums/Bass) từ buổi brainstorm mang từ project cũ sang
metadata: 
  node_type: memory
  type: project
  originSessionId: aba847bb-6c0a-42c4-b443-5a537aa55053
  modified: 2026-08-26T06:56:53.964Z
---

Feature **Stem Splitter** (tách Vocals/Instrumental/Drums/Bass) đã brainstorm
ở project cũ (`green_ba_music_player`), nội dung đầy đủ đã chuyển vào
`docs/stem-splitter-brainstorm.md` trong project này.

Quyết định đã chốt:
- Model: **Spleeter** (Deezer) — không phải Demucs. Demucs bị loại vì
  pretrained weight cấm dùng thương mại (chỉ code là MIT, weight thì
  "provided only for scientific purposes" theo chính Meta xác nhận).
- Runtime mobile: **TFLite**, không phải ONNX — vì Spleeter gốc là
  TensorFlow, convert sang ONNX gần như chưa có precedent.
- Deploy trước: **offline/on-device** trước, online (server) để phase sau,
  tách flow riêng — không ép chung interface ngay để tránh over-engineer.
- Rủi ro kỹ thuật đã biết: `.tflite` ~150MB (bản 4stems), bắt buộc
  `TensorFlowLiteSelectTfOps` (không chạy TFLite core thuần), không tận dụng
  được GPU/NNAPI (dynamic shape → CPU-only), cần chunk audio 2s + overlap
  4096 sample để né OOM.
- Bước tiếp theo (chưa làm): spike convert checkpoint 4stems → TFLite theo
  quy trình `tinoucas/spleeter-tflite-convert`, đo latency/memory/chất lượng
  thực tế trước khi cam kết đi tiếp on-device.

**Update 2026-08-20 — đã tích hợp xong bản demo (chưa verify trên thiết bị
thật):**
- Dùng luôn bản `.tflite` convert sẵn từ `jinay1991/spleeter` release
  `v2.3` (`4stems.tar.gz`, asset `models/4stems/4stems.tflite`, ~157MB) —
  README của chính asset xác nhận convert từ official Deezer checkpoint
  v1.4.0 (MIT), nên license kế thừa OK, không cần tự chạy
  `tinoucas/spleeter-tflite-convert` nữa.
- **Pitfall quan trọng:** thứ tự output tensor của file `.tflite` này
  **KHÔNG tuần tự theo index 0-3** — đã dùng `ai-edge-litert` (Python) để
  inspect `interpreter.get_output_details()` và xác nhận index thực tế là
  ngẫu nhiên (914/853/975/792), phải resolve output theo **tensor name**:
  input = `"waveform"` (rank-2 `[frameCount, 2]`, không có batch dim);
  output = `strided_slice_13`=vocal, `strided_slice_23`=drums,
  `strided_slice_33`=bass, `strided_slice_43`=accompaniment. Code Android
  (`SpleeterStemSeparator`) resolve output index bằng cách match tensor name
  tại runtime, không hardcode 0/1/2/3 — nếu sau này đổi sang model convert
  khác, PHẢI re-verify lại tensor name/order bằng cách này trước khi tin
  code cũ.
- Model bắt buộc Flex delegate (`FlexRFFT`/`FlexIRFFT`/`FlexConv2D`/
  `FlexPad`/`FlexTranspose`) — xác nhận lại đúng như brainstorm ban đầu, cả
  `ai-edge-litert` lẫn `tensorflow-cpu` (Python) đều báo lỗi thiếu Flex nếu
  không link `tensorflow-lite-select-tf-ops`.

**Update 2026-08-20 (tiếp) — bug crash + root cause đã tìm ra và fix xong,
đã verify thật trên thiết bị Android (Samsung, arm64-v8a), không phải giả
định:**
- **Triệu chứng:** `IllegalArgumentException: Cannot copy from a
  TensorFlowLite tensor (strided_slice_13) with shape [1, 1] to a Java
  object with shape [N, 2]` — crash mọi lúc, không phụ thuộc độ dài input
  (test cả 2s lẫn 30s đều crash y hệt).
- **Root cause thật (đã xác minh bằng cách chạy `saved_model` gốc — không
  phải `.tflite` — qua `tensorflow-cpu` thật, cho input 2 giây: output đúng
  full-length `(88200, 2)` cho cả 4 stem):** SavedModel gốc hoàn toàn ĐÚNG.
  Bug nằm ở cách gọi TFLite Java Interpreter: gọi thủ công
  `interpreter.resizeInput(0, [frameCount, 2])` rồi `allocateTensors()`
  TRƯỚC khi gọi `runForMultipleInputsOutputs()` làm hỏng việc dynamic-shape
  propagate qua Flex delegate partition — kết quả output luôn bị "đóng
  băng" ở shape mặc định `[1,1]`. Đã thử CẢ 2 bản `.tflite` (bản convert sẵn
  của `jinay1991` VÀ bản tự convert lại bằng `TFLiteConverter.from_saved_model`
  chính thức, dùng `tf.lite.OpsSet.SELECT_TF_OPS`) — cả 2 đều bị lỗi y hệt
  khi gọi resize thủ công, nên đây là vấn đề trong cách gọi Interpreter API
  của TFLite (khi có Flex delegate), không phải bug riêng của 1 bản convert.
- **Fix:** BỎ HẲN lời gọi thủ công `resizeInput()`/`allocateTensors()` trong
  `SpleeterStemSeparator.separate()` — chỉ cần truyền input/output Java array
  đã đúng shape ([frameCount, 2], suy từ chính input) thẳng vào
  `runForMultipleInputsOutputs()`, để nó tự resize+allocate nội bộ trong 1
  bước. Đã verify: file output đúng byte-size kỳ vọng, không crash, cả 2s
  lẫn 30s.
- **Bài học áp dụng cho tương lai:** với TFLite model có Flex delegate +
  dynamic input shape, KHÔNG tự gọi `resizeInput`/`allocateTensors` riêng lẻ
  trước `run()`/`runForMultipleInputsOutputs()` — để hàm run tự lo toàn bộ.
  Nếu cần biết output shape trước khi có buffer, suy ra từ input shape theo
  logic của model (Spleeter luôn giữ nguyên frame/channel count mỗi stem),
  không query `getOutputTensor().shape()` (không đáng tin ở giai đoạn nào cả
  — trước invoke luôn là placeholder, và query sau resize thủ công cũng sai).
- Amplitude vocals/drums/bass rất nhỏ so với "other" ở đoạn test 2s đầu bài —
  đã verify khớp với chính SavedModel gốc cho cùng input, nên đây là đặc
  điểm audio của đoạn test (đầu bài ít vocal/drums/bass) chứ không phải bug.
- Numeric correctness (chất lượng tách 4 stem có tốt không) vẫn cần user tự
  nghe đánh giá — chưa có cách đo SDR tự động trong spike này.
- **User đã nghe thử 4 stem trên thiết bị thật và xác nhận "chất lượng tốt"
  (2026-08-20).** → Spike ban đầu từ buổi brainstorm (mục tiêu: "load thử
  trên Android, đo chất lượng thực tế trước khi cam kết đi tiếp on-device")
  coi như đã có kết quả tích cực — pipeline Spleeter (TFLite + Flex ops) khả
  thi trên device thật, không chỉ về mặt kỹ thuật (chạy không crash) mà cả
  chất lượng audio. Việc còn lại trước khi lên production: đo latency/memory
  cụ thể trên bài hát dài thật (chưa làm — mới test tới 30s), quyết định
  chunking cho audio dài, và mở rộng decoder ngoài WAV.
- Native lib `tensorflow-lite-select-tf-ops` rất nặng: ~100-120MB **mỗi
  ABI**. Đã giới hạn `ndk.abiFilters` còn `arm64-v8a` + `x86_64` trong
  `app/build.gradle.kts` (APK debug giảm từ 573MB → 386MB) — cần nhớ đây là
  giới hạn tạm cho spike, phải xem lại trước khi release.
- Spike-scope decoder (`WavPcmDecoder`) **chỉ đọc WAV PCM 16-bit** — chưa có
  decode MP3/FLAC/AAC (cần MediaCodec hoặc FFmpeg, chưa làm). File picker
  hiện giới hạn mime `audio/wav`.

**Why:** Buổi brainstorm gốc đã loại bỏ FFmpeg thuần (không đủ chất lượng
tách 4 stem) và DSP thủ công cổ điển (ADRess/NMF/REPET/HPSS — effort ngang
AI integration nhưng chất lượng thấp hơn hẳn, SDR ~2-4dB vs Demucs ~7-9dB).
Quyết định model/runtime bị ràng buộc chặt bởi license (Demucs weight
non-commercial) chứ không phải chất lượng kỹ thuật thuần túy.

**How to apply:** Khi tiếp tục thiết kế/implement feature này, mặc định dùng
Spleeter + TFLite cho nhánh offline, không đề xuất lại Demucs/ONNX trừ khi
user chủ động đổi hướng. Domain interface (`SeparationRepository` hay tương
tự) nên tách riêng khỏi nhánh online ngay từ đầu — đừng trừu tượng hóa chung
sớm cho nhánh chưa build.

**Update 2026-08-20 — đã research Open-Unmix làm alternative nhẹ hơn Spleeter,
KẾT LUẬN: loại bỏ, không đổi hướng:**
- License weights `umx`/`umxhq`: MIT (an toàn commercial) — nhưng variant
  `umxl` (SDR cao nhất) lại **CC BY-NC-SA non-commercial**, giống trap của
  Demucs. Nếu sau này ai đề xuất lại Open-Unmix, phải chỉ định rõ variant
  `umx`/`umxhq`, tuyệt đối không dùng `umxl`.
- Size: ~140MB (4 file `.pth` riêng theo từng stem) — **không nhẹ hơn**
  Spleeter float32 (157MB), và thua xa bản Spleeter đã quantize (37.7MB).
  Chưa có ai làm bản quantize/TFLite tương đương cho Open-Unmix.
- Quality (SDR, MUSDB18, theo chính paper Spleeter của Deezer): Spleeter
  thắng Open-Unmix cả 4 stem (Vocals 6.86 vs 6.32, Drums 6.71 vs 5.73,
  Bass 5.51 vs 5.23, Other 4.55 vs 4.02).
  Architecture Open-Unmix là 3-layer BiLSTM/stem (không phải CNN/U-Net như
  Spleeter) — về lý thuyết STFT/ISTFT nằm ngoài graph nên có thể né được
  Flex delegate khi convert TFLite, nhưng **chưa có precedent nào verify
  chạy thật trên Android** — đây là rủi ro chưa kiểm chứng, không phải ưu
  điểm đã chứng minh.
- MDX-Net cũng bị loại: weight license không rõ ràng (nhiều fork lẫn lộn),
  architecture hybrid 2-stream nặng hơn Spleeter, không đúng hướng "nhẹ".
- Nếu muốn giảm size tiếp trong tương lai, hướng khả thi hơn Open-Unmix:
  (a) full-integer quantization (int8 cả activation, sâu hơn dynamic-range
  đang dùng), hoặc (b) pruning/distillation trên chính Spleeter weight.
  Chưa làm, chỉ là hướng gợi ý.

**Update 2026-08-20 — đã chốt kế hoạch consolidate module SAU KHI build
custom Flex delegate xong (chưa làm, chỉ là plan đã confirm với user):**
- `:audio_stem_split_tensorflow` và `:audio_stem_split_quantize` hiện là
  bản copy-paste giống nhau 100% (đã verify bằng diff sau khi normalize tên
  package) — chỉ khác đúng 1 file: model asset (`4stems.tflite` 157.3MB
  float32 vs 39.57MB quantize, cùng tensor name/kiến trúc). `ChunkedSeparator.kt`,
  `StemSplitEngine.kt`, `SpleeterStemSeparator.kt` byte-for-byte giống nhau.
- Kiến trúc mới đã chốt CUỐI CÙNG (user đổi ý qua lại nhiều lần — đây là bản
  chốt sau cùng, không phải bản trung gian trước đó):
  ```
  :audio_stem_split
    :core                     -> depends on :audio_stem_split:native_build:custom
                                  (hoặc :origin, switchable)
    :quantize                 -> depends on :core
    :tensorflow               -> depends on :core
    :native_build
      :custom                 (AAR custom build từ Bazel — build_aar.sh)
      :origin                 (chỉ wrap lại 2 dependency Maven gốc:
                                tensorflow-lite + tensorflow-lite-select-tf-ops,
                                không build native gì cả)
  ```
  Lý do giữ `:custom`/`:origin` tách biệt (đối xứng nhau): user muốn
  **switch qua lại** giữa bản custom Flex delegate và bản Maven gốc
  (so sánh/fallback), nên `:core` chỉ cần đổi 1 dòng dependency để chuyển,
  không đụng code logic. Toàn bộ nằm trong 1 cây `:audio_stem_split` cho gọn
  (không có module top-level rời nào khác ngoài `:audio_stem_split` bản thân
  nó và `:app`).
- `:core` nhận model asset path qua constructor param (không còn hardcode
  `const val MODEL_ASSET_PATH` như hiện tại) — `:quantize`/`:tensorflow`
  chỉ còn nhiệm vụ bundle đúng file `.tflite` + truyền path/tag vào `:core`.
- Đánh đổi đã được user chấp nhận: từ bỏ mục tiêu portability ban đầu
  ("copy 1 module là chạy được ngay ở project khác") để đổi lấy DRY —
  vì portability chưa từng thực sự được dùng, còn duplication là thật.

**Update 2026-08-20 — đã thử full-integer (int8) quantization thật, KẾT LUẬN:
bị chặn cứng, không khả thi với model này:**
- Convert bằng `TFLITE_BUILTINS_INT8 + SELECT_TF_OPS` + representative
  dataset (chunk từ `sample_song.wav`) crash ngay ở bước **calibration**:
  `RuntimeError: Select TensorFlow op(s) ... not supported by this
  interpreter. Node number 41 (FlexTranspose) failed to prepare.`
- Root cause: full-integer quantization cần chạy representative dataset qua
  toàn graph để đo activation range, nhưng bước calibration của TFLite
  Converter dùng interpreter builtin-only, KHÔNG link Flex delegate — nên
  crash ngay khi gặp `FlexConv2D/FlexIRFFT/FlexPad/FlexTranspose` (đúng 4 op
  Spleeter bắt buộc phải có). Đây là giới hạn thật của TFLite Python API
  (pip `tensorflow-cpu`), không phải do cấu hình sai.
- Dynamic-range quantization (37.7MB, đã làm ở module `:audio_stem_split_quantize`)
  là giới hạn thực tế đã đạt được. Không đề xuất lại full-integer trừ khi có
  ai tự build custom TFLite calibration wrapper có link sẵn Flex ops ở tầng
  C++ (effort rất lớn, vẫn không chắc quantize được phần FFT/complex ops).

**Update 2026-08-20 — đã research hướng "build custom Flex delegate chỉ
chứa đúng 4 op cần" (thay `tensorflow-lite-select-tf-ops` tổng quát
~100-120MB/ABI), KẾT LUẬN: khả thi, payoff tốt, nhưng USER QUYẾT ĐỊNH LÀM
SAU (deferred, chưa bắt đầu):**
- Google có script chính thức `tensorflow/lite/tools/build_aar.sh
  --input_models=<path>/4stems.tflite --target_archs=<abi list>` — tự scan
  model để suy ra cần op nào, không cần tự viết Bazel target thủ công cho
  4 op. Đây là tính năng chính thức của TF, không phải hack tự chế.
- Số liệu thực tế tham khảo (GitHub issue #62914, build cho aarch64): full
  flex lib 99MB → selective build chỉ giữ đúng op cần: **7MB (~93% giảm)**.
  Nếu tỷ lệ tương tự áp dụng cho Android, `tensorflow-lite-select-tf-ops`
  (~100-120MB/ABI hiện tại) có thể giảm về single-digit-đến-vài-chục MB/ABI.
- Chi phí setup: cần checkout toàn bộ TensorFlow source + Bazel version
  khớp đúng TF đã dùng để convert model + NDK toolchain cho cross-compile —
  một lần (model đã ổn định, không dự kiến đổi), tốn có thể vài giờ + vài
  chục GB disk. Output là 1 file `.aar` custom, đổi cách khai báo dependency
  Gradle (local AAR file thay Maven artifact).
- Output vẫn ra file `.so` RIÊNG theo từng ABI (native code luôn compile
  theo arch, không có file `.so` chung) — giống cấu trúc artifact Maven
  hiện tại, chỉ là mỗi file `.so` đó nhẹ hơn nhiều. Nếu ship qua `.aab`, máy
  user chỉ tải đúng slice ABI của họ.
- **User đã chốt: nếu làm, build đủ 4 ABI (`armeabi-v7a, arm64-v8a, x86,
  x86_64`)** — nghĩa là khi thực hiện, phải REVERT lại `ndk.abiFilters`
  trong `app/build.gradle.kts` (đang giới hạn 2 ABI `arm64-v8a`+`x86_64`) để
  khớp, không thì app vẫn tự strip 2 ABI kia dù AAR có build sẵn.
- **Trạng thái: ĐANG LÀM (2026-08-20) — user đã confirm bắt đầu, không còn
  deferred.** Đã setup xong toolchain (Bazelisk, NDK r21e riêng biệt vì NDK
  27 bỏ cấu trúc `platforms/` cũ mà TF 2.14 configure.py cần, TF source
  checkout tại tag v2.14.0 khớp đúng version `tensorflow-lite`/
  `tensorflow-lite-select-tf-ops` đang dùng trong `libs.versions.toml`,
  KHÔNG phải v2.21.0 dùng để convert model). Đã fix 1 lỗi source thật:
  `tensorflow/tsl/lib/io/cache.h` thiếu `#include <cstdint>` (GCC 13 mới
  hơn, không tương thích với TF 2.14 code cũ) — fix bằng cách patch trực
  tiếp file đó, KHÔNG dùng blanket compiler flag (`--host_copt`/`--copt`
  force-include toàn cục đã thử và fail — phá compile của C-only code như
  zlib và cả file assembly `.S`, do force-include áp dụng bất kể loại file).
  Build `build_aar.sh` với input là cả 2 model (`4stems.tflite` gốc +
  quantize) để đảm bảo AAR phủ đủ op cho cả 2 engine, target đủ 4 ABI
  (`armeabi-v7a,arm64-v8a,x86,x86_64`). Build rất nặng (~15700 targets do
  phải build cả toolchain LLVM/MLIR làm host tool) — đã giảm
  `--jobs=8 --local_ram_resources=HOST_RAM*0.5` trong `.tf_configure.bazelrc`
  vì bản đầu (20 job song song) có dấu hiệu làm máy tự restart. Nhiều lần
  build bị kill giữa chừng (session teardown/terminate signal, không phải
  lỗi build) — Bazel cache trên disk giữ nguyên tiến độ, chỉ cần chạy lại
  đúng lệnh `build_aar.sh` là resume tiếp, không mất công.
  Baseline đã đo THẬT (từ Maven AAR `tensorflow-lite-select-tf-ops:2.14.0`):
  arm64-v8a 98.67MB, armeabi-v7a 70.70MB, x86 118.83MB, x86_64 120.38MB.

**Update 2026-08-20 — build custom Flex delegate ĐÃ XONG, số liệu thật đo
được, nhưng phát hiện 2 bug quan trọng trong quá trình verify:**
- Kết quả size thật (từ raw .so trong AAR): arm64-v8a 98.67MB→**10.32MB**
  (~89.5%), armeabi-v7a 70.70MB→**6.01MB** (~91.5%), x86 118.83MB→**11.73MB**
  (~90.1%), x86_64 120.38MB→**12.02MB** (~90.0%). Tốt hơn ước tính ban đầu.
- **Bug 1 (đã fix)**: TF 2.14 Bazel BUILD xếp `Interpreter.java` vào nhóm
  `JAVA_EXPERIMENTAL_SRCS`, không nằm trong `java_stable_srcs` (default của
  `build_aar.sh`) — bản build đầu thiếu hẳn class `Interpreter`, chỉ có
  `InterpreterApi`/`InterpreterImpl`/`InterpreterFactory`, gây lỗi compile
  "Unresolved reference 'Interpreter'". Fix: patch `build_aar.sh`
  (function `generate_tflite_aar`) thêm `experimental = True,` vào lời gọi
  `tflite_custom_android_library(...)`.
- **Bug 2 (đã fix, NGHIÊM TRỌNG hơn — phát hiện SAU KHI chạy thật trên
  device, không phải lúc compile)**: crash thật `UnsatisfiedLinkError:
  dlopen failed: cannot locate symbol
  "_ZNK6google8protobuf7Message11GetTypeNameEv"` khi load
  `libtensorflowlite_flex_jni.so`. Root cause: 2 lệnh `bazel build` mà
  `build_aar.sh` dùng để build AAR custom của mình (`generate_tflite_aar` ở
  dòng ~93, `generate_flex_aar` ở dòng ~131) **thiếu `--config=monolithic`**
  — trong khi chính bản build "generic" (không truyền `--input_models`,
  dùng để tạo ra bản giống Maven official) LẠI CÓ flag này. Thiếu
  `--config=monolithic` khiến `.bazelrc` giữ nguyên
  `framework_shared_object=true`/`tsl_protobuf_header_only=true` — protobuf
  không được link tĩnh vào `.so`, nên thiếu symbol ở runtime. Fix: thêm
  `--config=monolithic` vào cả 2 lệnh bazel build đó. Bài học: build custom
  Flex delegate PHẢI test chạy thật trên device (không chỉ compile pass) —
  loại lỗi linking này compile-time hoàn toàn không phát hiện được.
- **Update tiếp — thử fix Bug 2 bằng `--config=monolithic` đầy đủ (3 define:
  `framework_shared_object=false`, `tsl_protobuf_header_only=false`,
  `experimental_link_static_libraries_once=false`) THẤT BẠI sau 64 phút
  build**: gặp lỗi THẬT không liên quan gì đến Android AAR —
  `//tensorflow:tf_python_api_gen_v2` (genrule sinh Python API bindings,
  hoàn toàn không cần cho việc build AAR Android) crash với
  `Check failed: existing == nullptr ... UnaryVariantDeviceCopy ... already
  registered` — có vẻ `experimental_link_static_libraries_once=false` làm
  Bazel build thêm nhiều target không liên quan, và genrule đó có bug thật
  khi statically-link nhiều thứ trùng registration. Đã thử hướng hẹp hơn:
  chỉ dùng `--define=framework_shared_object=false
  --define=tsl_protobuf_header_only=false` (bỏ
  `experimental_link_static_libraries_once=false`) để né target lỗi đó mà
  vẫn fix được vấn đề protobuf static link. Kết quả: THẤT BẠI Y HỆT — action
  bị cache lại từ lần trước (chỉ mất 4.5s), xác nhận `tsl_protobuf_header_only=false`
  MỘT MÌNH đã đủ trigger lỗi này, không liên quan
  `experimental_link_static_libraries_once`.
- **Đã patch source trực tiếp** (`tensorflow/core/framework/variant_op_registry.h`,
  hàm `RegisterDeviceCopyFn`): đổi `CHECK_EQ(existing, nullptr) << "...
  already registered"` (crash cứng) thành `if (existing != nullptr) return;`
  (bỏ qua đăng ký trùng, không crash). Lý do an toàn: target bị lỗi
  (`tf_python_api_gen_v2`) là HOST TOOL sinh Python API bindings, hoàn toàn
  không liên quan đến `.so` Android mình ship — patch này chỉ ảnh hưởng
  build-time tool, không đụng runtime behavior của TFLite/Flex delegate
  thật.
- **Pattern lặp lại nhiều lần**: sau fix #1 (`variant_op_registry.h`), gặp
  tiếp fix #2 (`executor_factory.cc: RegisterOp` — "Two executor factories
  are being registered"), fix #3 (`function.cc: gradient::RegisterOp` —
  "Duplicated gradient for MapAccumulate"), fix #4
  (`tsl/framework/allocator_registry.cc: Register` — "conflicts with
  previous registration"). User đã confirm qua `AskUserQuestion`: **cứ tiếp
  tục patch không cần hỏi lại nữa** — mỗi lỗi đều CÙNG root cause
  (`--define=tsl_protobuf_header_only=false` khiến 1 số translation unit bị
  link 2 lần vào binary host tool `tf_python_api_gen_v2`) và CÙNG cách fix
  (đổi `CHECK`/`LOG(FATAL)` khi đăng ký trùng thành bỏ qua âm thầm, comment
  giải thích lý do an toàn). Nếu quay lại làm tiếp: tìm log lỗi mới nhất
  trong `build_aar*.log`, xác định file/dòng bị `CHECK`/`LOG(FATAL)` khi
  insert trùng vào registry map, áp dụng đúng pattern này, build lại.
- **Update — build custom Flex delegate ĐÃ THÀNH CÔNG HOÀN TOÀN** sau tổng
  5 lần patch cùng pattern (variant_op_registry.h, executor_factory.cc,
  function.cc gradient, allocator_registry.cc, op.cc OpRegistry — tất cả
  đều host-tool-only, không đụng runtime thật). Đã verify ở tầng binary:
  `readelf -d libtensorflowlite_flex_jni.so` chỉ còn NEEDED system lib
  (libdl/libm/liblog/libc), không còn phụ thuộc ngoài nào — và search
  undefined symbol `GetTypeName` = 0 kết quả, xác nhận đã static-link đủ
  protobuf. Size cuối (tăng nhẹ so với bản lỗi trước vì giờ có static
  protobuf thật, nhưng vẫn giảm rất nhiều so với Maven gốc):
  arm64-v8a 98.67MB→**12.07MB** (~87.8%), armeabi-v7a 70.70MB→**7.03MB**
  (~90.1%), x86 118.83MB→**13.73MB** (~88.4%), x86_64 120.38MB→**13.98MB**
  (~88.4%). AAR đã copy vào `audio_stem_split/native_build/custom/libs/`.
  **Chưa verify thật trên device** (chỉ verify tầng binary/static-link) —
  cần user tự test trước khi tin chắc 100%.

**Update 2026-08-21 — phát hiện + fix bug NGHIÊM TRỌNG KHÁC trong chính
model quantize (hoàn toàn không liên quan native lib), lộ ra sau khi Bug 3
(asset-path collision) được fix:**
- Crash thật trên device: `IllegalArgumentException: ... transpose_conv.cc:299
  weights->type != input->type (INT8 != FLOAT32). Node number 100
  (TRANSPOSE_CONV) failed to prepare.`
- Root cause verify từ chính source TF 2.14: kernel `tensorflow/lite/kernels/transpose_conv.cc`
  bắt buộc `weights->type == input->type` — KHÔNG có nhánh hybrid nào cho
  phép weight INT8 + input FLOAT32 (khác với `CONV_2D`/`FULLY_CONNECTED` có
  hỗ trợ hybrid dynamic-range). Đây là gap đã biết của TFLite (GitHub issue
  #36707 "TFLite can't quantize op transpose_conv"). Nhưng quantizer
  (`tensorflow/lite/tools/optimize/quantize_weights.cc`) LẠI liệt
  `TRANSPOSE_CONV` vào danh sách op được quantize weight — mismatch thật
  giữa quantizer và kernel runtime, không phải lỗi cấu hình của mình.
- Đã thử `experimental_new_quantizer=False` và `experimental_new_dynamic_range_quantizer=False`
  — không giải quyết được (converter vẫn quantize transpose_conv weight y
  hệt, output size giống bit-for-bit).
- **Fix cuối cùng (đã áp dụng)**: patch trực tiếp file `.tflite` đã quantize
  bằng Python (`ai_edge_litert.schema_py_generated` + `flatbuffers`) — tìm
  đúng 20 tensor weight của 20 (trong 24) op `TRANSPOSE_CONV` bị quantize
  INT8 (4 op nhỏ nhất — output channel=1 — đã tự động giữ FLOAT32 vì dưới
  ngưỡng 1024 element của quantizer), dequantize ngược về FLOAT32
  (`float = int8 * scale[channel]`, per-channel axis=0, zero_point luôn=0
  nên công thức đơn giản), rồi repack lại flatbuffer. Giữ nguyên quantize
  cho phần Conv2D còn lại (~90% số layer).
- Verify bằng Python (`ai_edge_litert.Interpreter`, không cần Flex delegate
  thật): `allocate_tensors()` (bước Prepare — chính là bước crash cũ) PASS
  hoàn toàn ở cả input shape mặc định và resize về shape thật. Lỗi duy nhất
  còn lại là thiếu Flex delegate (bình thường vì Python interpreter local
  không link Flex) — không phải lỗi TRANSPOSE_CONV nữa.
- Model size sau fix: **104.98MB** (tăng từ 39.57MB vì mất quantize benefit
  ở đúng các layer TRANSPOSE_CONV lớn, nhưng vẫn giảm ~33% so với bản gốc
  157.31MB). Đã copy đè vào
  `audio_stem_split/quantize/src/main/assets/models/quantize/4stems.tflite`,
  `:app` build lại thành công. **Chưa test thật trên device** — chỉ verify
  bằng Python interpreter (không link Flex), cần user tự confirm trên máy
  thật.

**Update 2026-08-21 — đã hoàn thành refactor module theo plan đã chốt
trước đó (gộp `:audio_stem_split_tensorflow`/`:audio_stem_split_quantize`
thành 1 cây `:audio_stem_split` dùng chung `:core`):**
- Cấu trúc cuối cùng đã implement xong, compile pass:
  ```
  :audio_stem_split
    :core                     (com.audioseparation.core — toàn bộ logic
                                cũ, nhận modelAssetPath + engineTag qua
                                constructor thay vì hardcode)
    :tensorflow               (chỉ chứa model asset + 2 const, api project(":audio_stem_split:core"))
    :quantize                 (tương tự, model asset riêng)
    :native_build
      :custom                 (AAR custom build từ Bazel — di chuyển từ
                                :flex_delegate_custom cũ)
      :origin                 (mới — chỉ wrap lại 2 dependency Maven gốc:
                                tensorflow-lite + tensorflow-lite-select-tf-ops)
  ```
- `:core` khai báo dependency tới ĐÚNG 1 trong 2 module native_build —
  hiện đang tạm để `:native_build:origin` (Maven gốc, ổn định) theo yêu
  cầu user để test app trước, có comment hướng dẫn cách đổi sang
  `:native_build:custom` khi cần. Chỉ cần đổi 1 dòng trong
  `audio_stem_split/core/build.gradle.kts`.
- `:app`'s Hilt DI (`StemSplitEngineModule.kt`) đổi từ 2 type khác nhau
  (`TensorflowStemSplitEngine`/`QuantizeStemSplitEngine` alias) sang
  **1 type `com.audioseparation.core.StemSplitEngine` + 2 qualifier**
  (`@TensorflowEngine`/`@QuantizeEngine`) vì giờ cả 2 engine literally là
  cùng 1 class, chỉ khác param constructor. `DefaultStemSplitterRepository`
  cũng đơn giản hoá theo — chỉ còn 1 `toDomain()` extension (trước đây có
  2, một cho mỗi type riêng biệt).
  - `settings.gradle.kts` dùng Gradle nested module path
    (`include(":audio_stem_split:core")` v.v.) — build system tự map ra
    physical dir `audio_stem_split/core/`.
- Model asset path đã fix từ trước (`models/tensorflow/4stems.tflite` vs
  `models/quantize/4stems.tflite`) được giữ nguyên qua refactor, không bị
  regression về bug asset-merge-collision.
- **Bug 3 (đã fix, KHÔNG liên quan native lib — bug cũ có sẵn)**: 2 module
  `audio_stem_split_tensorflow`/`audio_stem_split_quantize` cùng dùng path
  asset `models/4stems.tflite` → Gradle merge asset của `:app` chỉ giữ lại
  1 bản (bản tensorflow 157MB), bản quantize 39.57MB bị đè mất, không có
  warning. Nghĩa là engine "Quantize" trong app từ trước đến giờ **luôn
  chạy nhầm model float32** — mọi so sánh tốc độ Quantize vs TensorFlow đã
  làm trong session này (log `[Quantize]` vs `[Tensorflow]`) **không có giá
  trị**, vì thực chất chạy cùng 1 model. Fix: đổi path riêng —
  `models/tensorflow/4stems.tflite` và `models/quantize/4stems.tflite`,
  update `MODEL_ASSET_PATH` constant tương ứng trong cả 2
  `SpleeterStemSeparator.kt`. **Cần re-test lại so sánh Quantize vs
  Tensorflow sau fix này — số liệu cũ trong session không dùng được.**

**Update 2026-08-20 — đã research hướng "online/server-side separation"
(phase 2 theo brainstorm gốc), KẾT LUẬN: giữ nguyên Spleeter, nhưng
USER QUYẾT ĐỊNH DEFERRED — chưa dựng server, note lại làm sau:**
- Demucs/htdemucs weights vẫn non-commercial (verify lại trực tiếp từ
  maintainer Meta trên GitHub issue #327, chưa đổi từ 2022) — do MUSDB18
  (CC BY-NC-SA) "nhiễm" NC constraint vào weight train từ nó. Vẫn loại,
  không đổi khi chuyển từ mobile sang server (đây là vấn đề pháp lý của
  weight, không phải giới hạn platform).
- UVR/MDX-Net (Kim Vocal...) vẫn "unclear/no explicit permissive license" —
  phải liên hệ trực tiếp từng người train, không scalable. Loại.
- **Spleeter weights KHÔNG bị vấn đề NC-poisoning như Demucs** — verify từ
  Deezer research page: train trên data nội bộ Deezer (MUSDB18 chỉ dùng
  benchmark/eval, không train) → cả code lẫn weight đều MIT thật, an toàn
  commercial. Server-side nên tiếp tục dùng chính Spleeter, không đổi model.
- Hạ tầng server không cần build từ đầu: `spleeter-web`
  (github.com/JeffreyCA/spleeter-web) — MIT, self-hosted free, Django+React
  full-stack có Docker+GPU support, dùng làm reference architecture cho REST
  API layer. Chi phí thật chỉ là tiền VPS/GPU tự host, không có license fee.
  App Android không cần UI web của nó — chỉ cần lấy phần API tối thiểu
  (upload → Spleeter xử lý → trả 4 stem), có thể viết lại 1 API mỏng
  (FastAPI/Flask) thay vì dùng cả bộ Django+React.
- Serve model: TensorFlow Serving (không cần convert ONNX — Spleeter dùng
  TF1.x ops legacy, thiếu ONNX op tương đương) — chỉ cần wrap checkpoint có
  sẵn thành SavedModel.
- **Trạng thái: DEFERRED — user nói "Note lại để sau này chúng ta sẽ triển
  khai sau", chưa bắt đầu.** Khi quay lại: bắt đầu bằng spike API tối thiểu
  chạy local (không thuê VPS ngay) để verify flow upload→xử lý→trả file
  trước khi quyết định hosting thật.

**Update 2026-08-21 — research thêm các app online separation trên
Play Store/web đang làm thế nào (Moises, LALAL.AI, VocalRemover.org,
PhonicMind, AudioShake, Splitter.ai, RipX, UVR), để tham khảo cho hướng
online (chỉ research, chưa code/chưa đổi quyết định nào):**
- **GPU inference là chuẩn chung** cho mọi cloud service (Moises, LALAL,
  media.io, PhonicMind, AudioShake) — không ai chạy CPU-only ở tầng server
  cho consumer scale; chỉ desktop tool (RipX, UVR) chạy CPU/local-GPU vì
  không phải trả tiền host.
- **Free tier ≠ model khác/chất lượng thấp hơn** — pattern phổ biến nhất là
  **quota + queue-priority** (free = ít phút + hàng đợi chậm, paid = nhiều
  phút + hàng đợi nhanh), CÙNG 1 model backend. LALAL.AI có 2 queue rõ nhất
  ("Fast" vs "Relaxed"). Rẻ hơn nhiều so với maintain 2 model chất lượng
  khác nhau.
- **Architecture hầu hết proprietary, không công bố** (Moises gọi là
  "Orchestrator", LALAL gọi "Andromeda") — chỉ AudioShake có patent công khai
  (USPTO 12437786/12399678), còn lại chỉ có Meta (Demucs) và Deezer
  (Spleeter, model đang dùng trong project này) công bố research thật.
- **AudioShake là case đặc biệt đáng tham khảo** — hybrid: cloud cho
  batch/chất lượng cao + SDK on-device cho real-time (iOS/macOS/Windows/
  Android/Linux). Không phải all-or-nothing cloud-vs-device.
- **Pattern kiến trúc chung "separation as a service"**: client upload lên
  object storage (S3-like) → queue trigger job → GPU worker pull model đã
  cache sẵn → chạy inference → ghi kết quả lại storage → client poll hoặc
  nhận webhook để download. Worker stateless, message chỉ xoá khỏi queue
  sau khi upload thành công (retry-on-crash). Auto-scale-to-zero để tiết
  kiệm GPU cost lúc idle.
- **3 takeaway áp dụng cho project này khi quay lại làm online (chưa quyết
  định, chỉ note để tham khảo)**:
  1. Nên thiết kế async (upload → queue → GPU worker → storage → client
     poll/push), KHÔNG làm synchronous request-response — vì xử lý tốn thời
     gian thật.
  2. Nếu có free/paid tier: ưu tiên pattern quota+queue-priority (rẻ, dễ
     build) hơn là 2 model quality khác nhau.
  3. Có thể học theo AudioShake — thêm server tier như 1 lựa chọn "chất
     lượng cao hơn/nhiều stem hơn" xếp lên trên pipeline on-device
     Spleeter/TFLite đã có, không cần thay thế hoàn toàn.
- Vẫn giữ quyết định cũ: model server-side tiếp tục dùng Spleeter (không
  Demucs vì license, xem update trước) — research lần này không đổi quyết
  định model, chỉ bổ sung tham khảo về hạ tầng/business model.
- Base implementation nếu làm: **`spleeter-web`** (JeffreyCA/spleeter-web,
  MIT, Django+React+Celery+Redis, Docker+GPU support) — dùng làm vỏ service
  bọc quanh Spleeter, vì Deezer's `spleeter` repo gốc chỉ là model+CLI,
  không có API/queue/storage. Cần viết thêm API mỏng riêng cho Android gọi
  vào (không dùng thẳng UI React của nó).

**Update 2026-08-21 — user tự đánh giá rủi ro kinh tế của hướng online,
KẾT LUẬN: DEFERRED tiếp, lý do lần này là business risk, không phải kỹ
thuật (khác các lần deferred trước — trước đây deferred vì "chưa cần ngay",
lần này deferred vì "chưa chắc nên làm"):**
- User tự nêu đúng 3 chi phí cốt lõi: xử lý CCU (auto-scale GPU worker,
  cold-start latency khi scale-up), thuê GPU (trả theo giờ máy chạy, không
  theo request — khác VPS thường), thuê server (chi phí cố định hàng tháng
  kể cả 0 user).
- **Bản chất rủi ro**: chi phí hosting online là **fixed/theo-giờ**, doanh
  thu là **theo-user** — với app chưa có traction, gần như chắc lỗ ở giai
  đoạn đầu. Khác hẳn on-device: compute do máy user trả, không tốn gì thêm
  khi tăng user, không có rủi ro tài chính này.
- **Hướng giảm rủi ro đã note nếu sau này muốn dò thử** (chưa quyết định
  làm, chỉ là phương án ít rủi ro hơn nếu quay lại): **serverless GPU
  pay-per-request** (RunPod Serverless, Modal, Replicate...) — trả đúng số
  giây inference thật, 0 cost lúc idle, né được bài toán CCU/idle-GPU. Vẫn
  KHÔNG giải quyết được câu hỏi gốc "có đủ user trả tiền để bù không" — thứ
  chỉ biết được sau khi có traction thật từ bản on-device.
- **How to apply**: KHÔNG chủ động đề xuất lại hướng online cho đến khi có
  1 trong 2 điều kiện: (a) bản on-device đã có traction/user thật đủ để ước
  tính demand, hoặc (b) user chủ động hỏi lại. Nếu quay lại, ưu tiên
  serverless pay-per-request thay vì thuê GPU instance cố định, để giảm
  rủi ro tài chính ở bước dò thử đầu tiên.

**Update 2026-08-21 — fix "APK does not support 16KB devices" (Google Play
bắt buộc từ 01/11/2025) cho custom Flex delegate AAR, ĐÃ XONG + verify đầy
đủ trên APK thật:**
- Root cause verify bằng `llvm-objdump -p <so> | grep -A1 LOAD`: cả 2 file
  `.so` custom-build (`libtensorflowlite_jni.so`,
  `libtensorflowlite_flex_jni.so`) đều `align 2**12` (4KB) — trong khi lib
  khác trong APK (`libandroidx.graphics.path.so`, build bằng NDK hiện đại
  hơn) đã `align 2**14` sẵn. NDK r21e (bắt buộc dùng cho TF 2.14, xem lý do ở
  update trước) là NDK cũ, mặc định chưa emit 16KB alignment.
- Fix theo đúng hướng dẫn chính thức
  (`developer.android.com/guide/practices/page-sizes`, cho NDK r27 hoặc cũ
  hơn): thêm `--linkopt=-Wl,-z,max-page-size=16384
  --linkopt=-Wl,-z,common-page-size=16384` vào CẢ 2 lệnh `bazel build` trong
  `build_aar.sh` (`generate_tflite_aar` và `generate_flex_aar`) — linker
  `lld` bundled theo NDK r21e hiểu được flag này, KHÔNG gặp lỗi cú pháp như
  rủi ro đã lo trước khi build (không cần fallback/hỏi lại user).
- Rebuild full lại từ đầu (~25239 target, ~100 phút) vì flag build thay đổi
  invalidate cache liên quan link step — nhưng 5 patch duplicate-registration
  cũ (xem update trước) vẫn hoạt động đúng dưới flag mới, không phát sinh
  lỗi mới nào.
- Verify đầy đủ 2 tầng: (1) raw `.so` trong AAR vừa build — cả 4 ABI × 2 AAR
  = 8 file đều `align 2**14`; (2) raw `.so` **thật sự nằm trong
  `app-debug.apk`** sau khi build lại `:app` — cũng cả 8 file đều
  `align 2**14`. Không chỉ verify ở tầng AAR như các fix trước — đây là lần
  đầu verify tới tận file trong APK cuối.
- AAR mới đã copy vào `audio_stem_split/native_build/custom/libs/`
  (tensorflow-lite.aar 4.5MB, tensorflow-lite-select-tf-ops.aar 17.2MB).
  `:app:compileDebugKotlin` + `:app:testDebugUnitTest` (stem_splitter tests)
  + `:app:assembleDebug` đều pass. APK debug hiện tại (quantize engine +
  native_build:custom, 4 ABI, :original đang tạm disable) = **179MB**.
- **Chưa test thật trên device** cho lần rebuild này (chỉ verify
  static/binary layer + Gradle build) — cần user tự cài + chạy thử tính năng
  thật trước khi tin chắc 16KB fix không phá vỡ runtime behavior nào khác.

**Update 2026-08-21 — research app Play Store xử lí OFFLINE/on-device
(đối lập với research online ở update trước), để so sánh với hướng project
đang đi (chỉ research, chưa đổi gì):**
- **ĐÃ ĐÍNH CHÍNH (2026-08-21) — "unMix" KHÔNG phải app offline thật, research
  trước SAI**: research gốc claim "Vocal Remover – unMix Offline"/"unMix"
  (~82k review, 4.5★) là bằng chứng tốt nhất cho offline ML thật (dựa vào
  tên app + review complaint "choppy audio and artifacts"), nhưng **user
  tự kiểm tra trực tiếp app này và xác nhận nó chạy ONLINE**, không phải
  offline như tên/marketing copy gợi ý. Đây là bài học: KHÔNG tin tên app
  + review suy luận gián tiếp, cần verify trực tiếp (mở app, tắt mạng thử)
  trước khi coi là "confirmed". Research gốc chỉ dựa vào Play Store
  listing text + review snippet (agent tự nhận "confirmed via listing
  text, not independently tested") — đã bị chứng minh sai bằng cách kiểm
  tra thật.
- **"Music & Vocal Splitter offline" (`com.ideastocode.musicvocalsplitter`) —
  ĐÃ VERIFY THẬT bằng cách pull APK trực tiếp từ máy (user cài sẵn, `adb
  pull` base.apk + split_config.arm64_v8a.apk, giải nén, đọc thẳng file
  model/native lib/dex string) — bằng chứng file-level, KHÔNG phải suy
  luận từ marketing/review như unMix trước đó (đã bị đính chính là sai).
  KẾT QUẢ: ML THẬT 100%, và tìm được app tự công khai attribution ngay
  trong string resource của chính nó (dex string, có thể là màn hình
  "About"):**
  > "This App uses Spleeter-based ONNX source separation models
  > distributed through the sherpa-onnx project."
  > "This application is an independent implementation... not affiliated
  > with or endorsed by Microsoft, k2-fsa, sherpa-onnx, Spleeter, or their
  > contributors."
  - **Model**: Spleeter-based (ĐÚNG model gốc project này đang dùng!),
    convert ONNX qua project mã nguồn mở **sherpa-onnx** (k2-fsa) — không
    phải Open-Unmix dù tên class Kotlin trong app là `UMXLEngine.kt` (tên
    gọi cũ/nhầm còn sót lại từ lúc dev có thể từng thử Open-Unmix trước
    khi đổi qua Spleeter — đừng tin tên class, đã verify kiến trúc thật
    qua op list trong file `.onnx`: `conv1-conv5` + 10 `bn*.running_mean`
    (BatchNorm) + `LeakyRelu` + `ConvTranspose` = đúng U-Net encoder/decoder
    của Spleeter, KHÔNG phải BiLSTM của Open-Unmix).
  - **Runtime**: **ONNX Runtime** (Microsoft, `libonnxruntime.so` 27.4MB +
    `libonnxruntime4j_jni.so`) — khác hẳn hướng TFLite của project này.
    Producer ghi trong file .onnx là `"pytorch 2.7.0"` — export qua
    PyTorch, không phải trực tiếp từ checkpoint TF gốc của Deezer.
  - **File model**: `vocals.fp16.onnx` + `accompaniment.fp16.onnx`, mỗi
    file **~19.68MB** (fp16, CHỈ 2-stem vocals/accompaniment) — nhẹ hơn
    hẳn bản 4-stem của project này (157MB float32 / 105MB quantize-fix) vì
    3 lý do: fp16 (nửa size float32), 2-stem thay 4-stem, và có thể kiến
    trúc/config nhỏ hơn bản 4stems chính thức.
  - **License**: vẫn là Spleeter MIT gốc (qua sherpa-onnx) — CÙNG nguồn
    license project này đang dùng, không có rủi ro pháp lý mới phát sinh
    từ finding này.
  - **Offline thật**: có `INTERNET`+`ACCESS_NETWORK_STATE` permission
    nhưng chỉ dùng cho `com.android.vending.BILLING`/ads (app có billing
    permission, khả năng có premium tier) — model + runtime bundle sẵn
    trong APK (base.apk có 2 file .onnx trong `assets/`, arm64 split có
    `.so` runtime), infer hoàn toàn local, không gọi server nào cho chính
    tính năng tách nhạc.
  - **How to apply**: đây là case đối chiếu trực tiếp giá trị nhất tìm
    được từ research app Play Store — CÙNG dùng Spleeter như project này,
    nhưng chọn ONNX Runtime + fp16 + chỉ 2-stem để nhẹ hơn, khác hướng
    TFLite + 4-stem hiện tại. Nếu sau này muốn giảm size, đây là data
    point thật (không phải lý thuyết) cho thấy fp16 + giảm stem count là
    hướng khả thi, có người làm thật và ship được.
  - **Bài học phương pháp luận quan trọng nhất**: verify bằng cách pull
    APK thật + đọc file/string trực tiếp (`adb pull` + `unzip` + `strings`)
    cho kết quả CHẮC CHẮN hơn hẳn so với chỉ đọc Play Store listing/review
    (cách đã dùng cho unMix và bị sai) — nên áp dụng cách này bất cứ khi
    nào cần verify "app X có dùng ML thật không" trong tương lai, thay vì
    suy luận gián tiếp.
- **Update 2026-08-21 (tiếp) — ĐÃ verify thêm 2 app nữa bằng cách pull APK
  thật (cùng phương pháp), cả 2 đều xác nhận dùng Spleeter thật:**
  - **"AI Vocal Remover Offline" (`io.jkhddev.music_player`)**: Flutter app,
    dùng **MNN** (Alibaba Mobile Neural Network, framework thứ 3 khác biệt
    ngoài TFLite/ONNX) + FFmpeg đầy đủ (`libavcodec/avformat/avutil/swresample/swscale`,
    `libmp3lame`) để decode. Model: 2 file `0.7z`/`1.7z` (~9.4MB mỗi file,
    khác nội dung — pattern 2-stem) nhưng **KHÔNG phải 7z thật** (magic
    bytes không khớp chuẩn 7z/TFLite/ONNX nào) — format custom/obfuscate,
    KHÔNG giải mã được nội dung, không xác định được chính xác là Spleeter
    hay model khác — chỉ xác nhận chắc runtime ML thật (MNN), không xác
    nhận được model gốc.
  - **"Vocal Remover" (`ai.vocal.remover.splitter.karaoke.instrumental`,
    Play Store link user cung cấp khớp đúng package) — thay cho "Ultimate
    Vocal Remover Offline" (package đó không tồn tại/sai từ research gốc,
    user đã chọn app đúng cài trên máy qua AskUserQuestion)**: bằng chứng
    RÕ NHẤT trong 3 app đã verify —
    - `libSpleeter.so` (488KB) — thư viện **TỰ VIẾT C++ riêng**, tên thẳng
      "Spleeter", KHÔNG dùng TFLite/ONNX/MNN. String nội bộ:
      `"engine/Spleeter"`, format load weight `"F%d.conv.b"`/`"F%d.conv.w"`/
      `"stem.conv.b"`/`"stem.conv.w"` (khớp kiến trúc conv-based U-Net,
      giống 2 app trước), namespace `mir::BeatModel::conv2d` ("mir" =
      Music Information Retrieval). Giống cách tiếp cận của
      `sevagh/demucs.cpp` (viết C++ riêng thay vì dùng framework tổng
      quát) nhưng áp dụng cho Spleeter.
    - Model: `assets/models/spleeter_2stems_11k_v1.splx` (78.6MB, nằm
      trong Play Feature Delivery "install-time asset pack", không phải
      base APK) — TÊN FILE xác nhận thẳng: Spleeter, 2-stems.
    - **Model bị MÃ HOÁ thật**: magic header `SPLXENC1` ("SPLX ENCrypted
      v1"), byte sau header có entropy cao (giống AES/stream cipher) —
      ĐÃ DỪNG LẠI ở đây, không thử decrypt (vượt ranh giới research hợp
      lý, đây là biện pháp bảo vệ IP có chủ đích).
    - Có thêm `libmidirender.so`, `libLyrics.so`, `libtoken.so` (khả năng
      license/DRM check), Firebase Crashlytics — sản phẩm production đầy
      đủ hơn 2 app trước về mặt kỹ thuật.
  - **Tổng kết 3 app đã verify — CÙNG dùng Spleeter, 3 chiến lược runtime
    khác nhau**: (1) Music & Vocal Splitter → ONNX Runtime, file `.onnx`
    rõ ràng không bảo vệ; (2) AI Vocal Remover Offline → MNN, file custom
    obfuscate nhẹ; (3) Vocal Remover (ai.vocal...) → C++ tự viết riêng,
    model **mã hoá thật**. Mức đầu tư bảo vệ IP tăng dần đúng theo mức độ
    "chuyên nghiệp" của app (có Crashlytics, DRM-token, asset pack riêng).
  - **How to apply**: nếu sau này cần ước tính "đối thủ bảo vệ model kỹ
    đến đâu" hay "học kiến trúc gì" — pattern chung của cả 3: conv-based
    U-Net (không LSTM), quantize/fp16 để giảm size, và **hầu hết chọn
    2-stem thay 4-stem** để tối ưu size hơn nữa — khớp đúng hướng
    `two_stem` project này đang chuẩn bị làm.
- **Offline ML separation trên mobile là hiếm thật, không chỉ do market
  chọn cloud** — có bằng chứng kỹ thuật: 1 project mã nguồn mở thương mại
  hoá đã ngừng app thật trên Play Store trước khi open-source (xem
  `sevagh/demucs-android` dưới). **Đã đính chính (2026-08-21, sau khi đọc
  trực tiếp README + PERFORMANCE.md của repo)**: KHÔNG tìm được lý do
  "why" trực tiếp nào từ tác giả (không có blog/HN comment giải thích) —
  claim "monetize khó" ở bản gốc research là suy đoán, KHÔNG có bằng chứng.
  Cái verify được thật: (1) tác giả pivot sang web/WASM
  (`freemusicdemixer.com`) thay vì tiếp tục native app — hành động có thật
  nhưng lý do vẫn là suy luận; (2) performance CPU thật của chính
  `demucs.cpp` (engine app đó dùng): 1 bài 4 phút mất **~4m9s** ngay cả trên
  **Ryzen 5950X 16-core** (config nhanh nhất họ đo) — gần bằng real-time
  trên CPU DESKTOP MẠNH, chưa nói CPU điện thoại. Đây là bằng chứng
  performance thật, nhưng là của **Demucs (Hybrid-Transformer)**, nặng hơn
  hẳn CNN U-Net đơn giản của Spleeter — KHÔNG nên suy rộng thẳng sang kết
  luận Spleeter/project này cũng khó tương tự.
  (3) Bonus liên quan câu hỏi GPU delegate: họ thử GPU (NVBLAS) rồi TỪ CHỐI
  dùng, lý do ghi rõ trong PERFORMANCE.md: *"workload's small matrix
  operations and memory constraints on target platforms (Android,
  WebAssembly)"* — tín hiệu cảnh báo thật cho hướng GPU delegate (xem update
  GPU/Flex-ops ở trên), dù đây là NVBLAS + kiến trúc Demucs-Transformer
  (khác TFLite GPU delegate + CNN U-Net của Spleeter), nên chỉ nên coi là
  điểm cần cẩn trọng thêm, không phải bằng chứng phủ quyết GPU delegate cho
  model đang dùng.
- **Open-source prior art trực tiếp liên quan (GitHub) — đáng so sánh với
  implementation hiện tại của project**:
  - [`Fr4nKB/SpleeterAndroidPort`](https://github.com/Fr4nKB/SpleeterAndroidPort)
    và [`FaceOnLive/Spleeter-Android-iOS`](https://github.com/FaceOnLive/Spleeter-Android-iOS)
    — CÙNG hướng Spleeter→TFLite→Android như project này; FaceOnLive claim
    làm được 5-stem fully on-device.
  - [`demixr/demixr-app`](https://github.com/demixr/demixr-app) — Demucs
    (htdemucs) 4-stem, dual backend GPU (ExecuTorch/CoreML/Vulkan) +
    CPU (ONNX Runtime), **model download lần đầu thay vì bundle sẵn** (né
    app size lớn — khác cách project này đang bundle model trong APK). Đo
    được: GPU nhanh hơn CPU **2.5-8.4x** cho bài hát 4 phút — data point cụ
    thể xác nhận CPU-only (như project này) là hướng chậm hơn hẳn, không
    phải giả định. Đã bỏ variant 6-stem (+guitar/piano) vì chất lượng kém —
    tham khảo tốt nếu sau này cân nhắc thêm stem.
  - [`sevagh/demucs-android`](https://github.com/sevagh/demucs-android) —
    dùng `demucs.cpp` (C++/Eigen thuần, không TFLite/PyTorch) để đủ nhanh
    trên CPU cho full htdemucs — từng là app Play Store thật, đã
    archived/deprecated (01/2025) rồi mới open-source. Đáng xem lý do ngừng
    nếu sau này lo về viability dài hạn của hướng on-device.
  - [`StemSplit/demucs-onnx`](https://github.com/StemSplit/demucs-onnx) —
    HT-Demucs FT export ONNX, numpy+onnxruntime thuần.
- **How to apply**: nếu sau này benchmark lại chất lượng/tốc độ on-device
  của project, có thể tham khảo trực tiếp 2 repo Spleeter-Android cùng
  hướng (Fr4nKB, FaceOnLive) để so sánh implementation, và số liệu
  GPU-vs-CPU của demixr-app để có baseline khi cân nhắc NNAPI/GPU delegate
  trong tương lai (hiện project bị giới hạn CPU-only do dynamic input
  shape, xem update trước).

**Update 2026-08-21 — đã inspect thật graph `4stems.tflite` (dùng Python
package `tflite` + `flatbuffers`, cài qua `pip3 install --user
--break-system-packages` vì máy không cho pip system-wide, không dùng
venv được do thiếu `python3-venv`) để trả lời câu hỏi "GPU delegate có ích
gì không với model này" — KẾT LUẬN: CÓ TIỀM NĂNG THẬT, ngược với suy đoán
ban đầu:**
- Script: `/tmp/.../scratchpad/inspect_flex_ratio.py` (parse operator_codes
  + operators của subgraph 0, đếm builtin vs custom/Flex op, cộng tổng số
  phần tử của tensor có buffer data — dùng làm proxy "trọng số compute").
- **Số liệu thật (giống nhau ở cả `:original` và `:quantize` — cùng graph,
  chỉ khác kiểu dữ liệu tensor)**: 633 operator/subgraph, chỉ 14 op
  (2.2%) là Flex/custom (`FlexConv2D`×4, `FlexTranspose`×5, `FlexIRFFT`×4,
  `FlexPad`×1) — số Flex ops này CHỈ chiếm **0.0% tổng weight params**
  (3219/39312050 phần tử). **99.99% weight params chạy qua builtin
  `CONV_2D` (24 op, 44.4%) + `TRANSPOSE_CONV` (24 op, 55.5%)** — đúng
  encoder/decoder U-Net (6 layer × 4 stem = 24, khớp kiến trúc Spleeter
  4-stem).
- **Sửa lại suy đoán sai trước đó** (lượt trả lời trước khi inspect thật,
  đã nói "nếu FlexConv2D là conv layer chính thì GPU delegate vô nghĩa")
  — SAI, đã verify bằng data thật: Flex ops chỉ nằm ở phần biên
  (STFT/ISTFT framing/reconstruct), không phải core U-Net. Phần compute
  nặng nhất (toàn bộ conv layer) là builtin, TFLite GPU delegate hỗ trợ
  được về nguyên tắc.
- **Điều kiện còn thiếu trước khi GPU delegate thật sự chạy được**:
  1. Vẫn phải fix dynamic input shape (pad chunk cuối cho đủ
     `chunkFrameCount` cố định) — GPU delegate cần shape cố định lúc tạo.
  2. Nên test GPU delegate trên `:original` (float32) trước, KHÔNG phải
     `:quantize` — GPU delegate hỗ trợ INT8 hạn chế/mới hơn so với
     float32, `:quantize` có INT8 trên chính `CONV_2D`/`TRANSPOSE_CONV`
     (trừ 20 tensor TRANSPOSE_CONV đã fix về float32, xem update trước).
  3. Delegate sẽ partition graph thành ít nhất 2-3 phần (CPU cho front-end
     STFT + GPU cho bulk U-Net + CPU cho back-end ISTFT) — số lần cross
     GPU/CPU ít (14 Flex op trên 633), không bị fragment nát như lo ban
     đầu, nhưng vẫn cần verify thật.
  4. GPU delegate có bug/instability theo vendor GPU (đã note ở research
     app đối thủ) — vẫn cần test rộng trên nhiều device thật trước khi
     tin chắc, không chỉ dựa vào số liệu graph tĩnh này.
- **How to apply**: nếu quay lại làm GPU delegate, đây là bằng chứng đủ để
  BẮT ĐẦU PROTOTYPE (không còn ở mức "chưa biết có đáng làm không") — bắt
  đầu bằng: (a) pad chunk cuối cho shape cố định trong `ChunkedSeparator`,
  (b) thêm `tensorflow-lite-gpu` dependency + `GpuDelegate()` optional
  trong `SpleeterStemSeparator` (chỉ cho `:original`, có CPU fallback),
  (c) đo tốc độ thật trên device thật trước/sau, KHÔNG áp dụng cho
  `:quantize` trước khi có thêm data về GPU+INT8.

**Update 2026-08-21 — ĐÃ IMPLEMENT xong prototype GPU delegate (code +
build pass, CHƯA test device thật) — user yêu cầu làm luôn, và giữa lúc
làm đã yêu cầu thêm bổ sung cả `:quantize` (không chỉ `:original` như plan
gốc) vì `:quantize` mới là engine đang chạy thật trong app:**
- Code đã implement đúng plan đã note trong README trước đó: `useGpuDelegate:
  Boolean` trên `SpleeterStemSeparator`/`StemSplitEngine`, `CompatibilityList`
  check trước khi tạo `GpuDelegate` (try/catch fallback CPU), `requiresFixedInputShape`
  trên `ChunkedSeparator` (pad chunk cuối bằng silent frame, truncate output
  sau khi separate). Hilt qualifier `@OriginalGpuEngine` VÀ `@QuantizeGpuEngine`
  (thêm ngoài plan gốc theo yêu cầu giữa chừng) trong `StemSplitEngineModule.kt`.
  Chưa wire vào `DefaultStemSplitterRepository`/UI — chỉ có trong DI graph.
- **2 lỗi dependency thật gặp phải, đã fix, đáng nhớ nếu động lại code
  này sau này**:
  1. `org.tensorflow:tensorflow-lite-gpu:2.14.0` một mình KHÔNG đủ —
     `GpuDelegate.Options extends GpuDelegateFactory.Options`, và
     `GpuDelegateFactory` nằm ở artifact RIÊNG `org.tensorflow:tensorflow-lite-gpu-api`,
     không được kéo theo transitive. Thiếu nó → lỗi Kotlin
     `Cannot access class 'Options'...` — đọc lỗi tưởng là do xung đột
     class (đoán sai lúc đầu, tưởng do AAR custom không tương thích Maven,
     đã thử sai hướng: exclude tensorflow-lite-api, đổi sang
     `:native_build:origin` — cả 2 đều KHÔNG cần thiết). Xác nhận đúng
     nguyên nhân bằng cách decompile trực tiếp 3 AAR (`javap`) để tìm class
     `GpuDelegateFactory` thật nằm ở đâu, không đoán.
  2. Sau khi thêm `tensorflow-lite-gpu-api`, gặp lỗi THẬT khác ở
     `checkDebugDuplicateClasses`: `tensorflow-lite-gpu` transitive kéo
     `tensorflow-lite-api`, trùng class (`DataType`, `Delegate`,
     `InterpreterApi`, `Tensor`, `TensorFlowLite`...) với chính AAR custom
     build (Bazel build tự chứa toàn bộ class, không tách api/runtime như
     Maven). Fix: `exclude(group="org.tensorflow", module="tensorflow-lite-api")`
     CHỈ trên `tensorflow-lite-gpu` (không phải trên `tensorflow-lite-gpu-api`
     — artifact đó không có transitive dep nào, verify bằng
     `./gradlew :audio_stem_split:core:dependencies`).
  - **Kết luận quan trọng**: AAR custom (Bazel) + GPU delegate Maven HOÀN
    TOÀN dùng được cùng nhau, không cần build lại GPU delegate riêng qua
    Bazel như lo ngại trước đó trong README — chỉ cần đúng 2 dependency +
    1 exclude.
- **User yêu cầu bỏ `:original`, chỉ cần apply GPU cho `:quantize`** ("apply
  cho quantize là được mà bạn") — đã revert lại đúng trạng thái cũ:
  `app/build.gradle.kts` comment lại `:audio_stem_split:original`,
  `StemSplitEngineModule.kt` comment lại `@OriginalEngine` provider, XOÁ
  hẳn `@OriginalGpuEngine` (không giữ lại dù chỉ code, vì không cần) —
  chỉ còn `@QuantizeEngine` + `@QuantizeGpuEngine` (mới) tồn tại thật.
- `:app:compileDebugKotlin`, `:app:testDebugUnitTest` (stem_splitter),
  `:app:assembleDebug` đều pass sau revert.
- **Phát hiện pitfall đo size APK**: sau khi bỏ `:original`, `app-debug.apk`
  trên đĩa vẫn đọc ra 342MB (không giảm) — do AGP dùng zipflinger đóng gói
  incremental, không tự shrink file khi bớt dependency, để lại "free space"
  cũ trong file. Phải chạy `./gradlew :app:assembleDebug --rerun-tasks` (ép
  đóng gói lại từ đầu) mới ra số đúng: **192MB** (179MB baseline quantize +
  ~13MB từ `tensorflow-lite-gpu`/`tensorflow-lite-gpu-api`). **Bài học**:
  không tin số đo size APK ngay sau khi bớt dependency mà chưa
  `--rerun-tasks`/`clean` — verify bằng `python3 zipfile` (tổng
  `compress_size` thật) nếu nghi ngờ số trên đĩa sai.
- **Chưa verify thật trên device** — toàn bộ phần "unverified" đã note ở
  update trước (delegate overhead per-chunk vì chunk ngắn 2s, GPU driver
  bug theo vendor, INT8+GPU compatibility cho `:quantize`) vẫn còn nguyên,
  CHƯA có data thật nào trả lời được các câu hỏi đó — bước tiếp theo khi
  quay lại là test thật trên device, không phải code thêm.

**Update 2026-08-21 (tiếp) — user đổi ý, yêu cầu wire lại `:original` +
thêm `OriginalGpu` vào UI để A/B test CPU vs GPU thật trên device, xếp
button 2 hàng:**
- Re-enable `:audio_stem_split:original` trong `app/build.gradle.kts`,
  restore `@OriginalEngine` + thêm mới `@OriginalGpuEngine` trong
  `StemSplitEngineModule.kt`.
- **Rename `StemSplitEngineType.Tensorflow` → `Original`** (đổi luôn cho
  nhất quán với tên module `:original`/qualifier `@OriginalEngine`, tránh
  lẫn lộn khi đặt cạnh `OriginalGpu` mới) — enum cuối:
  `{ Original, OriginalGpu, Quantize, QuantizeGpu }`. Đã grep xác nhận
  không còn sót "Tensorflow" ở đâu trong `app/src` (string resource, UI
  label, repository, viewmodel comment đều đã update theo).
- `DefaultStemSplitterRepository` inject đủ 4 engine, mỗi engine 1
  output dir riêng (`stem_splitter/original`, `/original_gpu`,
  `/quantize`, `/quantize_gpu`) — tránh đè file lên nhau khi so sánh.
- `EngineSelector` trong `StemSplitterScreen.kt` đổi từ 1 `Row` sang
  `Column` chứa 2 `Row` (2x2): hàng 1 = Original/OriginalGpu, hàng 2 =
  Quantize/QuantizeGpu — theo cặp CPU/GPU cùng tier, không theo thứ tự
  khác. Bỏ hẳn logic disable Tensorflow cũ (không còn engine nào bị
  disable trong UI nữa).
- `:app:compileDebugKotlin`, `:app:testDebugUnitTest` (stem_splitter),
  `:app:assembleDebug` đều pass.
- **APK debug cuối cùng (4 engine, đủ `:original`+`:quantize`+GPU libs):
  342MB** (verify bằng `--rerun-tasks` để tránh lỗi zipflinger stale đã
  gặp lần trước — 179MB quantize-only → 192MB +GPU libs → 342MB +
  original model). Đây là APK debug cho mục đích TEST/so sánh, không
  phải số cuối cùng dự kiến ship.
- README đã update mục "GPU delegate prototype" để phản ánh đúng: cả
  `:original` và `:quantize` đều có GPU variant, cả 4 hiện diện trong UI.
- **Vẫn CHƯA test thật trên device** — đây là bước tiếp theo, quan trọng
  nhất còn lại của toàn bộ nhánh công việc GPU delegate.

**Update 2026-08-21 (tiếp) — ĐÃ TEST THẬT trên device (Pixel 9, kết USB,
`adb`), dùng `sample_song.wav` bundled (~30s). KẾT LUẬN: GPU delegate
KHÔNG có ích trên máy này, còn phát hiện 2 bug thật qua quá trình test:**
- **Số liệu thật (đo bằng log `ChunkedSeparator: session finished,
  totalElapsed`)**:
  - Original (CPU): **16127ms**
  - Original (GPU): **18311ms** — chậm hơn CPU
  - Quantized (CPU): **10426ms**
  - Quantized (GPU): **17422ms** — chậm hơn CPU tới ~67%
- **`CompatibilityList.isDelegateSupportedOnThisDevice` = false cho CẢ 2
  model** trên Pixel 9 (Tensor G4) → GPU delegate fallback CPU hoàn toàn,
  log thật: `"GPU delegate not supported on this device, falling back to
  CPU"`. Lưu ý quan trọng: TFLite 2.14.0 (bản đang dùng) phát hành TRƯỚC
  khi Pixel 9 ra mắt — compatibility database có thể chỉ đơn giản chưa
  biết GPU Tensor G4, không chắc là driver thật không chạy được. Cần bản
  TFLite mới hơn (hoặc test máy khác) để biết chắc GPU delegate có khả
  thi thật không — KHÔNG nên kết luận "GPU delegate vô dụng hoàn toàn"
  chỉ từ 1 device này.
- **Bug #1 (thật, đã root-cause, CHƯA fix)**: `ChunkedSeparator` pad chunk
  cuối lên full `chunkFrameCount` (~1.3M frame) bất cứ khi nào
  `useGpuDelegate=true` khi TẠO engine — bất kể delegate THỰC SỰ tạo được
  hay fallback CPU. Khi fallback xảy ra (như trên Pixel 9), app vẫn chạy
  2 lần full-size inference (thay vì 1 full + 1 nhỏ ~4096 frame) → đây là
  lý do CHÍNH khiến mọi *Gpu variant đo được CHẬM HƠN bản CPU thường, dù
  compute thực tế giống nhau 100%. **Cách fix đúng**: `requiresFixedInputShape`
  trong `ChunkedSeparator` nên phản ánh delegate CÓ THỰC SỰ được tạo
  không (query `SpleeterStemSeparator` sau khi interpreter đã lazy-init),
  không phải chỉ dựa vào flag `useGpuDelegate` lúc constructor. Cần thêm
  property public kiểu `isGpuDelegateActive: Boolean` trên
  `SpleeterStemSeparator`, đọc SAU LẦN `separate()` đầu tiên (vì cả
  `gpuDelegate` và `interpreter` đều lazy) — case audio ngắn chỉ có 1
  chunk duy nhất (chunk "cuối" cũng là chunk đầu) vẫn còn edge case
  chưa nghĩ kỹ (chưa biết delegate status trước khi tạo interpreter lần
  đầu). **User đã quyết định KHÔNG fix**, lý do: "thực tế chúng ta chỉ
  chọn 1 engine thôi" — bug này chỉ có ý nghĩa khi so sánh CPU-vs-GPU của
  CÙNG 1 engine song song (A/B test); app thật sẽ chỉ ship đúng 1 engine
  cố định, không có baseline CPU nào để bị "chậm hơn" cả, nên fix không
  có giá trị thực tế. Giữ lại làm known issue trong README, KHÔNG code
  gì thêm.
- **Bug #2 (thật, phát hiện tình cờ qua crash)**: cả 4 engine
  (`@OriginalEngine`/`@OriginalGpuEngine`/`@QuantizeEngine`/`@QuantizeGpuEngine`)
  đều là Hilt `@Singleton` riêng biệt — mỗi engine giữ 1 TFLite
  Interpreter + model TRONG RAM VĨNH VIỄN sau lần dùng đầu tiên (lazy
  nhưng không bao giờ release tự động). Bấm thử lần lượt cả 4 engine
  trong 1 session (đúng cách mình test) làm RAM cộng dồn tới ~524MB
  (157+157+105+105MB) — gây **OOM-kill ÂM THẦM** (process chết, không có
  Java exception, không có dropbox `data_app_crash` record, chỉ biến mất
  và Android tự restart app) khi máy đang thiếu RAM thật (verify được:
  đúng lúc đó 1 app khác trên máy — `vocal_remover_music_separator` — bị
  `lowmemorykiller` kill vì "low watermark is breached and swap is low").
  Confirm root cause bằng cách `am force-stop` rồi mở lại app CHỈ TEST 1
  engine (Original GPU) riêng lẻ — chạy xong không crash, số liệu thu
  được đúng (18311ms) — xác nhận đây là vấn đề RAM tích lũy do test nhiều
  engine liên tiếp, KHÔNG phải bug riêng trong GPU delegate code.
- **Cách điều tra khi crash không rõ nguyên nhân trên device thật (bài
  học method luận, áp dụng lần sau)**: logcat buffer rotate rất nhanh khi
  có nhiều app khác chạy song song (chỉ vài phút đã mất hết log liên
  quan) — `adb shell dumpsys dropbox --print` bền hơn logcat, giữ được
  `data_app_crash` record cũ hơn NHIỀU (tìm được crash cũ từ sáng cùng
  ngày, đã fix trước đó, để phân biệt với crash mới). Nếu dropbox KHÔNG
  có record mới tương ứng thời điểm crash → khả năng cao là OOM-kill/native
  crash im lặng, không phải Java exception — nên kiểm tra `dumpsys
  meminfo <package>` và tìm dấu hiệu `lowmemorykiller` trong logcat ở
  cùng thời điểm, không chỉ tìm "FATAL"/"AndroidRuntime".
- **How to apply**: nếu quay lại làm GPU delegate, ưu tiên fix Bug #1
  trước (ảnh hưởng thật, đo được cụ thể), Bug #2 chỉ là rủi ro lúc TEST
  nhiều engine cùng lúc — người dùng thật sẽ không tự nhiên bấm thử cả 4
  nút trong 1 session như mình test, nhưng vẫn nên cân nhắc thêm cách
  release interpreter không dùng nữa nếu giữ nguyên kiến trúc 4 engine
  song song lâu dài.

**Update 2026-08-22 — sau khi wire UI two_stem xong (đổi tên nút thành
"4-Stem"/"2-Stem", bỏ 2 nút GPU theo yêu cầu user), test thật trên device
CRASH ngay khi chọn engine 2-stem — root cause THẬT, không phải bug logic
Kotlin, mà là gap trong chính plan build AAR custom trước đó:**
- **Lỗi**: `IllegalArgumentException: ... Didn't find op for builtin
  opcode 'LEAKY_RELU' version '1' ... Are you using an old TFLite binary
  with a newer model?` — crash ngay lúc tạo `Interpreter` (native), không
  liên quan Flex op (đã verify Flex op khớp nhau ở research trước).
- **Root cause verify bằng chính script `inspect_flex_ratio.py` đã dùng
  nhiều lần trước đó**: `4stems.tflite` dùng activation **`ELU`** (44 op),
  `2stems.tflite` dùng activation **`LEAKY_RELU`** (10 op) — kiến trúc
  gốc 2 checkpoint Deezer khác nhau thật, không phải do convert sai.
- **Bài học quan trọng, đã bỏ sót lúc research/plan trước**: khi verify
  "2stems dùng đúng 4 Flex op giống 4stems" (research trước, dẫn tới
  quyết định KHÔNG cần rebuild AAR), chỉ check trùng **Flex ops**, quên
  check luôn **BUILTIN ops** — `tflite_custom_android_library`
  (`build_aar.sh`) scope CẢ HAI loại op theo đúng `--input_models` truyền
  vào lúc build, không chỉ Flex. AAR custom hiện tại chỉ build từ 2 file
  `4stems` (`4stems_tensorflow.tflite`/`4stems_quantize.tflite`) nên
  thiếu hẳn kernel `LEAKY_RELU`.
- **Fix đang chạy (2026-08-22)**: rebuild lại `native_build:custom`'s AAR
  bằng đúng `build_aar.sh`, lần này `--input_models` truyền ĐỦ 4 file thật
  đang bundle trong app (`four_stem/original/4stems.tflite`,
  `four_stem/quantize/4stems.tflite`, `two_stem/original/2stems.tflite`,
  `two_stem/quantize/2stems.tflite`) để AAR bao trùm cả `ELU` và
  `LEAKY_RELU` (và cả Flex ops của cả 2 kiến trúc, phòng hờ). Log:
  `/tmp/build_aar_2stem_leakyrelu.log`. Toolchain cũ vẫn dùng lại được
  (Bazelisk, NDK r21e, `tensorflow_src` checkout tại
  `audio_stem_split/native_build/custom/tensorflow_src/`), không cần setup
  lại từ đầu.
- **How to apply lần sau**: khi thêm bất kỳ model mới nào dùng chung
  `native_build:custom`, PHẢI verify khớp **cả builtin op VÀ Flex op**
  bằng `inspect_flex_ratio.py` (hoặc tương đương) trước khi kết luận
  "dùng lại AAR được, không cần rebuild" — chỉ check 1 trong 2 loại op là
  không đủ, đây chính là lỗi đã gây crash thật lần này.

**Update 2026-08-22 — SAU KHI fix LEAKY_RELU xong, crash THỨ 2 xuất hiện
(`transpose_conv.cc:299 weights->type != input->type`) — ĐÃ fix, root cause
KHÁC hẳn LEAKY_RELU, và là lỗ hổng có sẵn từ lâu, không phải do rebuild AAR
gây ra:**
- Crash xảy ra khi chọn **"2-Stem Quantized"** (không phải "2-Stem
  Original" như nghi ngờ ban đầu lúc đọc log lần đầu — đã verify kỹ bằng
  cách so khớp node index #92 trong log crash với dtype thật của từng file
  qua script tự viết `inspect_transpose_conv_dtypes.py`: node #92 là
  FLOAT32 trong `two_stem/original/2stems.tflite` nhưng INT8 trong
  `two_stem/quantize/2stems.tflite` — khớp chính xác file quantize).
- **Root cause thật**: `two_stem/quantize/2stems.tflite` bị dynamic-range
  quantize 10/12 layer TRANSPOSE_CONV xuống INT8 weight — ĐÚNG bug hybrid
  kernel không tồn tại đã fix cho `four_stem/quantize` (xem update
  2026-08-21 phía trên), nhưng lúc convert/quantize `two_stem` (tải+quantize
  y hệt quy trình 4stem theo yêu cầu user), **KHÔNG áp dụng lại fix
  dequantize TRANSPOSE_CONV này cho model 2stem** — lỗ hổng sót lại từ lúc
  làm two_stem, không phải do việc rebuild AAR (LEAKY_RELU) gây ra thêm bug
  mới. Bước verify cũ ("Python `allocate_tensors()` không crash") ghi trong
  Pending Tasks trước đó là **không đủ** — không rõ vì sao (có thể do dùng
  `ai_edge_litert` interpreter khác implementation kernel so với bản TFLite
  Java thật trên device) — bài học: **verify TRANSPOSE_CONV int8 phải check
  trực tiếp dtype tensor qua flatbuffer** (như `inspect_transpose_conv_dtypes.py`),
  không tin `allocate_tensors()` Python pass là đủ.
- **Fix**: áp dụng lại đúng quy trình flatbuffer surgery đã dùng cho
  `four_stem/quantize` — dùng `tensorflow.lite.python.schema_py_generated`
  (object API `ModelT.InitFromObj`/`.Pack()`, TF 2.21.0 có sẵn, không cần
  `ai_edge_litert`) để unpack toàn bộ model, dequantize đúng 10 tensor
  weight của TRANSPOSE_CONV (per-channel `float = (int8 - zero_point) *
  scale[channel]`, axis lấy từ `quantization.quantizedDimension`), đổi
  `tensor.type` sang FLOAT32, xoá `quantization` params, rồi repack lại
  bằng `flatbuffers.Builder` + `model.Pack(builder)`. Script:
  `dequantize_transpose_conv.py` (scratchpad) — tổng quát, có thể dùng lại
  cho bất kỳ file `.tflite` nào bị lỗi tương tự trong tương lai (5stem nếu
  quantize sau này cũng cần chạy qua script này).
  Size sau fix: 19.8MB → 52.5MB (mất phần lớn quantize benefit ở đúng các
  layer TRANSPOSE_CONV, giữ nguyên quantize ở CONV_2D). Không cần rebuild
  AAR (kernel FLOAT32 TRANSPOSE_CONV vốn có sẵn, chỉ thiếu kernel hybrid
  INT8+FLOAT32 vốn không tồn tại ở TFLite).
- **Đã verify THẬT trên device (Pixel 9)**: cả "2-Stem Original" và
  "2-Stem Quantized" chạy sạch, không crash, có kết quả Vocals/Accompaniment
  nghe được. Trạng thái 2-stem coi như ĐÃ ỔN ĐỊNH, không còn crash nào mở.
- **How to apply lần sau (quan trọng cho 5stem sắp làm)**: BẤT KỲ model
  Spleeter mới nào (5stems...) nếu có bản quantize, PHẢI tự động chạy qua
  `inspect_transpose_conv_dtypes.py` để check TRANSPOSE_CONV dtype, và nếu
  có INT8 thì chạy `dequantize_transpose_conv.py` TRƯỚC KHI coi model đó là
  "đã quantize xong" — đừng lặp lại lỗi sót fix này lần thứ 3.

**Update 2026-08-22 — đang bổ sung tier 5-stem (vocals/piano/drums/bass/other),
đã research + convert + verify xong, đang chờ rebuild AAR:**
- Checkpoint chính thức: `https://github.com/deezer/spleeter/releases/download/v1.4.0/5stems.tar.gz`
  (182.8MB, cùng release v1.4.0 MIT license với 2stems/4stems đã dùng — không
  có rủi ro pháp lý mới). Khác 2stems (đã có sẵn `saved_model/`), file
  5stems ship dạng **raw TF1 checkpoint** (`model.meta`/`model.index`/
  `model.data-*`) — phải tự export SavedModel bằng
  `tf.compat.v1.train.import_meta_graph` + `saver.restore` +
  `tf.compat.v1.saved_model.simple_save`, không cần cài package `spleeter`
  (meta graph đã chứa đủ cấu trúc, không cần code Python gốc định nghĩa
  model).
- Kiến trúc: `softmax_unet` (khác `unet` thường của 2/4stems) — vẫn
  activation **ELU** giống 4stems (không phải LEAKY_RELU như 2stems), cộng
  thêm 1 op **SOFTMAX** (stack 5 mask rồi softmax theo chiều instrument để
  tổng mask = 1) — SOFTMAX là builtin TFLite op mới, **chưa có trong AAR
  custom hiện tại** (verify bằng cách check op inventory của cả 4 model cũ,
  0 op SOFTMAX nào) → bắt buộc phải rebuild `native_build:custom`.
- **Output tensor name — đã verify bằng cách trace ngược graph, KHÔNG suy
  đoán theo thứ tự số** (bài học từ pitfall 4stems cũ): tìm 5 op
  `strided_slice` là sink (0 consumer) trong toàn graph (`strided_slice_18/
  28/38/48/58`), rồi BFS ngược từng op tới khi gặp đúng 1 trong 5 marker op
  có tên chứa tên nhạc cụ thật (`vocals_spectrogram/mul`,
  `piano_spectrogram/mul`, `drums_spectrogram/mul`, `bass_spectrogram/mul`,
  `other_spectrogram/mul` — các scope name này CÓ tồn tại trong graph, khác
  với lo ngại ban đầu). Kết quả xác nhận: `strided_slice_18`=vocals,
  `_28`=piano, `_38`=drums, `_48`=bass, `_58`=other. Input vẫn `"waveform"`
  giống 2/4stems.
- Size thật sau convert (TF 2.21.0, SELECT_TF_OPS, khớp gần đúng dự đoán từ
  tỷ lệ tar.gz size trước khi convert): **original 196.6MB** (dự đoán trước
  ~196-200MB, đúng), **quantize 49.5MB trước fix / 131.2MB sau fix**
  TRANSPOSE_CONV (25/30 layer TRANSPOSE_CONV bị INT8 hoá, đã dequantize hết
  bằng `dequantize_transpose_conv.py` NGAY LÚC CONVERT, không đợi crash thật
  mới fix — áp dụng đúng "How to apply" ghi phía trên). Flex ops: đúng
  4 op cũ (`FlexConv2D`/`FlexIRFFT`/`FlexPad`/`FlexTranspose`), là subset
  của bộ AAR hiện có nên không phát sinh Flex op mới, chỉ thiếu builtin
  SOFTMAX.
- Đã scaffold xong module `audio_stem_split/five_stem/{original,quantize}`
  (mirror 100% pattern `two_stem`), domain (`FiveStemStems` data class +
  `SeparationResult.FiveStem` — KHÔNG nhồi field `piano` vào `SeparatedStems`
  chung để tránh làm bẩn shape 4-stem), DI (2 qualifier
  `@FiveStemOriginalEngine`/`@FiveStemQuantizeEngine`), UI (thêm row 3 engine
  selector, `StemKind.Piano`, đổi tên `StemSplitEngineType.isFourStem` →
  `supportsAccompanimentToggle` vì giờ cả 4-stem VÀ 5-stem đều có toggle
  accompaniment, chỉ 2-stem không có).
- **Đang chờ**: rebuild `native_build:custom` AAR với `--input_models` gồm
  ĐỦ 6 file (four_stem + two_stem + five_stem, original+quantize mỗi tier)
  để builtin op scope phủ cả SOFTMAX — áp dụng đúng bài học "phải verify cả
  builtin op VÀ Flex op" đã ghi ở update LEAKY_RELU. Sau khi AAR xong: rebuild
  `:app`, cài + test thật trên Pixel 9 cho cả "5-Stem Original" và "5-Stem
  Quantized" trước khi coi tier này ổn định — CHƯA test thật trên device ở
  thời điểm ghi note này.

**Update 2026-08-22 — user hỏi về 6stem, KẾT LUẬN: không tồn tại, không nên
tự chế ngay bây giờ:**
- Đã verify trực tiếp qua GitHub release `v1.4.0` của `deezer/spleeter`:
  chỉ có `2stems`/`4stems`/`5stems` (+ 1 bản `5stems-finetune`) — không có
  `6stems` chính thức nào từ Deezer, ở release nào.
- Nếu sau này muốn stem thứ 6 (ví dụ Guitar): (a) chain thêm 1 model tách
  riêng lên trên output "other"/"piano" của 5stems — nhưng Spleeter không
  có checkpoint train riêng cho cặp đó, vẫn phải tìm model ngoài họ Spleeter
  cho bước này; hoặc (b) đổi hẳn sang 1 family model khác có hỗ trợ 6 stem
  native (ví dụ 1 số config MDX23C từ cộng đồng Sound Demixing Challenge có
  thêm "guitar") — nhưng license của các model cộng đồng này chưa verify,
  rủi ro giống Demucs/MDX-Net đã loại trước đây (xem update 2026-08-20 về
  Open-Unmix/MDX-Net). Cả 2 hướng đều tốn công tương đương việc vừa làm cho
  5stems (research+convert+verify+rebuild AAR) mà không có gì đảm bảo license
  sạch như Spleeter.
- **How to apply**: KHÔNG chủ động đề xuất 6-stem. Nếu user hỏi lại, trả lời
  y hệt kết luận này — 5-stem là giới hạn thực tế của hệ Spleeter đang dùng.

**Update 2026-08-22 — five_stem HOÀN TẤT, đã verify thật trên device (Pixel 9)
cho cả 2 engine, KHÔNG còn việc pending nào cho tier này:**
- Rebuild `native_build:custom` AAR với đủ 6 model (`--input_models` gồm
  four_stem+two_stem+five_stem, original+quantize mỗi tier) chạy xong sau
  ~2.4 giờ (20,759 actions) — build client bị kill/mất kết nối giữa chừng 1
  lần (session teardown, đúng pattern đã ghi trước đây), nhưng Bazel server
  vẫn sống + cache disk giữ nguyên nên chạy lại đúng lệnh là resume tiếp,
  không mất tiến độ. Một lần chạy lại vô tình tạo ra 2 process bazel client
  cùng lúc — Bazel tự phát hiện và xếp hàng process thứ 2 (`Another command
  is running, waiting...`), process đó fail vô hại ở cuối vì lúc nó tới lượt
  chạy thì process đầu đã cleanup thư mục tmp — không ảnh hưởng gì tới output
  thật, bài học: nếu nghi ngờ 1 build bị chết, PHẢI `pgrep -af <cmd>` verify
  trước khi chạy lại, và nếu tình cờ chạy trùng thì cứ để Bazel tự xử lý
  (không cần kill), chỉ cần đảm bảo dùng ĐÚNG output của process nào hoàn
  tất "Build completed successfully" thật.
- **Test thật trên device: cả "5-Stem Original" và "5-Stem Quantized" chạy
  sạch, không crash** (`session finished: 2 chunks`), UI hiển thị đúng 5 stem
  (Vocals/Piano/Drums/Bass/Instrumental) + Accompaniment toggle hoạt động
  đúng. SOFTMAX (builtin op mới từ kiến trúc `softmax_unet`) và mapping
  tensor name (`strided_slice_18/28/38/48/58` → vocals/piano/drums/bass/
  other, đã verify bằng graph-trace lúc convert) đều đúng thật, không phải
  chỉ đúng trên Python.
- Tier 5-stem coi như ỔN ĐỊNH — không còn crash/lỗi nào mở cho cả 3 tier
  (2/4/5-stem) tại thời điểm này.

**Update 2026-08-22 — phát hiện + fix bug 16KB alignment MỚI, KHÔNG liên
quan five_stem — do chính GPU delegate prototype (đã unwire khỏi UI/DI từ
trước) vẫn còn sót code+dependency, đã XOÁ HOÀN TOÀN (không còn "để đó cũng
được" như trước):**
- User báo "16KB devices lại bị rồi" — verify lại bằng đúng cách đã dùng
  trước đây (`readelf -lW <so> | grep LOAD`) cho TẤT CẢ `.so` trong APK, chứ
  không chỉ 2 file từ AAR custom của mình: phát hiện `libtensorflowlite_gpu_jni.so`
  (từ dependency Maven `org.tensorflow:tensorflow-lite-gpu`) có `align
  0x1000` (4KB) — trong khi 2 lib từ AAR custom của mình (`libtensorflowlite_jni.so`,
  `libtensorflowlite_flex_jni.so`) vẫn đúng `align 0x4000` (16KB), fix cũ vẫn
  giữ nguyên. Bug KHÔNG phải do lần rebuild AAR cho five_stem gây ra — do lib
  Maven gốc (build sẵn bởi TensorFlow, không qua pipeline Bazel của mình) từ
  chưa bao giờ được áp linkopt fix, và trước đó lib này chỉ "unused nhưng vẫn
  bundle" (từ session GPU prototype, đã unwire khỏi UI/DI nhưng code/dependency
  vẫn còn "để đó" theo README's TODO) — giờ mới thành blocker thật.
- **Fix: xoá HOÀN TOÀN GPU delegate, không chỉ unwire nữa** — vì code Kotlin
  (`SpleeterStemSeparator.kt`) import trực tiếp `GpuDelegate`/`CompatibilityList`
  từ đúng dependency gây lỗi, nên không thể giữ code mà xoá dependency (sẽ
  không compile). Đã xoá: `useGpuDelegate`/`requiresFixedInputShape` param +
  toàn bộ logic liên quan trong `SpleeterStemSeparator`/`StemSplitEngine`/
  `ChunkedSeparator` (kể cả `padToFixedShapeIfNeeded`), 1 test case trong
  `ChunkedSeparatorTest` exercise đúng path đó, 2 dependency
  `tensorflow-lite-gpu`/`tensorflow-lite-gpu-api` trong `core/build.gradle.kts`
  VÀ trong `gradle/libs.versions.toml`.
- **Đã verify THẬT sau fix**: extract lại APK mới build, `libtensorflowlite_gpu_jni.so`
  biến mất hoàn toàn khỏi cả 4 ABI, 3 `.so` còn lại đều `align 0x4000`. Cài
  lên device, app chạy sạch không crash sau khi gỡ toàn bộ GPU code.
- **Gotcha lúc verify**: APK ở `app/build/intermediates/apk/debug/app-debug.apk`
  bị STALE (giữ timestamp cũ, không phải bản build mới nhất) — đây đúng là
  cái "AGP zipflinger đôi khi không cập nhật file" đã note trong README từ
  trước. File ĐÚNG cần check là `app/build/outputs/apk/debug/app-debug.apk`
  (so sánh timestamp + size để chắc chắn, không tin đường dẫn quen thuộc).
- **How to apply lần sau**: nếu 16KB check lại fail trong tương lai, ĐỪNG
  giả định là do AAR custom (lib mình build luôn giữ fix qua mọi lần rebuild,
  đã verify lại đúng lần này) — check TẤT CẢ `.so` trong APK, không chỉ 2 lib
  custom, vì thủ phạm thường là 1 dependency Maven khác (bên thứ 3) chưa bao
  giờ qua pipeline fix của mình.
- README đã update: section "GPU delegate" giờ ghi rõ 2 lý do bị bỏ (không
  benefit + phá 16KB), và giữ lại chi tiết cách re-enable (dependency,
  code pattern, gotcha) làm tài liệu tham khảo nếu sau này quay lại — theo
  đúng yêu cầu user "note tại sao không dùng nữa, nhưng giữ chi tiết cách
  enable".

**Update 2026-08-24 — nghiên cứu hướng ONNX (thay thế TFLite cho `two_stem`),
đã spike thật + verify end-to-end, KẾT LUẬN: khả thi kỹ thuật, effort thật lớn
hơn hy vọng ban đầu nhưng đã confirm bằng số liệu, không còn là ẩn số:**
- Động lực: 3 app đối thủ (`com.ideastocode.musicvocalsplitter`,
  `io.jkhddev.music_player`, `ai.vocal.remover.splitter.karaoke.instrumental`)
  đều dùng Spleeter nhưng runtime nhẹ hơn hẳn TFLite (39MB ONNX fp16 / ~18.8MB
  MNN / 78.6MB encrypted, so với 105-157MB TFLite hiện tại).
- Đã tạo module `:audio_stem_split:onnx:native_build:origin` (mirror
  `:native_build:origin`, wrap Maven `onnxruntime-android:1.29.0` — verify
  version thật từ Maven Central metadata, không đoán). Build pass, AAR thật
  đã tải, có `.so` đủ 4 ABI. Chưa có code nào dùng module này (chưa có
  `OnnxStemSeparator`).
- **Refactor nền tảng đã làm trước, không liên quan riêng ONNX**: tách
  interface `StemSeparator` (`separate`/`cancel`/`release`) trong `:core`,
  `SpleeterStemSeparator` implement nó, `StemSplitEngine` nhận
  `separator: StemSeparator` + `stemKeys: List<String>` qua constructor
  (inject) thay vì tự construct `SpleeterStemSeparator` — để nhánh TFLite
  không cần đổi gì khi thêm runtime khác. Đã update `StemSplitEngineModule`
  (6 engine) + `InterpreterOptionsBenchmarkTest`, verify thật trên Pixel 9.
- **Spike `tf2onnx` convert trực tiếp từ checkpoint Deezer `2stems.tar.gz`
  (v1.4.0, MIT, tải thật) — THẤT BẠI, đúng dự đoán**: lỗi ngay ở
  `stft/rfft`/`Abs`/`inverse_stft/irfft` — `tf2onnx`'s RFFT/IRFFT converter chỉ
  handle 1 pattern graph cụ thể (complex number leading-dim=2, RFFT chỉ được
  consume bởi `ComplexAbs`), graph thật của Spleeter dùng shape khác
  (`Transpose` sau RFFT) — structural mismatch, không phải lỗi flag/opset.
  Xác nhận: không có shortcut convert, phải viết lại forward pass bằng
  PyTorch rồi port weight, đúng như nghi ngờ từ producer `"pytorch 2.7.0"`
  trong file `.onnx` của Music Splitter.
- **Đã viết lại kiến trúc Spleeter 2stems bằng PyTorch, port weight thật, và
  verify end-to-end bit-exact với TF checkpoint — không phải suy đoán:**
  - Lấy đúng source `unet.py`/`model/__init__.py`/`utils/tensor.py`/
    `resources/2stems.json` từ `deezer/spleeter` tag `v1.4.0` (không đoán
    kiến trúc). Config xác nhận: `frame_length=4096`, `frame_step=1024`,
    `T=512`, `F=1024`, `n_channels=2`, `separation_exponent=2`,
    `mask_extension="zeros"`, model type `unet.unet` (KHÔNG phải
    `softmax_unet` — mỗi instrument có sigmoid mask độc lập, không
    softmax-normalize chung như `five_stem`).
  - Inspect checkpoint thật xác nhận input `waveform` `[None,2]`, output
    `strided_slice_13`=vocals/`strided_slice_23`=accompaniment (trace ngược
    graph tới `{instrument}_spectrogram/mul`, không đoán theo thứ tự).
  - **3 quirk kiến trúc thật phải giữ nguyên, dễ làm sai nếu "dọn dẹp" theo
    trực giác**: (1) `up1` (decoder đầu) nhận `conv6` RAW (trước
    BatchNorm+activation) — `batch6`/activation của nó là dead output trong
    graph gốc; (2) mọi skip-connection concat dùng `convN` RAW (trước BN),
    không phải `relN` đã activate; (3) Dropout bỏ hẳn (identity lúc inference,
    tương đương chính xác, không phải approximation).
  - **3 primitive rủi ro nhất đã validate riêng, bit-exact với TF thật trước
    khi ráp full model** (không tin suông): Conv2D SAME padding (stride 2,
    kernel 5) — TF SAME pad formula `pad_total=max((out-1)*stride+kernel-in,0)`,
    chia `pad_total//2` trước/`pad_total-pad_total//2` sau; Conv2DTranspose
    SAME — làm full valid transpose conv rồi CROP theo đúng công thức đảo
    ngược (tính pad như thể chiều ngược lại là forward conv, rồi cắt); STFT/
    ISTFT — `pad_end=True` của TF nghĩa là `num_frames=ceil(n/frame_step)`
    (không phụ thuộc frame_length), và `inverse_stft` với `window_fn` thường
    (không phải `inverse_stft_window_fn`) là overlap-add THÔ, không tự chia
    theo tổng bình phương window (khác `torch.istft` mặc định có COLA
    normalization) — đây là lý do code Spleeter cần hệ số bù thủ công
    `WINDOW_COMPENSATION_FACTOR=2/3`, phải tự viết ISTFT tay, không dùng
    `torch.istft()` trực tiếp.
  - Full pipeline (STFT → pad_and_partition theo T=512 → 2× U-Net PyTorch →
    Wiener-like mask normalize theo `separation_exponent` → mask extension
    zeros → ISTFT×2/3) chạy trên input thật, so với cùng input qua TF
    checkpoint gốc: **max abs diff 1.25e-6** (2 instrument) — đúng floating
    noise cho pipeline 24-layer conv + STFT/ISTFT, không phải xấp xỉ.
  - Weight lấy qua `tf.compat.v1.global_variables()` match tên (không dùng
    `get_tensor_by_name` trên tên biến trực tiếp — đó là resource handle,
    không phải giá trị, throw `numpy.void` type error).
- **Export ONNX (opset 17) chỉ phần U-Net/mask-network (không bao gồm STFT/
  ISTFT) — thành công, verify bằng `onnxruntime` thật:**
  - Op list export ra: **100% builtin ONNX** (`Conv`, `ConvTranspose`,
    `LeakyRelu`, `Relu`, `Sigmoid`, `Add`, `Mul`...) — không 1 custom op nào,
    khác hẳn TFLite (cần 4 Flex op cho STFT/IRFFT). Nghĩa là **không cần build
    native custom** cho ONNX Runtime — AAR Maven gốc (`:onnx:native_build:origin`
    đã tạo) chạy được thẳng, không cần lặp lại công Bazel/NDK đã làm cho
    TFLite Flex delegate.
  - Verify onnxruntime (Python) vs PyTorch: diff 1.1e-5 / 2.4e-7 — khớp.
  - Size: float32 78.7MB (2 instrument gộp 1 file) → **fp16 39.5MB** (convert
    bằng `onnxconverter_common.float16`) — khớp gần đúng số Music Splitter đã
    verify trước đó (~39MB, 19.68MB×2) → xác nhận độc lập approach đúng, không
    phải trùng hợp. fp16 vs float32 max diff trên mask ~0.018 (range [0,1]) —
    chưa test ảnh hưởng chất lượng audio nghe thật.
- **Quyết định kiến trúc phát sinh, CHƯA làm, cần quyết định tiếp**: model
  ONNX export ra **không bao gồm STFT/ISTFT** (khác `.tflite` hiện tại, có
  STFT/ISTFT ngay trong graph) — boundary này khớp với cách Music Splitter đặt
  tên file (`vocals.fp16.onnx`/`accompaniment.fp16.onnx` riêng, gợi ý chỉ chứa
  network). Hệ quả: cần viết STFT (windowing+FFT) và ISTFT (overlap-add,
  KHÔNG dùng COLA normalization, nhân thêm 2/3) bằng Kotlin — code MỚI hoàn
  toàn, Android không có FFT builtin, hiện chưa tồn tại vì TFLite tự làm việc
  này trong graph. Đây là việc thật cần làm thêm, không phải chi tiết nhỏ.
- **Script spike nằm ở scratchpad session
  (`/tmp/.../scratchpad/onnx_spike/`), CHƯA commit vào repo** — gồm
  `pytorch_pipeline.py` (full re-implementation + weight loader),
  `export_onnx.py`, `validate_padding.py`/`validate_padding2.py`/
  `validate_dilated.py`/`validate_stft.py`/`validate_istft.py` (validate từng
  primitive riêng lẻ trước khi ráp). Scratchpad có thể bị dọn giữa các session
  (đã xảy ra 1 lần trong session này với file khác) — nếu quay lại làm tiếp
  ONNX mà thấy script này mất, phải viết lại từ đầu theo đúng các bước đã ghi
  trong update này (đủ chi tiết để tái tạo).
- **How to apply**: nếu quyết định tiếp tục hướng ONNX, 2 việc còn lại là (1)
  viết STFT/ISTFT bằng Kotlin (việc mới, chưa từng làm trong project), (2)
  quyết định lưu script convert vào repo hay không (để tái tạo `.onnx` khi
  cần, giống cách README ghi lại bước rebuild Flex delegate AAR cho TFLite).
  Nếu KHÔNG tiếp tục, giữ nguyên TFLite — nhánh đó đã hardened xong (cancel/
  release, numThreads tuning) trong session này, không có gì cấp bách phải
  đổi.

**Update 2026-08-24 (tiếp) — đã viết STFT/ISTFT bằng Kotlin cho nhánh ONNX,
test-first, verify bằng số liệu Python/numpy thật, KẾT LUẬN: xong, đã có nền
DSP cần thiết, chưa nối vào `OnnxStemSeparator` (chưa làm, chưa được yêu
cầu):**
- Package mới `audio_stem_split/core/.../dsp/` (pure Kotlin, không phụ thuộc
  Android — cùng tinh thần `:core` "Hilt-unaware, safe to copy"): `Fft.kt`
  (radix-2 Cooley-Tukey, iterative, in-place, bit-reversal permute chuẩn),
  `RealFft.kt` (rfft/irfft qua Hermitian symmetry, không tính 2 lần), `Complex
  Spectrum.kt` (value carrier, KHÔNG dùng `data class` vì array property sẽ
  làm `equals()`/`hashCode()` tự sinh sai — so sánh theo reference thay vì
  nội dung), `SpectrogramTransform.kt` (forward/inverse khớp
  `tf.signal.stft(pad_end=True)`/`inverse_stft(window_fn=hann)` — đã validate
  bit-exact với TF thật trong spike trước, xem update phía trên).
- **2 hành vi dễ làm sai nếu chỉ "implement STFT theo trực giác", đã tránh
  được vì đã validate với TF thật trước khi viết Kotlin**: (1) frame count
  của `pad_end=True` là `ceil(n/frameStep)`, KHÔNG phụ thuộc `frameLength`
  (khác các thư viện STFT thường "drop" đoạn cuối không đủ 1 frame); (2)
  `inverse()` overlap-add THÔ, không tự chia theo tổng bình phương window
  (khác `torch.istft`/`librosa.istft` default có COLA normalization) —
  hệ số bù `WINDOW_COMPENSATION_FACTOR=2/3` CỐ Ý không nằm trong
  `SpectrogramTransform` (không phải property chung của STFT/ISTFT, chỉ là
  fudge riêng của Spleeter) — caller (`OnnxStemSeparator` tương lai) phải tự
  áp dụng.
- **Test-first, dùng đúng số liệu tham chiếu từ Python đã validate trước đó**
  (không tự nghĩ ra input rồi tự verify vòng tròn): `FftTest.kt` so với
  `numpy.fft.fft` cho input N=8 cụ thể; `SpectrogramTransformTest.kt` dùng
  1 signal dạng công thức closed-form (`0.3*sin(0.013*i)+0.15*sin(0.041*i+1)`,
  tái tạo được y hệt ở cả Python và Kotlin không cần transfer array lớn), so
  khớp frame 0/1/5 (đủ để chắc không chỉ đúng frame đầu) và giá trị
  reconstruct tại index 0-4/3000-3004 sau khi nhân hệ số 2/3 — toàn bộ 6 test
  pass ngay lần chạy đầu, không cần sửa gì (nhờ đã validate từng primitive
  riêng — Conv2D SAME, Conv2DTranspose SAME, STFT, ISTFT — trong Python
  trước khi viết Kotlin, xem update ONNX spike phía trên).
- **Việc còn lại, CHƯA làm**: chưa có `OnnxStemSeparator` (chưa implement
  `StemSeparator` interface bằng ONNX Runtime + `SpectrogramTransform` này +
  weight `.onnx` đã export). Nền DSP đã sẵn sàng, chỉ còn việc ráp: đọc mix
  waveform → `SpectrogramTransform.forward` mỗi channel → `pad_and_partition`
  theo T=512 → chạy 2 U-Net ONNX (`OrtSession`) → Wiener-like mask normalize
  (`separation_exponent=2`) → mask extension zeros → `SpectrogramTransform.inverse`
  × `2/3` → cắt về đúng độ dài waveform gốc. Toàn bộ logic này đã có sẵn bản
  Python tham chiếu bit-exact trong `pytorch_pipeline.py` (spike, ephemeral
  scratchpad) — port sang Kotlin nên bám sát đúng thứ tự đó, không suy luận
  lại từ đầu.

## Update 2026-08-24 — OnnxStemSeparator ráp xong + wire vào UI

- `OnnxStemSeparator.kt` (`:audio_stem_split:onnx:two_stem`) đã implement đầy đủ `StemSeparator`,
  port đúng pipeline đã verify bit-exact ở `pytorch_pipeline.py` (STFT → magnitude → loop segment
  batch=1 vì export không có `dynamic_axes` → `OrtSession.run()` → Wiener normalize → mask
  extension zeros → complex-multiply → ISTFT × 2/3). Model asset `spleeter_2stems_fp16.onnx`
  (39.5MB) đã copy từ scratchpad vào `src/main/assets/models/onnx/two_stem/` — không còn ở vùng
  ephemeral nữa.
- API ONNX Runtime dùng (`RunOptions.setTerminate`, `Result.get(String)` theo tên không theo
  index, `OrtException extends Exception` không phải `IllegalArgumentException`) đều verify qua
  `javap` decompile thật, không đoán.
- Đã wire nút "2-Stem ONNX" vào `StemSplitterScreen` (cùng row với TwoStemOriginal/
  TwoStemQuantize) + toàn bộ chuỗi DI/repository: `StemSplitEngineType.TwoStemOnnx` (enum mới) →
  `@TwoStemOnnxEngine` qualifier trong `StemSplitEngineModule` → `DefaultStemSplitterRepository`
  (3 `when` block: separate/cancel/outputDirNameFor) → `app/build.gradle.kts` thêm
  `implementation(project(":audio_stem_split:onnx:two_stem"))` + `noCompress += "onnx"`.
  `compileDebugKotlin` + `assembleDebug` (cả module lẫn `:app`) đều pass; đã unzip APK debug xác
  nhận asset `.onnx` + `libonnxruntime.so` (4 ABI) nằm đúng trong APK.
- **Nợ kỹ thuật còn treo, CHƯA làm** (đã nói rõ với user, chưa được yêu cầu làm tiếp):
  1. `OrtException` khi `setTerminate(true)` cắt run() giữa chừng — catch trong
     `DefaultStemSplitterRepository.separate()` hiện LUÔN map thành `InferenceFailed`, KHÔNG có
     message-text match như nhánh TFLite (`"cancel"`), vì message thật của ONNX Runtime khi bị
     terminate CHƯA được verify trên device thật. Nghĩa là nút Cancel cho engine ONNX hiện sẽ báo
     lỗi "inference failed" thay vì "cancelled" — cần test thật rồi sửa lại message match.
  2. Chưa verify ONNX Runtime có bug "session hỏng sau khi bị terminate, phải rebuild" giống bug
     đã tìm thấy + fix cho TFLite Interpreter không (xem [[project_stem_splitter_decisions]] phần
     ONNX spike trước). Chưa test thật.
  3. Chưa có unit test cho `OnnxStemSeparator` — có cơ hội test bằng JVM thuần (artifact
     `onnxruntime` khác `onnxruntime-android`) chạy thật file `.onnx` mà không cần device, TFLite
     không có cơ hội này. Chưa làm.
  4. APK debug hiện bundle `libonnxruntime.so` cho cả 4 ABI (~32MB riêng arm64) + model 39.5MB —
     tăng đáng kể APK size, cộng dồn với 6 model .tflite đã có từ trước. Chưa tối ưu (ABI split
     hoặc PAD on-demand download — đã thảo luận PAD trước đó trong session này).

## Update 2026-08-24 — four_stem ONNX xong, generalize OnnxStemSeparator sang N instrument

- Fetch thật `4stems.json`/`5stems.json` từ Spleeter repo xác nhận: 4stems dùng `model.type:
  "unet.unet"` (giống two_stem, sigmoid độc lập mỗi instrument) NHƯNG activation override thành
  `ELU` (cả conv lẫn deconv) — khác default LeakyReLU/ReLU mà `pytorch_pipeline.py` (two_stem) đã
  hardcode. 5stems dùng `"unet.softmax_unet"` — đọc `unet.py` + `model_init.py` xác nhận
  `_build_manual_output_waveform` (Wiener-ratio normalize) chạy y hệt PHÍA SAU cả hai loại model,
  chỉ khác bước tạo "output" mỗi instrument: `unet.unet` = sigmoid(logit)*mix, `softmax_unet` =
  softmax_qua_N_instrument(logit)*mix. Nghĩa là downstream Kotlin (Wiener-ratio, mask extension,
  complex-multiply, ISTFT) generalize được cho cả 3 loại, chỉ khác cách bake activation vào lúc
  export ONNX.
- Weight offset pattern xác nhận qua `dump_vars.py`/`find_outputs.py` trên checkpoint 4stems thật:
  instrument thứ i (0-indexed, theo `instrument_list` trong 4stems.json = ["vocals","drums",
  "bass","other"]) dùng `conv_offset=7*i, bn_offset=12*i, deconv_offset=6*i` — đúng pattern đã
  dùng cho two_stem's instrument thứ 2 (7/12/6), tổng quát hóa sạch. Output tensor TF thật:
  `strided_slice_13/23/33/43` (pattern `13+10*i`).
- Validate bit-exact PyTorch-vs-TF-checkpoint pass ngay lần đầu (max diff ~4.8e-7, giống order of
  magnitude two_stem) — nhờ verify offset/activation trước khi viết code thay vì đoán.
- Export ONNX (`spleeter_4stems.onnx`, 157.5MB float32) → fp16 (`spleeter_4stems_fp16.onnx`,
  79MB) — đúng khoảng gấp đôi two_stem's 39.5MB (hợp lý, 4 instrument = gấp đôi 2). fp16 vs fp32
  diff nhỏ (~0.013 max trên [0,1] mask) khi test với input magnitude thực tế (non-negative);
  LƯU Ý: test với `torch.randn` (có giá trị âm, không phải magnitude thực) từng ra NaN ở nhánh
  "bass" — nguyên nhân là input không thực tế (magnitude luôn ≥0) gây BatchNorm/sqrt edge case
  fp16 overflow, KHÔNG phải bug of model — nhưng đây là rủi ro fp16 tồn tại (dynamic range hẹp
  hơn fp32) nếu audio đầu vào có biên độ cực đoan, chưa stress-test kỹ trên input thực tế đa dạng.
- **Refactor quan trọng**: tách `OnnxStemSeparator` ra khỏi `:onnx:two_stem` thành module mới
  `:audio_stem_split:onnx:core`, generalize từ hardcode 2 instrument (`vocals`/`accompaniment`)
  sang `instruments: List<String>` bất kỳ — mirror chính xác pattern `SpleeterStemSeparator` đã
  dùng cho TFLite (1 class chung, tham số hóa qua config, share bởi mọi module stem-count). Quy
  ước: output tensor ONNX luôn tên `"{instrument}_mask"`, class không cần biết instrument đến từ
  sigmoid hay softmax. `:onnx:two_stem`/`:onnx:four_stem` giờ chỉ chứa Config (`MODEL_ASSET_PATH`,
  `ENGINE_TAG`, `INSTRUMENTS`) + asset — `api(project(":audio_stem_split:onnx:core"))`.
- Đã wire đầy đủ: `StemSplitEngineType.FourStemOnnx` → `@FourStemOnnxEngine` qualifier →
  `DefaultStemSplitterRepository` (3 when-block, tái dùng nguyên `toFourStemDomain()` có sẵn vì
  key "vocals"/"drums"/"bass"/"other" khớp encoding TFLite four_stem) → nút "4-Stem ONNX" chung
  row với "2-Stem ONNX" (2 nút, tránh lặp bug overflow row 3 nút đã gặp trước đó).
  `compileDebugKotlin` + `assembleDebug` pass; unzip APK confirm cả 2 asset .onnx + `libonnxruntime.so`
  dùng chung (không nhân đôi native lib).
- Còn treo y nguyên 4 tech debt từ update trước (chưa động tới): OrtException cancel-message chưa
  verify, session-corruption-after-cancel chưa test thật, chưa unit test `OnnxStemSeparator`,
  APK size (giờ đã +79MB nữa từ four_stem, tổng ONNX riêng ~190MB: 2 model + 4 ABI native lib).
- **CHƯA làm five_stem** — cần thêm: bake softmax (không phải sigmoid) vào PyTorch export module
  cho 5 instrument, dùng cùng `apply_unet_pytorch` với ELU (giống four_stem) nhưng activation
  cuối là softmax qua trục instrument thay vì sigmoid độc lập từng instrument. Kotlin
  `OnnxStemSeparator` KHÔNG cần sửa gì thêm — đã generalize sẵn để nhận N mask "đã sẵn sàng nhân
  với mix magnitude" bất kể nguồn gốc sigmoid/softmax.

## Update 2026-08-24 — five_stem ONNX xong; 4stem ONNX ĐANG CRASH (chưa fix, theo yêu cầu user)

- User báo "onnx 4stem có crash" nhưng chủ động yêu cầu làm tiếp five_stem trước, fix crash sau —
  CHƯA có log/stacktrace nào được thu thập, chưa điều tra nguyên nhân. Đây là bug ưu tiên cần hỏi
  user xin logcat/repro steps ở lần làm việc tiếp theo trước khi đoán nguyên nhân.
- five_stem: fetch checkpoint thật, `dump_vars.py` xác nhận 0 Sigmoid + 1 Softmax + 60 Elu (12×5)
  — đúng như dự đoán từ `5stems.json` (`model.type: "unet.softmax_unet"`, activation ELU). Offset
  pattern giống hệt four_stem (`7*i/12*i/6*i`), output tensor TF thật `strided_slice_{18,28,38,48,58}`
  (pattern `18+10*i`, khác base offset four_stem nhưng cùng step +10 — do graph có thêm
  Softmax/stack ops đẩy số thứ tự lên, không phải bug).
- Validate bit-exact PyTorch (softmax qua 5 instrument, KHÔNG phải sigmoid độc lập) vs TF checkpoint
  thật pass ngay lần đầu (max diff ~4e-7). Bake softmax vào PyTorch export module (`torch.stack` 5
  logit theo dim cuối → `torch.softmax(dim=-1)` → mỗi instrument lấy 1 slice) — verify thêm sau
  export: tổng mask 5 instrument lệch 1.0 chỉ ~2.4e-7 (float32) / ~4e-4 (fp16), xác nhận property
  softmax sống sót qua export + quantize.
- Export `spleeter_5stems.onnx` (196.9MB float32) → fp16 `spleeter_5stems_fp16.onnx` (98.8MB).
  Test fp16 với input magnitude thực tế (non-negative): không NaN, diff nhỏ (~0.011 max).
- **Kotlin: KHÔNG cần sửa `OnnxStemSeparator`** — đúng như dự đoán, class đã generalize sẵn N
  instrument từ update four_stem, chỉ cần Config mới (`FiveStemOnnxConfig`: MODEL_ASSET_PATH,
  ENGINE_TAG, `INSTRUMENTS = ["vocals","piano","drums","bass","other"]`).
- Module mới `:audio_stem_split:onnx:five_stem` (chỉ Config + asset, `api(":onnx:core")`) — wire
  đủ 6 điểm: enum `FiveStemOnnx`, `@FiveStemOnnxEngine` qualifier, `DefaultStemSplitterRepository`
  (tái dùng `toFiveStemDomain()` có sẵn, key khớp), `app/build.gradle.kts`, UI, string resource.
- **Fix tận gốc bug UI row-overflow** (thay vì tiếp tục né bằng cách chia row thủ công mỗi lần
  thêm engine — không scale): thêm `horizontalScroll(rememberScrollState())` vào `Row` trong
  `EngineSelectorRow` (`StemSplitterScreen.kt`). Giờ cả 3 engine ONNX (`TwoStemOnnx`/`FourStemOnnx`/
  `FiveStemOnnx`) nằm chung 1 row, an toàn với mọi số lượng nút tương lai.
- `compileDebugKotlin` + `assembleDebug` pass; APK chứa đủ 3 asset .onnx (39.5+79+98.8 = ~217MB
  riêng model, cộng ~70MB native lib onnxruntime dùng chung 4 ABI).
- Tech debt tổng hợp hiện tại: (1) **4stem ONNX crash — CHƯA điều tra**, (2) OrtException
  cancel-message chưa verify message thật, (3) session-corruption-after-cancel chưa test thật,
  (4) chưa có unit test `OnnxStemSeparator` nào (kể cả two/four/five), (5) APK size ONNX riêng đã
  ~290MB tổng (model+native lib), chưa tối ưu.

## Update 2026-08-24 — Fix crash 4stem ONNX (OOM) bằng flat array, verify thật trên Pixel 9

- Root cause xác nhận qua log logcat thật (không đoán): `OutOfMemoryError` tại
  `OnnxStemSeparator.reconstructWaveform`/`separate()` khi chạy FourStemOnnx (sau khi TwoStemOnnx
  chạy ổn). Nguyên nhân: `ratioByInstrument: Array<Array<Array<DoubleArray>>>` (4 tầng nested
  array) size ∝ số instrument × frameCount × FFT_BINS(2049), phải sống hết suốt `separate()`
  (Wiener-ratio cần tất cả instrument cùng lúc) — four_stem gấp đôi memory two_stem (~170MB vs
  ~85MB) cộng hàng chục nghìn object `Array`/`DoubleArray` con (mỗi frame×channel một object
  riêng) gây GC overhead + fragment heap, vượt hard limit 512MB.
- Đã viết `OnnxEngineDeviceTest.kt` (androidTest, giữ lại trong repo như benchmark one-off, giống
  pattern `InterpreterOptionsBenchmarkTest`) chạy tuần tự cả 3 engine ONNX trên sample audio thật,
  chạy qua `./gradlew :app:connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=...`,
  bắt logcat bằng `adb -s <serial> logcat -c` trước / `logcat -d` sau — tái hiện crash NGAY LẦN
  ĐẦU với stacktrace chính xác đến dòng.
- Cũng thêm timing log vào `OnnxStemSeparator.separate()` (trước đó class hoàn toàn không log gì)
  — Log.d tag `OnnxStemSeparator[$engineTag]`, breakdown sessionInit/stft/inference/reconstruct/
  total. Phát hiện: STFT+reconstruct (Kotlin thuần) chiếm đa số thời gian, ONNX inference thật
  chỉ ~2-5s trong tổng 27-57s.
- **Fix**: đổi toàn bộ structure instrument-scaled từ nested Array sang flat 1D array + index tay:
  - `magnitude`: `DoubleArray(frameCount*CHANNEL_COUNT*FBINS)`, index `(frame*CHANNEL_COUNT+channel)*FBINS+bin`.
  - `ratioByInstrument`: `Array(instruments.size) { DoubleArray(frameCount*CHANNEL_COUNT*FFT_BINS) }`
    — chỉ còn 1 tầng Array (size = N instrument, nhỏ), không còn nested theo frame/channel nữa.
  - ONNX mask output: đổi từ `result.get(name).get().value as Array<Array<Array<FloatArray>>>`
    (materialize full nested array copy mỗi segment) sang `(result.get(name).get() as OnnxTensor)
    .floatBuffer` (đọc thẳng native memory, verify method tồn tại qua `javap` trên
    onnxruntime-android AAR thật) — tránh churn ~1M-element nested array mỗi segment.
  - Giải phóng sớm: sau khi `reconstructWaveform(ratioByInstrument[i])` xong, gán
    `ratioByInstrument[i] = EMPTY_RATIO_MASK` ngay để GC thu hồi trước khi xử lý instrument tiếp
    theo, thay vì giữ tất cả N mảng sống tới cuối `separate()`.
  - `stftByChannel`/`ComplexSpectrum`/`SpectrogramTransform` (module `:core/dsp` dùng chung, có
    unit test) KHÔNG đổi — chỉ flatten phần local trong `OnnxStemSeparator`, đúng scope crash.
- **Verify thật trên Pixel 9 (không chỉ tin code review)**: chạy lại `OnnxEngineDeviceTest` sau
  fix — PASS, cả 3 engine (Two/Four/Five-Stem) chạy hết, không OOM. Timing: reconstruct tăng gần
  tuyến tính theo số instrument (16.6s→32.8s→42.2s cho 2/4/5 instrument) — đúng kỳ vọng thuật
  toán (mỗi instrument cần 1 lượt ISTFT riêng), không còn tăng phi tuyến/crash như trước.
- Tech debt còn lại (không đổi): OrtException cancel-message chưa verify, session-corruption-
  after-cancel chưa test, chưa unit test JVM cho `OnnxStemSeparator`, tổng thời gian xử lý ONNX
  khá chậm so với TFLite (chưa tối ưu — có thể do numThreads/session options ONNX chưa tune, ONNX
  Runtime CPU EP chưa dùng fp16 kernel thật sự nên fp16 model không nhanh hơn fp32 về compute).

## Update 2026-08-24 — Thêm numThreads/useXNNPACK cho OnnxStemSeparator, benchmark: không giúp gì

- Thêm `_numThreads: Int? = null` / `_useXNNPACK: Boolean? = null` vào constructor
  `OnnxStemSeparator` (mirror `SpleeterStemSeparator`, cùng naming convention `_` để tránh bug
  shadowing trong `apply {}` — dù verify `OrtSession.SessionOptions` không có getter cùng tên nên
  rủi ro shadowing thực ra không tồn tại ở đây, vẫn giữ convention cho nhất quán). API dùng:
  `SessionOptions.setIntraOpNumThreads(Int)` / `.addXnnpack(emptyMap())` — verify tồn tại qua
  `javap` trên AAR thật (`onnxruntime-android-1.29.0.aar`). Đã wire `_numThreads = numThreads`
  (biến core-count-2 có sẵn) vào cả 3 provider ONNX trong `StemSplitEngineModule`. `_useXNNPACK`
  KHÔNG wire giá trị cụ thể (giữ null) — theo đúng tiền lệ TFLite (benchmark không thấy lợi ích).
- **Benchmark thật trên Pixel 9** (`OnnxEngineDeviceTest.benchmarkNumThreads()`, FourStemOnnx,
  cùng `sample_song.wav`, 2 lần/candidate): default 49.14s, numThreads=6 → 48.85s (chưa tới 1%
  khác biệt), numThreads=8 → 51.1s (CHẬM hơn default). **Kết luận: tuning numThreads gần như vô
  dụng cho ONNX**, khác hẳn TFLite (numThreads=6 nhanh hơn default ~17%). Lý do: inference thần
  kinh thật chỉ chiếm 2-5s trong tổng 45-57s — phần lớn thời gian nằm ở STFT/ISTFT/Wiener-ratio
  Kotlin đơn luồng, tăng thread cho ONNX chỉ tối ưu được phần nhỏ không đáng kể của tổng thời gian.
- Hệ quả cho hướng tối ưu tiếp theo: muốn ONNX nhanh hơn thật sự phải tối ưu phần Kotlin DSP
  (song song hoá STFT/ISTFT giữa các instrument/channel qua coroutine, hoặc bake STFT/ISTFT vào
  lại graph ONNX như TFLite đã làm — nhưng cách 2 sẽ cần custom op, mất chính lợi thế "không cần
  native build tùy biến" đã có), KHÔNG phải tune thread cho session ONNX.
- So sánh táo-với-táo đã chốt (cùng `sample_song.wav`, cùng FourStem): TFLite quantize tuned
  (12.0s) vs ONNX fp16 (45.8-49.1s) — chậm hơn ~4x, không phải ước lượng mơ hồ "chậm hơn đáng kể"
  như viết ban đầu trong artifact README.

## Update 2026-08-24 — Song song hoá reconstruct (ISTFT) theo instrument bằng coroutine

- Parallelize bước `reconstructWaveform` (ISTFT per-instrument, trong `separate()`'s result-building
  loop) — độc lập hoàn toàn giữa các instrument (mỗi cái chỉ đọc `ratioByInstrument[i]` riêng +
  `stftByChannel` chung read-only), nên có thể chạy đồng thời qua coroutine thay vì tuần tự.
- **Thử KHÔNG giới hạn concurrency trước (N instrument cùng lúc) → crash OOM ngay ở FourStemOnnx
  lần chạy đầu tiên trên device thật** — tái hiện đúng bug OOM tuần trước, vì chạy song song nghĩa
  là toàn bộ N mảng `ratioByInstrument[i]` (~40MB/cái) phải sống cùng lúc suốt pha reconstruct,
  thay vì được giải phóng dần từng cái một như bản tuần tự (bản tuần tự giải phóng ngay sau khi
  dùng xong mỗi instrument — đây chính là optimization đã làm ở fix OOM trước, và chạy song song
  không giới hạn vô tình undo optimization đó). Đây LÀ trade-off đã lường trước lúc nhận yêu cầu,
  và đã bị xác nhận đúng bằng test thật, không chỉ suy luận.
- **Fix**: `Dispatchers.Default.limitedParallelism(MAX_PARALLEL_RECONSTRUCTIONS = 2)` — giới hạn
  tối đa 2 instrument tái tạo đồng thời bất kể N là bao nhiêu, verify lại trên device cả 3 engine
  (two/four/five-stem) pass, không OOM.
- Kết quả benchmark thật (Pixel 9, `sample_song.wav`, so sánh field `reconstruct` trong log
  `OnnxStemSeparator`):
  - 2-stem: 16.6s → 8.5s (~2x, cap=2 = full parallel cho 2 instrument)
  - 4-stem: 32.8s → 18.1s (~1.8x)
  - 5-stem: 42.2s → 32.9s (~1.3x, cap=2 nghĩa là 5 instrument phải chạy làm 3 đợt: 2+2+1)
  - Tổng thời gian (`total`): 2-stem 27.6s→19.5s, 4-stem 45.8s→34.7s, 5-stem 56.6s→52.5s.
- Cần thêm `implementation(libs.kotlinx.coroutines.android)` vào `:audio_stem_split:onnx:core`'s
  build.gradle.kts (trước đó chỉ có transitively qua `:audio_stem_split:core` nhưng khai bằng
  `implementation` ở đó nên không lộ ra ngoài — phải khai trực tiếp).
- Vẫn còn dư địa tối ưu: `MAX_PARALLEL_RECONSTRUCTIONS=2` là con số verify-an-toàn đầu tiên tìm
  được, chưa thử 3 (có thể vẫn an toàn và nhanh hơn nữa cho four/five-stem) — chưa test.

## Update 2026-08-24 — Thử MAX_PARALLEL_RECONSTRUCTIONS=3: cũng OOM, revert về 2

- Thử tăng `MAX_PARALLEL_RECONSTRUCTIONS` từ 2 lên 3 để xem có nhanh hơn không — verify thật trên
  Pixel 9: **crash OOM ngay ở FourStemOnnx**, y hệt lỗi khi thử unbounded. 2-stem vẫn ổn (cap=3
  không khác gì cap=2 khi chỉ có 2 instrument). Kết luận: **2 không phải là số bảo thủ chọn đại,
  mà là ceiling thật của heap budget này** — đã verify cả 2 hướng (2 an toàn, 3 và unbounded đều
  OOM). Revert về `MAX_PARALLEL_RECONSTRUCTIONS = 2`, đã compile lại xác nhận.
- Ghi chú cho tương lai: đừng tăng số này mà không re-verify trên device thật — đã đổi comment
  trong code để nói rõ đây là giá trị đo được, không phải giả định.

## Update 2026-08-24 — Đo thêm TFLite 2-stem/5-stem numThreads, hoàn thiện bảng so sánh timing

- Mở rộng `InterpreterOptionsBenchmarkTest` thêm `benchmarkTwoStemAndFiveStemQuantize()` (default
  vs numThreads=6, 2 lần/candidate, cùng `sample_song.wav`) để lấp chỗ trống — trước đó chỉ có số
  đo cho FourStemQuantize. Kết quả thật trên Pixel 9:
  - TwoStemQuantize: default 8.77s, numThreads=6 → 7.6s
  - FiveStemQuantize: default 18.64s, numThreads=6 → 15.9s
  (FourStemQuantize đã có từ trước: default 14.7-14.9s, numThreads=6 → 12.0s)
- Bảng so sánh táo-với-táo hoàn chỉnh (TFLite tuned vs ONNX đã tối ưu cap=2), đã cập nhật vào
  artifact README: ONNX chậm hơn TFLite tuned ~2.6-2.9x (2-stem), ~2.9x (4-stem), ~3.3x (5-stem) —
  pattern nhất quán qua cả 3 tier, không phải chỉ đúng ngẫu nhiên ở 4-stem.
- Artifact cũng đã fix 1 lỗi trình bày: bảng gộp "stem tier + native build" trước đó khiến người
  đọc hiểu lầm `:native_build:custom`/`:native_build:origin` là riêng của 5-stem (vì nhóm "Native
  build" nằm ngay sau nhóm "5-stem" trong bảng, không có phân cách rõ) — đã tách thành 2 bảng
  riêng: "Model theo từng stem tier" và "Native build runtime (dùng chung cho cả 3 tier)".

## Update 2026-08-24 — Fix bug "ONNX stem không cancel được"

- User báo cancel không hoạt động cho ONNX. Root cause đọc code tìm ra ngay: `activeRunOptions`
  (thứ duy nhất `cancel()` cũ tác động qua `setTerminate(true)`) chỉ non-null trong lúc
  `activeSession.run()` một segment đang chạy — chỉ 2-5s trong tổng 20-50s. Toàn bộ pha STFT
  (~8.5s) và reconstruct (18-33s, phần lớn thời gian) hoàn toàn không có checkpoint nào để nhận
  cancel request — bấm "Hủy" lúc đó là no-op tuyệt đối, không phải bug tinh vi cần repro nhiều lần.
- **Fix**: thêm `class OnnxSeparationCancelledException : RuntimeException(...)` (khác biệt rõ với
  `OrtException`/TFLite's `IllegalArgumentException`, không dựa vào message-match) + cờ
  `@Volatile cancelRequested` (reset đầu mỗi `separate()`, set trong `cancel()`/`release()` cùng
  lúc với `setTerminate(true)`) + hàm `checkNotCancelled()` rải ở: giữa 2 channel STFT, trước mỗi
  segment trong inference loop, đầu mỗi coroutine reconstruct, giữa 2 channel trong
  `reconstructWaveform`. `DefaultStemSplitterRepository` thêm catch riêng
  `OnnxSeparationCancelledException` → `Result.Failure(StemSplitterError.Cancelled)`.
- **Verify thật trên Pixel 9** (2 test mới trong `OnnxEngineDeviceTest`, cancel lúc đang ở pha
  STFT và lúc đang ở pha reconstruct): cả 2 đều pass — cancel lúc 3000ms → trả về sau 5682ms (~2.7s
  sau cancel); cancel lúc 15000ms → trả về sau 18681ms (~3.7s sau cancel). Trước fix, cả 2 case này
  sẽ chạy hết toàn bộ ~34-46s bất kể cancel.
- Vẫn còn treo: chưa verify case cancel đúng lúc ONNX `run()` đang chạy (window rất nhỏ) có làm
  hỏng session cần rebuild giống bug TFLite Interpreter đã tìm thấy hay không — 2 test mới không
  target chính xác window đó (chỉ trúng may rủi), cần test riêng nếu muốn verify đầy đủ.

## Update 2026-08-24 — Benchmark thật vs app đối thủ (ai.vocal.remover.splitter.karaoke.instrumental)

- Pull APK thật của app đối thủ (`ai.vocal.remover.splitter.karaoke.instrumental`, cài sẵn trên
  Pixel 9 để research) qua `adb pull` (base+split_config.arm64_v8a+split_install_time_asset_pack).
  Phát hiện quan trọng:
  - Native lib `libSpleeter.so` (488KB) — họ build native C++ riêng cho Spleeter, KHÔNG dùng
    TFLite/ONNX Runtime qua Java binding như mình (tránh JNI marshalling overhead).
  - Model asset trong `split_install_time_asset_pack.apk` (Play Feature Delivery, install-time):
    `assets/models/spleeter_2stems_11k_v1.splx` — 78.6MB, format riêng (`.splx`, không phải
    `.tflite`/`.onnx` chuẩn). Tên "11k" gợi ý chạy ở 11kHz — chỉ ¼ resolution so với 44.1kHz
    Spleeter gốc mình đang dùng. CHƯA verify chắc 100% (chỉ suy từ tên file), nhưng nhất quán với
    kết quả benchmark tốc độ cực nhanh dưới đây.
  - App hỗ trợ 2-stem Instrumental + Acapella (≈ vocals) — khớp đúng tier `two_stem` của mình.
  - Output là `.mp3` (không phải FLAC như nghi ban đầu — user tự phát hiện và tự đính chính).
- **Benchmark thật, đo bằng cách bấm nút thật qua `adb shell input tap` + đọc timestamp file output
  (`adb shell stat`) trừ timestamp lúc tap** (không phải log app, vì là app đối thủ không control
  được code):
  - File 73 phút (`Merge_20260824_083734.mp3`, 4381.7s, size ~73MB): app đối thủ xử lý xong trong
    **49.2s** → **~89x realtime**.
  - File ~15.89 phút (`Merge_20260822_133848i.mp3`, 953.18s, size 15.4MB): app đối thủ **37s**
    (~25.8x realtime) vs mình **TFLite 2-stem quantize 184s/3'04"** (~5.18x realtime) — **đối thủ
    nhanh hơn mình ~5x trên file thật, dài thật** (không phải chỉ đúng ở clip test 30s nhân tạo).
  - **Đã loại trừ khả năng xử lý server/cloud**: check `adb shell dumpsys connectivity` lúc đang xử
    lý cho thấy `Active default network: none` — máy hoàn toàn offline, nên 89x/25.8x realtime là
    tốc độ on-device thật 100%, không phải round-trip server.
  - Ghi chú thêm: 184s thực đo (2-stem quantize TFLite trên file 15.89 phút) *tốt hơn* con số ngoại
    suy tuyến tính từ benchmark clip 30s (~241.5s) — vì overhead cố định (sessionInit, load model)
    được amortize trên file dài hơn, chiếm tỷ trọng nhỏ hơn. Vẫn kém đối thủ ~5x.
- Kết luận: gap tốc độ với đối thủ là THẬT, nhất quán qua nhiều file/độ dài khác nhau, không phải
  do mono/stereo (đã tự test loại trừ ở update trước) hay cloud (đã loại trừ ở đây). Nguyên nhân
  nhiều khả năng nhất: native C++ implementation + sample rate/architecture rút gọn (11kHz?, model
  nhỏ hơn) — đổi lại rất có thể đánh đổi chất lượng tách, đặc biệt high-frequency, nhưng CHƯA verify
  bằng nghe thử thật (chỉ là suy luận có cơ sở, không phải đã confirm).

## Update 2026-08-24 — ĐÍNH CHÍNH: giả thuyết "11k = sample rate thấp" của app đối thủ bị bác bỏ

- Giả thuyết trước ("spleeter_2stems_11k_v1.splx" → 11kHz internal sample rate → giải thích tốc độ
  nhanh) chỉ dựa vào TÊN FILE, chưa verify bằng dữ liệu thật — đúng kiểu suy luận cần tránh theo
  văn hoá "verify, don't assume" xuyên suốt project này.
- Đã tự verify bằng bằng chứng khách quan: pull file output thật của họ
  (`Merge_20260824_083734 (Instrumental)...mp3`, file 73 phút), dựng spectrogram bằng
  `ffmpeg -lavfi showspectrumpic`. Kết quả: **tín hiệu có năng lượng rõ ràng tới ~15-17kHz, KHÔNG
  có cutoff cứng ở ~5.5kHz** (Nyquist limit nếu thật sự 11025Hz). Giả thuyết bị bác bỏ trực tiếp.
- Kết luận đã đính chính: "11k" trong tên file nhiều khả năng KHÔNG phải sample rate (có thể là số
  lượng track train, version nội bộ, hoặc tham số kiến trúc khác) — chưa biết chính xác là gì.
- Đã tự làm 2 thí nghiệm (JVM DSP speed test giảm sample rate 4x, và test thật app mình với file
  audio resample 11kHz) chứng minh RÕ RÀNG rằng NẾU giảm sample rate thật sự thì sẽ nhanh hơn đáng
  kể (~3.5-5x tuỳ theo có scale frame_length hay không) — nhưng đây là thí nghiệm ĐỘC LẬP dùng
  model/audio của MÌNH để hiểu cơ chế, KHÔNG phải bằng chứng cho việc đối thủ có làm vậy hay không.
  Phải phân biệt rõ 2 việc: "cơ chế này CÓ THỂ giải thích tốc độ nhanh" (đã chứng minh khả thi bằng
  thí nghiệm riêng) vs "đối thủ THỰC SỰ làm vậy" (đã bác bỏ bằng spectrogram thật).
- Nguyên nhân tốc độ nhanh của đối thủ (~25-89x realtime, vẫn đúng, đã verify kỹ ở update trước)
  quay lại còn 2 khả năng CHƯA loại trừ, chưa verify thêm: (1) native C++ implementation
  (`libSpleeter.so`, tránh JNI overhead), (2) kiến trúc model nhỏ gọn hơn Spleeter gốc dù vẫn chạy
  ở 44.1kHz đầy đủ. Chưa có cách verify 2 giả thuyết này mà không đụng tới IP của họ (đã từ chối ý
  tưởng decompile+chạy model của họ trước đó, đúng lý do license/IP).
- Chất lượng tách của đối thủ ("kết quả kém hay không") — CHƯA verify, chỉ mới xem spectrogram
  full-mix content (còn nguyên nhạc, không phải nghe thử A/B chất lượng TÁCH). Cần nghe thử/so
  sánh trực tiếp mới kết luận được, chưa làm.

## Update 2026-08-24 — Xác nhận native C++ là nguyên nhân chính (không phải sample rate)

- Sau khi bác bỏ giả thuyết 11kHz bằng spectrogram+đo định lượng (update trước), verify tiếp giả
  thuyết native C++ bằng thực nghiệm sạch — viết `native_fft.cpp` (NDK/CMake, module mới
  `:audio_stem_split:native_fft_experiment`, KHÔNG wire vào production, chỉ dùng cho benchmark)
  mirror CHÍNH XÁC thuật toán `Fft.kt` (radix-2 Cooley-Tukey, cùng bit-reverse permute, cùng cấu
  trúc butterfly stage) — để so sánh thuần "ngôn ngữ/runtime", không lẫn khác biệt thuật toán.
- Benchmark thật trên Pixel 9 (`NativeFftBenchmarkTest`, đặt trong
  `:audio_stem_split:core/src/androidTest` vì `Fft` là `internal` trong module đó — không sửa
  visibility production code chỉ để test): 2584 lần FFT 4096-point (≈ 1 pha STFT của clip 30s ×
  2 channel), 3 lần chạy:
  - Kotlin: 9593/9478/9405 ms
  - Native C++: 2824/2830/2805 ms
  - **Speedup nhất quán ~3.35-3.40x** (trung bình ~3.37x)
- **Kết luận cuối cho investigation "vì sao đối thủ nhanh"**: gap thực đo (~5x cho file dài thật,
  TFLite tuned 184s vs đối thủ 37s) chủ yếu do **native C++ implementation** (verify bằng thực
  nghiệm sạch ~3.4x, không đụng IP đối thủ) — KHÔNG phải giảm sample rate (đã bác bỏ bằng bằng
  chứng phổ tần thật ở update trước). Phần dư nhỏ (~1.5x) hợp lý đến từ overhead khác trong pipeline
  (JNI marshalling của ONNX/TFLite Java binding, các bước xử lý mảng khác ngoài FFT thuần) — chưa
  tách riêng đo được, nhưng không cần thiết nữa vì đã xác định đúng nguyên nhân chính.
- Setup kỹ thuật ghi nhớ cho lần sau nếu cần viết native code khác: `std::swap<double>` gây lỗi
  linker "undefined hidden symbol" trên NDK 27 + `-static-libstdc++` + `-O3` (nghi do libc++ header-
  only template không export đúng dưới config này) — fix bằng cách tự viết swap thủ công (3 dòng),
  không cần debug sâu nguyên nhân linker vì có thể né hoàn toàn.
- Module `:audio_stem_split:native_fft_experiment` là module NGHIÊN CỨU, không dùng cho production
  — không wire vào `:app` (đã revert khỏi app/build.gradle.kts), chỉ dùng qua
  `:audio_stem_split:core`'s androidTest.

## Update 2026-08-24 — NNAPI delegate: thử, crash cứng, đã gỡ hoàn toàn (giống tiền lệ GPU delegate)

- Verify trước khi code: `NnApiDelegate` + `TfLiteNnapiDelegateCreate` xác nhận CÓ compiled trong
  `:native_build:custom`'s .so thật (qua `nm`/`strings`, không bị Bazel custom scoping strip) — nên
  không phải lỗi thiếu symbol.
- Implement `_useNnapi: Boolean?` param cho `SpleeterStemSeparator` (mirror `_numThreads`/
  `_useXNNPACK`), thêm `NnApiDelegate()` vào `Interpreter.Options()` khi true, cleanup đúng thứ tự
  (đóng Interpreter trước, delegate sau) ở cả rebuild-after-cancel lẫn `release()`.
- **Benchmark thật trên Pixel 9 → CRASH cứng, không phải chỉ "không có lợi" như GPU delegate**:
  ```
  I/Manager: Found interface google-edgetpu (version = 2.0)   ← máy CÓ Edge TPU thật
  E/TestRunner: java.lang.IllegalArgumentException: Internal error: Error applying delegate:
      at org.tensorflow.lite.NativeInterpreterWrapper.createInterpreter(Native Method)
  ```
  Lỗi ngay lúc tạo `Interpreter`, message chung chung không rõ nguyên nhân cụ thể.
- Giả thuyết nguyên nhân (chưa verify sâu hơn, đủ để kết luận không đáng theo đuổi tiếp): model
  này đã áp Flex delegate (SELECT_TF_OPS) để xử lý custom op — kết hợp 2 delegate rewrite-graph
  (Flex + NNAPI) trên cùng 1 Interpreter là combo dễ vỡ; NNAPI thường kỳ vọng graph builtin nguyên
  bản, không phải graph đã bị Flex delegate partition trước. Vì kiến trúc Spleeter buộc phải dùng
  Flex (STFT/IRFFT không phải builtin op), NNAPI nhiều khả năng KHÔNG BAO GIỜ hoạt động được với
  dòng model này, không phải vấn đề cấu hình có thể fix.
- **Đã gỡ hoàn toàn** code NNAPI khỏi `SpleeterStemSeparator`/`InterpreterOptionsBenchmarkTest` —
  đúng tiền lệ GPU delegate của project (thử → không khả thi → gỡ sạch, không để code chết). Verify
  compile lại sạch sau khi gỡ.
- Còn lại 1 hướng chưa thử cho TFLite: **full-integer quantization với calibration dataset** (khác
  training — chỉ cần audio đại diện bất kỳ, không cần label/stem, không vướng license) — chưa làm.

## Update 2026-08-25 — NNAPI cho ONNX: chạy được (không crash) nhưng không có lợi ích, đã gỡ

- Áp dụng đúng bài học từ TFLite: thử NNAPI cho ONNX (`SessionOptions.addNnapi()`, verify tồn tại
  qua javap trước đó) vì đồ thị ONNX 100% standard op, không có Flex-delegate-equivalent nên không
  bị đúng conflict đã làm NNAPI-TFLite crash.
- **Kết quả**: không crash (khác hẳn TFLite) — nhưng benchmark thật trên Pixel 9 (FourStemOnnx,
  2 lần/candidate) cho thấy **không có lợi ích tốc độ**:
  ```
  useNnapi=default: avgMs=34602.5
  useNnapi=true:    avgMs=35449.0   (chậm hơn ~2.4%, nằm trong nhiễu đo)
  ```
  Breakdown `inference` (thời gian ONNX chạy thật) gần như y hệt giữa 2 case (~3.9-4.1s) — nhiều
  khả năng NNAPI fallback về CPU execution y hệt default, chỉ khác không crash.
- Đã gỡ hoàn toàn code (`_useNnapi` param, `addNnapi()` call, benchmark test) khỏi
  `OnnxStemSeparator`/`OnnxEngineDeviceTest` — đúng tiền lệ GPU delegate + NNAPI-TFLite: test →
  không có lợi → gỡ, không giữ code chết.
- **Tổng kết cả 2 lần thử NNAPI** (TFLite: crash cứng; ONNX: chạy được nhưng vô dụng): NNAPI không
  phải hướng tối ưu khả thi cho model Spleeter trên Pixel 9 dù máy có Edge TPU thật — kết luận đủ
  chắc chắn (2 backend khác nhau, cùng kết quả tiêu cực) để không cần thử thêm.

## Update 2026-08-25 — Full-integer quantization: bắt đầu, phát hiện mất script convert TFLite gốc

- Bắt tay vào hướng còn lại (full-integer quantization, calibration dataset). Phát hiện: **script
  Python đã convert ra `2stems.tflite`/`4stems.tflite`/`5stems.tflite` hiện có trong app KHÔNG CÒN
  TỒN TẠI** — chạy ở 1 session cũ, `/tmp` đã bị dọn. Chỉ còn lại pipeline export ONNX (PyTorch
  reimplementation) — khác hoàn toàn hướng TFLite (TFLite bake STFT/ISTFT vào graph qua
  SELECT_TF_OPS, không viết tay như ONNX).
- Vẫn còn checkpoint TF1 gốc (weight thật, đáng tin cậy) cho cả 2/4/5-stem + source gốc của
  Spleeter (`model/__init__.py`, `model/functions/unet.py`, MIT license) từng dùng để export ONNX
  — đủ để dựng lại graph TF cho TFLite từ đầu (thay `tf.contrib.signal` bằng `tf.signal.*` là chạy
  được trên TF 2.21 hiện có sẵn trên máy).
- **Đã backup toàn bộ (~1.4GB) vào `checkpoints_backup/` ở root project** (không phải gradle
  module, không ảnh hưởng build; project không phải git repo nên an toàn, không lo bị commit
  nhầm) — gồm `checkpoints_backup/{root=2stems,4stems/,5stems/}`: checkpoint .data/.index/.meta,
  script export ONNX, file .onnx đã convert sẵn. Lý do backup: đúng bài học vừa rút ra ở trên (mất
  script TFLite vì để trong /tmp job cũ) — **không được để bất kỳ artifact quan trọng nào
  (checkpoint, script convert) chỉ tồn tại trong `/tmp` hoặc job tmp dir** (`~/.claude/jobs/*/tmp/`),
  cả 2 chỗ đều bị dọn khi session/job kết thúc. Chỗ bền duy nhất: bên trong project dir, hoặc nơi
  user chỉ định.
- Thiếu 1 phần nhỏ: `spleeter/utils/tensor.py` (`pad_and_partition`/`pad_and_reshape`) không có
  sẵn trên máy — phải viết lại theo logic public (MIT) của repo `deezer/spleeter`, validate lại
  bằng cách so khớp output với `.tflite` gốc đang chạy production (oracle) trên cùng audio mẫu.
- Đang chạy: dựng lại graph two_stem từ checkpoint, validate bit-exact với `2stems.tflite` hiện
  có trước, rồi mới convert sang .tflite float32 (CHƯA quantize) để xác nhận pipeline convert lại
  đúng — chỉ sau khi bước này pass mới làm representative_dataset quantization thật.
- Sau đó tìm thêm được `tensor_utils.py` gốc (chính là `spleeter/utils/tensor.py` — có
  `pad_and_partition`/`pad_and_reshape` thật) nằm lẫn trong backup, đã copy vào chỗ agent đang làm
  — khỏi phải đoán/viết lại như dự kiến ban đầu, độ tin cậy cao hơn hẳn.
  Cấu trúc backup cuối cùng: `checkpoints_backup/{2stems,4stems,5stems}/` (checkpoint + script +
  tensor_utils.py) và `checkpoints_backup/production_assets/{two,four,five}_stem/{original,quantize}/`
  (6 file .tflite đang chạy production, đã verify checksum khớp 100% với bản trong app) +
  `production_assets/onnx/` (3 file .onnx fp16 đang dùng). Đây là bản backup DUY NHẤT — project
  không phải git nên các file .tflite production này không có safety net nào khác nếu lỡ ghi đè.
- Đồng thời backup luôn **source code Kotlin của module `:audio_stem_split`** (OnnxStemSeparator,
  SpleeterStemSeparator, four_stem/five_stem, native_fft_experiment...) vào
  `source_backup/audio_stem_split_<timestamp>.tar.gz` ở root project (tar, loại `build/`/`.gradle/`
  /`.cxx`) — cùng lý do: project không phải git, không có history nào để revert. Đây là bản backup
  một-lần-tại-thời-điểm-này, KHÔNG tự động cập nhật — nếu sửa code nhiều thêm sau này thì nên tạo
  bản tar mới (không ghi đè bản cũ, để so sánh được nếu cần).

## Update 2026-08-25 — Dựng lại thành công pipeline convert TFLite two_stem, validate bit-exact

- Agent dựng lại graph TF1 gốc (EstimatorSpecBuilder + unet.py + tensor_utils.py chính hãng, MIT)
  từ checkpoint thật, restore weight, convert sang .tflite float32 (SELECT_TF_OPS: FlexConv2D,
  FlexIRFFT, FlexPad, FlexTranspose). **Kết quả: output số (vocals/accompaniment) khớp
  `max_abs_diff = 0.0` tuyệt đối** với `2stems.tflite` đang chạy production — pipeline convert
  coi như đã khôi phục hoàn toàn, đáng tin cậy để dùng tiếp cho full-integer quantization.
  (MD5 file .tflite KHÔNG khớp bản production — bình thường, do khác byte metadata/buffer-order
  giữa 2 lần convert, không liên quan đến giá trị số đầu ra.)
- 2 bug môi trường phải tự vá khi restore checkpoint TF1 cũ (2019) bằng TF 2.21/Keras 3 hiện tại —
  đáng lưu lại phòng khi làm four_stem/five_stem sau này:
  1. `tf.compat.v1.train.Saver` fail vì Keras 3 tạo checkpoint-key kiểu mới, không khớp checkpoint
     flat-name cũ → phải tự đọc qua `tf.train.load_checkpoint` rồi assign thủ công.
  2. **Bẫy nguy hiểm, âm thầm không lỗi**: `layer.gamma/.beta/.kernel.assign()` trong Keras 3 trả
     về wrapper `keras.src.backend.Variable` — gọi `.assign()` thẳng trên wrapper là **no-op âm
     thầm** (không throw, không tạo AssignVariableOp thật) → cả 2 nhánh instrument giữ giá trị init
     giống hệt nhau, output 2 stem **identical bit-for-bit** trông như "chạy được" nhưng sai hoàn
     toàn. Fix: `variable.value.assign(ph)` (lấy ResourceVariable thật bên trong wrapper). Nếu lần
     sau thấy 2 stem output giống hệt nhau bất thường — kiểm tra ngay chỗ này trước.
- Đã backup pipeline + kết quả vào `checkpoints_backup/tflite_conversion_pipeline/two_stem/`
  (code `run_predict_graph.py`/`convert_to_tflite.py`/package `spleeter/` tự dựng lại +
  `saved_model_2stems/` trung gian + `two_stem_rebuilt_float32.tflite` đã validate).
- Bước tiếp theo (chưa làm, cần user xác nhận trước khi động vào asset thật trong app): áp dụng
  `converter.representative_dataset` lên chính pipeline này để ra bản full-integer quantize, so
  sánh chất lượng/tốc độ với bản `quantize` (dynamic-range) hiện có, rồi mới thay thế nếu tốt hơn.

## Update 2026-08-25 — Full-integer quantization two_stem: convert OK, nhưng chất lượng kém rõ rệt

- Convert thành công, KHÔNG gặp lại bug TRANSPOSE_CONV (khác lo ngại ban đầu) — representative
  dataset 7 đoạn (3-5s) trải đều `sample_song.wav` (30s, giới hạn vì file mẫu chỉ dài chừng đó).
- Giảm size rất mạnh: **75.02MB (float32) → 50.07MB (quantize dynamic-range hiện tại) →
  18.89MB (full-integer mới)** — giảm 74.8% so với float32, 62.3% so với bản dynamic-range đang
  chạy production.
- **Nhưng chất lượng giảm rõ rệt so với float32** (đo trên toàn bộ 30s, so với oracle bit-exact):
  | Track | full_int8 SNR/corr | dynamic-range (production) SNR/corr |
  |---|---|---|
  | vocals | **1.86 dB / 0.68** | 14.84 dB / 0.98 |
  | accompaniment | 9.23 dB / 0.94 | 20.16 dB / 0.995 |
  SNR 1.86dB cho vocals gần như nhiễu ngang tín hiệu — dự đoán nghe artifact rõ. Nguyên nhân nghi
  ngờ: Flex ops (STFT/IRFFT + FlexConv2D của layer conv2d đầu do input shape động) buộc giữ
  float32, chỉ phần U-net ngoài Flex được lượng tử int8 thật; cộng thêm representative dataset chỉ
  7 đoạn từ 1 bài có thể chưa đại diện đủ range activation.
- **Chưa kết luận cuối cùng** — số liệu SNR gợi ý mạnh là không đạt chất lượng production, nhưng
  CHƯA nghe thử thật bằng tai để xác nhận. File WAV để nghe A/B (float32 / quantize_dynamic /
  quantize_full_int8, mỗi bộ có vocals.wav + accompaniment.wav) đã backup ở
  `checkpoints_backup/tflite_conversion_pipeline/two_stem/listen_test/`. Model:
  `checkpoints_backup/tflite_conversion_pipeline/two_stem/two_stem_full_int8.tflite`.
- Nếu nghe thử xác nhận tệ như số liệu: full-integer quantization theo cấu hình này (chỉ 7 đoạn
  calibration, giữ Flex ops float32 bắt buộc) **không khả thi cho production** ở dạng hiện tại —
  hướng cải thiện khả dĩ nếu muốn thử tiếp (chưa làm): representative dataset đa dạng hơn (nhiều
  bài, không chỉ 1 file 30s), hoặc thử per-channel quantization khác, nhưng khả năng cao giới hạn
  gốc là kiến trúc Flex-op-heavy của Spleeter không hợp với full-integer quantization.

## Update 2026-08-25 — User nghe thử: chất lượng "tạm ổn" (khác dự đoán từ SNR)

- User đã nghe trực tiếp `quantize_full_int8/vocals.wav` — đánh giá **"chất lượng tạm ổn"**, trái
  với dự đoán của tôi dựa trên SNR=1.86dB (dự đoán artifact rõ). **Bài học**: SNR đo so với oracle
  float32 bit-exact đo lệch số học thuần, không phải lệch cảm nhận — với nhạc, psychoacoustic
  masking có thể khiến sai số lượng tử hóa không nghe rõ dù số liệu thấp. Đừng chỉ dựa SNR/corr để
  kết luận chất lượng audio — luôn cần nghe thật để xác nhận, số liệu chỉ để tham khảo/so sánh
  tương đối giữa các cấu hình, không phải ngưỡng pass/fail tuyệt đối.
- Mối quan tâm thật của user chuyển sang **thời gian xử lý**, không phải chất lượng — đang benchmark
  trên Pixel 9 thật.

## Update 2026-08-25 — Blocker mới: TF version mismatch giữa converter và native runtime trong app

- Khi wire `two_stem_full_int8.tflite` vào androidTest để benchmark tốc độ trên Pixel 9 (asset đặt
  ở `app/src/androidTest/assets/`, không đụng module thật — chỉ dùng cho benchmark), **crash ngay
  lúc tạo Interpreter**:
  ```
  IllegalArgumentException: Internal error: Cannot create interpreter: Didn't find op for builtin
  opcode 'QUANTIZE' version '1'. An older version of this builtin might be supported.
  ```
- Nguyên nhân xác định được: `:native_build:custom` (runtime TFLite thật app đang dùng, custom
  build hỗ trợ Flex ops SELECT_TF_OPS) build từ **TensorFlow 2.14.0**
  (`audio_stem_split/native_build/custom/tensorflow_src/tensorflow/core/public/version.h`) — còn
  bản full-integer vừa convert dùng `venv_oracle` = **TensorFlow 2.16.1** (bắt buộc phải dùng bản
  này ở bước convert vì venv chính TF 2.21 thiếu Flex delegate hoạt động cho calibration). Op
  `QUANTIZE` đổi version giữa 2.14→2.16, không tương thích ngược.
  **Suy luận quan trọng**: bản `quantize` (dynamic-range) đang chạy production KHÔNG bị vướng lỗi
  này dù chạy trên cùng runtime 2.14.0 — dynamic-range không chèn node QUANTIZE/DEQUANTIZE quanh
  activation giống full-integer (chỉ quantize weight tĩnh), nên không đụng tới op này.
- Đang thử fix: convert lại bằng đúng TF 2.14.0 (venv riêng) để khớp opcode version với runtime
  native đang đóng gói trong app — rủi ro: TF 2.14.0 (cuối 2023) có thể không hỗ trợ Python 3.12
  (Python hệ thống hiện tại), nếu vậy cần cân nhắc hướng khác (rebuild lại `:native_build:custom`
  từ TF mới hơn — việc LỚN hơn nhiều, chưa nên làm vội).
- **Bài học chung cho lần sau**: bất kỳ .tflite nào convert bằng TF version KHÁC với TF version đã
  build ra `:native_build:custom` đều có rủi ro op-version-mismatch — luôn phải verify trên chính
  runtime thật của app (không chỉ verify bằng `tf.lite.Interpreter` từ pip TensorFlow trên máy dev,
  vì đó là runtime KHÁC, sẽ không phát hiện được lỗi này).

## Update 2026-08-25 — KẾT LUẬN CUỐI: full-integer quantization đã rollback hoàn toàn, không dùng

- Sau khi rebuild AAR thành công (thêm QUANTIZE/DEQUANTIZE, xem update trước) và benchmark thật
  trên Pixel 9: **full_int8 nhanh hơn `quantize` (dynamic-range) chỉ ~9%** (6.92s vs 7.6s tuned,
  cùng clip 30s) — không đủ thuyết phục để đánh đổi (đã wire tạm 1 engine `TwoStemQuantizeFullInt8`
  vào app thật để user tự nghe/test, chất lượng nghe "tạm ổn" nhưng 9% quá nhỏ so với mục tiêu thật
  là thu hẹp khoảng cách với đối thủ).
- So với khoảng cách tốc độ thật với đối thủ (5x-25x tuỳ file, xem update trước), 9% không giải
  quyết được gì — **cả 2 đòn bẩy hợp pháp đã dùng gần hết** cho nhánh TFLite (native qua Flex delegate
  đã có từ đầu, quantization chỉ cho 9%) mà khoảng cách vẫn rất lớn → kết luận khoảng cách nhiều khả
  năng đến từ kiến trúc/model khác biệt thật, không phải kỹ thuật tối ưu chung.
- Đã đánh giá luôn hướng "train lại model" (kiến trúc nhỏ hơn, hoặc resolution thấp hơn khớp 11kHz)
  — **bị chặn ngay từ bước data**: MUSDB18/MedleyDB/MoisesDB chỉ license non-commercial, Slakh2100
  thương mại sạch nhưng không có vocal thật. User xác nhận không đủ nguồn lực theo hướng này.
- **Quyết định cuối: ROLLBACK HOÀN TOÀN**, đúng tiền lệ GPU delegate/NNAPI (thử → không đủ lợi ích
  → gỡ sạch, không giữ code chết):
  - AAR native (`tensorflow-lite.aar`/`tensorflow-lite-select-tf-ops.aar`) đã restore về bản gốc
    từ `checkpoints_backup/native_build_custom_aar_backup/`, verify checksum khớp 100%.
  - Đã gỡ sạch module `two_stem/quantize_full_int8` + toàn bộ wiring (enum `StemSplitEngineType`,
    qualifier + provider trong `StemSplitEngineModule`, constructor/when-branch trong
    `DefaultStemSplitterRepository`, UI row + label trong `StemSplitterScreen`, string resource,
    test method `benchmarkTwoStemFullInt8` trong androidTest) — verify bằng grep không còn tham
    chiếu nào sót, compile sạch.
  - **Mọi artifact vẫn giữ lại trong `checkpoints_backup/`** (pipeline convert, model đã quantize,
    file nghe thử, cả 2 file AAR rebuild) để tham khảo lại nếu sau này có nguồn lực quay lại hướng
    train model riêng — không xoá, chỉ không dùng trong app hiện tại.
- **Tổng kết hướng tối ưu tốc độ TFLite cho production**: đã thử hết các đòn bẩy hợp lệ khả thi
  (numThreads tuning, coroutine parallelism, NNAPI, full-integer quantization) — tất cả đã có kết
  luận rõ ràng (một số áp dụng được — numThreads/parallelism đang dùng thật; một số không — NNAPI,
  full-int8). Không còn hướng tối ưu chưa thử trong tầm nguồn lực hiện tại.

## Update 2026-08-26 — Breakdown thời gian THẬT lần đầu đo tách riêng + đòn bẩy ByteBuffer (21% invoke)

- Lần đầu đo tách riêng where-time-goes (trước giờ chỉ có wall-clock tổng). Khai thác log per-chunk
  có sẵn (`SpleeterStemSeparator` allocateBuffers/runForMultipleInputsOutputs; `ChunkedSeparator`
  separate=/write=; `MediaCodecPcmDecoder` pureDecodeTime/sinkTime) trên clip 30s (Pixel 9, threads=6).
  **Breakdown 2-stem (~6.8s total):** main inference ~5447ms (80%), tail-chunk 4096-frame ~493-686ms
  (7-9% — LÃNG PHÍ), decode ~474-1246ms (7-18%), write ~308ms (4.5%), buffer alloc ~100ms. 5-stem
  tail-chunk waste ~1400-1746ms.
- **Tail-chunk waste**: `ChunkedSeparator.DEFAULT_OVERLAP_FRAME_COUNT=4096` luôn giữ lại 4096 frame
  cuối mỗi chunk 30s để crossfade → flush thành 1 chunk đuôi tí hon ở `finish()`, trả full Flex
  fixed-cost để xử lý 0.09s audio. **CHỈ đáng kể với clip ngắn ~30s** (7-11%); bài dài thật (nhiều
  phút) chỉ 1 tail/file → không đáng kể. Không phải ưu tiên cho use-case thật.
- **ĐÒN BẨY TỐT NHẤT — Tensor OUTPUT bằng direct ByteBuffer phẳng thay `Array<FloatArray>`**: spike
  A/B đo thật trên Pixel 9 (cùng Interpreter, cùng chunk 30s, `OutputMarshalSpikeTest`):
  ```
  array=[3905,3785,3939] avg=3876ms | byteBuffer=[3084,3012,3081] avg=3059ms
  outputMarshalSaving=817ms (21.1% của invoke)
  ```
  Nguyên nhân: TFLite copy output từng ROW của mảng lồng nhau (~2.6M FloatArray(2) rows/stem) qua
  JNI thay vì 1 bulk memcpy vào ByteBuffer phẳng. Nằm trên critical path (operationLock serialize),
  áp dụng MỌI chunk/file/tier, KHÔNG bị pipeline lever nào giấu được → gain cộng dồn. End-to-end
  2-stem ~12%; 4/5-stem tiết kiệm tuyệt đối lớn hơn (nhiều stem hơn). Bonus: RAM/chunk giảm ~5x
  (on-heap nested → off-heap flat) — an toàn cho lịch sử OOM 4/5-stem. KHÔNG đổi model/native/chất
  lượng.
  **LANDMINE khi implement**: sau cancel, Flex output tensor có thể pinned về shape [1,1]; đường
  Array<FloatArray> hiện tại throw IllegalArgumentException (được dùng để set needsRebuildAfterCancel).
  ByteBuffer chỉ check capacity → KHÔNG throw, ghi garbage im lặng. Phải THÊM explicit check
  `getOutputTensor(idx).shape()` sau invoke để giữ nguyên cơ chế phát hiện cancel-corruption.
- **Xếp hạng đòn bẩy (workflow 15-agent + đo thật):** #1 ByteBuffer output (21% invoke, mọi file,
  rủi ro thấp-trung, chỉ đụng SpleeterStemSeparator). #2 pipeline decode‖inference (producer/consumer
  Channel, ~12-15% file DÀI nhiều chunk, ~0% clip 30s, rủi ro cancel/OOM cao). #3 pre-warm Interpreter
  (marginal, chỉ add-on của #2). REJECT: write‖inference (1-2.5%), chunk-size sweep (cơ chế sai —
  cost scale theo frame không theo call), output-buffer-reuse đơn thuần (1-2.5% + landmine shallow-copy
  pendingTail).
- **Kỳ vọng thực tế**: các đòn bẩy này cộng lại ~15-25%, KHÔNG thu hẹp gap 5x với đối thủ (gap đó
  cần đổi model/kiến trúc — đã chốt không khả thi vì license data). Nhưng ByteBuffer là win sạch
  (bit-identical output, giảm RAM) đáng làm độc lập.

## Update 2026-08-26 — ĐÃ SHIP ByteBuffer output trong SpleeterStemSeparator (bit-identical, ~9-12%)

- Implement bản blast-radius nhỏ nhất: CHỈ sửa `SpleeterStemSeparator.separate()` — TFLite ghi output
  vào direct `ByteBuffer` phẳng (interleaved L,R,L,R…) thay `Array<FloatArray>`, rồi reshape về
  `Array<FloatArray>` bằng Kotlin thuần (`asFloatBuffer().get(flat)` bulk + reshape). GIỮ NGUYÊN
  return type `Map<String, Array<FloatArray>>` → consumer (ChunkedSeparator/StemMixer/WavPcmEncoder)
  và ONNX KHÔNG đổi gì, interface `StemSeparator` không đổi.
- Đã thêm shape-guard sau invoke (`getOutputTensor(idx).shape()` phải = [frameCount, 2]) để giữ cơ
  chế phát hiện cancel-corruption (ByteBuffer không throw như Array khi tensor pinned [1,1]).
- **Verify correctness**: `OutputMarshalSpikeTest` assert reshape(ByteBuffer) == Array output,
  `maxAbsDiff=0.0` — bit-identical tuyệt đối, logic interleaving đúng.
- **Kết quả benchmark THẬT Pixel 9 (threads=6):** 2-stem 7348→6664ms (~9.3%), 5-stem 16194→14321ms
  (~11.6%). Per-chunk `runForMultipleInputsOutputs`: 2-stem −880ms/chunk, 5-stem −1470ms/chunk
  (reshape chỉ +43-112ms). Áp dụng MỌI chunk/file/tier.
- **Khác hẳn full-int8 đã rollback**: đây là win SẠCH — không rebuild native, không đổi model,
  output bit-identical (không đổi chất lượng), 1 file, verify được. Giữ lại.
- File test: `OutputMarshalSpikeTest.kt` (giữ như research artifact, cùng nhóm InterpreterOptionsBenchmarkTest);
  cần `androidTestImplementation(project(":audio_stem_split:native_build:custom"))` trong app/build.gradle.kts
  để access Interpreter trực tiếp.
- **CHƯA làm (đòn bẩy #2, để user quyết)**: pipeline decode‖inference (producer/consumer Channel)
  — ~12-15% file DÀI nhiều chunk nhưng ~0% clip ngắn, rủi ro cao (đụng cancel path hard-won + OOM
  512MB heap). Cân nhắc kỹ risk/reward trước khi làm.

## Update 2026-08-26 — RE-AUDIT toàn bộ app đối thủ (SỬA nhầm lẫn app + phát hiện hướng MNN)

- **SỬA NHẦM LẪN QUAN TRỌNG**: app benchmark "37s/25x realtime" trước đây là `ai.vocal.remover...`
  ("Vocal Remover", native bespoke `libSpleeter.so`), KHÔNG phải app user thực sự dùng. App user
  dùng là **KaraokeBox = `io.jkhddev.music_player`** — engine KHÁC HẲN (**MNN**, không phải native
  Spleeter C++). Tốc độ thật của KaraokeBox CHƯA đo (user nghĩ nó nhanh, cần verify riêng).
- Đã pull + đọc APK (black-box: aapt2 label + unzip .so + model assets, KHÔNG decompile/chạy model)
  toàn bộ 7 app separation trên máy. Bảng đối chiếu đúng (tên hiển thị / package / engine / model):
  | App | Package | Engine (.so) | Model | Size |
  |---|---|---|---|---|
  | **KaraokeBox** | io.jkhddev.music_player | **MNN** (libMNN.so) + Flutter | 2× MNN (từ ONNX, vocals+accomp, `assets/flutter_assets/tfs/{0,1}.7z` — thực ra là MNN flatbuffer đổi đuôi, KHÔNG nén) | ~19.7MB (nửa cỡ fp16 Spleeter → leaner/quantized) |
  | Vocal Remover | ai.vocal.remover.splitter.karaoke.instrumental | **bespoke libSpleeter.so** (native C++ 488KB) | .splx encrypted | ~78.6MB |
  | Music & Vocal Splitter | com.ideastocode.musicvocalsplitter | **ONNX Runtime** (libonnxruntime.so 27MB) | vocals.fp16.onnx + accompaniment.fp16.onnx | ~39MB (≈ ONNX của mình) |
  | Vocal Remover Pro | vocal.remover.backing.tracks.acapella.extractor.song.maker | **ONNX + TFLite Flex** (libtensorflowlite_flex_jni 68MB!) + LanSong | fcpe_int8.onnx, model_5fold.onnx (chord), basic_pitch.onnx | multi-model |
  | Vocal Remover | com.vocalremoverai.app | Flutter (libdartjni), KHÔNG có NN .so/model | — | CLOUD |
  | unMix | com.vocalremover.unmix | KHÔNG có NN .so/model (ads dex) | — | CLOUD |
  | Vocal Remover Music Separator | music.remove.vocal_remover_music_separator | ffmpeg (libavfilter), KHÔNG có NN model | — | ffmpeg/cloud |
- **3 nhóm kiến trúc**: (1) native bespoke C++ (ai.vocal); (2) NN framework on-device — MNN
  (KaraokeBox), ONNX (ideastocode), ONNX+TFLite (Vocal Remover Pro); (3) cloud/ffmpeg (3 app còn lại,
  không tách trên máy).
- **HƯỚNG MỚI HỢP PHÁP phát hiện từ re-audit — MNN**: app nhỏ/nhanh nhất on-device (KaraokeBox)
  dùng **MNN** — framework mình CHƯA thử. MNN (Alibaba, Apache-2.0, open-source) thường nhanh hơn
  TFLite trên mobile + hỗ trợ int8 tốt. **Mình ĐÃ CÓ SẴN `spleeter_2stems.onnx`/fp16 (39.5MB) trong
  checkpoints_backup** → convert sang MNN (dùng MNN converter trên MODEL CỦA MÌNH, không đụng model
  đối thủ) là 100% hợp pháp. Đây là hướng đáng thử hơn pipeline lever — có thể vừa nhanh hơn TFLite
  vừa nhỏ hơn. CHƯA làm, để user quyết.

## Update 2026-08-25 — CORRECTION: nguyên nhân thật KHÔNG PHẢI TF version, mà là selective-build op resolver

- Đã cài được `python3.11` (qua deadsnakes PPA, Ubuntu 24.04/noble không có sẵn python3.11 —
  cần thêm PPA trước) để convert lại đúng TF 2.14.0 khớp version runtime native. **Kết quả: op
  table của bản convert bằng TF 2.14.0 và TF 2.16.1 GIỐNG HỆT NHAU 100%** (kể cả `QUANTIZE
  version=1` gây crash) — bác bỏ hoàn toàn giả thuyết "op version khác nhau giữa 2 bản TF" đã ghi
  ở Update trước đó. **Sửa lại**: nguyên nhân thật là `:native_build:custom` build theo kiểu
  **selective build** (`tensorflow-lite.aar`/`tensorflow-lite-select-tf-ops.aar` scoped theo đúng
  comment trong `build.gradle.kts`) — op resolver chỉ đăng ký kernel cho các op mà 2 model đang
  ship (`original` float32 + `quantize` dynamic-range) từng dùng. Cả hai model đó chưa bao giờ có
  node `QUANTIZE` (dynamic-range chỉ lượng tử weight tĩnh, không chèn QUANTIZE/DEQUANTIZE quanh
  activation) → op này **không tồn tại trong runtime ở bất kỳ version nào**, không liên quan TF
  version dùng để convert.
- **Kết luận cuối cùng**: để full-integer quantization chạy được trên app, bắt buộc phải **rebuild
  `tensorflow-lite.aar` từ Bazel** (`build_aar.sh` trong `native_build/custom`), thêm model
  full-integer vào danh sách model tham chiếu để selective-build đăng ký thêm `QUANTIZE`/
  `DEQUANTIZE` (và khả năng vài op khác đổi version: `ADD`, `CONCATENATION`, `FILL`...). Quy mô
  việc này tương đương lần build native đầu tiên — KHÔNG PHẢI việc nhỏ, chưa quyết định có làm
  hay không (đang chờ ý kiến user, ưu tiên ban đầu là tốc độ xử lý nhưng chưa đo được số liệu thật
  vì bị chặn đúng ở bước này).
- **Bài học sửa lại**: khi gặp lỗi thiếu op trên runtime custom-build, đừng vội kết luận do TF
  version converter — kiểm tra TRƯỚC xem runtime có phải selective/scoped build không (đọc
  `build.gradle.kts`/script build AAR), vì đó là nguyên nhân dễ xảy ra hơn nhiều với kiểu build
  custom rút gọn op này.
- File kết quả (convert bằng TF 2.14.0, không dùng được nhưng giữ lại tham khảo):
  `/home/khapv/.claude/jobs/95bd196e/tmp/quantize_spike/two_stem_full_int8_tf214.tflite`.

## Update 2026-08-26 — Benchmark thật KaraokeBox (MNN) + đang thử ONNX→MNN cho model mình

- **User đo tay KaraokeBox** (io.jkhddev, MNN) trên file kiểm soát `test_44k.mp3` (10:00, 44.1k,
  2-stem): **64s → ~9.4x realtime**. Cùng độ dài: app mình (TFLite 2-stem) ~5.18x realtime (~116s
  cho 10 phút) → **KaraokeBox nhanh hơn ~1.8x**. 3 mức đã biết: native-C++ (ai.vocal) ~25x >> MNN
  (KaraokeBox) ~9.4x >> TFLite mình ~5.2x.
- **~1.8x là mốc KHẢ THI** (không cần C++ bespoke như gap 5x) → củng cố mạnh hướng MNN. Lưu ý: 1.8x
  = "MNN + model nửa cỡ (~19.7MB)" vs "TFLite + model đầy đủ (~52MB)", chưa tách bạch MNN vs
  model-nhỏ — thí nghiệm ONNX→MNN (model đầy đủ của mình + thử int8 wq8) sẽ tách được.
- File kiểm soát ở `/sdcard/Download/test_44k.mp3` + `test_8k.mp3` (cùng nội dung 10:00, khác sample
  rate) cho benchmark tay.
- **User đo tiếp 8k: cũng ~64s (≈ 44.1k)** → thời gian KaraokeBox BẤT BIẾN theo sample rate input
  → nó **resample nội bộ về rate cố định** trước khi chạy model (feed 8k không nhanh hơn vì upsample
  lại). **ĐÓNG HOÀN TOÀN giả thuyết "đối thủ nhanh nhờ sample rate thấp"** — bác bỏ trên CẢ 2 app
  (ai.vocal qua spectrogram 15-17kHz; KaraokeBox qua timing bất biến). Tốc độ họ = MNN + model nhỏ,
  KHÔNG phải xử lý ít data. Cũng tái xác nhận: giảm sample rate không giúp app mình nếu không train
  lại (model input shape cố định [1,2,512,1024] = STFT config cố định = rate cố định).
- **User đo app MÌNH (đã có ByteBuffer) trên CÙNG file test_44k 10:00, 2-stem: 83s → ~7.2x realtime.**
  So sánh THẬT cùng file/máy: KaraokeBox 64s (~9.4x) vs mình 83s (~7.2x) → **gap thật chỉ ~1.3x
  (~30%)**, KHÔNG phải 1.8x (số 1.8x là do ngoại suy từ 5.18x cũ đã stale — trước ByteBuffer). ByteBuffer
  đã nâng mình từ ~5.2x lên ~7.2x thật → win thật, đáng kể. Mình đang bám sát KaraokeBox; nếu MNN cho
  dù một phần lợi thế thì có thể ngang/vượt. (Giả định 83s là tier 2-stem quantize production.)
- **User đo bản RELEASE trên cùng file test_44k 10:00, 2-stem: 76s → ~7.9x realtime** (debug 83s →
  release 76s, nhanh ~8% nhờ phần Kotlin chạy tối ưu khi debuggable=false; inference native không đổi).
  So công bằng release-vs-release: KaraokeBox 64s (~9.4x) vs mình 76s (~7.9x) → **gap chỉ còn ~1.19x
  (~19%)**. Kết luận: KaraokeBox (MNN) chỉ hơn mình ~19% — không còn đáng lo; chỉ ai.vocal.remover
  (~25x, bespoke C++) mới thực sự vượt trội nhưng là outlier cần person-months chuyên gia DSP, không
  đáng đuổi. Nếu MNN của mình cho ~20% lợi thế inference → ngang/vượt KaraokeBox.
- **Đánh giá bespoke C++ rewrite (user hỏi)**: KaraokeBox dùng MNN (native framework tối ưu) mà chỉ
  9.4x → "chạy native" KHÔNG tự đạt 25x; 25x của ai.vocal cần kernel NEON hand-written + int8 dotprod
  + có thể model nhỏ hơn = person-months chuyên gia SIMD, ROI thấp. Khuyến nghị: KHÔNG rewrite bespoke;
  hoàn tất MNN (ROI tốt nhất, ~9-10x với công sức nhỏ) rồi dừng.

## Update 2026-08-26 — MNN spike XONG: convert BROKEN + không hứa hẹn → DỪNG hướng MNN

- Agent convert `spleeter_2stems.onnx` → MNN (fp32 75MB, wq8 19MB) + build binary arm64 + đo Pixel 9.
- **BLOCKER correctness**: MNN 3.6.1 convert SAI — `vocals_mask` corr≈0 (xác nhận bằng chính tool test
  của MNN, cả 2 output FAIL). Root cause: bug fusion quanh node `/Mul_44` (BatchNorm 1-channel + dilated
  Conv2D). Fix cần graph-surgery/upstream — ngoài scope.
- **Speed x86 (apples-to-apples, tin được)**: MNN fp32 136ms/pass, wq8 134ms vs ONNX RT 102ms → MNN
  CHẬM HƠN ORT cho graph này.
- **Speed ARM Pixel 9 (KHÔNG tin được)**: fp32 55ms, fp16 51ms, wq8 73ms/pass — nhưng đo trên graph
  BỊ HỎNG (convert sai có thể tính thiếu việc). 50ms/segment = nhanh hơn ORT 14-34x là phi lý → số bogus.
- **Insight quan trọng**: U-Net inference vốn ĐÃ RẺ (ORT làm cả clip chỉ 2-5s); bottleneck thật là
  **STFT/ISTFT/reconstruct**, không phải U-Net. MNN chỉ thay U-Net → không đụng bottleneck.
- **KẾT LUẬN: DỪNG hướng MNN.** Convert broken + x86 cho thấy không nhanh hơn ORT + U-Net không phải
  bottleneck → không đáng fix convert bug. KaraokeBox nhanh ~9.4x có thể nhờ model nhỏ hơn + STFT native
  của họ, KHÔNG chỉ nhờ MNN runtime.
- **Đánh giá hướng ffmpeg decode/sample-rate (user nêu)**: upside rất thấp — decode chỉ ~5-7% pipeline
  (đổi sang ffmpeg cứu <1% + thêm ~8MB lib); giảm sample rate không giúp (đã bác bỏ, model shape cố định);
  bitrate không ảnh hưởng tốc độ tách. Không đáng làm.
- **Trạng thái tổng thể**: app mình release ~7.9x realtime, chỉ chậm hơn KaraokeBox (MNN) ~19% và đó
  gần như là trần khả thi không cần bespoke C++. Win sạch đã lấy: ByteBuffer (~9-12%) + release build
  (~8%). Các hướng còn lại (MNN, ffmpeg, full-int8, pipeline, sample-rate) đều đã đánh giá là không
  đáng/không khả thi.

## Update 2026-08-26 — LẬT KÈO: "gap 5x" là ẢO; đối thủ nhanh nhờ UX (streaming/on-demand), KHÔNG phải compute

- **User đo THỜI GIAN THẬT của ai.vocal.remover (xử lý xong cả bài, sẵn sàng Save): ~50-60s cho file
  ~10 phút → ~10.7x realtime, KHÔNG phải 25x.** Con số "37s/25x" trước đây là **time-to-first-result**
  (lúc play preview được từ chunk đầu), bị đo nhầm thành full-completion qua timestamp file.
- **Bảng throughput THẬT (đã sửa)**: ai.vocal ~10.7x, KaraokeBox (MNN) ~9.4x, app mình (release) ~7.9x.
  **Gap raw compute thật chỉ ~1.36x (ai.vocal) / ~1.19x (KaraokeBox) — KHÔNG có gap 5x.** Gap 5x cũ là
  ảo do đo nhầm streaming-preview.
- **Cơ chế "feels instant" của đối thủ = UX, không phải compute**: (1) streaming preview — chunk đầu
  xong là play được ngay (time-to-first-result ~vài giây); (2) **on-demand seek-prioritized separation**
  — user seek tới đoạn 9 thì separate riêng đoạn đó (loading) + play, BỎ QUA 2-8 cho tới khi seek/nền
  tự fill. Chia bài thành ~10 khoảng, mỗi khoảng separate độc lập.
- **KẾT LUẬN CHIẾN LƯỢC CUỐI**: (a) raw compute của mình ĐÃ ngang ngửa đối thủ (~20-36%, trong tầm
  noise + model-size) → NGƯNG tối ưu compute, đã chạm trần hợp lý; (b) bespoke C++ CHẮC CHẮN không đáng
  (gap thật 1.36x không phải 5x); (c) **move giá trị nhất còn lại = feature streaming/on-demand preview**
  — model mình LÀM ĐƯỢC (Spleeter xử lý segment T=512 độc lập, separate đoạn bất kỳ không cần đoạn khác;
  SpleeterStemSeparator không phải đổi). Việc chính: random-access decode 1 range (ffmpeg/MediaExtractor
  seekTo — ĐÂY là chỗ ý tưởng ffmpeg của user đúng, cho CAPABILITY random-access chứ không phải speed) +
  separate on-demand + player/state + cancel-on-seek. Feature UX mới → cần viết plan trước khi implement.
- Đang chạy (agent nền): convert `spleeter_2stems.onnx` (U-Net only, input mix_magnitude
  [1,2,512,1024] → 2 mask, XÁC NHẬN không có STFT trong graph — giống dạng model MNN KaraokeBox) →
  MNN fp32 + wq8, verify correctness, build binary MNN arm64 (`MNNV2Basic.out`) đo trên Pixel 9.
  Đây là số DECIDER cho MNN-vs-TFLite trên cùng model/máy.

## ONNX tier — KHÔNG đầu tư thêm (quyết định 2026-08-28)
User chốt: **không improve ONNX** vì performance không tốt hơn TFLite. Nên KHÔNG đề xuất lại việc
viết test cho ONNX, verify cancel-during-run trên device, hay tối ưu tier này — dù audit có nêu
"OnnxStemSeparator có 0 test ở mọi nơi" và comment trong chính file đó tự thừa nhận đường
cancel-rồi-reuse-session chưa verify trên device. Đây là rủi ro ĐÃ BIẾT và ĐƯỢC CHẤP NHẬN, không
phải thiếu sót cần vá. Nếu sau này ONNX được cân nhắc lại (đổi model/runtime), hai món đó là việc
đầu tiên phải làm.

## Giới hạn độ dài file WAV (fix 2026-08-28)
`WavPcmEncoder` giờ có `MAX_FRAME_COUNT` (~3.38h @44.1kHz stereo) và **fail fast** trong
`writeFrames()` thay vì để `frameCount * blockAlign` (Int*Int) tràn âm thầm và ghi size âm vào
header. Trần này đến từ RIFF 32-bit + chính `WavPcmDecoder` của module đọc lại size bằng `.int`.
`StreamWriter` có tham số `maxFrameCount` injectable để test guard mà không phải ghi ~2GB — cùng
pattern `ChunkedSeparator.chunkFrameCount`. Muốn vượt trần này thì phải đổi sang RF64/W64, không
phải nới constant.
