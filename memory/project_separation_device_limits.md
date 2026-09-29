---
name: project-separation-device-limits
description: Ngưỡng RAM + segment 8s — hai máy từng chết nay chạy trọn; M20 sống nhưng giết 52 process khác nên 4-stem vẫn chặn ở 3.5GB
metadata: 
  node_type: memory
  type: project
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-16T09:08:35.890Z
---

## ⚠ Sửa 2026-09-29: luật segment bên dưới ĐÃ BỎ

Sau khi sync lib sang mask model (2026-09-28), arena tính theo patch (524,288 mẫu) chứ không theo segment.
Giờ chỉ còn một hằng số `SEGMENT_DURATION_US = 9.8s` cho mọi máy (`domain/model/SeparationFeasibility.kt`,
test `SegmentDurationTest`). Số đo mới: A20s 2-stem Rss ~480–512 MB (cũ 1106), 4-stem chạy trọn file ở
~840 MB (cũ bị kill). Gate RAM (2.5/3.5 GB) CHƯA đổi. Chi tiết: `docs/features/lib-sync-2026-09-28/checklist.md`.
Các bảng bên dưới là số của waveform model, chỉ còn giá trị lịch sử.

## Ngưỡng (2026-09-16, waveform model) — `domain/model/SeparationFeasibility.kt`

```
2 stems:  MemTotal > 2.5 GB      (was 3 GB)
4 stems:  MemTotal > 3.5 GB      (was 4 GB)
segment:  (ĐÃ BỎ 2026-09-29) 8s nếu MemTotal ≤ 6 GB, 15s nếu trên
input:    ≤ 5 GB → tối đa 15 phút / 200 MB; trên 5 GB → không giới hạn
```

Ngưỡng luôn đặt **dưới** máy đã chạy được (2.5 chứ không phải 2.67; 3.5 chứ không phải 3.63).

## Vì sao ngưỡng dịch được: segment 15s → 8s

Sweep Pixel 9, 4-stem, file 15'53", 2 lượt mỗi cấu hình:

| segment | peak native heap | ms/audio-sec | chunk đầu |
|---|---|---|---|
| 15s | 2139 / 2146 MB | 284 / 281 | 5.4s |
| 10s | 1844 / 1854 MB | 339 / 358 | 3.5s |
| **8s** | **1436 / 1423 MB** | 234 / 295 | **3.2s** |

**8s trả lại 723 MB mà không chậm hơn.** Heap lặp trong 1%; pace dao động 26% nên chỉ đủ nói "8s
không tệ hơn 15s". **10s tệ hơn cả hai hàng xóm ở cả hai lượt** — mô hình overhead (context 2s cố
định) dự đoán đường cong đơn điệu và sai; đừng cố giải thích, chỉ ghi nhận.

Migration note của lib nói chunk lever "does not apply to the streaming engine" — **sai với app
này**. Họ đo 10s (đúng là tệ) rồi kết luận cho mọi giá trị.

## Device matrix đo lại @8s

| máy | MemTotal | mode | trước (15s) | @8s | peak heap | pace |
|---|---:|---|---|---|---:|---:|
| Pixel 9 | 11.28 GB | 4-stem | chạy | chạy | 2146 MB | 281 |
| Realme RMX3710 | 5.70 GB | 4-stem | chạy | — | — | 335 |
| Huawei INE-LX2r | 3.63 GB | 4-stem | **chết ở 60s** | **chạy trọn** | 1521 MB | 1024 |
| Samsung M20 | 2.67 GB | 2-stem | **chết** | **chạy trọn** | 976 MB | 507 |
| Samsung M20 | 2.67 GB | 4-stem | — | chạy trọn | 1392 MB | 1070 |

## M20 chạy được 4-stem nhưng VẪN chặn — lý do quan trọng

Chạy trọn 2 lần (máy rảnh, và với 5 app nặng mở sẵn còn 640 MB trống). Nhưng nó lấy 1396 MB bằng
cách để hệ thống giết mọi thứ khác: **Chrome 4 lần, Play Store, Play Services, dịch vụ Samsung —
52 kill**, app nặng còn sống tụt từ 7 process xuống 2.

Huawei 3.63 GB đạt đỉnh **42%** RAM và không kéo theo ai; M20 đạt **52%** và dọn sạch máy. Ngưỡng
3.5 GB vẽ quanh khoảng cách đó. **"App sống sót" không phải tiêu chí — "người dùng mất gì" mới là.**

## Limit input: luật THỜI GIAN, không phải bộ nhớ

Peak không tăng theo độ dài (file 73 phút đỉnh THẤP hơn file 3 phút). Vách pace nằm giữa 3.63 và
5.70 GB (1024 → 335, gấp 3), gần như phẳng từ 5.70 lên 11.28 → mốc unlimit **5 GB**, cố ý khác mốc
6 GB của segment. 200 MB không phải limit duration trá hình: file 15' MP3 = 21 MB, WAV 44.1kHz =
158 MB đều lọt; nó chỉ bắt sample rate bất thường (192kHz = 46 MB/phút).

## Bỏ đi khỏi bản cũ

- `availMem` KHÔNG phải biến quyết định (bản cũ ghi vậy) — code vẫn dùng `totalMem`, vì availMem co
  giãn theo việc hệ thống giết app.
- Pace cũ (376/607/949/1453/3144) đo trước khi sửa `ENGINE_PARALLELISM` 1→2, đã lỗi thời hoàn toàn.

Liên quan: [[pattern-unload-model-native-heap]], [[project-separation-open-items]],
[[pattern-save-pipeline-bottleneck]]
