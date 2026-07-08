---
name: Git - Tuyệt đối không tự ý commit
description: Cả main agent lẫn subagent đều không được chạy git commit/push trừ khi user yêu cầu rõ ràng
type: feedback
originSessionId: 9b5e7455-32a8-4ddb-afbf-b018e3b89366
---
Tuyệt đối không tự ý chạy `git commit`, `git push`, hoặc bất kỳ lệnh git nào làm thay đổi lịch sử/trạng thái repo — kể cả khi dispatch subagent.

**Why:** User muốn kiểm soát hoàn toàn mọi thay đổi git. Việc tự ý commit (dù từ subagent) là vi phạm quyền quyết định của user.

**How to apply:**
- Chỉ được đọc git (`git log`, `git diff`, `git status`, `git show`) — không viết.
- Khi dispatch subagent: phải ghi rõ trong prompt "KHÔNG được chạy git commit hay git push".
- Chỉ commit khi user nói rõ: "commit", "commit lại", "tạo commit", "git commit", v.v.
