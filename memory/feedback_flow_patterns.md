---
name: feedback-flow-patterns
description: "Pattern Flow/State học từ feature Video to Audio — sealed scan state, domain interface, shared singleton, flowOn tại source"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 53ec8f3f-3839-4e45-8e29-8bf52f9cb8ed
---

Các pattern phát hiện khi refactor `VideoRepository`:

**1. Sealed scan state thay vì 3 field riêng**
```kotlin
// ❌ Cũ — consumer phải combine thủ công
val videos: StateFlow<List<VideoFile>>
val isScanning: StateFlow<Boolean>
val scanError: Flow<Unit>

// ✅ Mới — một flow, state rõ ràng
sealed interface VideoScanState {
    data object Scanning : VideoScanState
    data class Ready(val videos: List<VideoFile>) : VideoScanState
    data object Error : VideoScanState
}
fun observeScanState(): Flow<VideoScanState>
```

**2. Domain interface dùng `fun observeX(): Flow<T>`**
- Không dùng `val x: StateFlow<T>` — lộ impl detail, khó mock trong test
- `StateFlow` chỉ nên tồn tại trong impl (`MutableStateFlow`) và output của `stateIn()` trong VM

**3. Shared singleton state**
- Nhiều VM cần cùng data → `MutableStateFlow` trong `@Singleton` + `@ApplicationScope`
- Cold `Flow` = mỗi subscriber trigger một operation mới (scan, query...) — KHÔNG dùng cho shared state
- `startScan()` explicit để defer đến khi có permission, không auto-start khi collect

**4. Dispatcher xác định tại launch site**
- Scanner/DAO và repository impl đều không biết dispatcher — raw operation thuần
- `Dispatchers.IO` chỉ đặt tại nơi launch coroutine: `scope.launch(Dispatchers.IO) { repo.observeAll().collect {} }`
- Lý do: đọc launch site là thấy ngay threading context; `flowOn` ẩn trong impl là hidden behavior

**Why:** Phát hiện khi refactor `DefaultVideoRepository` — ban đầu có 3 field riêng, gây duplicate combine ở mọi VM.

**How to apply:** Khi thiết kế repository có scan/load state, default dùng sealed state pattern thay vì field riêng lẻ.
