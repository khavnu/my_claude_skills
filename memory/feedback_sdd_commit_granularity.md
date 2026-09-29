---
name: feedback_sdd_commit_granularity
description: "User wants coarse, phase-based commits (not one commit per plan task) when executing multi-task plans via subagent-driven-development"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 63051cfc-1237-41ac-8e16-237e84974539
  modified: 2026-08-14T01:00:38.394Z
---

When running `superpowers:subagent-driven-development` (or any multi-task plan execution) on this project, commit at the granularity of functional phases/milestones, not one commit per plan task. One-commit-per-task produces a long, fragmented log (e.g. 25 commits for a single feature) that the user finds hard to review.

**Why:** User explicitly said the per-task commit history from the audio-trim-editor plan (2026-08-13/14) was "hơi nhiều và phân mảnh" (too many and fragmented) and proposed an alternative phase breakdown instead.

**How to apply:**
- Before starting SDD execution on a plan, propose a phase grouping to the user (e.g. "1. Scaffold Activity, 2. Enable Compose/libs, 3. UI components one-by-one with fake ViewModel data, 4. Repository with temporary/fake business values, 5. Real native/ffmpeg module wired in last") and get their sign-off on both the grouping AND the exact commit message text before executing.
- Commit message style observed as their preference: prefix `Refactor edit audio: <short phase description>` (or equivalent `<feature-name-in-progress>: <phase>` for other features), one line, no body needed for routine phase commits.
- Tests for a phase are written alongside that phase's commit, not as a separate commit.
- This describes a genuine BUILD ORDER preference too, not just commit cosmetics: UI first against fake/hardcoded data, then real repository with temporary values, then real backend (native/ffmpeg) wired in last — matches their own global CLAUDE.md rule "Incremental delivery: bước 1 = UI shell với fake/empty data, bước 2 = wire data thật." When starting a new feature, ask whether they want this literal top-down-with-fakes build order (not just squashed commit messages after the fact) — see [[feedback_auto_build]] for the related auto-build-after-changes preference.
- Still run per-task-equivalent review internally (spec compliance + quality) before folding work into a phase commit — the user's complaint was about commit COUNT/granularity, not about skipping verification.
