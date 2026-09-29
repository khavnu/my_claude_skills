---
name: gridlayout-gone-keeps-cell
description: "GridLayout không reflow khi child GONE — ô vẫn bị chiếm, nên cell ẩn có điều kiện phải xếp cuối"
metadata: 
  node_type: memory
  type: project
  originSessionId: e02b1c32-3888-4db9-86df-11a27581791b
  modified: 2026-09-18T01:46:53.782Z
---

`android.widget.GridLayout` coi child `GONE` là zero width/height chứ **không** bỏ qua nó khi
đánh số ô. Ô của child GONE vẫn bị cấp phát → lưới thủng lỗ giữa hàng. Cột/hàng chỉ collapse
khi **mọi** child trong đó đều GONE (và child có `layout_gravity`). Nguồn: AOSP
`GridLayout.java` javadoc "Interpretation of GONE" + `createGroupBounds()` comment
*"we must include views that are GONE here"*.

Hệ quả khi dùng GridLayout làm flow container: **cell nào bị ẩn/hiện lúc runtime phải là
child cuối cùng**, để cả hàng cuối collapse gọn thay vì để lỗ.

Áp dụng trong repo này ở card action màn Detail (`@style/DetailButtonContainer`, columnCount =
`@integer/detail_action_columns` — 3 phone / 5 tablet sw600dp):
- `other_square_code_detail_fragment.xml` — Edit/Copy bật tắt theo `DetailOtherCodesFragment
  #updateDisplay` (hiện với Aztec/DataMatrix, ẩn với barcode 1D) → phải xếp **sau** Search/Share/Save.
- `qr_url` (`layout_open_url`) và `qr_text` (`layout_search`) may mắn nằm một mình ở cột cuối
  nên GONE thì cột tự collapse thành lưới 2 cột, không cần đảo thứ tự.

ConstraintLayout `Flow` xử lý GONE đúng nhưng hàng cuối spread theo số phần tử của riêng hàng đó
→ không canh được theo lưới cột. FlexboxLayout làm được cả hai nhưng phải thêm dependency.

Liên quan: [[adjustresize-dead-on-targetsdk35]]
