---
name: wmusi-device-verify
description: How to render and screenshot WMusi UI on the attached Pixel 9 (API 37) for visual checks against Figma
metadata:
  node_type: memory
  type: reference
  originSessionId: e7439767-dcde-4ea8-b28d-b211a6457f14
  modified: 2026-09-30T03:37:55.245Z
---

adb is NOT on PATH: use `export PATH=$PATH:/home/khapv/Android/Sdk/platform-tools`. Attached device (2026-09-30): Pixel 9, API 37, serial 47231FEAQ001B9.

Visual check pattern (verified 2026-09-30): an androidTest captures `onRoot().captureToImage()` and writes the PNG to the `additionalTestOutputDir` instrumentation arg. After `./gradlew :<module>:connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=<FQCN>`, the PNGs are in `<module>/build/outputs/connected_android_test_additional_output/debugAndroidTest/connected/Pixel 9 - 17/`. Writing to getExternalFilesDir does not work, because the test APK is uninstalled after the run. Example: core/designsystem FoundationsCatalogTest.

Any module with Compose UI tests needs `androidTestImplementation(libs.androidx.espresso.core)` (3.7+). Otherwise every test crashes on API 37 with NoSuchMethodException InputManager.getInstance.

A test whose content runs an infinite animation (spinning disc, animated equalizer) fails with ComposeNotIdleException. Set `composeRule.mainClock.autoAdvance = false` before `setContent`, then `advanceTimeBy(ms)` before capturing. Example: MediaAndListsTest (verified 2026-09-30).

JUnit4 androidTest written as `fun x() = runBlocking { ... }`: if the last expression is not Unit, the method is non-void and the whole class fails with "Failed to instantiate test runner class AndroidJUnit4ClassRunner" (root cause InvalidTestClassError). Use `runBlocking<Unit> { }`. Seen in :audio (was core/player) ExoPlayerEngineTest, 2026-09-30.

Gradle connected tests run on EVERY attached device/emulator. Pin the phone with `export ANDROID_SERIAL=47231FEAQ001B9` (an API 36 emulator was attached too, 2026-09-30).
Perf on device: keep the process top-app (empty activity via ActivityScenarioRule; instrumentation alone sits in cpuset /foreground) and warm the CPU (~200 ms busy loop) before each sample. CORRECTED 2026-09-30: I first blamed the 3-6x swings on cpuset, but another project (com.audioseparation.lyrics.whisper, heavy Whisper tests) was running instrumentation on the SAME Pixel 9 at the same time. Before perf measurement, check `adb shell ps -A | grep '\.test'` and `adb logcat -b events -d | grep am_kill` for other test packages; results taken while they ran are not valid.
Soak tests via Gradle connectedAndroidTest die after ~30 min of no instrumentation output (host-side Gradle/UTP ends → am instrument dies → UiAutomation DeadObjectException in the test; the service kept playing). Suspected UTP no-output timeout, not confirmed. For long runs use `adb shell am instrument -w -e class ... <pkg>.test/<runner>` directly, or emit status output periodically.

Scratchpad (/tmp/claude-1000/...) is WIPED when the session restarts: lost a pre-change snapshot + patch + soak log on 2026-09-30. Keep anything needed later under the repo (e.g. audio/build/…, ignored) or a commit/worktree, never only in scratchpad.
Main-thread root cause tracing that works: wrap the operation in the androidTest with `Debug.startMethodTracingSampling(path, 64MB, 200us)` / `stopMethodTracing()` (PerfSupport.maybeMethodTrace, arg methodTrace=true), pull the .trace, then `trace_processor <file> -q` (download https://get.perfetto.dev/trace_processor) and query `slice` joined with `thread_track`/`thread` where thread.name='main', grouping children by parent_id. Do not trust frame-gap numbers from a traced run: starting/stopping tracing pauses all threads.
UiAutomator on SystemUI media controls: the animated seek bar never goes idle, so every click waits seconds for idle (looked like 1.5–3.9 s app latency). Set `Configurator.getInstance().waitForIdleTimeout = 100`. SystemUI API 36 ids: com.android.systemui:id/actionNext / actionPrev / actionPlayPause (desc "Next track" / "Previous track" / "Pause"/"Play"). Emulator has no screen lock → sleep+wake lands on home, lock screen media cannot be checked there.
Test-runner pitfalls found 2026-09-30 (each cost a rerun):
- `-Pandroid.testInstrumentationRunnerArguments.class=A,B,C` ran ONLY the first class (only A appeared in androidTest-results). Run one Gradle call per class, or use `package=`.
- UTP writes a JUnit `assumeTrue` skip as `<failure>` in the XML and fails the build. Gate manual-only tests with `@ManualRunOnly` + `notAnnotation` (see audio/build.gradle.kts), not `Assume`.
- Emulator AVD name is "Pixel_9(AVD) - 16": results dir paths contain spaces/parens — quote them or use `find … -print0 | xargs -0`.
- Multi-phase tests across a process kill (`ProcessRestartTest`): `./gradlew :audio:installDebugAndroidTest`, then `adb shell am instrument -w -e class …#phase1_save -e restartPhase save com.wife.recommend.music.audio.test/com.wife.recommend.music.audio.HiltTestRunner`, `am force-stop com.wife.recommend.music.audio.test`, then phase2/3 with `-e keepPlaybackState true`. Direct am instrument keeps files in /sdcard/Android/data/<pkg>.test/files/perf (Gradle runs uninstall them).
- `PlaybackController.currentPositionMs()` must be called on Main in tests (MediaController wrong-thread IllegalStateException).

Added 2026-10-01 (UI milestone, each verified on emulator-5554 API 36):
- Every `:app:connectedDebugAndroidTest` run uninstalls the app: data and READ_MEDIA_AUDIO are gone, so the real app opens on onboarding again. To check it after tests: `./gradlew :app:installDebug`, `adb shell pm grant com.wife.recommend.music android.permission.READ_MEDIA_AUDIO`, start MainActivity, tap "Next" (permission already granted → straight to Home).
- `-Pandroid.testInstrumentationRunnerArguments.class=A,B` ran only the first class here; run one class per Gradle call.
- `captureToImage` on a ModalBottomSheet (dialog window) times out after 2 s (ComposeTimeoutException in forceRedraw). Screenshot sheets with `adb exec-out screencap` on the real app instead.
- UI tests of a Route that calls `hiltViewModel()` crash with "ComponentActivity does not implement GeneratedComponent". Either test the pure Screen/Tab composables with sample data (LibraryScreenTest) or use `@HiltAndroidTest` + `createAndroidComposeRule<HiltTestActivity>()` (debug-only activity, app/src/debug).
- A broken audio file for the "can't play" path: random bytes as .mp3 get duration NULL and the library's scan filter hides them. Push a real mp3, `content call --uri content://media --method scan_volume --arg external_primary`, then overwrite it with `adb shell 'head -c <size> /dev/urandom > <path>'`. MediaStore keeps the duration, and playing it fails.
- (2026-10-01) Two same-direction HorizontalPagers nested (shell tabs → Library tabs) chain the drag with no custom NestedScrollConnection: inner pager first, leftover to the outer one. Verified by `WMusiAppTest.when_swiping_from_home_then_library_tabs_come_one_by_one_before_settings_and_back` and adb swipes.
- (2026-10-01) `:app` Hilt UI tests need `testOptions.execution = "ANDROIDX_TEST_ORCHESTRATOR"`, otherwise the second test crashes with "multiple DataStores active for the same file" (each test builds a new singleton graph in the same process).
- (2026-10-01) `dumpsys sensorservice`: count only the block between "N open event connections" and "open direct connections" (`sed -n '/open event connections/,/open direct connections/p'`); a plain grep also matches "Previous Registrations" history lines and gives wrong counts.
- (2026-10-01) WMusiPlaybackService: `stopSelf()` alone never ends it while the app's in-process MediaController (MediaControllerPlaybackController) is bound — release the MediaSession first (`releaseSession()`), then stopSelf. Check with `dumpsys activity services com.wife.recommend.music` (ServiceRecord count) + `dumpsys media_session` + `dumpsys notification --noredact`.
- (2026-10-01) Swipe the app out of Recents on the emulator: `input keyevent KEYCODE_APP_SWITCH`, then `input swipe 540 1300 540 200 300`.
