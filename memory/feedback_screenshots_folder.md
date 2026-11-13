---
name: feedback-screenshots-folder
description: Screenshots/captures I take go to /home/khapv/Tmp/claude/<project>/<feature>/ — never inside the repo
metadata:
  node_type: memory
  type: feedback
  originSessionId: f8af6503-0c14-4b8d-b9c4-880554cd647d
  modified: 2026-10-15T01:21:26.783Z
---

Any screenshot or capture worth keeping (device evidence, Figma renders, before/after diffs) goes to `/home/khapv/Tmp/claude/<project>/<feature>/`; for this repo `<project>` = `andorid_music_editor`. Create per-project/per-feature subfolders as needed. Pure scratch work (e.g. reading Figma) can stay in the session scratchpad.

**Why:** 2026-10-15 the user saw 137 untracked PNGs under `docs/features/**` in `git status`. After two intermediate attempts (in-repo `/screenshots/` + `.gitignore`, then `../screenshots/`), the user designated `/home/khapv/Tmp/claude` as the place for all my captures, across projects. Existing files moved to `/home/khapv/Tmp/claude/andorid_music_editor/{landscape-support,lib-sync-2026-09-28,video-tools}/`.

**How to apply:** never write `.png` into the repo and never edit `.gitignore` for captures; after a capture session `git status --porcelain --untracked-files=all | grep png` must be empty. Related: [[reference-device-shot-helpers]].
