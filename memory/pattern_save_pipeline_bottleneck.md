---
name: pattern-save-pipeline-bottleneck
description: "Save của separation = stitch + encode + publish; encode bị FFmpeg serialize nên song song hoá vô ích, stitch thì nối byte được 8x"
metadata: 
  node_type: memory
  type: project
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-15T10:40:32.658Z
---

Đo trên Pixel 9, file 953 giây (15'53"), 4 stem, MP3 192kbps, ngày 2026-09-15.

## Ba giai đoạn, ba chủ sở hữu khác nhau

| | 2 stems | 4 stems | Ai làm |
|---|---|---|---|
| Stitch (nối segment) | 12.7s → **3.1s** | 29.0s → **3.2s** | Lib `WavPcmConcat` |
| Encode | 18.5s | **44.2s** | App → FFmpeg |
| Publish (MediaStore) | 0.4s | 1.2s | App |
| **Tổng Save** | 31.6s → 19s | **74.4s → 48.2s** | |

Encode chiếm ~90% sau khi stitch đã tối ưu. Publish không đáng kể (1.6%).

## Encode KHÔNG song song hoá được — đừng thử lại

`FfmpegAudioProcessorDataSource.executeMutex` là bản sao ở tầng Kotlin của **global execute lock
bên trong wrapper FFmpeg** (comment trong file nói rõ). Bọc 4 encode vào `async` thì cả 4 xếp hàng
ở mutex đó — thời gian y hệt, chỉ thêm phức tạp và mất ngữ nghĩa "fail thì giữ phần đã lưu".

`SaveSeparatedStemsUseCase.saveEachStem` dùng `forEach` tuần tự là ĐÚNG, không phải thiếu sót.

Hệ quả: **y stem tốn y × thời gian 1 stem** (đo được 2→4 stem là 2.36×). Trừ khi bật Mix — nhánh
`saveBlend` trộn N stem rồi encode MỘT lần, rẻ hơn hẳn N file riêng.

## Stitch: nối byte, không decode float

Xem [[reference-lib-knowledge-in-repo]] — lib đã nhận bản vá này (`WavPcmConcat`). Bài học chung:
nối các file cùng format = copy byte; decode int16→float→int16 ở giữa là công không sản phẩm.
Round-trip đó gần như lossless (chỉ `-32768` lệch 1 LSB) nên "tránh méo tiếng" KHÔNG phải lý do —
lý do là **42 triệu `FloatArray` mỗi stem**, đúng lúc process còn giữ arena TFLite ~2.6GB.

Kiểm chứng mạnh nhất: **md5 file MP3 xuất ra trùng khít** giữa đường float cũ và đường byte mới.

## Đo lại thế nào

Log tag `SeparationTiming`, mức `Timber.d` (chỉ có ở debug build):
```
save: stitched 4 stem(s) in 3149 ms
save: Vocals — encode 11861 ms, publish 424 ms
save: wrote 4 file(s) from 4 stem(s) in 48156 ms (SeparateFiles, MP3)
```
Log in **tên stem, không in tên file** — `nameHint` mang tên người dùng tự đặt.

Liên quan: [[project-separation-open-items]], [[reference-separation-debug-toolkit]],
[[pattern-unload-model-native-heap]]
