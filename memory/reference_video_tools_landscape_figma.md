---
name: reference-video-tools-landscape-figma
description: "Figma landscape cho video tools (Compress/Remove audio/Add audio) nằm ở file s3U7R11f4UEGgwphncOJOQ page 3.Lanscape, KHÔNG phải file landscape audio bv1NOlAO7pbMyksVs7XnpH"
metadata:
  node_type: memory
  type: reference
  originSessionId: 71a8dc64-edac-4386-9060-b65d48abd648
  modified: 2026-10-21T02:00:03.012Z
---

Video tools có Figma riêng: `s3U7R11f4UEGgwphncOJOQ` (Music_editor). Portrait ở page `2.Design` section v1.3 (`1:4056` Compress, `1:4598` Remove audio, `1:4777` Add audio). Landscape dựng 2026-10-21 ở page `3.Lanscape` (`20:2726`): section `23:2725` Compress, `23:3466` Remove audio, `23:3817` Add audio.

File landscape của các tool audio (`bv1NOlAO7pbMyksVs7XnpH`, page `3.Landscape`) KHÔNG chứa video tools — đừng tìm ở đó. Plugin API không clone được node giữa 2 file, nên chrome landscape (top bar 800, side panel, scrim) phải dựng lại từ portrait cùng file.

Chỉ dựng màn tool + màn result (save success). Dialog processing, rename side panel, Select audio list KHÔNG dựng riêng: user nói chúng đã có landscape trên branch `update/landscape_support` (chưa merge vào nhánh video) — 2026-10-21.

~~Code landscape cho video tools CHƯA làm (2026-10-21)~~ — sửa 2026-10-26: đã làm và merge vào `release/1.2` (vd `411f54f3 Landscape: VideoSaveSuccessScreen ...`); `landscapeCutoutPadding()`/`AdaptiveSheet`/`SidePanel` đã có trên nhánh này.

Lưới dùng chung với bộ audio: frame 800x360, nội dung bắt đầu y=92, cột trái x=82 w=310, cột phải x=408 w=376; side panel x=440 w=360 bo trái 16; list screen (Select audio) full width 16..784. Liên quan [[feedback-landscape-column-alignment]].

**Cập nhật 2026-10-26:** user dựng lại portrait Compress video ở section `36:2725` (page 2.Design, v1.3): `36:2726` màn chính, `36:2953` "Video nhỏ / đã nén sẵn" (option disabled = container opacity 0.5, vòng tròn `-41%`). Frame cũ `1:4056` có thể đã lỗi thời — đọc `36:2725` trước. Nút Play trên video: node `1:4066`, 40dp, drop shadow đen 25% offset (2,5) blur 3. Figma audio compress KHÔNG nằm trong file này.

**Màn "Save successfully" landscape (2026-10-29, #489):** audio = file `bv1NOlAO7pbMyksVs7XnpH` page `3.Landscape` frame `160:4105`; video = file này frame `23:3168` (card), `23:3307` (player), `23:3818` (Remove audio), `23:3964` (Add audio). Đã dựng lại theo #489: cột trái (scrollable) card + Share… + Suggested Tools, divider dọc, cột phải header badge căn giữa + 2 nút xếp dọc, căn giữa dọc. Header badge portrait mới nằm ở `36:3196` (frame `1.4.0 Save successfully_GIF`); file audio KHÔNG có asset badge — đã upload frame cuối `res/raw/save_success_icon.webp` (PIL → PNG) qua `upload_assets` vào node `231:5094`.

**Tablet (2026-10-30, #491):** file audio `bv1NOlAO7pbMyksVs7XnpH` có page riêng cho tablet `6.Tablet` (`235:3`, user tạo 2026-10-30) — frame tablet mới đặt ở đây, không ở 3.Landscape. `233:5088` "8.1 Splitted - Tablet Landscape" (1280x800) trong section `236:2` "8. Split". Cột trái x66 w558 / phải x656 w608; vùng nền 300, segment 200 (khớp `TABLET_WAVEFORM_AREA_HEIGHT`/`TABLET_SEGMENT_HEIGHT`), cụm play ghim đáy. (Sửa 2026-10-30: bản đầu cho segment lấp kín vùng nền — user bác, ticket muốn giảm nền + tăng waveform.)
