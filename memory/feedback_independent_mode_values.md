---
name: feedback_independent_mode_values
description: "Khi UI có nhiều mode/unit — lưu giá trị riêng cho từng mode, không convert"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a57bc916-11a4-47b4-9e20-bf77f2207f33
---

Khi UI có nhiều mode hiển thị cùng một khái niệm (ví dụ: percent vs dB, px vs rem, bpm vs ms), lưu giá trị riêng cho từng mode thay vì lưu một giá trị canonical rồi convert.

**Pattern:**
```kotlin
data class UiState(
    val mode: Mode = Mode.A,
    val valueA: Float = defaultA,   // giá trị riêng của mode A
    val valueB: Float = defaultB,   // giá trị riêng của mode B
)

fun switchMode(mode: Mode) {
    _uiState.update { it.copy(mode = mode) }
    // KHÔNG convert valueA → valueB hay ngược lại
}
```

**Why:** Convert giữa các mode thường lossy (float precision, scale mismatch) và confusing khi đọc state. Hai giá trị độc lập → user có thể switch qua lại mà không mất giá trị đã set ở mode kia. Computation từ giá trị nào dùng `when (mode)` tại nơi cần (save, preview, display).

**How to apply:** Bất cứ khi nào có radio/tab chọn đơn vị hoặc mode → đặt câu hỏi "2 giá trị này có thực sự phụ thuộc nhau không?" Nếu user có thể muốn nhớ cả 2 → lưu độc lập.
