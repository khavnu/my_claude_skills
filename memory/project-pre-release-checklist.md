---
name: project-pre-release-checklist
description: "Work deferred until WMusi goes to Play — baseline/startup profile, PAD for Whisper models, first DB migration; check this before any release build"
metadata:
  node_type: memory
  type: project
  originSessionId: 872f5bd0-58be-4d8c-a959-90ead984cee5
  modified: 2026-10-20T09:18:55.712Z
---

Things agreed to do only before the first Play release (none started as of 2026-10-20):

1. **Baseline Profile + Startup Profile** (added 2026-10-20, user agreed). WMusi has no `baselineprofile` module and no `baseline-prof.txt` (grep `*.kts`/`*.toml` for `baselineprofile|profileinstaller|macrobenchmark` → no hits); AGP 9.4.1 supports everything. Today a release only carries library profiles (Compose), so app code (Now Playing, lyrics, lists) JITs on first run — the N8 release number 3.41 % in [[wmusi-measure-jank-on-release]] is without an app profile. Journeys to cover: startup → Home → Now Playing → Sing, fling the song list. After adding it, re-measure N8 to see the delta.
2. **PAD for the recognition models** — today bundled in the APK; details in [[project-karaoke]] (2026-10-19 update).
3. **First Room migration** — no Migration classes until release; see [[project-no-db-migrations]].

**Why:** these are deliberately deferred, not forgotten; the user doesn't want them re-proposed mid-feature.
**How to apply:** when the user mentions release / Play / internal testing track, bring up this list. Play internal app sharing does NOT apply profiles — use the internal testing track to check them.
4. **Vietnamese aligner training data (added 2026-10-23)**: `w2v2_int8pc.ort` (dragonSwing, Apache-2.0) was trained on VLSP 2020, listed as research-only → legal review or swap the model before a commercial release. Details: docs/features/lyrics-recognition/model-licenses.md.
