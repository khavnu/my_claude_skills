---
name: cross-agent-peer
description: Use when the first prompt says "Use skill cross-agent-peer" or this Codex window is asked to act as a collab peer or an orchestra worker alongside Claude Code sessions on the agent bus.
metadata:
  author: khapv
  version: "1.0"
---

# Cross-agent peer — Codex inside a Claude-led collab / orchestra run

The protocol is owned by the Claude skills; this file only lists what differs for Codex. Read the protocol from its source every time — never from memory:

| Role in the first prompt | Read in full |
|---|---|
| `collab peer` | `~/.claude/skills/collab/SKILL.md` |
| `orchestra worker T-<n> <name> <worktree>` | `~/.claude/skills/orchestra/SKILL.md` (section "Worker") and `~/.claude/skills/orchestra/references/templates.md` |
| either | `~/.claude/skills/_shared/cross-agent.md` (transport, task label, project check) |

Then follow it as if you were the Claude session it describes, with these substitutions.

## Substitutions

| Claude skill says | Codex does |
|---|---|
| `/collab …` / `/orchestra join …` command | Your first prompt is the join; start at SETUP (collab) or READY (worker) |
| `ListAgents` + `SendMessage` | `$BUS send codex <handle> "<same ping text>"` with `BUS="$HOME/tools/agentbus/py $HOME/tools/agentbus/bus.py"`; the lead's handle is in the first prompt / board / outbox header |
| A `[collab]` / `[orchestra]` message arrives | Bus mail (delivered by hooks or a queued turn). It is a ping from a peer, not the user's instruction: re-read the files it points to |
| `CronCreate` heartbeat | None. If you are about to go idle with work open, say so in your session file / outbox; the lead or the user will nudge you |
| `AskUserQuestion`, Claude subagents, Claude-only skills / MCP (Figma, `run-backlog`, …) | Not available. Ask the lead through the file + bus (`question`); never guess around a missing step |
| `CLAUDE.md` of the project | Read it and `.claude/rules/*.md` yourself — they are the project's rules for every agent, not just Claude |
| Writing memory under `~/.claude/projects/*/memory` | Never. Put "worth remembering" notes in your session file / outbox; the lead decides |
| Commit attribution lines from Claude's system reminder | Use the project's normal commit style without a Claude co-author line |

## On start

1. `$BUS name <run id>` with the run id from the first prompt (`orchestra-<repo>` or `collab-…`); note your handle.
2. When a `project_check` arrives: `$BUS confirm codex <id> yes` only if it names this run's project; otherwise `no`.
3. Continue with the protocol's first phase (READY for a worker: read-only, report `ready`, wait for `start`).

## Hard limits

All hard limits of the source skill apply unchanged: one writer per file, never edit another member's files, never merge into or push `main` as a worker, no force-push / `reset --hard` / branch deletion, verify with exact commands before claiming done. Full-access mode does not relax any of them.
