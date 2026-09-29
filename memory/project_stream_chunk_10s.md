---
name: project_stream_chunk_10s
description: "Stream segment 10s (2026-09-04): latency tới tiếng đầu giảm 2x; nhưng đo KHI ĐANG PHÁT thì 4-Stem chỉ còn 1.04x realtime và spinner nháy — 15s sạch hoàn toàn"
metadata: 
  node_type: memory
  type: project
  originSessionId: e0e87c8a-7800-4c48-8018-92b52653531d
  modified: 2026-09-04T11:01:44.957Z
---

`StreamStemSplitEngine.DEFAULT_SEGMENT_US` = **15s** kể từ 2026-09-07 (28s → 10s → 15s). Đã đo trên
Pixel 9, bài 3:50: first segment 13.4→6.6s (2-Stem Q), 18.1→8.8s (4-Stem Q), 19.4→10.3s (5-Stem O);
cả bài chậm hơn 7.6% (2-Stem) đến 20.8% (4-Stem).

**Why:** 28s được chọn chỉ vì 28+2×1 rơi đúng trần 30s/1.32M frame của một lần `separate()` — không
phải quyết định về latency, mà latency mới là lý do streaming tồn tại. Throughput chỉ ảnh hưởng
`save()` — đó là kết luận lúc đó, và nó SAI, xem mục dưới.

**Đo lại KHI ĐANG PHÁT (2026-09-07) — đổi kết luận.** Mọi tốc độ lấp đo lúc máy rảnh đều lạc quan:
4-Stem Quantized tụt từ 1.8x xuống **1.04x** khi 4 ExoPlayer cùng chạy. Ở 1.04x phần lấp không bao
giờ tạo được đệm — chỉ đứng trước playhead ~2s suốt bài — nên spinner buffering nháy mỗi 2s trong
~40s đầu (lặp lại được). **Nháy là spinner, không phải tiếng: 0 AudioTrack underrun; chưa verify
bằng tai.** 28s: 1.43x, sạch. **15s: 1.09x, SẠCH HOÀN TOÀN** → đã chốt **15s**.

**How to apply:** độ dài segment là quyết định về **độ sâu buffer**, KHÔNG phải throughput — 15s chỉ
hơn 10s 0.05x tốc độ lấp nhưng hết sạch nháy, vì player cần *bao nhiêu giây audio mỗi lần giao hàng*.
Đừng bao giờ chọn segment dựa trên số đo lúc máy rảnh. 5-Stem Original mới chỉ đo lúc rảnh (1.4x) →
giả định nó tụt dưới realtime khi phát. 10s vẫn hợp lý cho tích hợp **chỉ 2-stem** (1.9x, sạch).
Ngưỡng 30s/1.32M frame vẫn hiệu lực; ở 15s clamp là no-op tới 48kHz nhưng **bắt đầu cắn trên
~77.8kHz** (96kHz → 11.78s) — nên test phải có CẶP: một cái pin "không clamp ở 44.1/48k", một cái pin
đúng giá trị clamp ở 96k.

**Bug "fill dừng sớm" ĐÃ SỬA 2026-09-07** — xem [[project_fill_preemption_bug]]. Và chính nó là lý do
15s trông kém: mọi số đo trước đó đều lấy khi bug còn sống. **A/B sạch sau fix (cùng thermal status 1,
4-Stem Q, đang phát): 15s = 114.2s (2.01x), 28s = 93.1s (2.47x).** 28s thật sự tốt hơn ~23% về
throughput, nhưng throughput chỉ do `save()` trả, cả hai đều xa trên vạch 1.0x, và 15s tới tiếng đầu
sớm hơn 4.3s (13.8s vs 18.1s). Biên 1.09x từng làm 15s trông rủi ro là do BUG.

**CHỐT 15s (2026-09-07) — là quyết định của BENCH, không phải product.** User đã xem số A/B sạch và
nói sẽ cân nhắc lại khi đưa vào product. Đừng tự đổi. Bốn dữ kiện sẽ đổi câu trả lời lúc đó:
`save()` có trên hot path không; máy chậm nhất hỗ trợ là gì (mọi số đều từ 1 chiếc Pixel 9); engine
nào ship (số là 4-Stem Q; **5-Stem Original chưa đo lại khi đang phát sau fix**); bài dài bao nhiêu
(fill tỉ lệ độ dài bài, latency thì không). Override được theo từng tier qua ctor param
`StreamStemSplitEngine(segmentDurationUs = ...)` mà không phải đụng default.

Harness + log thật: `.superpowers/sdd/2026-09-04-stream-chunk-size/`. Liên quan:
[[project_streaming_phase2_shipped]].

**Hai cái bẫy khi đo trên device (đã mất thời gian vì cả hai):**
1. Chọn file TRƯỚC rồi tap engine chip = chạy 2 session (`onAudioFileSelected` đã gọi
   `startObserving()`), segment 0 của session cũ rơi vào timeline session mới → "first segment 2.5s"
   giả. Phải chọn variant trước, file sau.
2. `adb logcat -d` ở CUỐI run: ring buffer bị WindowManagerShell verbose làm tràn và wrap giữa run →
   báo "no segments" cho một lần tách đã xong. Phải stream `adb logcat | grep --line-buffered` ra
   file suốt run.
