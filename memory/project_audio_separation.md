---
name: project-audio-separation
description: "Feature Audio Separation — lib audio_stem_split, flow streaming đã chốt, và các quyết định chưa nằm trong code"
metadata: 
  node_type: memory
  type: project
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-09T07:49:23.692Z
---

Feature Audio Separation (wireframe Figma `xPC3QxMt965PxCNFaZCrEs` section `88:1716`, các màn 18.x).
Tính tới 2026-09-08 mới làm xong 18.0/18.1 (pick file + limit) và 18.2.1 (config, UI thuần).

**Lib**: `:audio_stem_split` tại `/home/khapv/AndroidStudioProjects/AudioSeparation`, do chính user
viết, sẽ **copy hết module** vào repo. Spleeter chạy TFLite on-device. Dùng: streaming +
quantized + 2-stem + 4-stem + `:presence` + `:playback`. 5-stem để sẵn, chưa wire.
Checklist tích hợp đầy đủ ở `docs/audio-stem-split-lib-requests.md` trong repo.

**Flow đã chốt** (khác wireframe, user quyết):
tách 1 chunk (~14s) → nhảy thẳng sang 18.7 result, tách tiếp ở nền → user chỉnh effect,
lưu thành **pending params** chứ không render → bấm Save mới chờ tách xong + apply + ghi file.
18.6 rút xuống còn trạng thái ngắn, không còn là màn chờ dài.

**Vì sao effect là params**: preview Volume và Fade đều **miễn phí** — `setStemVolume` /
`setStemFade` đổi live, không render. Mix preview cũng vậy (N player phát cùng lúc).
Lần render duy nhất là lúc Save.

**Đính chính tên frame** (dễ nhầm): 18.3 = config 4-stem, 18.5 = weak device. Màn chờ là
**18.6 / 18.6.1**, màn kết quả là **18.7 (2 stem) / 18.8 (4 stem)**, 18.13 = Play result.

**Ba quyết định UI chốt 2026-09-09** (design không vẽ, user chọn):
- Row stem lúc chưa tách xong: **play được ngay**, ẩn hẳn dòng `04:15 │ 2.9 MB` (null → không render),
  `Save all` disable tới khi đủ segment. Không disable row, không progress bar per-row.
- Dialog chờ chunk đầu: **18.6.1** (spinner) → dùng `ProgressDialog` có sẵn, không viết dialog % mới.
- Kebab: dùng `ic_more` (chấm đặc) thay vì xin export chấm viền của Figma.

**Ràng buộc phải nhớ**:
- Engine **không bao giờ** `release()` — DI singleton, release là một chiều. Hủy = `cancel()`.
- 4-stem trên file 15 phút mất ~13.8 phút → **vượt trần ~10 phút của WorkManager thường**.
  Phải long-running worker `setForeground()` hoặc foreground service.
- APK tăng: **+347 MB** universal 4 ABI, **+211 MB** cài arm64, **~95 MB** tải qua AAB
  (dưới ngưỡng 200 MB của Play → không cần Play Asset Delivery).
- ETA "~1 min / ~3 min" trên wireframe **sai thực tế**: bài 4 phút thì 2-stem ≈ 2 phút,
  4-stem ≈ 3.5–4 phút.

Liên quan: [[feedback_coroutine_finally_ui_state]], [[pattern_blocking_jni_timeout_detached]],
[[feedback_incremental_ui_first]].
