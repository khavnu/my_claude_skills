---
name: adjustresize-dead-on-targetsdk35
description: targetSdk 35+ vô hiệu hoá android:windowSoftInputMode=adjustResize; trong android_qr5 hành vi này được dựng lại thủ công ở CreateActivity
metadata: 
  node_type: memory
  type: project
  originSessionId: 251b41e3-d059-4932-9857-8baad4a99169
  modified: 2026-09-09T02:54:02.967Z
---

`android_qr5` target SDK 36 → **`android:windowSoftInputMode="adjustResize"` trong manifest không
còn tác dụng** trên Android 15/16. Ground truth (`$ANDROID_SDK/sources/android-36/android/view/Window.java`,
javadoc `setDecorFitsSystemWindows`):

> If set to `false`, the framework will not fit the content view to the insets…
> **If the app targets VANILLA_ICE_CREAM or above, the behavior will be like setting this to
> `false`, and cannot be changed.**

Hệ quả: window không co lại khi keyboard mở → banner ads ở đáy bị bàn phím che hoàn toàn.
Nguyên nhân **không phải** `enableEdgeToEdge()` trong `FullScreenActivity` — gỡ nó đi cũng không
cứu được, vì targetSdk mới là thứ ép.

**Cách project xử lý (2026-09-09):** `CreateActivity.applyImeInsetsForAdjustResize()` — gọi cuối
`initView()`, cài `ViewCompat.setOnApplyWindowInsetsListener` lên `android.R.id.content`, set bottom
padding = `WindowInsetsCompat.Type.ime()).bottom`. Có guard `isEdgeToEdgeEnable()` (API ≤34 framework
tự lo) và guard `softInputMode & SOFT_INPUT_MASK_ADJUST == SOFT_INPUT_ADJUST_RESIZE` để manifest vẫn
là source of truth. Phạm vi = đúng 22 màn tạo mã (`extends CreateActivity`/`CreateOtherCodesActivity`).

Workaround cũ — `onKeyboardOpen()` + `setPadding(..., 500)` hardcode ở `CreateText/Message/Email/
Event/Contact` — đã **comment lại** (không xoá, theo yêu cầu), vì để sống sẽ cộng dồn padding.

**Why:** rất dễ chẩn đoán nhầm sang "layout sai" hoặc "đổi manifest là xong". Đổi manifest một mình
là no-op trên máy test (Pixel 9 / API 36).

**Cấu trúc chuẩn của layout màn tạo mã (thống nhất 2026-09-09, cả 11 file):**

```
root (LinearLayout dọc — hoặc RelativeLayout bọc 1 LinearLayout dọc layout_above="@id/layout_bottom")
├── status_bar_bg
├── create_action_bar              ← cố định
├── ScrollView  height=0dp weight=1  ← BẮT BUỘC, thằng duy nhất nhận co giãn
├── include @layout/btn_create_done  ← pin ngoài ScrollView, ngay trên banner
└── layout_ads_container (hoặc layout_bottom bọc nó)
```

`ScrollView` phải là `0dp` + `weight=1`; `wrap_content`/`match_parent` không weight sẽ đẩy
DONE + banner ra khỏi mép màn. Riêng `create_event_activity` root là RelativeLayout nên dùng
ràng buộc: ScrollView `layout_above="@id/layout_btn_done"`, include có `android:id="@+id/layout_btn_done"`
và `layout_above="@id/layout_bottom"`.

`btn_create_done.xml` là file dùng chung — margin ngang `@dimen/_10sdp` để thẳng lề với EditText
trong các màn create (chúng cũng dùng `_10sdp`). Sửa 1 file này là đổi chiều rộng cho cả 22 màn.

**How to apply:** Màn nào cần resize theo keyboard mà KHÔNG extends `CreateActivity`
(`SendFeedback`, `EditQrCode`, `ManageSearchEngine`, `Detail`, `HistoryBatch`, `FolderBrowser`…) thì
vẫn còn lỗi — cần port cùng cơ chế. **Đừng** đưa lên `FullScreenActivity` một cách vô điều kiện:
`HomeActivity` cố ý để `adjustNothing` vì chứa camera preview, xem [[zxing-preview-stale-on-resize]].
Liên quan: [[ads-buildconfig-flags-are-dead]].
