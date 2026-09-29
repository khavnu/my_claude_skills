---
name: project-audio-trim-module-no-buildlogic
description: "On branch update/audio_editor (and any branch forked from before build-logic existed), there is no :build-logic convention-plugin module — new Gradle modules must be wired manually."
metadata: 
  node_type: memory
  type: project
  originSessionId: 63051cfc-1237-41ac-8e16-237e84974539
  modified: 2026-08-24T06:31:20.268Z
---

**UPDATE 2026-08-24:** the standalone `:audio_trim` module (and its siblings `:common`/`:copy`/`:ffmpeg`) no longer exist — all four were merged into a single `:audio_editor` module on `refactor/audio_editor_modular` (domain/data/di/ui at top level, `feature/trim`/`feature/copy` sub-packages, `com.ffmpeg.wrapper` kept as-is). The manual hand-wiring approach described below (no convention plugins) is what the merged `audio_editor/build.gradle.kts` still uses — that part of this memory remains accurate.

The root project CLAUDE.md describes `:build-logic:convention` plugins (`AndroidFeatureConventionPlugin`, `AndroidLibraryComposeConventionPlugin`, `AndroidHiltConventionPlugin`, etc.) as the required way to configure new modules. That infrastructure does **not exist** on `update/audio_editor` (branched from `4bc2c9071`, before `:build-logic` was introduced upstream) — there is no `build-logic/` directory at all on this branch.

**Why:** the CLAUDE.md reflects a newer branch's state (likely `master`/`refactor/audio_editor`), not this older fork point.

**How to apply:** on this branch, new modules must be wired manually, mirroring `:video`/`:core_module` (plain `com.android.library` + `org.jetbrains.kotlin.android` + `org.jetbrains.kotlin.kapt` + `com.google.dagger.hilt.android`, manual `dependencies {}` block using `libs.` version-catalog accessors — no convention-plugin `id()` shortcuts). Example: the `:audio_trim` module (extracted from `feature/audio_editor` inside `:app`) was built this way. Before assuming convention plugins are available on any branch, check `find . -maxdepth 1 -iname '*build-logic*'` first — don't trust CLAUDE.md's module-setup instructions blindly across branches.

See also [[project_audio_editor_port]] (if it exists) for the broader verbatim-port effort this module extraction was part of.
