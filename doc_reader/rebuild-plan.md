# Plan tổng quát — xây lại engine đọc file Office

Mức roadmap: mỗi phase có mục tiêu, phạm vi, tiêu chí xong. Chi tiết từng phase (task, test, file) bổ sung sau.
Ngày lập: 2026-11-17. Tham chiếu: `README.md` (flow, quyết định), `doc-engine.md` (nguyên tắc P1–P10), `research/01..06`.

## Flow đích

```
1. Mở file      → file seekable, kiểm tra kích thước/RAM, mở zip hoặc OLE
2. Đọc → model  → streaming từng block/slide/row → DocModel / SlideModel / Sheet store
3. LAYOUT       → ngắt dòng, chia trang, đặt bảng/ảnh → PageModel (danh sách lệnh vẽ)
4. Lưu trang    → N trang trong RAM, phần dư ghi ra disk
5. Render       → painter vẽ PageModel lên Canvas, chỉ trang/tile đang thấy
```

**Ngoài phạm vi:** sửa PDF, PDF → Word (research 07, 08). Xem PDF thì không đi qua flow này (dùng Pdfium vẽ thẳng).

## Cách tiếp cận

- **Lát mỏng xuyên 5 bước trước, mở rộng sau.** Phase 1 cho ra trang `.docx` đầu tiên trên màn hình, dù chỉ có chữ thuần.
  Mỗi phase sau làm dày thêm một bước hoặc thêm một định dạng; cả 5 bước luôn chạy được.
- **Hợp đồng trước, implementation sau.** `PageModel`/`PageItem` và các model là xương sống; chốt sớm, có version.
- **Đo trước, tune sau.** Mỗi phase có tiêu chí xong đo được, so với render tham chiếu, kèm baseline chỉ cho đi lên (ratchet).
- **Core thuần JVM, phần Android mỏng.** Mọi thứ trừ vẽ/view/đo chữ đều test được trên JVM với heap 512m.

---

## Phase 0 — Chốt quyết định và dựng nền đo

| | |
|---|---|
| Mục tiêu | Mọi phase sau có chỗ đặt code và cách đo |
| Việc chính | Chốt các quyết định ở README (chuẩn Word hay LibreOffice; bảng tin `tblGrid` hay tự autofit; giữ POI cho định dạng cũ; nơi xây lib) · Tạo khung module: core (JVM) + android (render/view) · Corpus tầng 1 (fixture nhỏ) và tầng 2 (file thật + PDF render tham chiếu) · Harness chạy được: dump model/page → golden, so số trang / text / SSIM với tham chiếu, ghi baseline |
| Tiêu chí xong | Một lệnh chạy ra bảng số trên corpus (lúc này toàn 0 / skip) · CI hoặc lệnh local chạy test core với heap 512m |
| Research | README §Quyết định, `doc-engine.md` §7, `repo-snapshot/README.md` |
| Rủi ro | Chưa có render tham chiếu thì không đo được độ đúng → phase này là điều kiện bắt buộc, không bỏ |

## Phase 1 — Lát mỏng `.docx` xuyên 5 bước

| | |
|---|---|
| Mục tiêu | Mở `.docx` chỉ có đoạn văn, thấy đúng trang trên màn hình |
| Phạm vi | B1: mở zip, đọc relationships, kiểm tra kích thước · B2: paragraph + run (font, size, bold/italic, màu), section đầu tiên · B3: đo chữ qua interface `TextMeasurer` (bản Android + bản JVM), ngắt dòng, chia trang, căn lề · B4: giữ toàn bộ trang trong RAM (chưa spill) · B5: painter vẽ text line, view cuộn dọc đơn giản |
| Chưa làm | style cascade, bảng, ảnh, header/footer, streaming, tile |
| Tiêu chí xong | Golden cho model + page của fixture · Số trang khớp tham chiếu trên tập file chỉ có chữ · Đo chữ khi layout và khi vẽ cho cùng độ rộng (test sai số) |
| Research | 01 §2–4, 02 §4–5 (line breaking), 06 §4–5 (PageItem, painter, `RunPaints`) |
| Rủi ro | Đo chữ lệch giữa layout và vẽ → chữ tràn; chốt cơ chế đo/vẽ chung ngay từ phase này |

## Phase 2 — Hạ tầng streaming và hiệu năng

| | |
|---|---|
| Mục tiêu | File lớn mở nhanh, RAM không tỉ lệ với kích thước file |
| Phạm vi | B1: spool main part, giới hạn zip bomb, huỷ khi đóng · B2: body đọc streaming `Flow<Block>`, quét section trước · B3: layout progressive (phát `PageLaid` từng trang) · B4: `PageModelStore` (N trang RAM, spill qua codec nhị phân có version) · B5: lượt preview → full, tile khi zoom, cache theo phân số heap, ghim tile đang hiện, scheduler ưu tiên trang đang nhìn |
| Tiêu chí xong | Trang 1 hiện khi file đọc chưa tới 50% · Test heap 512m qua file lớn · Ngưỡng thời gian mở file và RAM đỉnh đo trên **release build** |
| Research | `doc-engine.md` P2–P5, 01 §3, 02 §3, 06 §3, §5–6 |
| Rủi ro | Đo trên debug build sẽ ra số sai → luôn đo release |

## Phase 3 — Word đầy đủ

| | |
|---|---|
| Mục tiêu | Đạt chất lượng hiển thị Word của bản hiện tại |
| Phạm vi (thứ tự gợi ý) | Style/numbering/theme cascade → spacing, line height, tab, justify → bảng (grid, merge, chia hàng qua trang) → ảnh inline → drawing, float, wrap → header/footer, footnote → field (PAGE/NUMPAGES dạng slot vẽ lại) → section, cột → font embedded, fallback → bidi, math, revision, comment (tuỳ ưu tiên) |
| Tiêu chí xong | Mỗi tính năng có fixture + golden · Metric so tham chiếu (số trang, text, SSIM) không thấp hơn bản hiện tại trên corpus tầng 2 |
| Research | 01 (toàn bộ), 02 (toàn bộ) |
| Rủi ro | Phase lớn nhất, dễ thành vá từng mẫu → giữ quy trình đo trước, chốt đáp án trước (`lessons.md`) |

## Phase 4 — Slide `.pptx`

| | |
|---|---|
| Mục tiêu | Xem slide, dùng lại bước 4–5 |
| Phạm vi | Đọc từng slide · kế thừa master → layout → slide, theme colour và colour transform · preset/custom geometry · text body, autofit, bullet · group transform, z-order (PushGroup/PopGroup) · ảnh, crop, fill, line, bảng |
| Tiêu chí xong | Golden model + layout · SSIM so render tham chiếu không thấp hơn bản hiện tại |
| Research | 04, 06 |

## Phase 5 — Sheet `.xlsx`

| | |
|---|---|
| Mục tiêu | Xem bảng tính; rẽ khác ở bước 3–4 |
| Phạm vi | B2: cell và shared string ghi ra disk, sheet đọc khi được mở · B3: layout theo block hàng × cột (không chia trang), style, format số, độ rộng cột, tràn chữ, merge, viền · B4–5: grid view riêng, prefetch block lân cận · Sau đó: CF, chart, drawing · Tuỳ chọn: chia trang khi in → `PageModel` |
| Tiêu chí xong | RAM gần như không tăng theo số hàng (đo với sheet lớn) · Golden layout block · So text/SSIM với tham chiếu |
| Research | 05, 06 |

## Phase 6 — Định dạng nhị phân cũ `.doc` / `.ppt` / `.xls`

| | |
|---|---|
| Mục tiêu | Map vào **cùng** model của Phase 3–5, không thêm pipeline mới |
| Phạm vi | POI chạy trên minSdk của app (JAR patch hoặc nâng minSdk) · kiểm tra RAM trước khi dựng model · `.doc` qua HWPF, `.ppt` qua HSLF (không gọi `java.awt`), `.xls` đọc theo record · ảnh spool ra disk |
| Tiêu chí xong | Fixture từng định dạng qua cùng golden layout · Không OOM với file lớn trong ngân sách heap |
| Research | 03, 04 (phần HSLF), 05 (phần BIFF8) |

## Phase 7 — Hardening và release

| | |
|---|---|
| Mục tiêu | An toàn với file bẩn, chạy đúng trên máy thật |
| Phạm vi | Corpus file độc hại (zip bomb, XML lồng sâu, part hỏng, font lỗi) · không throw, part hỏng thì vẽ placeholder · test trên API thấp nhất · kiểm R8 (strip resource, gộp class) · baseline profile · corpus tầng 3 (hàng nghìn file) chạy smoke: không crash, không OOM, thời gian trong ngưỡng |
| Tiêu chí xong | Smoke corpus tầng 3 sạch · số đo release đạt ngưỡng của Phase 2 |
| Research | `doc-engine.md` P8, §9 (cạm bẫy), 01–05 §7 |

## Phase 8 (tuỳ chọn) — Export PDF / Print

Dùng lại painter vẽ `PageModel` lên canvas PDF, ghi theo chunk, gộp ảnh trùng. Research 06 §5.

---

## Khung xuyên suốt mọi phase

- Mỗi phase kết thúc khi: build đủ source set (kể cả test), golden và metric không lùi, verify trên máy với phase có UI.
- Hằng số heuristic nằm trong một bảng tuning, có đơn vị và lý do.
- Luật hành vi ghi vào spec và tên test, không chỉ ghi trong commit message.
- Đổi `PageItem` thì bump version codec.

## Cần bổ sung khi đi vào chi tiết

- Chọn nơi xây (lib mới hay thay thế `doc_core`/`doc_reader`) và cấu trúc module cụ thể.
- Ngưỡng số cụ thể cho Phase 2 (thời gian mở file, RAM đỉnh, fps).
- Danh sách file corpus tầng 2 và nguồn render tham chiếu.
- Chia task, test strategy (test-first/test-after) cho từng phase.
