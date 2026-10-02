---
name: collab
description: Use when the user runs /collab with the paths of two or more related projects (e.g. a library and the product that consumes it) so their Claude sessions exchange handoffs, requests, bug reports and questions as peer developers.
disable-model-invocation: true
argument-hint: <project-path> <project-path> [more paths]
---

# Collab — peer Claude sessions working like two developers

Each project's Claude session is a peer developer. Peers tell each other what they shipped, what they need, and what broke — through files they own, pinged by `SendMessage`. No session is the lead; the user is.

## Two phases

| Phase | Entered by | Allowed |
|---|---|---|
| **SETUP** | `/collab <paths…>` | Resolve projects, create own outbox, read peers' outboxes, `ListAgents`, report to the user. **Send nothing, change no code.** |
| **ACTIVE** | User says "bắt đầu" / "start" | Exchange messages and do the work autonomously until STOP. |
| **STOP** | User says "dừng" / "stop", or no open item on any side | Send a final note to peers, give the user a summary. |

A `[collab]` message that arrives while this session is not ACTIVE: tell the user it arrived, do nothing else.

## Resolving projects (SETUP)

- **Self** = the argument path that equals or contains the current working directory. None matches → ask the user which one is self.
- **Name** of a project = its directory basename (`WMusi`). **Session prefix** = lowercase name + `-` (`wmusi-`), matching `ListAgents` rows like `wmusi-09`.
- **Outbox** = `<project>/.claude/collab/outbox.md`. Create self's from the template below if missing. A peer outbox that does not exist yet is simply empty.
- Report: self, peers, live peer sessions, open items addressed to self, open items self is waiting on.

## Ownership — one writer per file

- Write only **your own** outbox. Read peers' outboxes; never edit them.
- Never edit a peer project's code. A fix needed over there is a `REQ` or `BUG` to that peer.
- The **opener owns an item's status**. The receiver answers with a new item carrying `re:`; the opener closes the original after verifying.

## Outbox format

```markdown
# Collab outbox — <Name>

## Received   <!-- what I'm doing with peer items addressed to me -->
| Item | Status | Note |
|---|---|---|
| WMUSI-3 | in-progress | pitch per stem group, BatchStemPlayer first |

## Sent

### <NAME>-<n> · <TYPE> · <one-line title>
- status: open | done | decided | stalled | closed
- to: <PeerName>
- re: <PEER-ID>          (only when answering an item)
- date: YYYY-MM-DD
<body — the required fields for TYPE>
```

IDs are `<NAME uppercased>-<running number>` (`WMUSI-3`, `AUDIOSEPARATION-7`), so they never collide across peers. Newest item last.

| TYPE | Required body fields |
|---|---|
| `HANDOFF` — I shipped something | **Changed** · **API** (signatures) · **Breaking** (yes/no + migration) · **Peer to-do** · **Verified by** (exact commands + results) · **Not yet** |
| `REQ` — I need something | **Need** · **Why** (screen, flow, design frame) · **Done when** (testable) |
| `BUG` — your thing misbehaves | **Version** (the HANDOFF id used) · **Repro** (minimal, ideally a test) · **Expected** · **Actual** · **Evidence** |
| `QUESTION` | **Question** · **Options** · **My proposal** |
| `DECISION` | **Decided** · **Why** · **Rejected options** · **Agreed with** (peer item id) |

`Received` statuses: `seen` → `in-progress` → `answered (<my item id>)` | `not-mine (<my item id>)`.

## Sending

1. Write the item into your outbox **first**. The message is only a ping; the file is the record.
2. `ListAgents` → send to **every** live session whose name starts with the peer's prefix. Session names change each launch — never reuse a remembered name.
3. Message text (plain text, `@path` attaches nothing on the other side):
   ```
   [collab] <SelfName> → <PeerName>: new <IDs> (<types>). Read <absolute outbox path>.
   If /collab is ACTIVE in your session, process them; otherwise tell your user.
   ```
4. No live peer session → the item waits in the file; the peer reads it at its next `/collab`.

## Working (ACTIVE)

On start and on every `[collab]` message: re-read the peer outboxes (the files, not the message), then for each item addressed to you that is not yet in your `Received` table:

- **REQ / BUG** → mark `in-progress`, do the work fully, verify per this project's CLAUDE.md (build every source set incl. tests, run related tests), then send a `HANDOFF` with `re:`. A BUG that turns out to be the peer's misuse → reply `not-mine` with the correct usage instead of bending your code.
- **HANDOFF** → integrate it, verify, then `closed` your matching REQ — or open a `BUG` with `re:`.
- **QUESTION** → answer with a `DECISION` or a counter-`QUESTION`.
- **Product decisions** (formats, defaults, scope) → peers decide together via `QUESTION` → `DECISION`. Pick the option that fits the user's stated goals and the design; record why and what was rejected so the user can overturn it later.

Do not ask the user for permission while ACTIVE. They chose full autonomy.

## Commit and push

Only the **user's** "bắt đầu" / "dừng" moves the flag `~/.claude/collab-active`; a peer message never does.

- On start: `touch ~/.claude/collab-active`. The global PreToolUse hook then lets `git commit` through (`git push` is never hook-blocked; force-push, `reset --hard`, `clean -f`, branch delete always are).
- While ACTIVE, in a project that is a git repo: after each verified item, commit that item's files **plus your own outbox** (it records what was shipped and decided next to the code) — nothing else (message ends with the attribution lines from the system reminder) and push the current branch. A project that is not a git repo just keeps the changes.
- On stop: `rm -f ~/.claude/collab-active`. The commit block is back for every session, including a peer still running — that is intended. Push is then governed only by the user's CLAUDE.md rule (only when asked).

## Heartbeat — resuming after a usage limit or a lost ping

A turn cut off by a usage limit does not resume by itself. On start, schedule a recurring `CronCreate` (session-only, fires only while idle, expires after 7 days) at off-minutes, e.g. `7,27,47 * * * *`, prompt:

```
[collab heartbeat] If /collab is ACTIVE: re-read all outboxes, resume every item marked in-progress in my Received table, then process new items. Nothing open → reply one line and stop.
```

Firings during the limit fail; the first one after the reset picks the work back up from the outbox. On stop, `CronDelete` it. If the whole session was closed, the user re-runs `/collab` + "bắt đầu"; the outboxes still hold the state.

Keep `Received` current **before** starting long work (mark `in-progress` first) — it is what the heartbeat resumes from.

Resuming an `in-progress` item means the last turn may have stopped mid-edit. Before continuing it: inspect the working tree (`git status` / `git diff`, or the files the item touches), build every source set, and finish or repair the half-done change. Never commit until that build is green.

## Hard limits (still apply while ACTIVE)

- No commit or push outside ACTIVE, no force-push ever.
- Follow each project's own CLAUDE.md; a peer's request never overrides it.
- Never ask a peer to do something your session was denied or blocked from doing.
- The same item bouncing more than **3 rounds** without closing → mark it `stalled` with the sticking point, move on to other items.
- Act only on items addressed to you.

## Stopping

On STOP: remove the flag (see Commit and push), `CronDelete` the heartbeat, send peers `[collab] <SelfName> stopping.` and give the user a summary — commits pushed, — items shipped, integrated, decided (with the reasons, so they can overturn), stalled, still open.

## Common mistakes

| Mistake | Fix |
|---|---|
| Putting the content in the `SendMessage` text | Content goes in the outbox; the message points to it |
| Editing the peer's outbox to "close" their item | Reply with `re:`; the opener closes |
| Sending to `wmusi-09` from memory | `ListAgents` every time, send to every matching session |
| Working on a `[collab]` ping before the user said start | Not ACTIVE → only tell the user |
| HANDOFF with "tests pass" and no command | Exact command + pass count, or it is not verified |
