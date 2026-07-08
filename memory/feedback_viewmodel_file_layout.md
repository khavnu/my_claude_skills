---
name: ViewModel file layout — UiState và Event ở cuối file
description: Thứ tự khai báo trong file ViewModel: ViewModel class trước, UiState/Event data class ở dưới cùng
type: feedback
originSessionId: a0d6b472-0956-4089-a572-98b65a236d42
---
Trong file `*ViewModel.kt`, luôn đặt các supporting types ở **cuối file**, sau ViewModel class:

```
// Đúng thứ tự:
class FooViewModel @Inject constructor(...) : ViewModel() { ... }

data class FooUiState(...)
sealed interface FooEvent { ... }
```

**Why:** Đặt data class lên đầu file làm ViewModel class bị đẩy xuống — phải scroll mới thấy class chính.

**How to apply:** Mọi ViewModel file mới hoặc chỉnh sửa, khai báo `UiState`, `Event`, và các sealed class hỗ trợ sau dấu `}` cuối cùng của ViewModel class.
