---
name: project-jamendo-client-id-pending
description: 2026-10-07 the user will create a Jamendo API client_id later and tell me; then use it for singing tests of languages with no open recordings
metadata:
  type: project
---

Waiting on the user (asked 2026-10-07): a Jamendo developer client_id (free, developer.jamendo.com). When they give it:
API v3 `tracks/?client_id=…&lang=<code>&include=lyrics` → CC songs with lyrics per language (tr, fi, da, ro, hi, pt) for
the singing check (lyrics-speed K7, `lyrics-corpus/sung/build_sung.py`, report `SONGS=sung`).
**Why:** Commons had no usable sung recordings for those languages ([[reference-open-singing-datasets]]).
**How to apply:** take the id via an environment variable only — never write its value to memory, docs or code
(Secrets Policy). Remind the user if the singing check comes up again and it is still missing.
Also approved the same day: CC-NC research singing datasets are OK for these tests.
