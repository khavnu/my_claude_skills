---
name: feedback-incremental-ui-first
description: "Khi implement màn hình mới, tách thành 2 bước: UI với fake data trước, sau đó mới wire data thật"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 53ec8f3f-3839-4e45-8e29-8bf52f9cb8ed
---

Làm từng bước nhỏ, hoàn thành xong báo lại user trước khi làm tiếp. Không làm dồn tất cả một lúc.

Với màn hình mới — tách 2 phase:
1. **UI shell với fake/empty data** — Screen + ViewModel rỗng, user confirm layout
2. **Wire data thật** — repository, permission, fetcher, scan sau khi UI được confirm

**Why:** Feedback loop ngắn. UI thay đổi lớn không kéo theo fix data layer. Dễ đọc, dễ review từng bước.

**How to apply:** Mọi feature/màn hình mới ở mọi project. Rule này đã được lưu vào global CLAUDE.md (Workflow Rule #9).
