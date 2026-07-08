---
name: feedback-refactor-value-check
description: "Trước khi refactor/extract, tự hỏi abstraction che đi gì — không chỉ dời code"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 53ec8f3f-3839-4e45-8e29-8bf52f9cb8ed
---

Trước khi extract composable/class/function, tự hỏi: *"Abstraction này che đi complexity hay chỉ dời code sang chỗ khác?"*

**Why:** `rememberVideoPlayerState` refactor đúng rule 50 dòng nhưng Screen vẫn phải biết `.exoPlayer`, `.isPlaying`, `.playheadMs`, `.togglePlay()` — số touch point không giảm. User nhận xét: "chỉ là đưa exoPlayer ra chỗ khác."

**How to apply:** Extraction có giá trị khi: (1) caller không cần biết internals, (2) logic có thể tái sử dụng thực sự, (3) complexity thực sự ẩn đi. Nếu caller vẫn phải expose hết thì abstraction đó không có giá trị — giữ nguyên, không extract.

Liên quan: [[feedback_incremental_ui_first]]
