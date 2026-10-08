---
name: agentbus-claude-codex
description: "agentbus (Claude↔Codex message bus) installed opt-in at ~/tools/agentbus — launchers, install pitfalls, Codex hook trust"
metadata:
  node_type: memory
  type: reference
  originSessionId: b1461cbe-b9c8-4232-a13a-6562a70f16e0
  modified: 2026-10-08T07:53:03.420Z
---

agentbus (github.com/Ahmed/agentbus, commit 82c36e6) installed 2026-10-08 at `~/tools/agentbus`, opt-in only:
- Launchers (`claude-bus` `claudek-bus` `codex-bus` `bus-open` `bmail` `bwatch`) source of truth = `~/.claude/skills/_shared/cross-agent-setup/bin` (backed up), symlinked into `~/.local/bin`; `~/.codex/skills/cross-agent-peer` → `cross-agent-setup/codex-skill`. New-machine steps: `_shared/cross-agent.md` › Setup on a new machine.
- Claude hooks load per launch via `--settings ~/tools/agentbus/claude-settings.json`; global `~/.claude/settings.json` untouched.
- Codex hooks are global in `~/.codex/hooks.json` (file did not exist before; delete it to uninstall).

Pitfalls (verified):
- README install script does `hooks.update(...)` → would WIPE existing Claude hooks (Stop/PostToolUse/SessionStart/PreToolUse). Never run it.
- `requirements.txt` has `mcp>=1.24.0` unbounded → pip pulls mcp 2.x, FastMCP import breaks. Deps installed with `pip --target .deps "mcp<2"`; wrapper `./py` sets PYTHONPATH (no python3-venv on this machine).
- Unit tests: 159 run, 2 legacy-migration errors in `tests.test_delivery` (irrelevant to fresh install). Run: `cd ~/tools/agentbus && ./py -m unittest discover`.
- Codex 0.153.4 refuses to run new hooks until the user trusts them in the TUI (startup review or `/hooks`); trust lives in `config.toml` `hooks.state."<id>".trusted_hash`. `codex exec` silently skips untrusted hooks.
- Claude side verified: `claude-bus -p ...` wrote `/tmp/agentbus/state/session.claude*`.

- `codex-bus` bakes in the user's full-access flags (`--search`, notify curl to :32951, `--dangerously-bypass-approvals-and-sandbox`) + `--remote unix://`; `claude-bus` always appends the bus brief (shell.sh only briefs bare starts).
- 2026-10-08: manual round trip claude↔codex worked (project_check → confirm → pong). Idle wake NOT yet tested.

Skills wired 2026-10-08: `~/.claude/skills/_shared/cross-agent.md` (pool, allocation, transport rule: any non-default member → everyone on agentbus), `--pool` in `collab` + `orchestra`, Codex side `~/.codex/skills/cross-agent-peer/SKILL.md` (points at the Claude skill files, lists substitutions).

Status 2026-10-08 (paused — Codex + claudeK out of limit; resume when user says "test tiếp agentbus"):
- `bus-open <claude|claudeK|codex> <dir> <title> [args]` opens a GNOME Terminal window; verified for claude (window registered as claude-105, task test-bus).
- `codex --remote unix://` failed with "No such file … app-server-control.sock" when the daemon was down → `codex-bus` now runs `codex app-server daemon start` first (not yet re-tested from a cold daemon). Codex auto-updated to 0.161.0 meanwhile; hook trust may need re-approval.
- Next tests, in order: (1) idle wake: send from a plain session to an idle `claude-bus`/`claudek-bus` window, expect an unprompted reply; (2) `ListAgents` from the default account — does it list a claudeK session?; (3) small `/orchestra --pool` run. Record results in `~/.claude/skills/_shared/cross-agent.md` › Not yet verified.

