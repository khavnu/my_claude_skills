---
name: autonomy-long-task
description: WMusi — user granted full autonomy for the long run (detail screens → Figma sync → next tasks): pick order, decide unclear UX points, report only when done
metadata:
  type: feedback
---

2026-10-01 the user said: "Đây là 1 task dài, tôi cho phép bạn tự quyết định làm task nào trước, tự quyết định những điểm chưa rõ (dựa theo UI-UX tốt nhất mà bạn đánh giá), chỉ cần báo lại tôi sau khi hoàn thành".

**Why:** the user wants the run to go on without check-ins; CLAUDE.md rule 10 ("ask when uncertain") is overridden for this run by this explicit instruction.

**How to apply:** do not stop to ask about ordering or unclear design details — decide by best UI/UX judgment, write each decision down (checklist "Nhật ký quyết định" / plan ledger "Ruling:") so the user can review it afterwards, and report once at the end. Still stop for the irreversible/destructive (data deletion, DB migration risk), security-sensitive, or outward-facing actions not already authorized — commit + push per milestone IS authorized ([[commit-after-each-step]]).
