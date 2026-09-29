---
name: pattern-quiet-is-not-silent
description: "Báo cáo 'file không có âm thanh' phải đo max_volume trước khi tin — ngưỡng silence của app là -60 dBFS, tai người trên loa điện thoại thì nhầm ở -30 dB"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4a4bf1be-1d65-45b5-a7c4-ef9fc8732a6e
  modified: 2026-09-22T10:33:27.624Z
---

Ngưỡng im lặng của Audio Separation là `SILENCE_PEAK_CEILING = 0.001f` ≈ **-60 dBFS**
(`domain/model/SilenceDetection.kt`), xét theo **peak** chứ không phải trung bình.

Ngày 2026-09-22, ticket #410 được test bằng `Volume_large.mp3` với mô tả "file không có audio". Đo ra
`max_volume = -30.6 dB`, `mean_volume = -46.9 dB` — nhạc thật ở mức rất nhỏ, cao hơn ngưỡng 30 dB
(gấp ~33 lần biên độ). App tách file đó là ĐÚNG; nhánh silence chưa từng chạy. Mất một vòng
build-cài-test tay chỉ vì tin mô tả file thay vì đo.

**Why:** -30 dB trên loa điện thoại nghe như không có gì, nên người test thật lòng tin là file im
lặng. Khoảng cách giữa "nghe không thấy" và "im lặng số" rộng tới 30 dB.

**How to apply:** trước khi debug bất kỳ báo cáo nào có chữ "không có âm thanh / no audio / im
lặng", đo trước:

```bash
ffmpeg -i <file> -af volumedetect -f null /dev/null 2>&1 | grep volume
```

`max_volume` trên -60 dB ⇒ app coi là có tiếng, và mọi hành vi "vẫn xử lý bình thường" là đúng luật.
Chỉ khi `peak = 0.0` mới vào được nhánh No audio — xem file test ở
[[reference-separation-debug-toolkit]].

Nâng ngưỡng để bắt file -30 dB là quyết định sản phẩm, không phải bug fix: comment tại
`SilenceDetection.kt` đã cân nhắc và chọn thà cho qua bản thu nhỏ còn hơn từ chối nhầm.
