---
name: Callback Patterns — Async vs Sync
description: When to use sealed class vs raw Float callback for progress/state reporting
type: feedback
originSessionId: ac81b197-a1c1-4cfe-b509-90c11f3a43d3
---
Async lifecycle-aware operations → sealed class. Sync blocking functions → raw `(Float) -> Unit` callback.

**Why:** User corrected approach when I questioned `onProgress: (Float) -> Unit` on `ExcelToPdfConverter.convert()`. Multiple raw callbacks (`onSuccess`, `onError`, `onProgress`) for async operations is Java-thinking — Kotlin has sealed class + `when` for exhaustive, safe state handling. But for sync blocking functions (no lifecycle, no state machine), `(Float) -> Unit` is the correct tool.

**How to apply:**
- Async method with lifecycle (View, ViewModel, coroutine scope) → `onState: (SealedClass) -> Unit`
- Sync blocking function that needs progress → `onProgress: (Float) -> Unit`
- Never use multiple raw callbacks for async operations — they're non-exhaustive and unsafe
- Repository bridges sync callback to Flow via `channelFlow` + `trySend`
