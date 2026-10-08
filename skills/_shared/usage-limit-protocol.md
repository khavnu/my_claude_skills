# Usage-limit protocol — progress log, pause, auto-resume

Shared by `/orchestra`, `/long-feature`, `/collab`. A session that hits its usage limit stops mid-turn, and its subagents die with it — no final report, half-edited files in the tree. These rules make that cheap to recover from.

## 0. Modes: full run (default) and limit-aware (only when the user asks)

`~/.claude/usage-latest-<K|D>.json` is rewritten by the status line on every render, so it is always current and reading it costs one `jq` call. The SessionStart hook injects it into each new session. No polling cron.

**Full run — the default (user 2026-10-08).** Work at full pace and apply everything without asking; no throttling, no week warning. Limit handling is only:
- keep the progress log (section 1), so a cut mid-turn is cheap to recover;
- once 5h ≥ 90 % (from the hook or a re-read before heavy work), schedule the one-shot resume at reset + 5 min **in advance** (section 3) and keep working — a session already cut by the limit can no longer schedule anything. If the limit never cuts, the firing finds nothing paused and just continues.

**Limit-aware — only after the user says so** (e.g. "chú ý limit"), until they lift it. Re-read the file before heavy work (dispatching an agent, a worker or wave, a workflow, `connectedAndroidTest` / a full build loop):

| Reading | Do |
|---|---|
| 5h < 70 % | Normal |
| 5h 70–90 % | Light work only: reviews, docs, small fixes, finishing in-flight steps. No new Opus agent, no new worker |
| 5h ≥ 90 % | Pause (section 2) and schedule the resume (section 3) |
| week > 70 % | Tell the user once and propose cheaper models / fewer workers; the user decides |

Hard rules (no force-push, secrets, device/commit rules) apply in both modes.

## 1. Progress log (always, while working)

- Every long-running unit (main, worker, subagent) keeps an **append-only** progress file: after each **step boundary** (a sub-item done, a build green, a decision taken) append 2–4 lines with `>>` — what is done, what is next, which files are touched.
- Never rewrite the whole file to add a line (cost grows with every rewrite). Never re-read it while working — only when resuming.
- Subagent prompts say: "append progress to <report path> after each step; reply only with the short contract at the end".
- Workers on a branch commit + push each step that builds green; unbuildable work stays uncommitted and is described in the log.
- Main / the lead keeps one **resume note** (board for orchestra, checklist "Điểm dừng" for long-feature, outbox `Received` for collab): what is running, what is next, open questions.

## 2. Pause (user says the limit is close, or a limit warning shows in the conversation)

1. Do not start new large work (new waves, new agents, workflows). Finish or cleanly park the current step.
2. Commit + push what builds (only where the skill/project allows commits); describe the rest in the progress log.
3. Write the resume note (above) — include the running subagents and their report paths, since they will die.
4. Tell peers: orchestra main sends `main pausing` to workers (they do steps 2–3 for their own task); collab sends a `NOTE · pausing until HH:MM` to the peer.
5. Schedule the auto-resume (section 3) when the reset time is known.

## 3. Auto-resume after the reset

- The reset time comes from `~/.claude/usage-latest-<K|D>.json` (`five_hour.resets_at`, epoch seconds; written by the status line for the account of this session — K when `CLAUDE_CONFIG_DIR=~/.claude-k`, else D). A SessionStart hook injects it into every new session. Otherwise from the user or the limit message. Never guess a reset time.
- At the `[resume]` firing, re-read the file: if the 5h window is high again, park and schedule the next one-shot the same way.
- Schedule a **one-shot** `CronCreate` at **reset + 5 min** (e.g. reset 13:30 → `35 13 <dom> <month> *`, `recurring: false`) with the prompt:
  `[resume] Usage limit has reset. Read the resume note and progress logs, check git status/diff, build green, then continue the paused work.`
- It only fires if this session is still open and idle at that time (session-only cron). If the session was closed, the user re-opens it; the resume note carries the state.
- Recurring heartbeats (orchestra/collab) keep running: firings during the limit fail, the first one after the reset also resumes — the one-shot just makes it prompt.

## 4. Resuming

1. Read the resume note, then only the progress logs of the units that were running.
2. `git status` / `git diff`: finish or repair half-done edits; build every source set green before any commit.
3. A dead subagent is re-dispatched as a NEW agent with: "continue from the uncommitted work in the tree; read <report path> first; finish items X–Y". Do not try to resume a dead agent id.
4. Tell the user in one short message what resumed and what is next.
