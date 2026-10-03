# Orchestra file templates

All state files live in `<repo>/.claude/orchestra/` (excluded from git). The review file is the only one committed.

## board.md — main only

```markdown
# Orchestra board — <Repo>

goal: <the user's goal, one paragraph>
main session: <name from ListAgents "This session is …">
permission mode: <main's mode — every worker launches with the same>
config:
- max_parallel: 2
- reviews: docs/reviews
- build: <command from CLAUDE.md>
- test: <command from CLAUDE.md>
- copy into new worktrees: local.properties
- devices: <serial → task, Android only>

## Tasks
| ID | Name | Model | Status | Depends (hard / soft) | Wave | Address | Note |
|---|---|---|---|---|---|---|---|
| T-1 | player-contract | — | merged (main) | — | 0 | — | interfaces shared by T-2, T-3 |
| T-2 | visualizer | sonnet | review-requested | hard T-1 | 1 | `from` of its ready | round 2 |
| T-3 | lyrics-view | opus | in-progress | hard T-1 · soft T-2 | 1 | `from` of its ready | |

Statuses: planned · assigned · ready · in-progress · question · review-requested · changes-requested · merged · blocked · stalled · dropped
`(main)` in Status = main does it itself.

## Follow-ups
| From | Severity | Finding | Becomes |
|---|---|---|---|
| T-2 | medium | FFT buffer allocated per frame (SpectrumView.kt:88) | T-7 |

## Contracts
| Contract | Version | Module | Answers | Commit | Tasks that must adapt |
|---|---|---|---|---|---|---|---|
| Song + SongRepository | v1 | core:model | T-4 P1, T-3 P1 | b4c5d6e | T-3, T-4 |

## Decisions
- 2026-10-03 · T-2 · <decision> — why: … — rejected: …

## Main updates
- 2026-10-03 · a1b2c3d · added `PlayerTimeline` to :core:player (all workers merge origin/main)
```

## tasks/T-<n>-<name>.md — main only

```markdown
# T-<n> · <name> · <title>

- branch: feature/<name>
- worktree: <absolute path>
- device: <serial or none>

## Goal
<what and why, linked to design frames / docs>

## Scope
- may edit: <paths / modules>
- must not edit: <shared paths owned by main or other tasks>

## Done when
- <testable criterion>
- builds every source set, related tests pass

## Answers
### Q1 (from session file) — <answer> · 2026-10-03

## Review rounds
### Round 1 · <hash> · changes-requested
1. **high** · Foo.kt:42 — <problem> → <what to fix>
2. **low** · Bar.kt:10 — <note, accepted>
```

## sessions/T-<n>-<name>.md — that worker only

```markdown
# T-<n> · <name> — worker log

status: ready | in-progress | question | blocked | review-requested | changes-requested | merged

## Log
- 2026-10-03 10:05 · ready (worktree ok, local.properties present)
- 2026-10-03 10:12 · start received, branch at a1b2c3d
- 2026-10-03 11:40 · merged origin/main (main updated a1b2c3d)

## Questions
### Q1 · <question> · options: … · my proposal: …

## Contract proposals
### P1 · Song (for T-3, feature screens)
- Proposed: `data class Song(id: Long, uri: Uri, title: String, artist: String, durationMs: Long, albumId: Long)`
- Why: <what was measured or learned — e.g. these columns come from one MediaStore query, 1 200 songs in 180 ms; artwork needs a separate read>
- Status: proposed | adopted in <contract> v<k> | changed by main (see board Decisions)

## Review requests
### Request 1 · tip <hash>
- Verified by: `<exact command>` → <result, counts>
### Request 2 · tip <hash>
- Round 1 fixes: 1 → <what changed>; 2 → accepted as is
- Verified by: …
```

## docs/reviews/T-<n>-<name>.md — committed with the merge

```markdown
# Review — T-<n> · <name> · <title>

- branch: feature/<name> (merged at <merge hash's parent tip>)
- rounds: 2
- result: merged with 1 medium, 2 low accepted

## Round 1 · <hash> · changes requested
1. high · Foo.kt:42 — <problem> → fixed in <hash>
2. low · Bar.kt:10 — <note> → accepted

## Round 2 · <hash> · accepted
1. medium · SpectrumView.kt:88 — <problem> → follow-up T-7

## Verification
- worker: `<command>` → <result>
- main after merge: `<command>` → <result>
```
