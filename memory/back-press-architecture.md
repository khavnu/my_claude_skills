---
name: back-press-architecture
description: "Back trong app đi qua hook handleBackPressed() của BaseActivity, không phải onBackPressed(); app không có fragment back stack nào"
metadata: 
  node_type: memory
  type: project
  originSessionId: 61f6fef0-9830-411e-9ced-556d6c1f7939
  modified: 2026-09-14T04:55:23.628Z
---

Từ 2026-09-14, mọi xử lý back đã migrate sang `OnBackPressedDispatcher`. `BaseActivity` đăng ký
**một** `OnBackPressedCallback` duy nhất (luôn enabled) delegate vào `protected handleBackPressed()`.
Activity con override `handleBackPressed()`, gọi `super.handleBackPressed()` để rời màn; muốn finish
từ async callback (dialog button, interstitial dismiss) thì dùng `leaveScreenOnBack()` — nó
`setEnabled(false)` trước khi re-dispatch nên không đệ quy.

**Why:** targetSdk 36 bật predictive back → hệ thống không gọi `Activity.onBackPressed()` nữa. Cờ
`android:enableOnBackInvokedCallback="false"` trong manifest đã được gỡ.

**How to apply:** Không bao giờ override `onBackPressed()` trong codebase này. Nút back trên toolbar
gọi `getOnBackPressedDispatcher().onBackPressed()`, không gọi thẳng method.

Hai sự thật khảo sát được, tốn công derive lại:
- **Zero fragment back stack** — `addToBackStack`/`popBackStack` không xuất hiện ở đâu trong repo.
  Nên callback của `FragmentManager` luôn disabled → không có tranh chấp thứ tự LIFO khi thêm callback.
- **Dialog quit ở HomeActivity** là `androidx.activity.ComponentDialog`, không phải `Dialog` thuần —
  nó có `OnBackPressedDispatcher` riêng. Cần thế vì dialog `setCancelable(false)`: platform
  `Dialog.onKeyUp` vẫn gọi `onBackPressed()` bất kể cancelable, và `ComponentDialog` override
  `onBackPressed()` để đẩy vào dispatcher của nó. Dialog nào cần bắt back → dùng `ComponentDialog`,
  đừng dùng `setOnKeyListener(KEYCODE_BACK)` (predictive back có thể chặn key event không tới nơi).

Vì callback của `BaseActivity` luôn enabled, gesture predictive back sẽ **không có animation peek** —
back vẫn chạy đúng chức năng. Đánh đổi có chủ đích để giữ guard 500ms sau `onCreate`.

Liên quan: [[ads-buildconfig-flags-are-dead]]
