---
name: feedback-no-auto-translations
description: "Chuỗi mới chỉ thêm vào values/ (bản gốc); không tự thêm vào 58 file values-xx, kể cả chuỗi chỉ có định dạng"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d6752420-e93a-4f84-ba77-d391c305b1bf
  modified: 2026-11-02T08:36:12.698Z
---

Thêm string mới → chỉ thêm vào `app/src/main/res/values/` (bản gốc). KHÔNG tự chép/dịch sang các `values-xx/` (58 locale), kể cả khi chuỗi chỉ là định dạng không có chữ (vd `%1$d%%, ~ %2$s`).

**Why:** 2026-11-02 (#501) mình tự thêm `compress_video_level_subtitle_no_resolution` vào cả 58 file dịch, user yêu cầu gỡ ra — bản dịch do bên dịch làm theo đợt riêng.

**How to apply:**
- Thêm string: chỉ `values/`. Thiếu bản dịch = lint `MissingTranslation` (Error, không Fatal) → release vẫn build.
- Ngược lại khi XOÁ string khỏi `values/` thì PHẢI xoá cả ở `values-xx/`, không thì `ExtraTranslation` (Fatal) chặn release — xem [[pattern-removed-string-extra-translation]].
