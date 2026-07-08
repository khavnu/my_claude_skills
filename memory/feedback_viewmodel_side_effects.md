---
name: feedback_viewmodel_side_effects
description: "ViewModel pattern — update state trước, rồi gọi named side-effect functions dùng shared computation helper"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a57bc916-11a4-47b4-9e20-bf77f2207f33
---

Update state trước, sau đó gọi named private functions cho side effects. Shared computation là một helper riêng.

**Pattern:**
```kotlin
fun onXChanged(value: ...) {
    _uiState.update { it.copy(field = value) }
    updateDisplayedResult()   // side effect 1
    updateExternalSystem()    // side effect 2
}

private fun currentValue(): Float { ... }          // shared computation
private fun updateDisplayedResult() { ... }        // dùng currentValue()
private fun updateExternalSystem() { ... }         // dùng currentValue()
```

**Why:** Không inline logic vào từng branch của `when` — dẫn đến duplicate và khó test. State update + side effects tách biệt: state update là atomic, side effects chạy sau khi state đã đúng. `currentValue()` là single source of truth — mọi side effect đều đọc từ đây.

**How to apply:** Phát hiện pattern này tại bước pseudo-code, không phải sau khi code xong. Khi viết pseudo-code cho một VM function mà thấy nó làm 2+ việc khác nhau → đặt ngay câu hỏi "việc nào dùng chung computation?" → extract `currentX()` và named side-effect functions trước khi viết code thật. Nếu phải đợi đến review mới thấy → pseudo-code chưa đủ chi tiết.
