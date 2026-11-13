---
name: project-no-read-media-video
description: "Decision (2026-10-16) — the app does NOT request READ_MEDIA_VIDEO; it accepts not seeing videos it does not own, so name-clash checks can miss them"
metadata:
  node_type: memory
  type: project
  originSessionId: f8af6503-0c14-4b8d-b9c4-880554cd647d
  modified: 2026-10-16T01:11:32.483Z
---

The user decided on 2026-10-16 that the app will not request `READ_MEDIA_VIDEO`. Not being able to read videos the app does not own is accepted.

**What this means in practice (seen on the Pixel 9, 2026-10-15):**
- Files in `Movies/MusicEditor/...` whose `owner_package_name` is NULL (left by a previous install, or after `connectedAndroidTest` uninstalls the app) or that belong to another app do not appear in MediaStore queries.
- So `VideoOutputDataSource.exists()` and `firstFreeName()` treat those names as free. MediaStore then resolves the clash itself with `"Name (1).mp4"`, with a space. Nothing is overwritten.
- Videos this install saved are still readable without the permission: the Saved screen shows name, duration, resolution, size and thumbnail, and playback works.
- The manifest declares only `READ_MEDIA_AUDIO`. `pm grant … READ_MEDIA_VIDEO` silently does nothing.

**Why:** the user does not want to declare another media permission to Play.

**How to apply:** do not propose `READ_MEDIA_VIDEO` to fix name suffixes or to read others' videos. If a ticket reports "Name (1).mp4" instead of "Name(1).mp4", this is the cause, and it is accepted. The note lives in the KDoc of `VideoOutputDataSource.exists`.
