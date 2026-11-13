---
name: wmusi-measure-jank-on-release
description: Measure Compose jank (gfxinfo) only on a release build — debug numbers are ~3–4× worse and sent N8 through 3 needless optimisation rounds
metadata:
  node_type: memory
  type: feedback
  originSessionId: e7439767-dcde-4ea8-b28d-b211a6457f14
  modified: 2026-10-12T08:01:32.203Z
---

Jank/frame-time targets are measured on a **release** build, never debug.

**Why:** 2026-10-12, Sing N8 on Pixel 9, same code (c355db63): debug 12.1 % janky vs release 3.41 % (static lyrics 0.82 %). Three optimisation directions had been judged against debug numbers. Evidence: `docs/features/sing-engine/evidence/N8-timed-pixel9-dir3.txt` vs `N8-timed-pixel9-release.txt`.

**How to apply:** release has no signingConfig → `./gradlew :app:assembleRelease`, then `zipalign -p 4` + `apksigner sign --ks ~/.android/debug.keystore` (pass `android`, alias `androiddebugkey`) so it installs over the debug build with data kept; `adb shell cmd package compile -m speed-profile -f com.wife.recommend.music` to apply the baseline profile like a Play install; then `dumpsys gfxinfo … reset` / 60 s / `dumpsys gfxinfo`. Build in a temp `git worktree` when an agent is editing the main tree. Device rules: [[wmusi-device-verify]].
