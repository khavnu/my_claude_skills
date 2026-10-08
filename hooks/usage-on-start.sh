#!/usr/bin/env bash
# SessionStart: hand the agent this account's last known rate limits (written by statusline.sh),
# so it can pace heavy work and schedule a resume right after a reset without the user telling it.
if [ "${CLAUDE_CONFIG_DIR%/}" = "$HOME/.claude-k" ]; then label="K"; else label="D"; fi
file="$HOME/.claude/usage-latest-${label}.json"
[ -f "$file" ] || exit 0
python3 - "$file" "$label" <<'PY'
import json, sys, time
path, label = sys.argv[1], sys.argv[2]
d = json.load(open(path))
now = time.time()
def part(name, fmt):
    v = d.get(name) or {}
    pct, reset = v.get("used_percentage"), v.get("resets_at")
    if pct is None:
        return f"{name}: unknown"
    if reset and reset <= now:
        return f"{name}: was {pct}% but its window already reset at {time.strftime(fmt, time.localtime(reset))} (now fresh)"
    return f"{name}: {pct}% used, resets {time.strftime(fmt, time.localtime(reset)) if reset else '?'}"
age_min = int((now - d.get("updated_at", now)) / 60)
msg = (f"Usage limits for account {label} (snapshot {age_min} min old, refreshes with the status line): "
       f"{part('five_hour', '%H:%M')}; {part('seven_day', '%a %d/%m %H:%M')}. "
       "Mode: full run unless the user asked to watch the limit (~/.claude/skills/_shared/usage-limit-protocol.md section 0). "
       "If 5h >= 90%, schedule a one-shot CronCreate resume at reset + 5 min now, before the limit cuts the session.")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}}))
PY
