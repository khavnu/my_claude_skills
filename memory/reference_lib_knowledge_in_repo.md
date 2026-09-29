---
name: reference_lib_knowledge_in_repo
description: "Kiến thức về lib audio_stem_split (memory project gốc + docs lib + source demo app) đã chép vào docs/ của repo này — tra ở đó trước khi debug, đừng suy đoán lại"
metadata: 
  node_type: memory
  type: reference
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-08T10:20:57.373Z
---

Lib `:audio_stem_split` phát triển ở một workspace khác
(`~/AndroidStudioProjects/AudioSeparation`), nên memory của nó **không recall được** từ repo này —
memory khoá theo đường dẫn project. Toàn bộ đã chép vào repo ngày 2026-09-08:

| Ở đâu | Là gì |
|---|---|
| `docs/reference/lib-memory/` | 17 file memory của project lib + `README.md` bảng tra nhanh theo triệu chứng |
| `docs/reference/demo-app/` | 48 file source app demo — cách dùng lib thật (DI, repository, ViewModel) |
| `audio_stem_split/docs/` | `ENGINEERING-LOG.md`, `DIAGNOSING-AUDIO-BUGS.md` — đi theo code |
| `audio_stem_split/README.md` | 115 KB, contract của từng API |

**Why:** đã có lần tôi "phát hiện" ra `:playback` test flaky rồi viết lại thành checklist mới, trong
khi bên lib đã đo baseline và ghi sẵn từ trước — kèm một cạm bẫy tôi suýt đạp phải (sửa `idleUntil`
sang virtual clock làm số test đỏ tăng gấp 5). Tra trước thì tiết kiệm cả buổi.

**How to apply:** gặp bug/test đỏ liên quan tới separation, playback, R8, hay hiệu năng tách → đọc
`docs/reference/lib-memory/README.md` (bảng triệu chứng → file) TRƯỚC khi tự chẩn đoán. Cần biết cách
gọi API thì đọc `docs/reference/demo-app/` chứ đừng suy từ tên hàm.

Lưu ý: mấy mục thuộc workspace cũ (terminal AS, quy ước checkpoint, `adb` không có trong PATH) không
áp dụng cho repo này — README đã liệt kê.

## Khi vendor lib: đọc ENGINEERING-LOG phần "shipped" TRƯỚC khi wire

Mặc định của lib cố tình để `null` (giữ hành vi gốc của TFLite/ORT), nên **signature API không nói
gì về cấu hình đã được benchmark và chốt**. Quyết định nằm trong `audio_stem_split/docs/
ENGINEERING-LOG.md` và trong `docs/reference/demo-app/src/di/StemSplitEngineModule.kt`.

Đã bỏ sót một lần (2026-09-11): `SpleeterStemSeparator(_numThreads = null)` → app chạy ở cấu hình
**chậm nhất** trong ba cấu hình lib đã đo trên chính Pixel 9:

| numThreads | avg (clip 30s, FourStemQuantize) |
|---|---|
| mặc định (unset) | 14.7s |
| 6 = cores-2 | **12.0s** |
| 8 = mọi nhân | 12.9s |

Demo set `_numThreads = (availableProcessors() - 2).coerceAtLeast(1)` cho **cả 12 engine**, batch
lẫn streaming. `useXNNPACK` không đổi gì (model nặng Flex delegate) — bỏ qua được.

**Quy trình mỗi lần đồng bộ lib:** grep `## ` trong ENGINEERING-LOG cho các mục "shipped", đối chiếu
với cách app wire engine.


## Sync lib 2026-09-28 (mask model): quy trình và các bẫy đã gặp

Checklist + script: `docs/features/lib-sync-2026-09-28/` (`tools/sync-excludes.txt`, `run_bench.sh`, `analyze_stems.py`).

- **Base `77ff02f7` đã chứa sẵn các sửa đổi app làm lúc vendor.** Vì thế "lib khác base" KHÔNG có nghĩa là lib đi trước. Ví dụ `core/build.gradle.kts` (app bỏ `native_fft_experiment`): rsync đè vào là androidTest của core gãy. Sau rsync phải `git diff HEAD` từng file build.
- **Phải giữ nguyên `playback/**` của app** (#419 gain limiter; lib không đụng `StreamStemPlayer` từ 09-08).
- **Đưa file test vào app:** `adb shell "cat /sdcard/... | run-as <pkg> sh -c 'cat > files/x.mp3'"`. Nếu chỉ copy vào `Android/data/<pkg>/files` do shell tạo thì app không thấy file.
- **Dung lượng file APK debug vô nghĩa** (incremental packaging chừa chỗ trống): phải dùng tổng entry của `unzip -lv`.
- **Samsung A20s:** logcat ring nhỏ nên log `SeparationTiming` bị đẩy mất, dùng CSV của benchmark. Khi cắm 2 máy thì phải set `ANDROID_SERIAL`.
- **Residual `mix − Σstems` ≈ 0 là luôn đúng theo cách tính** khi có remainder stem. Muốn kiểm dải cao thì đo phần năng lượng dải cao nằm trong các stem mà model trực tiếp xuất ra.
