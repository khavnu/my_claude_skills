---
name: project_playback_test_flakiness
description: ":playback Robolectric suite flaky SẴN (loop test đỏ 1/5 ở baseline) — đừng nhận là regression; idleUntil PHẢI chặn theo wall-clock vì ExoPlayer load trên thread nền thật"
metadata:
  type: project
---

Đo 2026-09-08, **có bằng chứng baseline** chứ không phải cảm giác.

**`StreamStemPlayerTest` flaky từ trước, không phải do việc mới.** Với **0 test mới nào** của mình,
`when a loop is set with its end before its start` đỏ **1/5 lần**. Chạy cả module (`:playback`) thì
mỗi lần một test khác trong class đó đỏ (~1/3 lần): `valid loop`, `position is source-track time`,
`dry queue is buffering`, `stop is called then session torn down`. Comment của chính test loop đã ghi
nó pass "on timing luck".

**How to apply:**
- Trước khi kết luận "test tôi vừa thêm làm hỏng test cũ" → **gỡ test mới ra, chạy baseline 5 lần**.
  Lần này baseline cứu khỏi một chẩn đoán sai hoàn toàn.
- **Thêm test fade vào class RIÊNG** (`StreamStemPlayerFadeTest`), không nhét vào `StreamStemPlayerTest`.
  JUnit4 sắp thứ tự method theo hash → thêm method làm xáo trộn vị trí của MỌI test trong class, nên
  nuôi class fragile sẽ làm flake sẵn có trông như regression.
- **`idleUntil` PHẢI chặn theo wall-clock, đừng "sửa" thành thời gian ảo.** Tôi đã thử vì tưởng
  wall-clock là nguồn flaky (đúng bài học mà `idle()` đã ghi) → **tệ hơn hẳn: 5 test đỏ/lần thay vì 1**.
  Lý do: Robolectric chạy ExoPlayer THẬT, phần load nằm trên thread nền thật, `idle()` chỉ bơm main
  looper. Phải chờ thời gian thật. Đã hoàn nguyên.
- Test nào cần đọc gain của fade thì **bắt buộc chờ `isPlaying`**: `fadeGainOf` đọc
  `getCurrentPosition()`, chưa synced-start thì nó null và gain short-circuit về 1.0 → test thành
  **vacuous** (từng làm test "unknown duration" mất hết ý nghĩa mà vẫn xanh).
- Muốn quan sát "ticker còn sống không" sau `stop()`: đọc `Robolectric.getForegroundThreadScheduler().size()`.
  Session còn sống thì baseline là 1 (position ticker 250ms) → so **chênh lệch**, không so với 0.
  Sau `endSession` mới drain về 0.
- Đọc kết quả fail: **dùng `xml.etree` parse test-results**, đừng regex — regex `.*?` ghép sai tên test
  với message, đã khiến tôi đổ oan cho test khác 2 lần.

**2026-09-11: `:core` cũng có một test flaky, cùng tỉ lệ 1/5.** `StreamStemSplitEngineSessionDirTest > successive sessions write into different subdirs…`. Tôi đã kết luận sai rằng file test mới của mình làm nó gãy — bằng chứng là một lần chạy riêng (xanh) và một lần chạy suite không có file mới (xanh). Gỡ file ra chạy 5 lần: **1/5 fail**. Luật này không chỉ áp cho `:playback`: gỡ thay đổi ra, chạy **5 lần**, rồi mới đổ lỗi. Một lần xanh không phải baseline.
