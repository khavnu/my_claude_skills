---
name: project_lib_going_to_product
description: "AudioSeparation là test bench; :audio_stem_split sắp chuyển sang product — kiến thức về LIB phải nằm trong docs của lib, không nằm trong memory"
metadata:
  type: project
---

2026-09-08: user cho biết sắp đưa `:audio_stem_split` sang một project product.

**Hệ quả quan trọng: memory bị khoá theo đường dẫn project.** Thư mục memory này là
`~/.claude/projects/-home-khapv-AndroidStudioProjects-AudioSeparation/memory/` — sang project khác thì
KHÔNG được recall. Nên phân loại kiến thức trước khi lưu:

- **Thuộc về LIB → viết vào docs của lib** (đi theo code): `audio_stem_split/README.md` (cách dùng +
  known issues), `docs/ENGINEERING-LOG.md` (quyết định + war story), `docs/DIAGNOSING-AUDIO-BUGS.md`
  (quy trình đo khi có bug audio).
- **Thuộc về WORKSPACE này → memory** (không đi theo lib): `adb` không có trong PATH
  ([[project_fade_merge_export]]), bẫy substring khi sửa file bằng script
  ([[project_python_edit_traps]]), `:playback` flaky sẵn ([[project_playback_test_flakiness]]),
  một Gradle JVM tại một thời điểm, convention checkpoint ([[project_checkpoint_convention]]).

**How to apply:** khi phát hiện điều gì mới về hành vi của thư viện, hỏi "cái này còn đúng khi lib nằm
ở project khác không?" — nếu có thì nó thuộc docs của lib, không phải memory.
