---
name: feedback-codebasehq-api
description: "Khi user paste link tohsoft.codebasehq.com, tự động dùng API thay vì WebFetch"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3b05abae-52df-45aa-8631-1fa46ebdb135
---

Khi user paste link `tohsoft.codebasehq.com`, **tự động dùng API** thay vì WebFetch (WebFetch sẽ redirect về trang login).

**Why:** CodebaseHQ yêu cầu auth — WebFetch không vượt qua được. Credentials đã có tại `~/.claude/codebasehq-creds`.

**How to apply:**
- API base: `https://api3.codebasehq.com/{project}/tickets`
- Auth: HTTP Basic với `username:api_key` từ `~/.claude/codebasehq-creds`
- Pagination: 20 items/page, loop cho đến khi page rỗng hoặc < 20 items
- Dùng Python `urllib.request` (curl không có sẵn trong môi trường này)
