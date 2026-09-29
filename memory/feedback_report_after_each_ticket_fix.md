---
name: feedback_report_after_each_ticket_fix
description: "When fixing a batch of tickets one by one, stop and report after each fix — user commits before the next one starts"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d5afce81-0c43-40be-88aa-a7149278cf84
  modified: 2026-08-25T04:24:32.500Z
---

When working through a list of tickets/bugs sequentially, fix ONE ticket, compile-verify it, then stop and report to the user — do not continue to the next ticket on your own.

**Why:** the user commits each ticket's fix separately (one commit per ticket) and wants to review/commit before the next fix lands on top of it. Continuing straight into the next ticket makes the diff harder to split into separate commits.

**How to apply:** after finishing and verifying a single ticket fix, give a short summary (what changed, files touched) and wait for the user's next message before starting the next ticket — even if the user's earlier message listed multiple tickets to fix in one go. Related: [[project_audio_editor_reference_repo]].
