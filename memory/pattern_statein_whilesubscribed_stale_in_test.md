---
name: pattern_statein_whilesubscribed_stale_in_test
description: "Trong unit test, đọc viewModel.uiState.value khi chưa có collector luôn trả initial value — mọi VM trong repo đều dùng stateIn(WhileSubscribed), phải đọc bên trong Turbine block"
metadata: 
  node_type: memory
  type: project
  originSessionId: 963158e9-c09f-4361-9181-29bce6730c03
  modified: 2026-09-25T02:48:05.313Z
---

Mọi ViewModel trong repo đều theo pattern:

```kotlin
val uiState = _state.map { it.toUiState() }
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), _state.value.toUiState())
```

`WhileSubscribed` nghĩa là upstream CHỈ được collect khi có subscriber. Trong unit test, nếu chưa
có ai collect thì `viewModel.uiState.value` đứng nguyên ở **initial value** mãi mãi — kể cả sau
`advanceUntilIdle()`.

```kotlin
// ❌ Fail với "actual value is null" dù VM đã load xong
val viewModel = viewModelWith(audioFile())
advanceUntilIdle()
assertNotNull(viewModel.uiState.value.audioFile)

// ✅ Đọc bên trong Turbine block — .test{} chính là subscriber
viewModel.uiState.test {
    assertNotNull(expectMostRecentItem().audioFile)
    viewModel.doSomething()
    advanceUntilIdle()
    assertEquals(..., expectMostRecentItem())
    cancelAndIgnoreRemainingEvents()
}
```

**Why:** Triệu chứng đánh lừa — test fail với "actual value is null" trông y hệt lỗi logic trong
ViewModel, nên phản xạ đầu tiên là đi debug production code. Thực ra production đúng, chỉ là test
đang đọc sai chỗ. Mất một vòng chạy Gradle mới nhận ra (ticket #445).

Bẫy phụ: `advanceUntilIdle()` gọi được BÊN TRONG `.test {}` block, không cần tách ra ngoài.

**How to apply:** Trong test VM, không bao giờ đọc `uiState.value` trực tiếp. Mọi assert đi qua
`uiState.test { expectMostRecentItem() }`. Ngoại lệ duy nhất an toàn: assert một field vẫn đang giữ
giá trị default (initial value tình cờ đúng) — nhưng đó là test yếu, đừng dựa vào.

Liên quan: [[feedback_flow_patterns.md]], [[pattern_gradle_cache_hides_broken_tests.md]]
