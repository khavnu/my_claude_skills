# Orchestra on Android projects

## Worktrees
- `local.properties` (sdk.dir) is untracked: copy it into every new worktree, or Gradle sync fails. Same for signing keys, `google-services.json` or other ignored files the build needs — list them in the board's `copy into new worktrees`.
- Each worktree has its own `build/` and `.gradle/` dirs: several GB per worktree. Check free disk before a wave.
- Opening a worktree in Android Studio is optional; the CLI builds with `./gradlew` (Windows: `gradlew.bat`).

## Build load
- Gradle daemons are shared across worktrees with the same Gradle/JDK, but each concurrent build holds its own daemon and RAM (`org.gradle.jvmargs`). With several workers building at once the PC can swap: lower `max_parallel` or tell workers to build only the modules they touch while iterating (`:feature:x:assembleDebug`, `:feature:x:testDebugUnitTest`) and the full build only before requesting review.
- Main's post-merge check is the full build + unit tests the project's `CLAUDE.md` prescribes.

## Devices
- `connectedAndroidTest` uninstalls the app under test: two sessions on one phone wipe each other's runs and data.
- Main assigns each device to at most one task (board `devices`, task file `device`). A worker always sets `ANDROID_SERIAL=<its serial>`; without an assigned device it runs no instrumented tests and asks main for one (`question`).
- Every device command goes through that device's lock: `flock /tmp/<project>-<device>.lock env ANDROID_SERIAL=<serial> …`. Main never runs `connectedAndroidTest` on a device a worker holds; if it must test there, it uses `am instrument` against the already-installed APKs, inside the lock.
- Workers force-stop the app after each run and say in their log when they release a device.

## Shared groundwork main usually does itself
- version catalog (`libs.versions.toml`) and convention plugins
- new modules other tasks depend on (`settings.gradle.kts` includes) — use the `new-module` skill
- navigation keys / routes and DI bindings shared between features
- design-system tokens and shared composables

Feature tasks can then use the `new-feature` skill inside their own module.
