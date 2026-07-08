---
name: feedback-package-structure
description: "Quy tắc tổ chức package/file cho feature — high cohesion, low coupling; tab tự chứa, navigation co-located, VM single responsibility"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 53ec8f3f-3839-4e45-8e29-8bf52f9cb8ed
---

Cấu trúc package/file phải theo nguyên tắc **high cohesion, low coupling**. Áp dụng khi viết code và lên plan.

## Quy tắc

**1. Tab phải tự chứa (self-contained)**
- Mỗi tab có package riêng, ViewModel riêng, tự quản lý state của nó.
- Parent screen KHÔNG truyền search state, filter state... vào tab — tab tự có VM để handle.
- Parent chỉ truyền callbacks tối giản (`onItemSelected`, `onNavigateBack`).

**2. Navigation của tab nằm trong tab đó**
- Folder tab có navigation riêng → đặt trong `tabs/folder_tab/navigation/`, không phải `foldersnavigation/` ngang hàng feature.
- Tên và vị trí phải nói lên quan hệ phụ thuộc: navigation *của* tab nào → nằm *trong* tab đó.

**3. ViewModel single responsibility**
- VM màn hình cha chỉ làm đúng một việc: orchestrate shared state (scan, permission, loading), relay error ra snackbar.
- Mỗi tab có VM riêng cho business logic của tab đó (search, filter, grouping...).
- Shared data (VD: scan result) → tách ra singleton `*State` class inject vào nhiều VM, không để VM cha làm trung gian.

**4. Cấu trúc chuẩn cho feature có tabs + nested navigation**
```
feature_name/
├── FeatureScreen.kt          — Route + Screen (slim, chỉ dùng UiState tối giản)
├── FeatureViewModel.kt       — scan/permission/loading/error relay
├── FeatureUiState.kt
├── components/               — shared UI components của feature
└── tabs/
    ├── tab_a/
    │   ├── TabAContent.kt    — self-contained, hiltViewModel() bên trong
    │   └── TabAViewModel.kt
    └── tab_b/
        ├── TabBContent.kt
        ├── TabBViewModel.kt
        ├── SubContent.kt     — extracted composables
        └── navigation/       — nested NavDisplay nếu có
            ├── BrowserScreen.kt
            └── BrowserViewModel.kt
```

**Why:** Cấu trúc flat hoặc navigation đặt sai chỗ gây confuse khi đọc code, không rõ quan hệ phụ thuộc, VM dễ bị fat.

**How to apply:** Khi lên plan cho feature mới có tabs, bắt buộc propose cấu trúc `tabs/` ngay từ đầu. Nếu tab cần nested navigation, tạo `navigation/` bên trong tab đó. Không tạo thư mục `*navigation/` hoặc `*nav/` ngang hàng với feature root.
