---
name: project-androidtest-no-backtick-names
description: androidTest methods cannot use backtick names with spaces (minSdk 23 dex < 040): compileDebugAndroidTestKotlin passes, dexBuilderDebugAndroidTest fails; use camelCase there.
metadata:
  type: project
---

Verified 2026-11-12 (ticket 2118): a Compose UI test named `` `when the queue is shuffled ...` `` compiled fine with `./gradlew :app:compileDebugAndroidTestKotlin`, then `connectedDebugAndroidTest` failed in `:app:dexBuilderDebugAndroidTest` with "Space characters in SimpleName ... are not allowed prior to DEX version 040" (minSdk 23). Unit tests (JVM) are fine with backticks.

**Why:** the global rule asks for backtick test names; it only holds for `src/test`. The compile step every change runs does not dex, so the failure shows only when the device test runs.

**How to apply:** in `app/src/androidTest` name tests in camelCase like the existing ones (`centeredEmptyStateStaysBelowTheSearchBarOnAShortScreen`). Plain `createComposeRule()` tests that draw `SongRow`/covers need `CompositionLocalProvider(LocalInspectionMode provides true)` (no Hilt component: `rememberCoverImageLoader` crashes otherwise; see `CropImageScreenTest`).
