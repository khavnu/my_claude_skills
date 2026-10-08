---
name: long-feature
description: Use when starting or continuing a large, long-running feature (multi-session, heavy processing, performance-sensitive — e.g. on-device ML, media pipelines, background jobs) — drives work from a checklist file with verifiable basic + advanced requirements, executed autonomously until every item is ticked with evidence.
---

# Long Feature — checklist-driven, tự chủ

Quy trình cho feature khó và dài. Khác quy trình thường (chờ user test từng bước):
**Claude tự chủ thực hiện và tự verify theo checklist**, chỉ dừng lại ở các checkpoint quy định bên dưới.

## Khi nào dùng

- User nói rõ (vd "làm theo checklist", "long-feature"), HOẶC
- Claude tự đề xuất khi thấy một trong các dấu hiệu: feature cần nhiều session, xử lí nặng
  (ML on-device, decode/encode, file lớn), chạy nền lâu, hoặc có yêu cầu hiệu suất/RAM/thời gian.
  Đề xuất bằng một câu: *"Feature này nên chạy theo `long-feature` vì [lý do]. Dùng không?"*, rồi chờ user trả lời.

## Các phase

```
0. Tham khảo đối thủ   (tuỳ chọn, do USER làm)
1. Soạn checklist       → CƠ BẢN (chức năng) + NÂNG CAO (target, ràng buộc)   ⏸ user duyệt
2. Thực hiện CƠ BẢN     → tự chủ, tick kèm bằng chứng                        ⏸ báo cáo khi xong nhóm
3. Thực hiện NÂNG CAO   → đo, tối ưu, tick kèm số đo                         ⏸ báo cáo khi xong nhóm
4. Hoàn thiện           → lặp lại đến khi tick hết, rồi retro
```

### Phase 0 — Tham khảo đối thủ
- User tự tìm, cài và dùng app đối thủ, sau đó trao đổi lại. Claude KHÔNG tự tìm hay cài app.
- Claude hỗ trợ: gợi ý những gì nên quan sát hoặc đo (flow, thời gian xử lí, RAM qua
  `adb shell dumpsys meminfo <pkg>`, dung lượng APK, hành vi khi chạy nền hoặc bị kill), và có thể
  chạy lệnh `adb` đo trên app đối thủ user đã cài.
- Kết quả ghi vào mục **Tham khảo** của checklist. Số đo của đối thủ dùng làm mốc cho target nâng cao.

### Phase 1 — Soạn checklist
- File: `docs/features/<feature-name>/checklist.md` trong repo (dùng template bên dưới). File này là
  nguồn sự thật xuyên session: đầu mỗi session phải đọc nó trước khi làm tiếp.
- Checklist NÂNG CAO phải **soạn ngay từ đầu** dù làm sau, vì target phi chức năng quyết định
  kiến trúc (vd thời gian xử lí vượt trần WorkManager → buộc phải foreground service;
  native heap lớn → cần unload hoặc chặn theo RAM máy). Phát hiện muộn thì phải làm lại phần cơ bản.
- Mỗi mục phải có **tiêu chí xong kiểm chứng được**: tên test, lệnh đo, con số, file mẫu, thiết bị.
  Không viết được tiêu chí → mục đó chưa rõ → hỏi user.
- Mục nâng cao đo trên **input thực tế và đủ lớn** (vd file ≥10 phút), vì input ngắn giấu lỗi.
- Edge case: chạy skill `edge-cases`, các dòng có Verify đưa vào checklist như mục thường.
- Feature có màn hình hoặc component UI mới hay sửa lại → soạn phần UI theo **Lối đi UI** bên dưới.
- ⏸ **Checkpoint bắt buộc**: user duyệt checklist trước khi code. Checklist là hợp đồng.

### Lối đi UI (khi feature có UI)
"Build xanh" và "test pass" không chứng minh được UI đúng thiết kế. Mục UI chỉ được tick khi có bằng chứng nhìn thấy được.

**Soạn checklist (Phase 1):**
- Mỗi màn hình hoặc component ghi rõ **nguồn thiết kế**: Figma URL + node id, hoặc "không có Figma".
  - Có Figma → chạy `figma-reader` tới hết Step 2.6 (token, layout overview, báo cáo composable tái dùng). Các bước
    đó cần user xác nhận, nên gộp kết quả vào checklist để user **duyệt cùng lúc** với checklist, không hỏi rải rác lúc code.
  - Không có Figma → chạy `create-design` phần Brief và chốt hướng thiết kế. User duyệt cùng checklist.
- Mỗi màn hình tách 2 mục theo Rule 9, theo đúng thứ tự: **shell với fake data** → **wire data thật**.
- Liệt kê các **trạng thái** cần chụp: empty / loading / error / dữ liệu dài nhất, cùng các biến thể project hỗ trợ
  (dark mode, landscape, tablet, font scale lớn, RTL). Bỏ biến thể nào thì ghi lý do.

**Tiêu chí "Xong khi" cho mục UI** — đủ cả 3:
1. Screenshot trên device/emulator cho từng trạng thái đã liệt kê (`adb exec-out screencap -p > <file>`), lưu ở
   `docs/features/<feature-name>/evidence/`.
2. Đối chiếu với Figma screenshot (`get_screenshot` của node), liệt kê từng chỗ khác biệt. Mục chỉ tick khi
   danh sách khác biệt trống, hoặc mỗi chỗ còn lại đã được user chấp nhận (ghi vào Nhật ký quyết định).
   Không có Figma → thay bằng Review Gate của `create-design` trên screenshot.
3. Có Figma → đã làm `figma-reader` Step 2.7 (audit thuộc tính toàn node) và Step 4 (checklist sau khi viết code).

**Khi thực hiện (Phase 2):**
- Làm shell trước, chụp và đối chiếu xong mới wire data. Wire xong thì chụp lại với data thật, vì text dài hoặc
  số lớn hay làm vỡ layout mà fake data không lộ ra.
- Chỗ khác biệt mà thiết kế không nói rõ (Figma thiếu trạng thái, hai frame mâu thuẫn, không biết khác biệt có chủ đích không)
  → dừng hỏi user (Rule 10). **Không tự chấp nhận khác biệt.**
- Ghi bằng chứng dưới mục: đường dẫn screenshot, node id đã đối chiếu, danh sách khác biệt và cách xử lý từng chỗ.

### Phase 2–3 — Thực hiện tự chủ
- Làm lần lượt từng mục. Tự verify bằng unit test, androidTest trên device hoặc đo qua `adb`, theo đúng
  tiêu chí đã ghi. Không cần chờ user test từng mục.
- Tick một mục **chỉ khi đã có bằng chứng**. Ghi bằng chứng ngay dưới mục (test class, lệnh đã chạy,
  số đo, ngày đo).
- Vẫn tuân thủ đầy đủ Build Verification, TDD, coding rules. Tự chủ không có nghĩa là bỏ bước.
- Cập nhật checklist ngay khi có thay đổi: tick mục, thêm mục mới phát sinh (đánh dấu `(mới)`),
  ghi quyết định vào mục **Nhật ký quyết định**.

### Khi nào PHẢI dừng lại hỏi user (dù đang tự chủ)
1. Xong một nhóm mục: báo cáo ngắn gồm mục đã tick, bằng chứng chính và vấn đề phát sinh.
2. Quyết định sản phẩm hoặc UX mà checklist/design không nói (Rule 10: không chắc thì hỏi, không đoán).
3. Target không đạt sau 2 hướng tối ưu khác nhau → trình bày số đo và trade-off, đề xuất
   hạ target hoặc đổi hướng. **Không tự hạ target.**
4. Muốn đổi, bỏ hoặc hoãn một mục đã được duyệt.
5. Cần thứ Claude không tự làm được: thiết bị cụ thể, file mẫu, tài khoản, cài app đối thủ.
6. Thay đổi không đảo ngược được (DB migration, xoá data, đổi proto field).

Không bao giờ tự commit hoặc push (Workflow Rule 6 vẫn áp dụng).

### Hết usage limit giữa chừng
Theo `~/.claude/skills/_shared/usage-limit-protocol.md`:
- **Ghi tiến độ:** mỗi mốc bước (một mục tick, build xanh, một quyết định) nối thêm 2–4 dòng vào mục
  **Điểm dừng** cuối checklist — đang ở mục nào, bằng chứng tới đâu, file nào đang sửa dở, agent con nào
  đang chạy (kèm đường dẫn report). Chỉ nối thêm, không viết lại cả file, không đọc lại khi đang làm.
- **Tạm dừng** (user báo sắp hết limit, hoặc thấy thông báo limit): không mở hạng mục / agent mới,
  dừng gọn bước hiện tại, cập nhật Điểm dừng.
- **Tự chạy lại:** biết giờ reset (đọc `~/.claude/usage-latest-<K|D>.json` hoặc user báo; không đoán) → `CronCreate` một lần lúc reset + 5 phút
  (reset 13:30 → 13:35) với prompt `[resume] …` trong protocol. Tiếp tục = đọc Điểm dừng, `git status`/`git diff`,
  build xanh, agent con đã chết thì giao agent mới làm tiếp phần dở.

### Phase 4 — Hoàn thiện
- Mọi mục đã tick và có bằng chứng, hoặc được user cho phép hoãn (ghi rõ lý do).
- Chạy lại toàn bộ test liên quan và đo lại các target nâng cao lần cuối trên build cuối.
- Retro (Workflow Rule 11): ghi memory cho pattern hoặc pitfall tốn thời gian. Mục hoãn có chủ đích →
  ghi memory `project_<feature>_open_items` để session sau không "phát hiện lại".

## Template checklist

```markdown
# <Feature name> — Checklist

Trạng thái: Phase <n> · Cập nhật: <YYYY-MM-DD>

## Tham khảo
| App | Quan sát | Số đo (thiết bị, input) |
|---|---|---|

## Cơ bản (chức năng)
### Nhóm A — <tên nhóm>
- [ ] A1. <yêu cầu>
  - Xong khi: <tiêu chí kiểm chứng được>
  - Bằng chứng: <test / lệnh / kết quả — điền khi tick>

### Nhóm UI — <màn hình> (chỉ khi có UI; xem Lối đi UI)
- Nguồn thiết kế: <Figma URL + node id | không có Figma → brief create-design>
- Trạng thái chụp: <empty / loading / error / dữ liệu dài / dark / landscape / …>
- [ ] U1. Shell với fake data
  - Xong khi: screenshot từng trạng thái + đối chiếu Figma, không còn khác biệt chưa được duyệt
  - Bằng chứng: <evidence/…png · node id · khác biệt + xử lý>
- [ ] U2. Wire data thật
  - Xong khi: chụp lại với data thật, layout không vỡ
  - Bằng chứng:

## Nâng cao (target & ràng buộc)
| # | Chỉ số | Target | Mốc đối thủ | Cách đo (thiết bị, input) | Kết quả | ✓ |
|---|---|---|---|---|---|---|
| N1 | Thời gian xử lí | | | | | |
| N2 | Peak RAM | | | | | |
| N3 | Dung lượng APK | | | | | |
| N4 | Chạy nền / bị kill | | | | | |
| N5 | Máy yếu (RAM thấp) | | | | | |

## Nhật ký quyết định
- <YYYY-MM-DD> — <quyết định> — <lý do> — <ai quyết>

## Hoãn có chủ đích
- <mục> — <lý do> — <user đồng ý ngày>

## Điểm dừng
<!-- nối thêm 2–4 dòng mỗi mốc bước: mục đang làm, bằng chứng, file sửa dở, agent con + report -->
```
