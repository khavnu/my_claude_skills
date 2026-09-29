---
name: project-adb-saf-picker
description: SAF file picker LÁI ĐƯỢC bằng adb — tap node clickable bao ngoài, không tap TextView; dùng root Downloads và List view
metadata:
  type: project
---

Lái được SAF picker (`ActivityResultContracts.OpenDocument`) từ adb để đưa file ngoài APK vào bench
app. Comment trong `app/src/main/java/com/example/audioseparation/feature/stem_splitter/BundledTrack.kt`
nói "A SAF picker cannot be driven from adb" — **sai**, và tin nó là lý do cả một corpus phải nhét
vào `res/raw`.

Ba thứ quyết định, thiếu cái nào cũng ra "picker đứng im" (đã mất ~20 phút vì cái thứ nhất):

1. **Tap node `clickable="true"` BAO NGOÀI, không tap TextView mang text.** Dòng file trong picker
   là TextView nằm trong `item_root` clickable. Tap đúng tâm chữ → không có gì xảy ra, dump vẫn ra
   màn hình cũ, trông y như treo. Cách làm: dump, tìm node theo text, rồi chọn node clickable nhỏ
   nhất CHỨA tâm node đó.
2. **Grid view chỉ cuộn, không mở file.** Bấm nút content-desc `List view` trước.
3. **Dùng root `Downloads`, đừng dùng `Audio`.** Root Audio gom theo nghệ sĩ, phải cuộn mò; Downloads
   là danh sách phẳng vài dòng. `adb push` file vào `/sdcard/Download/` là thấy ngay.
   Ô Search trong picker thì bấm được nhưng tap kết quả không ăn — đã thử 4 lần, bỏ.

Đường đi: `Chọn file nhạc` → content-desc `Show roots` → `Downloads` → `List view` → tên file.

Verify lại trong 10 giây: `adb -s <serial> shell dumpsys window | grep mCurrentFocus` — còn
`documentsui/...PickActivity` là chưa chọn được, đổi sang `com.example.audioseparation/.MainActivity`
là xong. Driver đã viết sẵn ở scratchpad `ui.py` của session, phần `Ui.tappable()` là chỗ cài rule 1.

Liên quan: [[project-fade-merge-export]] (bẫy `uiautomator dump` trả file cũ khi UI đang animate —
vẫn đúng, luôn `rm -f /sdcard/w.xml` trước mỗi lần dump).
