---
name: wmusi-min-api-pitfalls
description: minSdk 24 but no API 24/25 test device — run lint per module for NewApi; desugaring is on since 2026-10-19
metadata:
  type: feedback
---

Found 2026-10-19 by `./gradlew :app:lintDebug :data:lintDebug :audio:lintDebug …` (not by any test): minSdk is 24, but the emulators are API 27 (Pixel_2) and 36 (Pixel_9), so API 24/25-only crashes never surface. Lint found: java.time used with no core library desugaring (AppModule → crash at app start on Android 7), `Bitmap.Config.HARDWARE` read unguarded, `as? RecoverableSecurityException` (API 29 class) outside the version check on the Android ≤ 9 delete path. Fixed in 55b2df59.

**Why:** `:app:lintDebug` does NOT check library modules' code (checkDependencies is off) — the data-module NewApi only showed with `:data:lintDebug`.
**How to apply:** after adding framework/java.* API calls, run lintDebug on every changed module and treat NewApi as a blocker. Desugaring (desugar_jdk_libs 2.1.5) now covers java.time/java.util streams app-wide, but framework classes/fields (Bitmap.Config.HARDWARE, RecoverableSecurityException…) still need `Build.VERSION.SDK_INT` guards — including `as?`/`is` checks.
