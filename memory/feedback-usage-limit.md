---
name: feedback-usage-limit
description: Usage limits readable per account from ~/.claude/usage-latest-<K|D>.json; default = full run + pre-scheduled resume at reset+5 min; thresholds only when the user says "chú ý limit"
metadata:
  type: feedback
---

Updated 2026-10-08 (was: "the user tracks the limit, don't build checks" — superseded when the user pointed out the reset time is readable each session).

- `~/.claude/statusline.sh` writes `~/.claude/usage-latest-K.json` (session with `CLAUDE_CONFIG_DIR=~/.claude-k`) or `-D.json` (default dir) with `five_hour`/`seven_day` `{used_percentage, resets_at}`. Verify: `jq . ~/.claude/usage-latest-K.json`.
- SessionStart hook `~/.claude/hooks/usage-on-start.sh` injects the current account's numbers into each new session.
- Flow the user wants: session opens → read reset time → if 5h >= 90 %, park heavy work and CronCreate a one-shot at reset + 5 min → at that firing, re-check and schedule again if needed.
- Weekly %: just report it; the user decides on cutting scope. No hourly polling cron (each firing re-sends the whole context).

**Why:** the user said "thời gian limit reset chúng ta sẽ lấy được mỗi lần mở 1 session… đặt lịch luôn".
**How to apply:** the snapshot is only as fresh as the last status line render, but `resets_at` is absolute; crons die with the session.

**Default = full run (user 2026-10-08, replaces the earlier opt-in override):** "Tự động bật bạn nhé, khi nào tôi nhắc chú ý limit thì sẽ áp dụng check limit". Work at full pace, apply without asking; only keep the progress log and, once 5h ≥ 90 %, schedule the reset + 5 min resume in advance (a cut session can't schedule). The 70/90 thresholds apply only after the user says "chú ý limit". Recorded in usage-limit-protocol.md §0.
