---
name: feedback-build-run-tests
description: "Sau khi code change, luôn chạy test kèm build để không bỏ sót test file bị broken"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2cfc9170-4f8b-4b36-b06a-41022938b6bc
---

Sau mỗi code change, không chỉ chạy `compileDebugKotlin` mà phải chạy thêm `testDebugUnitTest` để catch broken tests.

**Why:** Khi rename function/param trong implementation, các test file liên quan có thể bị compile error hoặc logic failure mà chỉ chạy compile thì không phát hiện được (vd: EqualizerViewModelTest tham chiếu `DEFAULT_TOOL_FOLDER` đã bị xóa nhưng compile pass riêng không catch được).

**How to apply:** Workflow chuẩn sau mỗi thay đổi:
1. `./gradlew :<module>:compileDebugKotlin` — fast feedback
2. `./gradlew :<module>:testDebugUnitTest` — để catch broken tests
