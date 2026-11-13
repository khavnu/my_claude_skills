---
name: pattern-removed-string-extra-translation
description: Xoá string khỏi values/ trong khi nhánh khác thêm bản dịch → ExtraTranslation (Fatal) làm hỏng assembleRelease; debug build không lộ
metadata:
  node_type: memory
  type: project
  originSessionId: d6752420-e93a-4f84-ba77-d391c305b1bf
  modified: 2026-11-02T03:19:10.274Z
---

Xoá một `<string>` khỏi `values/` là chưa xong nếu nhánh khác (đợt dịch hàng loạt, vd commit "Translate ... into 58 languages" trên release/1.2) được viết khi string còn tồn tại. Sau khi rebase/merge, các file `values-xx/` còn key đó → lint `ExtraTranslation` mức **Fatal** → `lintVitalRelease` fail → `assembleRelease` fail. Debug build và unit test vẫn xanh nên không lộ.

Gặp 2026-11-02 (#496/#497 xoá `add_audio_new_audio_muted`, `add_audio_using_range`; rebase lên release/1.2 → 116 lỗi = 58 locale × 2).

**Why:** đợt dịch và đợt xoá string chạy song song trên 2 nhánh; git merge sạch vì không đụng cùng dòng.

**How to apply:**
- Sau mỗi lần rebase/pull từ release/1.2, nếu nhánh có commit xoá string: `grep -rl 'name="<key>"' app/src/main/res` phải ra 0.
- Kiểm nhanh không cần build release: `./gradlew :app:lintVitalAnalyzeRelease :app:lintVitalReportRelease -q 2>&1 | grep ExtraTranslation`.
- Sửa: `sed -i -E '/<string name="(key1|key2)">.*<\/string>/d'` trên các file tìm được; user chọn commit riêng (`AddAudio: Drop translations of ...`) thay vì gộp vào commit ticket.

Liên quan: [[pattern-gradle-cache-hides-broken-tests]] (cũng loại "debug xanh nhưng release/test gãy").
