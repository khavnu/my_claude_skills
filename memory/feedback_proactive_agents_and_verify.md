---
name: proactive-agents-and-verify
description: "Dùng parallel agents cho feature lớn và /verify sau feature — được user ủy quyền tự động kích hoạt, không cần hỏi"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c48f368f-f9d8-4f6c-a861-2186cba12c58
---

User đã ủy quyền Claude tự chủ động dùng 2 workflow sau — không cần hỏi, cứ dùng khi phù hợp:

## 1. Parallel agents cho feature lớn
Khi task có ≥ 2 layer độc lập (implement + test, hoặc 2 feature screens khác nhau):
- Dùng `/writing-plans` trước để có plan rõ
- Spawn **implement-agent** + **test-agent** song song (hoặc orchestrator-agent nếu muốn tự động review-fix loop)
- **reviewer-agent** check kết quả sau

**Why:** User thấy đang làm tuần tự — bỏ phí song song. Tiết kiệm 40-50% thời gian trên feature vừa.

**How to apply:** Trigger khi: feature có ≥ 2 screen, hoặc có cả business logic + UI cần làm, hoặc task chia được thành 2+ independent chunks không cần nhau.

## 2. /verify sau mỗi feature hoàn chỉnh
Sau khi implement xong và compile pass — trước khi báo "done" — chạy `/verify` để test app thực, golden path, và catch regression.

**Why:** UI scan/camera flow đặc biệt khó test chỉ bằng compile. Verify bắt được lỗi runtime mà compile không thấy.

**How to apply:** Trigger khi: feature liên quan đến UI flow (navigation, dialog, camera, scan), hoặc khi có nhiều thay đổi cross-screen. Bỏ qua nếu chỉ là fix nhỏ 1-2 dòng logic nội bộ.
