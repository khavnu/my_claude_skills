---
name: project-ffmpeg-wrapper-kotlin-version-conflict
description: "Superseded — the AAR approach (Kotlin metadata skip + minSdk override) was abandoned in favor of a real :ffmpeg source module. Kept for the diagnostic technique, not the fix."
metadata: 
  node_type: memory
  type: project
  originSessionId: 63051cfc-1237-41ac-8e16-237e84974539
  modified: 2026-08-18T03:00:00.539Z
---

**Superseded by [[project_ffmpeg_module_setup]].** This memory originally covered wiring the reference project's prebuilt `ffmpeg-wrapper.aar` (Kotlin 2.2.0 metadata vs. this app's Kotlin 2.0.21 compiler, needing `-Xskip-metadata-version-check`). That approach was abandoned once the user provided the actual `:ffmpeg` wrapper source project (`/home/khapv/Downloads/android/ffmpeg-wrapper` — JNI bridge Kotlin/C source, no prebuilt AAR) — building `:ffmpeg` from source with our own Kotlin 2.0.21 compiler makes the metadata mismatch a non-issue entirely (no cross-version metadata to skip).

**Why kept:** the diagnostic *technique* is still useful — verifying a Kotlin metadata version mismatch by checking `kotlin.Metadata(mv=[...])` via `javap -v` on extracted `.class` files, then testing empirically with a scratch file before deciding on a fix, rather than guessing.

See [[project_ffmpeg_module_setup]] for the actual working setup and the minSdk decision.
