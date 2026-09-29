---
name: project_audio_editor_icon_resources
description: "Pitfalls khi đổi màu/thay icon trong :audio_editor — density variants ẩn, AGP không resolve @color trong gradient vector, và node Figma nguồn"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5135b2b0-978e-49f7-9b1a-b141a4a421a0
  modified: 2026-08-25T10:45:09.525Z
---

Khi sửa icon của `:audio_editor` (green_ba_music_player), 3 điều đã cắn một lần:

1. **Luôn `find audio_editor/src -name "<tên>*"` chứ đừng chỉ `ls drawable/`.** Bộ `ic_trim_*` có bản PNG ở cả `drawable-hdpi/xhdpi/xxhdpi/xxxhdpi`. PNG ở density folder **đè** vector ở `drawable/`, nên thay bằng vector mà quên xoá PNG thì vector thành code chết và máy thật vẫn hiện icon cũ.

2. **AGP generate PNG fallback cho vector trong module này**, và bước đó **không resolve được `@color/...` nằm trong `<aapt:attr>` gradient** → lỗi `Unable to generate a PNG file from vector drawable from resource reference`. Fill phẳng dùng `@color` thì OK; riêng gradient stop phải inline hex (`ic_play_result.xml` / `ic_pause_result.xml` đang vậy, có comment trong file).

3. Màu accent sống ở `audio_editor/src/main/res/values/colors.xml` (`audio_editor_primary` = `#4E757A` = `app_highlight_color_3` của app theme, `audio_editor_primary_bright` = `#0D94A5` = `app_highlight_color_1`) và mirror trong `ui/theme/Color.kt`. Đổi accent = sửa 2 nơi đó + hex trong 2 file gradient ở trên.

**Nguồn Figma** của bộ icon editor: file `xPC3QxMt965PxCNFaZCrEs` ("Generate"), `Section 1` = node `77:975` — play `77:962`, pause `77:968`, waveform `77:976`, trim sides active `77:980` / disable `77:1008` (rộng 68 chứ không phải 60 như bản active), trim middle active `77:995` / disable `77:1023`. Section này đã được recolor sang palette app (2026-08-25).

Đọc/export dùng PAT trong `~/.claude/figma-accounts/figma-token.md` qua REST API (`/v1/files/.../nodes`, `/v1/images/...?format=svg`) — PAT **chỉ đọc**; muốn ghi vào file Figma phải qua Figma MCP `use_figma` (xem [[reference_codebase_api_access]] cho pattern wget vì sandbox không có curl).
