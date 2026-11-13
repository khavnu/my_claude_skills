---
name: feedback-landscape-commit-message
description: "Commit messages for landscape work use the prefix \"Landscape: \" followed by the name of the main screen/composable that changed"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 87fb5981-5bf1-470a-9072-56ede1d33a2e
  modified: 2026-10-13T04:32:05.944Z
---

Landscape commits are titled `Landscape: <main screen changed>`, kept short. Examples from the user (2026-10-13):
- `Landscape: Main Navigation rail` (root tabs + rail)
- `Landscape: HomeRoute` (the Home tab, named after its entry composable)
- Earlier commit in git history: `Landscape: AudioPermissionScreen`

**Why:** the user wants the git log to read as one line per screen updated for landscape.
**How to apply:** one commit per screen. Name the main composable or screen that changed (the Route or Screen name when there is one), not a description of the change. Stage only that screen's files and leave unrelated docs out. Still commit only when the user asks.

**QC ticket fixes (2026-10-26):** the user amended my `Landscape: … (#446)` commit to `[Touch: 446]Landscape: ChooseActionBottomSheet opens as a side panel` — ticket tag first as `[Touch: <id>]`, no space before the title, no body, no `Co-Authored-By`. Verify with `git log -1 --format=%B 1cd8090d`.

**Sửa 2026-10-27 (#468):** user tự đặt message `[Touch: 468] EqualizerBandEditor: fix dash line when landscape` thay cho đề xuất `[Touch: 468]Landscape: EQ 0 dB line stays inside the band panel` → **có dấu cách sau `]`**, prefix là **tên component/màn chính bị sửa** (không phải "Landscape"/"Video"), mô tả ngắn kiểu "fix <cái gì> when <khi nào>". Verify: `git log -1 --format=%B 558beaba`. Các commit ticket trước (#446–#465) không có dấu cách — từ giờ theo format mới; khi đề xuất message, đưa theo format này.
