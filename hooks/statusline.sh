#!/usr/bin/env bash
# Status line shared by both accounts (settings.json is symlinked into ~/.claude-k).
# Shows which account the session runs as, because both accounts share the same UI and config.
input=$(cat)

if [ "${CLAUDE_CONFIG_DIR%/}" = "$HOME/.claude-k" ]; then
  label="K"; command_name="claudeK"; color="35"
else
  label="D"; command_name="claudeD"; color="36"
fi

field() { printf '%s' "$input" | jq -r "$1 // empty"; }
# $1 = epoch seconds, $2 = date format; prints "?" when the CLI did not send a reset time
format_reset() { [ -n "$1" ] && date -d "@$1" +"$2" 2>/dev/null || echo "?"; }

# Snapshot the rate limits for the agent: it cannot see this status line, but it can read the
# file (cheap) to pace heavy work and to schedule a resume right after a reset. One file per
# account, written atomically so a reader never sees half a file.
usage_file="$HOME/.claude/usage-latest-${label}.json"
printf '%s' "$input" | jq -c '{updated_at: now | floor, five_hour: .rate_limits.five_hour, seven_day: .rate_limits.seven_day}' \
  > "$usage_file.tmp" 2>/dev/null && mv -f "$usage_file.tmp" "$usage_file"

model=$(field '.model.display_name')
five_hour=$(field '.rate_limits.five_hour.used_percentage')
five_hour_reset=$(format_reset "$(field '.rate_limits.five_hour.resets_at')" '%H:%M')
seven_day=$(field '.rate_limits.seven_day.used_percentage')
seven_day_reset=$(format_reset "$(field '.rate_limits.seven_day.resets_at')" '%a %d/%m %H:%M')

printf "\033[1;${color}mAs ${label} user\033[0m (%s) · %s · 5h %s%% (reset %s) · week %s%% (reset %s)" \
  "$command_name" "${model:-?}" "${five_hour:-?}" "$five_hour_reset" "${seven_day:-?}" "$seven_day_reset"
