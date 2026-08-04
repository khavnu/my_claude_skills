---
name: reference_dev_tohsoft_codebase_api
description: dev.tohsoft.com là Codebase instance; đọc ticket qua Codebase API3 với creds sẵn có
metadata: 
  node_type: memory
  type: reference
  originSessionId: 272458fd-c0cc-4b20-b90b-cd1b3f3a27b5
---

Link `dev.tohsoft.com/projects/{project}/tickets/{id}` là một Codebase instance (v4.1). Trang web cần session login nên WebFetch/HTML chỉ trả về form login. Nhưng đọc được qua **Codebase API3**:

- Endpoint: `https://api3.codebasehq.com/{project-permalink}/tickets/{id}` (ví dụ `android_music_editor/tickets/244`)
- Notes/comments: thêm `/notes` vào path
- Auth: HTTP Basic — `username:api_key` từ `~/.claude/codebasehq-creds` (username có dạng `account/user`, đã chứa slash)
- Header bắt buộc: `Accept: application/xml` (dùng `.json`/`.xml` trên domain gốc trả **406**; endpoint browser trả login form)

Dùng chung creds với [[reference_codebasehq]]. Xem thêm [[feedback_codebasehq_api]] (Python urllib, không dùng WebFetch). **Không** lưu giá trị key vào memory — key sống trong creds file, có thể bị refresh/rotate.
