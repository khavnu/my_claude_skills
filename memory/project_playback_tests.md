---
name: project_playback_tests
description: ":playback 0→36 test bằng Robolectric + ExoPlayer thật; lái playhead bằng seekTo chứ đừng chờ phát tới; mutation bắt 7 test của chính mình không assert gì"
metadata: 
  node_type: memory
  type: project
  originSessionId: e0e87c8a-7800-4c48-8018-92b52653531d
  modified: 2026-09-08T02:51:08.003Z
---

`:playback` (2.619 dòng, trước đây 0 test) giờ có **36 test**, không sửa dòng production nào.
Stack: JUnit4 + **Robolectric** + `media3-test-utils-robolectric` — ExoPlayer THẬT trên JVM, pin
`@Config(sdk = [34])`.

**Why Robolectric chứ không MockK** (dù CLAUDE.md khai stack MockK): mọi bug module này từng ship đều
là bug *hành vi Media3* (append khi `STATE_ENDED` không resume, drift correction đọc
`currentPosition` theo item thay vì source-time, ~58-69ms im lặng mỗi lần swap). Mock trả về đúng thứ
test bảo nó trả về → chỉ xác nhận lại cách hiểu đã đẻ ra bug.

**How to apply:**
- **Viết harness test TRƯỚC** (`StreamStemPlayerHarnessTest`): khẳng định ExoPlayer thật đạt
  `STATE_READY` từ WAV thật. Khi test hành vi đỏ, nó trả lời "harness hay player?" trước.
- **`@Config(sdk = [34])` là bắt buộc**: dưới API 33, `ContextCompat.registerReceiver` giả lập
  `RECEIVER_NOT_EXPORTED` bằng `${applicationId}.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION` — chỉ có
  sau khi manifest androidx.core được merge bởi một APP, không có trong test manifest của library.
- **QUAN TRỌNG NHẤT: lái playhead bằng `seekTo`, ĐỪNG chờ nhạc phát tới.** Đồng hồ ảo Robolectric và
  decode thật của ExoPlayer không gắn với nhau → mọi assertion cần playback tiến thật đều flaky. Sửa
  không phải bằng tăng timeout mà bằng cách **thôi cần tiến**: seek tới đúng chỗ rồi assert. Các test
  viết lại theo hướng này chạy 5/5 đều xanh (trước đó ~2/3).
- **Helper `idle(millis)` từng NÓI DỐI về thời gian**: chặn theo wall-clock nhưng mỗi vòng đẩy virtual
  time 20ms → đẩy đồng hồ vượt hàng chục giây, trả về vị trí 15810ms trên track 4000ms. Phải advance
  đúng số ms yêu cầu, theo bước 250ms (chu kỳ ticker). Sửa xong nó **lộ ra 3 test vốn chỉ bắt được
  mutation nhờ cái vượt đó** → phải khai báo precondition tường minh (`idleUntil { isPlaying }`).
- Đo "có đang phát không" thì đọc `dumpsys audio`, không đọc UI (xem [[project_r8_consumer_rules]]).

**Bài học lớn nhất — mutation test bắt 4 test của chính tôi là vacuous** (16 mutation, 4 lọt):
1. Test đọc state ở thời điểm không phân biệt được (buffering bật cả khi đang load, chưa `STATE_ENDED`).
2. Mutation bị chính `coerceIn(...)` trong hàm đang test **che mất** → phải assert *chặt hơn* biên,
   không phải "nằm trong range".
3. Test assert hành vi clamp **của Media3** chứ không phải của thư viện → **xoá test**, ghi lý do.
4. Test assert "không lỗi" cho một lỗi vốn không sinh ra lỗi (loop range sai chỉ teleport playhead).

Có mutation **unfalsifiable by construction** (guard `playersByKey.isEmpty()` trong `seekTo` sau
`stop()` — `endSession` đã clear map rồi): reframe test sang phần thật sự falsifiable.

**Bẫy công cụ:** `sed` với `\n` trong pattern KHÔNG match nhiều dòng → mutation im lặng không áp
dụng, báo "not caught" giả. Luôn dùng script fail lớn khi pattern vắng mặt.

**Thêm 3 loại test vô dụng nữa (vòng 2), tổng 7:**
5+6. `setStemVolume`/`setMasterVolume` stub thành `return` mà **không test nào đỏ** → **volume không
   đọc lại được qua API công khai của cả hai player** (rơi vào `ExoPlayer.volume`). Đã **xoá 2 test**.
   Muốn phủ phải thêm accessor đọc lại — quyết định về API, không phải về test.
7. `seekTo` sau `stop()`: bỏ **cả hai** guard vẫn không đỏ — sau `endSession` không còn source để hỏi
   lại, unfalsifiable by construction. Đổi sang assert `stop()` có phá session không.

**CẬP NHẬT 2026-09-08 — mục 5+6 đã bịt, và cái giá của việc trì hoãn nó:** đợt fade
([[project_fade_merge_export]]) buộc phải ra quyết định API đó. `appliedVolumeOf(stemKey): Float?`
trả về giá trị thực nằm trên `ExoPlayer.volume`, nên volume + master volume + fade giờ test được qua
một accessor duy nhất. **Trong lúc chưa có nó, đúng 2 bug fade đã lọt lên tay user** — fade không
tới player thì không phân biệt được với fade đã tới. Bài học: "không quan sát được" không phải lý do
chính đáng để bỏ trống lâu dài; nó là nợ, và nợ đó được trả bằng bug.
`:playback` giờ **56 test**.

**Chưa phủ:** drift correction/lockstep N player (cố ý — cần đúng cái uncoupling làm mọi thứ flaky,
test dựng trên đó là kịch bản chứ không phải tái hiện).

Ledger: `.superpowers/sdd/2026-09-07-playback-tests/`.
