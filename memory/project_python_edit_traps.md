---
name: project_python_edit_traps
description: "Sửa file Kotlin bằng script python: bẫy substring companion lồng nhau (dính 3 lần/ngày) và numpy int16 tràn khi verify audio"
metadata:
  type: feedback
---

Hai cái bẫy đã làm hỏng việc nhiều lần trong cùng một ngày (2026-09-08), đều thuộc loại **im lặng**:
script chạy thành công, kết quả sai.

**1. `s.replace("    private companion object {")` khớp nhầm companion LỒNG NHAU.**
Companion cấp class thụt 4 space, companion lồng trong class con thụt 8 space — mà chuỗi 4 space là
**substring** của chuỗi 8 space. `str.index`/`replace` khớp cái lồng trước (nó đứng trước trong file),
nên hằng số/test bị nhét vào trong `FakeSegmentSource` → `Unresolved reference` hàng loạt.
Dính **3 lần** trong một phiên.

**How to apply:** neo bằng regex đầu dòng — `re.search(r"^    private companion object \{$", s, re.M)`
— hoặc neo vào một dòng chỉ tồn tại ở đúng chỗ cần (`const val TICK_MS`). Cùng họ với bài học
`sed` + `\n` không match nhiều dòng ở [[project_playback_tests]].

**2. numpy cộng mảng `int16` TRONG `int16` → tràn im lặng.**
`voc + dru + bas + oth` rồi mới `.astype(float64)` = wrap trước khi cast. Nó báo mix lệch 24.586 frame,
worst 65.535 (lật dấu full-scale) — trông y hệt wraparound trong encoder, suýt đổ oan cho code đã ship.
Cast float64 **trước** khi cộng, và bật `np.seterr(all='raise')`.

**Nguyên tắc rút ra, áp dụng rộng:** khi một phép đo tố cáo code đã ship + đã test một lỗi *cơ bản*
(tràn số, lật dấu), **nghi phép đo trước**. Xem [[project_fade_merge_export]].

**3. Wrapper tự viết bọc call site thì phải chặn theo receiver.** Script bọc `.seekTo(` đã bọc nhầm cả
`viewModel.seekTo(fraction: Float)` — trùng tên nhưng khác hàm. Lọc theo `player.seekTo(` hoặc bỏ qua
arg khớp `capture(`/`any(`.

**2026-10-08 (lần nữa):** cắt chuỗi cần thay bằng `s[s.index(A):s.index(B) if B in s else len(s)]` — khi đánh dấu B
không có, đoạn cắt RỖNG và `s.replace('', new)` chèn `new` vào giữa MỌI ký tự (pixel_ui.py thành 80 KB rác).
**How to apply:** luôn `assert old in s and old` trước `replace`; file nhỏ thì viết lại cả file bằng Write.
