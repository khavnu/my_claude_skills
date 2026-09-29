---
name: pattern-gradle-cache-hides-broken-tests
description: compileDebugUnitTestKotlin báo SUCCESSFUL dù test gãy — đổi interface phải chạy --rerun-tasks mới lộ
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-15T02:07:51.517Z
---

Thêm một method vào interface (`SeparateAudioBenchmarkRepository.canRunMode`) làm 9 anonymous object
trong test gãy, nhưng `./gradlew :app:compileDebugKotlin :app:compileDebugUnitTestKotlin
:app:compileDebugAndroidTestKotlin` vẫn **BUILD SUCCESSFUL** — task up-to-date nên Gradle bỏ qua.
Chỉ `--rerun-tasks` mới lộ ra 4 lỗi androidTest + 5 lỗi unit test.

**Why:** rule "build luôn gồm build code TEST" tồn tại để bắt đúng loại lỗi này, nhưng cache vô hiệu
hoá nó. Lệnh chạy xanh tạo cảm giác đã verify trong khi chưa compile lại dòng nào.

**How to apply:** khi thay đổi **chữ ký public** (thêm/xoá method trên interface, đổi tham số
constructor, đổi kiểu trả về) → luôn thêm `--rerun-tasks` cho lần compile cuối trước khi báo xong.
Thay đổi chỉ trong thân hàm thì không cần.

Dấu hiệu nghi ngờ: vừa đổi interface mà compile xong trong <10s và không có dòng `> Task ...Kotlin`
nào chạy thật.

Liên quan: [[feedback-build-run-tests]]
