---
name: feedback-coroutine-finally-ui-state
description: finally block trong coroutine không được dùng để flip UI state — chỉ dùng cho resource cleanup
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6f65d4ff-5d1f-48ea-b098-c0a0b2ca7b34
---

Không dùng `finally` trong coroutine để set UI state (ví dụ `isPreparing = false`).

**Why:** `finally` luôn chạy kể cả khi `CancellationException` được throw — đó là design của Kotlin để đảm bảo cleanup. Nếu operation bị cancel trong khi đang blocked ở blocking call (ví dụ FFmpeg native), `CancellationException` chỉ được throw SAU KHI blocking call xong (vài giây sau). Lúc đó `finally` chạy muộn và set `isPreparing = false` của một operation khác đang chạy → dialog ẩn sớm, delay 4-5s trước khi UI phản hồi.

**How to apply:** 
- `finally` → chỉ dùng để release resource: close file, stop player, cancel timer, v.v.
- UI state (`isPreparing`, `isLoading`, ...) → set explicit trong từng outcome branch:
  - `Result.Success` → set false trước khi trigger side effect (play, navigate, ...)
  - `Result.Failure` → set false inline trong state update
  - Cancel path → `cancelXxxRender()` đã set trực tiếp trên Main thread, không cần coroutine
- Không cần `val thisJob = coroutineContext[Job]` guard — bỏ `finally` đi là đủ và sạch hơn.

```kotlin
// SAI — finally chạy sau CancellationException, set sai isPreparing
draftJob = viewModelScope.launch {
    try {
        when (val r = ensureRendered()) { ... }
    } finally {
        updateDraft { it.copy(isPreparing = false) }  // ← chạy muộn khi cancel
    }
}

// ĐÚNG — explicit per branch, cancel không đụng vào isPreparing
draftJob = viewModelScope.launch {
    when (val r = ensureRendered()) {
        is Result.Success -> {
            // ... setup player ...
            updateDraft { it.copy(isPreparing = false) }
            previewPlayer.play()
        }
        is Result.Failure -> _uiState.update {
            it.copy(errorMessage = ..., draft = it.draft?.copy(isPreparing = false))
        }
    }
}
```
