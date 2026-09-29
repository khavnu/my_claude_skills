---
name: project_fill_preemption_bug
description: "requestSegment preempt cả khi segment đích đã Ready → fill livelock khi đang phát; fix 1 điều kiện, nhanh hơn 1.85x"
metadata:
  type: project
---

`StreamSeparationSession.requestSegment` giờ chỉ preempt khi segment được yêu cầu **còn cần việc**:
`_statuses.value[index] !is SegmentStatus.Ready`. Sửa 2026-09-07.

**Why:** `requestSegment(i)` = "playhead giờ ở i", trước đây preempt bất cứ segment đang chạy nào khi
`current != i`. Đúng cho seek — nhưng khi đang phát, fill chạy TRƯỚC playhead, nên mỗi lần playhead
bước sang segment kế (đã Ready) là huỷ đúng việc đang chạy, rồi `nextPending()` chọn lại **đúng index
đó** và làm lại từ đầu. Segment nào cần lâu hơn thời gian playhead đi qua 1 segment → fill
**livelock**, không tiến chút nào cho tới khi playback cạn và playhead dừng.

**Bằng chứng:** khoảng chết 49.8s trong log, kết thúc đúng lúc playback cạn (playhead ngừng đổi); và
log `separateSegment[N]` **lặp** cho segment đã tách xong (do `separateSegment` log ở CUỐI, còn ghi
status nằm sau nó dưới `if (isActive)` — preempt rơi vào khe đó là mất trắng một segment đã xong).

**Kết quả:** 4-Stem Q, cùng bài, cùng thermal status 1, đang phát: **211.7s → 114.2s (1.85x nhanh
hơn)**, 0 duplicate, gap lớn nhất 49.8s → 9.9s.

**How to apply:**
- "3 lần dừng sớm không lặp lại" ban đầu bị xếp là intermittent — thực ra **2 trong 3 là bench của tôi
  tự cắt sau 30s không tăng**. Fill không chết, nó tạm dừng dài. Đọc log kỹ trước khi gắn nhãn
  "intermittent".
- Test có sẵn `requestSegment race never leaves a segment stuck Loading` dùng "re-seek vào segment đã
  Ready" làm **phương tiện** để lọt vào `cancelInFlight()` — fix bịt đúng đường đó nên phải đổi
  phương tiện. Target phải (a) còn cần việc, và (b) khiến worker swap sang segment **có gate**, nếu
  không thì chẳng còn gì in-flight để strand và race im lặng ngừng tái hiện.
- **Mutation thiếu đọc giống test yếu.** Tôi bỏ lock ở đoạn *start* của worker và kết luận đã làm yếu
  test — sai: đoạn cleanup sau `job.join()` vẫn lock nên worker vẫn bị chặn. Phải bỏ **cả hai** chỗ
  lock mới mở được race.

**5-Stem Original sau fix (đo 2026-09-07, đang phát, thermal 1): 143.7s = 1.60x realtime, 0 buffering,
0 underrun.** Tôi từng ghi "giả định nó tụt dưới realtime khi phát" — **SAI**, nó còn cao hơn cả 1.4x
đọc lúc rảnh trước fix. Công việc bị vứt đi do bug tốn nhiều hơn cái giá của một stem phụ.

**Chưa xử:** khe "log rồi mới ghi status" — một seek thật vẫn có thể bỏ đi 1 segment vừa xong. Lãng
phí 1 segment chứ không livelock, nên là defect riêng, không gộp.

Ledger: `.superpowers/sdd/2026-09-07-fill-stall-bug/`. Liên quan: [[project_stream_chunk_10s]].
