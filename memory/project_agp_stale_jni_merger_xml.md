---
name: project_agp_stale_jni_merger_xml
description: "Ghi đè .so in-place làm mergeXJniLibFolders NPE \"DataFile.getItems() because dataFile is null\" — xoá intermediates/incremental/mergeXJniLibFolders là hết."
metadata: 
  node_type: memory
  type: project
  originSessionId: 65f6c61d-676f-40d0-9fcf-114036fb906e
  modified: 2026-09-03T09:56:35.725Z
---

Ghi đè file `.so` **in-place** trong một jniLibs source set (cp lên file đã tồn tại, không
thêm/xoá path) làm task merge của AGP nổ:

```
Execution failed for task ':ijkplayer-java:mergeReleaseJniLibFolders'.
> Cannot invoke "com.android.ide.common.resources.DataFile.getItems()" because "dataFile" is null
```

**Why:** AGP giữ state incremental ở `<module>/build/intermediates/incremental/merge<Variant>JniLibFolders/merger.xml`.
State này ghi nhận file đã merge trước đó; file bị thay nội dung mà path không đổi làm nó
lệch pha → NPE. Không phải lỗi của .so, và **không** phải duplicate-path.

**How to apply:** xoá đúng state của variant đó rồi build lại, không cần full clean:

```bash
rm -rf <module>/build/intermediates/incremental/merge<Variant>JniLibFolders
```

Ví dụ: `rm -rf ijkplayer-java/build/intermediates/incremental/mergeReleaseJniLibFolders`.
Chỉ nổ ở variant bị ghi đè — variant khác vẫn build bình thường, nên dễ tưởng là lỗi .so.
Gặp mỗi lần drop bộ .so mới vào [[project_ijkplayer_jnilibs_variant_layout]].
