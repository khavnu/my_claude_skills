---
name: pattern-audio-focus-needs-top-activity
description: Android 15 chỉ cấp audio focus khi app ở TOP hoặc FGS mediaPlayback — androidTest phát nhạc phải tự mở Activity
metadata: 
  node_type: memory
  type: project
  originSessionId: bdb5dbc3-71e8-4f83-aed4-d682449c6e8a
  modified: 2026-09-10T08:34:45.661Z
---

Android 15 (Samsung `AS.HardeningEnforcer`) từ chối `requestAudioFocus` khi app không ở
`PROCESS_STATE_TOP`. FGS type `dataSync` (dùng cho separation chạy nền) **không** đủ — chỉ
`mediaPlayback` mới được miễn.

Triệu chứng trong androidTest: player `isBuffering` → `false` nhưng `isPlaying` không bao giờ `true`,
test timeout 30s mà không có exception nào. Log: `Focus request DENIED for uid:... procState:4`.

**Cách xử lí:** test nào phát tiếng thật phải bọc thân test trong
`ActivityScenario.launch(MainActivity::class.java).use { ... }` — đúng điều kiện user thật đang
nhìn màn hình. Đã áp dụng cho `PlaybackSurvivesReleaseTest` và `SeparationPlaybackEndToEndTest`.

Hệ quả sản phẩm: rời app khi đang preview thì tiếng dừng; tách file vẫn chạy nền bình thường.

Liên quan: [[project_audio_separation]], [[pattern_fgs_stop_before_startforeground]]
