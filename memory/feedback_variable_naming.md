---
name: feedback-variable-naming
description: Không dùng single-char hoặc abbreviation vô nghĩa cho local variable — phải dùng tên mô tả đầy đủ
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 53ec8f3f-3839-4e45-8e29-8bf52f9cb8ed
---

Không đặt tên biến là single char vô nghĩa như `s`, `r`, `v`, `e`.

**Why:** User chỉ ra `val s = _state.value` là tên vô nghĩa — phải là `val currentState = _state.value`.

**How to apply:** Mọi local variable phải có tên mô tả đủ nghĩa:
- `val s = _state.value` → `val currentState = _state.value`
- `val r = repo.get()` → `val result = repo.get()`
- Lambda param trong update block: `{ s -> s.copy(...) }` → `{ state -> state.copy(...) }`

Áp dụng cho cả lambda parameter, không chỉ `val`/`var` declaration.

## Higher-order function parameter naming

`block` là tên quá generic — đọc lên không nói được intent. Dùng tên semantic:
- `(T) -> T` transformation → `transform`
- `(T) -> Unit` side-effect → `action`
- `(T) -> Boolean` filter → `predicate`
- `() -> T` factory → `produce`
- `StateFlow.update { }` helper → `update`

```kotlin
// Sai
private fun updateDenoiseDraft(block: (DenoiseDraftUiState) -> DenoiseDraftUiState)

// Đúng
private fun updateDenoiseDraft(transform: (DenoiseDraftUiState) -> DenoiseDraftUiState)
```

## Named `let` lambda parameters

Luôn đặt tên explicit cho lambda param trong `?.let { }` khi có nested lambda hoặc khi implicit `it` gây ambiguity — tên phải mô tả đúng giá trị nhận được:

```kotlin
// Sai — `it` ở đây là gì? draft hay state?
state.denoiseDraft?.let { state.copy(denoiseDraft = block(it)) }

// Đúng — rõ ràng ngay
state.denoiseDraft?.let { oldDraft ->
    state.copy(denoiseDraft = transform(oldDraft))
}
```

Naming convention cho `let` param: `old{Type}`, `current{Type}`, hoặc tên domain ngắn gọn (`draft`, `file`, `preset`).
