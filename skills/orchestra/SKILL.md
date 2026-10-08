---
name: orchestra
description: Use when the user runs /orchestra to turn one session into a lead (main) that plans an idea into tasks, hands them to parallel worker CLI sessions (Claude by default; another Claude account or Codex via --pool) on their own git worktrees, reviews their branches and merges them locally — or runs /orchestra join to make a session one of those workers.
argument-hint: <goal or idea> [--pool claudeK,codex]  |  join <task-id> <name> <worktree-path> [— summary]
---

# Orchestra — one lead session, several satellite dev sessions

The session that runs `/orchestra <goal>` is **main**: a team lead. It plans, writes shared code, answers questions, reviews and merges. Each **worker** is a separate Claude Code CLI the user opens on its own git worktree and branch; it builds one task and asks for review. The user is above both: they approve the plan and can overrule any decision.

Everything is plain `git` plus files. No PR service is needed: workers push their branch, main reviews and merges locally with `--no-ff`, and pushes `main`.

## Phases

**Main**

| Phase | Entered by | Allowed |
|---|---|---|
| **SETUP** | `/orchestra <goal>` | Discuss with the user, survey the repo, draft the plan, show it. **Create nothing, change no code.** |
| **ACTIVE** | User approves the plan | Do main's own tasks, prepare each wave (worktrees + briefs), collect `ready`; on the user's "bắt đầu" / "start" dispatch the wave; coordinate, review, merge — autonomously. |
| **STOP** | User says "dừng" / "stop", or every task is merged or dropped | Final summary to the user, ping workers. |

**Worker**

| Phase | Entered by | Allowed |
|---|---|---|
| **READY** | User pastes `/orchestra join …` | Check its worktree, read its task, report `ready` to main. **Change no code.** |
| **ACTIVE** | `start` from main | Build the task, request review, fix, until merged. |

An `[orchestra]` message that this session's phase does not expect (e.g. anything but `start` while READY, anything while main is in SETUP): tell the user, do nothing else.

## Layout

```
<repo>/                                main's working tree, always on branch main
<repo>/.claude/orchestra/              state, never committed (add to .git/info/exclude)
    board.md                           main only — config, task table, follow-ups, decisions
    tasks/T-<n>-<name>.md              main only — spec, answers, review rounds for the worker
    sessions/T-<n>-<name>.md           that worker only — progress, questions, review requests
<repo>/docs/reviews/T-<n>-<name>.md    final review record, committed with the merge
<repo-parent>/<repo>-wt/<name>/        the worker's worktree, branch feature/<name>
```

**One writer per file.** Main never edits a worker's session file or worktree; a worker never edits the board, a task file, `main`, or another worker's files. Templates for every file are in `references/templates.md`.

A worker finds the main repo with `git worktree list` (first row) and uses absolute paths to the state files.

## Main — SETUP

0. Talk the goal through with the user until scope and priorities are clear. If the repo is empty or does not exist yet, follow **Empty project** below.
1. Read the project's `CLAUDE.md`, memory, backlog, module layout, and the build/test commands it prescribes. Note untracked files a fresh worktree needs to build (e.g. `local.properties`, keys, `.env`).
2. Split the goal into tasks. Each task has a short kebab-case **name** (`visualizer`), an id `T-<n>`, a **scope** (the files/modules it may touch), **Done when** (testable), and **depends on**.
   - Two tasks touching the same files or module never run in parallel — order them with a dependency.
   - Shared groundwork (version catalog, core modules, build config, module ownership) is a task **main does itself** before handing out the tasks that need it.
   - Do not guess the contracts between tasks up front: give each task a goal it can reach on primitive or module-internal types, and let the contracts come from the workers (see **Contracts**).
   - Mark every dependency **hard** or **soft**:
     - **hard** — the task cannot be built right without the other one merged. UI screens hard-depend on the design system: built before it, they are restyled later. A hard-dependent task is not prepared until its dependency is merged.
     - **soft** — the task can fake it: data and contracts (fake data, its own `UiState`, callbacks such as `onGrantPermission()`). Soft dependencies never delay a task; it maps onto the real contract when it lands.
   - A design system read from Figma is a **worker task**, not main's: the Figma output (screenshots, node trees, tokens) would flood main's context. Main does it itself only when it is tiny (a few colors and a theme, no components).
3. Group tasks into waves by **hard** dependencies only; capacity decides the rest. Default `max_parallel` = **2**; the user raises it when the PC copes (3–5 at most), lower it for heavy builds.
4. Show the user: tasks, waves, what main will code itself, the config. Wait for approval.

**Pool** (`--pool`, or the user says another account / CLI may be used): read `~/.claude/skills/_shared/cross-agent.md` before step 2. In the plan, give every task its pool member and reason (allocation table there), and state the transport (agentbus for the whole run). Main stays on this session.

See **Example** at the end for what a good split looks like.

### Empty project

Worktrees branch off `origin/main`, so a remote `main` with a buildable skeleton must exist before any worker starts.

In SETUP (still creating nothing):

1. Agree with the user on the product, platform and stack. The user normally has the remote ready before starting: read it with `git remote -v`. Only if there is none, ask for the URL — never create a remote repo yourself.
2. Plan **wave 0 = main's own work**: the skeleton (modules, dependencies, build config, DI, empty navigation) and **who owns what** — in particular the shared model/contract module belongs to main and starts (nearly) empty. Shared files that several tasks would otherwise edit (dependency catalog, manifest, settings) get their entries now.
3. Include in the plan the `CLAUDE.md` main will write: build/test commands and the conventions every worker must follow.

After approval (ACTIVE):

4. `git init -b main` if the folder is not a repo yet, write `CLAUDE.md`, build wave 0 green, commit, push `main`. Only then prepare wave 1.

## Main — ACTIVE

**Start:** add `.claude/orchestra/` to `.git/info/exclude`, call `ListAgents` and read this session's own name from its first line ("This session is <name>") — with a pool instead run `$BUS name orchestra-<repo>` and use the printed handle (this session must have been started with `claude-bus`; if not, tell the user to restart it that way first) — write `board.md` with that name as `main session` (workers message main by it), note this session's permission mode as `permission mode` (from the system prompt; ask the user if unsure). Schedule the heartbeat only once a worker is live (see Heartbeat).

**Worker per task.** With a pool, first pick the member (`claude` / `claudeK` / `codex`, see `cross-agent.md`); the model choice below applies to Claude members only, Codex uses its own configured model. Write member + model on the board.

**Model per task.** Pick each worker's model by the task's difficulty and write it on the board:
- **opus** — concurrency, service/playback lifecycle, IO and codecs, cancellation, anything a fix round would be expensive to redo;
- **sonnet** — UI, ports, ordinary feature work (the default);
- **haiku** — only tiny mechanical tasks. In the test run a Haiku worker skipped READY, did not push and ticked a Done-when it had not met: do not give it anything that needs the protocol followed closely.

**Prepare a wave** — for every task whose **hard** dependencies are merged, up to the free slots (`max_parallel`, default **2** — the user raises it when the PC copes):

```
git fetch origin
git worktree add -b feature/<name> <repo-parent>/<repo>-wt/<name> origin/main
```

Copy the untracked build files into the worktree, write `tasks/T-<n>-<name>.md`, set the board row to `assigned`, then print the brief in the user's language. The user opens each session themselves from it:

```
── T-3 · visualizer · sonnet ─────────────────────
Open a terminal in  F:\Work\Karaoke\music_karaoke-wt\visualizer  and run:

claude -n feature-visualizer --model sonnet --permission-mode <main's mode> "/orchestra join T-3 visualizer F:\Work\Karaoke\music_karaoke-wt\visualizer — waveform + spectrum visualizer for the player"

First time in this folder Claude Code asks to trust it: accept.
```

- `-n` names the session at launch — no `/rename` needed.
- `--permission-mode` must equal main's: a session in a different mode holds every cross-session message for its user's approval, so nothing runs on its own.
- The quoted `/orchestra join …` is the first prompt; the user does not paste anything.

**Short form** — for a session the user already opened (any folder, same permission mode as main), print just the line to paste:

```
/orchestra join T-3 visualizer F:\Work\Karaoke\music_karaoke-wt\visualizer — waveform + spectrum visualizer for the player
```

Optionally `/rename feature-visualizer` first, for the user's own overview. Opening the session inside the worktree is still better: the project's `CLAUDE.md` loads and the shell starts in the right place.

**Pool runs — main opens the workers itself** with `bus-open <member> <worktree> "orchestra-<repo> · T-<n> <name>" …` (see `cross-agent.md` › Opening members) instead of printing briefs; the brief text becomes the first prompt. A Codex worker cannot run `/orchestra join`; its first prompt is `Use skill cross-agent-peer. Role: orchestra worker T-<n> <name> <worktree>. Main handle: <handle>. <summary>`. Tell the user which windows opened and the first-launch approvals they must accept there.

Print all the wave's briefs at once and tell the user: open them, then say "bắt đầu".

**Readiness.** Each worker, once joined, writes `ready` in its session file and pings main. `ListAgents` may not list worker sessions even though messages flow: record each worker's **address** — the `from` attribute of its first message, or its bus handle with a pool — in the board's Tasks table, and send to that address. Main keeps a running list for the user: `Ready: T-2 designsystem, T-3 playback · Waiting: T-4 media-library`.

**Dispatch** — on the user's "bắt đầu" / "start":

1. Re-check each task of the wave: `ready` in its session file **and** an address recorded for it.
2. Send `start` to every ready worker; set them `in-progress` on the board.
3. For each task that is not ready, tell the user exactly what is missing and re-print its brief: "T-4 media-library chưa sẵn sàng — chưa có session nào join. Mở thêm: …". A `ready` worker whose session is gone → same, the user reopens it.
4. Do not hold the ready ones back for the missing ones unless the user says to wait. A late worker that reports `ready` while the wave is running gets `start` at once.

**Shared code by main:** commit on `main`, push, then ping every live worker: `main updated (<short hash>): <what changed>. Merge origin/main and adapt.` Record it on the board.

### Contracts — workers propose, main decides and broadcasts

The types and interfaces that cross module or layer boundaries (shared models, repository/service interfaces, state types) live in a module only main edits. They are settled **from the workers' findings**, not guessed in SETUP:

1. A worker builds its capability on primitive or internal types first (a player that plays a `Uri`; a scanner returning its own internal row type) and is never blocked waiting for a contract.
2. When it needs to expose something to another layer, it writes a **contract proposal** in its session file — the types/functions it wants, and why, from what it measured or learned — and pings main `contract-proposal`. It does not edit the shared module.
3. Main collects the proposals touching the same contract, reconciles them, and decides: record it in the board's **Contracts** (version, what changed, which proposals it answers) and conflicting choices in Decisions.
4. Main commits the contract to `main`, pushes, and pings every affected worker `main updated (contract <name> v<k>)`. They merge `origin/main` and switch to it through a thin mapping layer.
5. A later change to a merged contract goes the same way; main lists which tasks must adapt.

**Questions from workers:** answer in the task file. Decide product questions inside the user's stated goals and record why in the board's Decisions; anything outside them goes to the user.

**Review** — on `review-requested`:

1. `git fetch origin`, check the requested hash is the branch tip and that the branch already contains current `origin/main` (`git merge-base --is-ancestor origin/main origin/feature/<name>`). Stale (typically another task merged first) → ping the worker `main updated`; it merges `origin/main`, rebuilds, and requests review again. Do not review a stale tip.
2. **Delegate the review to a subagent** (model **sonnet** at least; **opus** for the final review of a risky task) so main's context stays free for coordination. Give it: the branch and tip hash, the task file (scope, Done when), the worker's **Verified by**, the project's `CLAUDE.md` rules, and the severity scale below. It reviews `git diff origin/main...origin/feature/<name>` (with the `code-review` skill when available), flags any file outside the task's scope, and — when the worker's evidence is missing or doubtful — builds and tests the branch in the **review worktree**, never in main's checkout:
   ```
   git worktree add --detach <repo-parent>/<repo>-wt/_review origin/feature/<name>   # first time
   git -C <repo-parent>/<repo>-wt/_review checkout --detach origin/feature/<name>    # next reviews
   ```
   The review worktree needs the same copied build files as a worker worktree. It returns only the findings (severity, `file:line`, problem, fix) and the commands it ran with results. Main reads the findings, checks any it doubts, and decides.

   Before merging, main **always runs the build and tests itself in `_review`** at the requested tip. In the test run the subagent ran them in the worker's worktree instead: a subagent's "tests pass" is a hint, not the gate.
3. Classify every finding and apply the gate:

| Severity | Gate |
|---|---|
| Critical | Always blocks. |
| High | Blocks by default. Main may accept **at most 1**, only if it cannot lose data, crash, or break a main flow — and it becomes a follow-up task. |
| Medium | Accept **at most 3**; each becomes a follow-up. More → changes requested. |
| Low | Accepted; listed in the review file. |

4. Write the round into the task file (`changes-requested` with numbered findings, `file:line`, what to fix) and ping the worker. A task bouncing more than **3 rounds** → stop and ask the user.

**Merge** — when the gate passes:

```
git switch main && git pull --ff-only
git merge --no-ff --no-commit origin/feature/<name>
# write docs/reviews/T-<n>-<name>.md (all rounds, accepted findings + their follow-up ids, verification)
git add docs/reviews/T-<n>-<name>.md
git commit -m "Merge feature/<name> (T-<n>): <title>" -m "Review: docs/reviews/T-<n>-<name>.md"
```

Then build and test `main` per `CLAUDE.md`. Broken → fix it on `main` (or `git revert -m 1` the merge and reopen the task); never push a red `main`. Push `main`, keep the remote branch (it is the record), add accepted findings as follow-up tasks, ping all workers `main updated`. Tell the user the worker's CLI can be closed, then `git worktree remove <path>`. Leave the local branch for the user to delete.

**Integration** — when every task of a wave is merged (or dropped). It does not hold back tasks whose own hard dependencies are already merged (screens start as soon as the design system merges); it runs alongside them:

1. Wire what the wave delivered into the app on `main` yourself: navigation entries, DI bindings, the flow between screens, real contract implementations replacing fakes.
2. Build and test, then **run the app** and walk the main flow the wave enabled (the `run` skill, or the project's own launch/verify skill; on Android also the device rules in `references/android.md`). Note what you actually saw.
3. A defect → fix it on `main` if it is wiring; if it sits inside a task's code, open a follow-up task. Commit, push, ping workers `main updated`.
4. Tell the user what now works end to end and what does not yet.

**Loop:** after each merge, re-check the board — prepare the newly unblocked tasks (briefs → `ready` → the user's "bắt đầu" → dispatch, as above), plan follow-ups into the next wave, and give the user a short round summary: merged, accepted findings and why, what is running, what waits on them.

## Worker — `/orchestra join T-<n> <name> <worktree> [— summary]`

1. **READY:** the join line carries the worktree path (`/orchestra join T-<n> <name> <worktree> — summary`). If this session was opened somewhere else, work there by absolute path: every git command as `git -C <worktree>`, every file by its absolute path, every build/test run as `cd <worktree> && …` in the same command (the shell's cwd resets between calls), and read `<worktree>/CLAUDE.md` yourself since it was not loaded. Locate main (`git -C <worktree> worktree list`, first row), read `board.md` and `tasks/T-<n>-<name>.md`. Check the worktree is on `feature/<name>` and the copied build files are there. Anything wrong → tell the user and main, do not report ready. The session name is cosmetic — messaging does not depend on it; if it is not `feature-<name>`, suggest the user type `/rename feature-<name>`.
2. Create `sessions/T-<n>-<name>.md` with `ready` and a one-line understanding of the task, ping main `ready` at the `main session` name from the board, schedule the heartbeat unless main or the user switched it off, tell the user you are waiting for main's start.
   **READY is read-only for the code:** no edits, no new files, no commits in the worktree — not even a "quick" start. Your turn ends after the ping; the next thing you do comes from `start`.
3. On `start`: set `in-progress`. Push the branch at once (`git push -u origin feature/<name>`) so main can see it from the first minute. Work only inside the task's scope. Something outside it is needed → ask main (`question`) and continue with what you can. Follow the project's `CLAUDE.md` in full.
   - Build on primitive or internal types. When another layer needs what you build, write a **contract proposal** and ping main `contract-proposal` (see **Contracts**); never edit the shared model/contract module yourself. Keep working while main decides.
4. Commit in small steps on `feature/<name>`; push the branch whenever you commit.
5. On `main updated`: commit or finish the current step, `git fetch origin && git merge origin/main`, resolve conflicts, rebuild, push.
6. **Request review** when Done when holds:
   - merge the latest `origin/main`, build every source set incl. tests, run the related tests;
   - push, then confirm the remote has your tip: `git ls-remote origin feature/<name>` must print the same hash as `git rev-parse HEAD`;
   - in your session file write `review-requested`, the tip hash, **Verified by** (exact commands + results), and **each Done-when line with the evidence that proves it** (the test name/assertion, the output line). A criterion without evidence is not met — do not tick it;
   - ping main.
7. On `changes-requested`: fix each numbered finding, note per finding what changed, push, request review again.
8. On `merged`: write a final line, tell the user this CLI can be closed, delete your heartbeat.
**Other skills inside a worker:** a task that is long or heavy (performance targets, multi-session) may run as `/long-feature` inside the worker; its checklist goes to main as a `question` and waits for main's OK before code. A worker never opens `/collab` with another project or session: anything outside goes through main, unless main hands it one specific request to carry.
**Hygiene:** stage only your task's paths (never `add -A` / `commit -a`) and check `git diff --cached --stat` before each commit. A subagent that has written no file in ~1 h is stalled: stop it and re-dispatch a new one on the work in the tree.
9. On `main stopping`: finish or cleanly pause the current step, commit and push what builds (work that does not build stays uncommitted and is described in the log), write where you stopped and what is left in your session file, delete your heartbeat, and tell the user. A later `/orchestra join` with the same task resumes from that log.

Never rebase a pushed branch and never force-push — integrate `main` by merging it in. Never merge into or push `main`.

## Messages

The file is the record; the message is a ping.

- **Worker → main:** send to the `main session` name in `board.md`.
- **Main → worker:** send to the worker's address recorded on the board (the `from` of its messages). `ListAgents` may not list workers; when it does, it confirms they are alive. A worker that restarts gets a new address — take it from its next `ready`.
- All sessions run in the same permission mode (the brief's `--permission-mode`); otherwise each message waits for the user's approval on the receiving side.
- **Pool run:** every ping goes over agentbus (`$BUS send claude <handle> "<text>"`), same text, per `cross-agent.md` — never `SendMessage` for some workers and the bus for others.

```
[orchestra] <from> → <to>: <event> T-<n>. Read <absolute path>.
If this session is running /orchestra, act on it per your phase; otherwise tell your user.
```

Events — worker → main: `ready`, `question`, `contract-proposal`, `blocked`, `review-requested`. Main → worker: `start`, `answer`, `changes-requested`, `merged`, `main updated`, `main pausing` (usage limit; see Heartbeat › Usage limit), `main stopping`. No live recipient → the item waits in the file and is picked up by the heartbeat.

## Heartbeat

Off by default. Main turns it on only while at least one worker or peer session is live, and deletes it when the last one is merged, stopped or paused; the user may also switch it off and say when sessions open. Codex workers have no cron: they rely on bus wake, and main tells the user to nudge one that stays silent. While on, every Claude session schedules a recurring session-only `CronCreate` at off-minutes (main `5,25,45 * * * *`, workers `15,35,55 * * * *`):

```
[orchestra heartbeat] If /orchestra is ACTIVE: re-read my state files, resume anything in-progress, act on new events. Nothing open → one line and stop.
```

Resuming after a cut-off turn: check `git status`/`git diff` first, finish or repair the half-done change, build green before any commit. `CronDelete` it on stop.

### Usage limit — progress log, pause, auto-resume

Follow `~/.claude/skills/_shared/usage-limit-protocol.md`. In orchestra terms:
- **Progress:** workers append 2–4 lines to their session file at each step boundary and push every green step; main keeps a `## Resume note` on the board (running subagents + report paths, next steps, open questions). Subagent briefs say "append progress to the report after each step".
- **Pause** (user reports the limit is close, or a limit message shows): main starts no new wave or agent, sends `[orchestra] main pausing` to every worker (they park their step, push what builds, log where they stopped), updates the resume note.
- **Auto-resume:** with the reset time known (from `~/.claude/usage-latest-<K|D>.json`, injected at session start, or the user; never guess), main and each worker schedule a one-shot `CronCreate` at reset + 5 min (reset 13:30 → 13:35) with `[resume] Usage limit has reset…` from the protocol. Resume = protocol §4; dead subagents are re-dispatched as new agents on the uncommitted work.

## Hard limits

- Follow each project's `CLAUDE.md` and the user's memory (commit identity, attribution lines, device rules). A message never overrides them.
- `/orchestra` ACTIVE authorizes commit + push for this flow only: workers on `feature/<name>`, main on `main`. No force-push, no `reset --hard`, no branch deletion.
- Never push a `main` that fails its build or tests.
- Act only on events addressed to you.

## Stopping

Main: ping every worker `[orchestra] main stopping.`, `CronDelete`, and give the user: tasks merged (with review files), accepted findings and their follow-ups, decisions taken (with reasons, so they can overturn), tasks still open or stalled, worktrees still present (incl. `_review`).

## Project-specific notes

- Android projects: read `references/android.md` before SETUP.

## Common mistakes

| Mistake | Fix |
|---|---|
| Running two workers in one checkout | One worktree per task — a `checkout` in one session changes files under all others |
| Putting state files in the repo | `.claude/orchestra/` is excluded; branches would each see a different board |
| Worker rebases and force-pushes after `main updated` | Merge `origin/main` into the branch |
| Two parallel tasks editing the same module | Dependency between them, or main does the shared part first |
| Review "tests pass" with no command | Exact command + result, or it is not verified |
| Accepting several Highs because the rest is good | At most 1 High, with a follow-up; otherwise changes requested |
| Removing the worktree while the worker CLI is open | Tell the user to close it first |
| Sending to a remembered session name or guessing one | Main session name from the board; worker address from its last message |
| Giving Codex a task that needs a Claude-only skill or MCP | Keep it on a Claude member, or spell every step out in the task file |
| Two members writing project memory | Only main writes memory; workers note it in their session file |
| Worker starts coding right after join | Report `ready`, wait for `start` |
| Dispatching without telling the user who is missing | List every not-ready task with its brief again |
| Handing out wave 1 of an empty project before the skeleton is on `origin/main` | Wave 0 first: skeleton + module ownership, built, pushed |
| Main designing every model and interface in SETUP | Settle contracts from the workers' proposals |
| A worker adding its own shared model to the contract module | Contract proposal to main; main commits and broadcasts |
| A worker idling until a contract is decided | Keep building on internal types; map later |
| Opening UI sessions before the design system is merged | UI hard-depends on it; prepare screens when it merges |
| Holding a task back for a soft dependency | Fake it; only hard dependencies order the waves |
| Main checking out a feature branch in its own tree to build it | Review worktree `<repo>-wt/_review`, detached |
| Reviewing a branch that does not contain current `origin/main` | Send `main updated`, wait for the re-request |
| Main reading every diff itself | Review subagent returns findings; main decides |
| Calling a wave done because every merge built green | Integrate, run the app, walk the main flow |

## Example — a music player app from an empty repo

After talking it through with the user (local music player: library, playback, Now Playing, Figma design ready):

**Wave 0 — main itself, pushed before anything else**
- Skeleton: `app`, `core:model` (owned by main, empty), `core:designsystem`, `core:player`, `core:data`, empty feature modules; dependency catalog with Compose, Media3, Hilt, Room; convention plugins; Hilt; empty navigation.
- Shared files pre-filled: service declaration and permissions in the manifest, so no wave-1 task edits it.
- No `Song`, no `PlayerController` yet — nobody knows their right shape before wave 1 has measured anything.

**Wave 1 — parallel, each proving a capability on its own types**

| Task | Scope | Done when |
|---|---|---|
| T-2 `designsystem` | `core:designsystem` | Colors, typography, light/dark theme and the common components read from Figma (the only session using Figma, so one rate limit); preview per component |
| T-3 `playback` | `core:player` | `MediaSessionService` + ExoPlayer playing a content `Uri` (not a file path — unreliable under scoped storage); queue of `Uri`s, play/pause, seek, shuffle/repeat, notification, audio focus; unit tests on queue logic |
| T-4 `media-library` | `core:data` | MediaStore scan into an internal row type + Room cache, read-media permission flow; measured scan time on N songs and which columns come cheap vs need tag reads |

They share no files and no types, so none waits for another.

**Contracts, settled during wave 1:**
- T-4 proposes `Song` from what the scan delivers cheaply (id, content `Uri`, title, artist, album, duration, albumId) and a `SongRepository` shape; T-3 proposes what a queue item needs and a `PlayerController` + `PlaybackState`.
- Main reconciles them (e.g. T-3 wanted artwork bytes, T-4 measured that as slow → `Song` carries `albumId`, artwork loads lazily — recorded in Decisions), commits `core:model` v1, broadcasts `main updated (contract Song v1)`.
- T-3 and T-4 merge `origin/main` and map their internal types onto it before requesting review.

**Wave 2 — screens, prepared the moment T-2 merges** (hard dependency on T-2; soft on contract v1): onboarding, song list, albums, Now Playing, mini player, settings — one task per feature module, as many as the free slots allow. A screen whose contract is not out yet runs on fake data and its own `UiState`, then maps `Song → SongRowUi` in its ViewModel when v1 lands. Navigation keys and the graph stay with main; each feature only exposes its entry.

```
Wave 0 (main):  skeleton + module ownership
Wave 1:         T-2 designsystem │ T-3 playback │ T-4 media-library   (contract Song v1 settled meanwhile)
Wave 2:         after T-2 merges → onboarding │ songs │ albums │ now-playing …
```
