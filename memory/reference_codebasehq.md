---
name: reference-codebasehq
description: "Link Codebase HQ dùng để quản lí code, issue, ticket cho project music editor"
metadata: 
  node_type: memory
  type: reference
  originSessionId: b7da009b-e188-4bb5-a593-9baa3f8ce3b5
---

Project management (code, issues, tickets) được quản lí tại: https://tohsoft.codebasehq.com/

- **API base**: `https://api3.codebasehq.com`
- **Auth**: HTTP Basic — credentials lưu tại `~/.claude/codebasehq-creds` (đọc bằng `source` trước khi gọi API)
- **Project permalink**: `android_music_editor`
- **Tickets API**: `GET /android_music_editor/tickets`

Khi user nhắc đến issue, ticket, hoặc task số cụ thể — dùng wget với Basic Auth để tra cứu API trên.
