---
name: project-ffmpeg-cpp-source-kept
description: "audio_editor's cpp/ source (ffmpeg_jni.c, license_verify.c, CMakeLists.txt) is intentionally kept even though Gradle never builds it — do not propose deleting it"
metadata: 
  node_type: memory
  type: project
  originSessionId: db872121-f45f-4014-bb28-c1aa999cd18d
  modified: 2026-08-24T06:30:22.019Z
---

`audio_editor/src/main/cpp/` (`CMakeLists.txt`, `ffmpeg_jni.c`, `license_verify.c`) ships alongside the prebuilt `.so` files in `jniLibs/` but is never compiled by Gradle — no `externalNativeBuild`/CMake hook exists anywhere in the build (confirmed via repo-wide grep during the 2026-08-24 `:audio_editor` module-merge refactor, see [[project_ffmpeg_module_setup]]).

User explicitly decided to keep it (2026-08-24) after I flagged the tradeoff.

**Why:** it's the only human-readable source of what the shipped `.so` actually does — including `license_verify.c`'s embedded certificate/signature check (compares the app's signing cert against a hardcoded expected value). If the app's signing key is ever rotated without knowing this check exists, audio processing could silently fail (license check failing) with no source left to diagnose why. `CMakeLists.txt` points at an external `output/` dir from the original reference project the `.so`s were ported from — this is the build recipe's documentation, not live build input.

**How to apply:** never propose removing `cpp/` as "dead code" or "redundant now that we have the .so" — it is redundant for *building*, not for *understanding/auditing* the native layer. Any change to it (or its removal) is a security/behavior question, not a refactor — treat it the same way a final code reviewer already flagged it during the module-merge: out of scope for mechanical refactors, needs its own explicit decision.
