---
name: project-jamendo-client-id-pending
description: Jamendo client_id RECEIVED 2026-10-09, stored in ~/.config/jamendo_client_id (600) -- read it from there, never print or copy its value
metadata:
  type: project
---

2026-10-09: the user gave the client_id (and the secret, which is NOT needed and was NOT stored -- advised them to rotate it).
It lives in `~/.config/jamendo_client_id` (chmod 600). Earlier plan:
API v3 `tracks/?client_id=…&lang=<code>&include=lyrics` → CC songs with lyrics per language (tr, fi, da, ro, hi, pt) for
the singing check (lyrics-speed K7, `lyrics-corpus/sung/build_sung.py`, report `SONGS=sung`).
**Why:** Commons had no usable sung recordings for those languages ([[reference-open-singing-datasets]]).
**How to apply:** read it from that file at run time only — never write its value to memory, docs or code
(Secrets Policy). Remind the user if the singing check comes up again and it is still missing.
Also approved the same day: CC-NC research singing datasets are OK for these tests.

License stance agreed 2026-10-09: API terms are free for NON-commercial use and forbid caching for offline use (gray for an
internal test corpus) → default to CC BY / CC BY-SA tracks only; nothing from Jamendo goes into the app.
