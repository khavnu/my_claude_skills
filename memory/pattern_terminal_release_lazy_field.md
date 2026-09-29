---
name: pattern-terminal-release-lazy-field
description: "`by lazy` + release() terminal = chỉ dùng được 1 lần; lần 2 im lặng không hoạt động"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-10T04:27:33.560Z
---

Tài nguyên có `release()` **terminal** (không undo được) mà giữ trong `by lazy` hoặc field gán ở
`init` của một `@Singleton` thì **chỉ chạy đúng một lần**. Lần thứ hai gọi lên instance đã chết:
không exception, không log — chỉ là **không có gì xảy ra**.

Gặp 2026-09-10 với `StreamStemPlayer`: tách file 1 → play OK; back ra (release) → tách file 2 →
play/seek không phản ứng.

**Why:** singleton sống lâu hơn feature. `release()` gắn với vòng đời feature, `by lazy` gắn với
vòng đời process — hai vòng đời khác nhau nên chúng lệch nhau ngay lần thứ hai.

**How to apply:**
- `private var x: T? = null` + `requireX() = x ?: create().also { x = it }`, **không** `by lazy`.
- `release()` phải `x = null` để lần sau dựng lại.
- **Reset luôn state flow** kèm theo: giữ giá trị cuối sẽ khiến instance đã chết trông như đang chạy.
- Mỗi instance một collector: cancel job cũ khi tạo instance mới.

**Bẫy khi viết test:** assert `isPlaying == true` KHÔNG bắt được lỗi này, vì state cũ còn nguyên
trong `MutableStateFlow`. Phải đòi **vị trí phát tiến lên** (đọc 2 lần cách nhau ~1.5s) — bằng chứng
duy nhất phân biệt "đang phát thật" với "số liệu cũ".

Tham chiếu: `data/separation/DefaultSeparationPlaybackRepository.kt`,
test `androidTest/.../PlaybackSurvivesReleaseTest.kt`.

Liên quan: [[project_audio_separation]], [[pattern_fgs_stop_before_startforeground]].
