---
name: project_checkpoint_convention
description: "Cách tạo checkpoint đúng: source-only ~4MB, PHẢI kèm file gradle gốc, và exclude phải đứng TRƯỚC include='*/' trong rsync"
metadata: 
  node_type: memory
  type: project
  originSessionId: e0e87c8a-7800-4c48-8018-92b52653531d
  modified: 2026-09-22T04:39:59.789Z
---

Checkpoint ở `checkpoints_backup/code_backup_<YYYY-MM-DD>_<HHMMSS>_<label>/`. **Source only**, không
model binary (`.tflite`/`.onnx`/`.aar`) — cỡ đúng là **~4-5 MB / ~300 file**. Ra 150 MB là sai.

**Hai điều các bản trước làm thiếu/sai, đã sửa từ 2026-09-07:**

1. **PHẢI kèm file gradle GỐC**: `settings.gradle.kts`, `build.gradle.kts`, `gradle.properties`,
   `gradle/libs.versions.toml`. Các checkpoint cũ chỉ lưu `build.gradle.kts` từng module → **không
   restore về trạng thái build được**. Ví dụ mất `libs.versions.toml` là mất luôn dep Robolectric,
   mất `app/build.gradle.kts` là mất `isMinifyEnabled`.

2. **Trong rsync, luật xét THEO THỨ TỰ, match đầu tiên thắng** → mọi `--exclude` thư mục phải đứng
   **TRƯỚC** `--include='*/'`. Đặt sau thì không bao giờ chạy: lần đầu tôi đặt sau và nó nuốt cả
   `tensorflow_src` lẫn mọi report trong `build/` → 151 MB / 6.088 file thay vì 4.6 MB / 302.

Exclude cần có: `build/ .gradle/ .cxx/ tensorflow_src/ assets/ libs/`.
Include: `*.kt *.kts *.toml *.pro *.md *.html *.sh *.py *.xml *.properties *.config`.
Thư mục cần lấy: `app audio_stem_split .superpowers docs gradle` + 3 file gradle gốc.

**`*.config` thêm vào 2026-09-22** vì `presence/yamnet/model_src/yamnet.required_operators.config`
(412 byte) định nghĩa đúng 26 op mà AAR trong `onnx_runtime/custom/libs/` được build theo. Không có
nó thì không ai biết runtime hỗ trợ gì, mà `libs/` lại đang bị exclude nên AAR cũng không có trong
checkpoint. Đây là kiểu mất mát im lặng: checkpoint vẫn ~5 MB, vẫn đủ file, chỉ thiếu đúng thứ nối
model với runtime. Model `.onnx`/`.ort` thì vẫn KHÔNG lấy (không khớp include nào) — đúng ý đồ.

3. **`--include='*.properties'` kéo theo BÍ MẬT — phải exclude thủ công.** Root project có
   `keystore/`, `keystore.properties` (chứa `storePassword`/`keyPassword` thật) và
   `local.properties`. Lần 2026-09-11 rsync copy đủ cả ba vào checkpoint, phải `rm -rf` lại. Sau khi
   tạo, luôn `ls` mức top-level: chỉ được thấy `app audio_stem_split docs gradle .superpowers` + 3
   file gradle + `CHECKPOINT.md`. Thấy `keystore*` / `local.properties` / `source_backup` là sai.

**Kiểm tra sau khi tạo** (đừng tin kích thước suông): đếm binary model = 0, grep vài thay đổi then
chốt của session có mặt không. Lưu ý `find -path '*build/*'` sẽ khớp nhầm `native_build/` — false
positive, không phải rác.

Nên kèm `CHECKPOINT.md` trong thư mục: nó chứa gì, KHÔNG chứa gì, và trạng thái then chốt lúc đó.
