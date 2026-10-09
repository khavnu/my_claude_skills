---
name: release-resource-shrinking
description: R8 resource shrinking (on since eb5d9bd) strips resources looked up by name; keep.xml in androidApp/src/main/res/raw; how to verify a release APK
metadata:
  type: project
---

QA #29 (2026-10-09): release 1.0.3 had no reminder sounds. `isShrinkResources = true` (commit eb5d9bd) removed all `res/raw/*.wav` because code reaches them only by name: `AndroidSoundPreview` (`getIdentifier(key, "raw")`) and `ReminderChannels.soundUriString` (`android.resource://<pkg>/raw/<key>`). Debug builds are not shrunk, so dev never sees it.

Fix: `androidApp/src/main/res/raw/keep.xml` with `tools:keep="@raw/classic,@raw/drop_echo,@raw/water_drop,@raw/water_flow"`.

**Why:** any new resource looked up by string (new sound, getIdentifier, android.resource URI) vanishes from release silently.
**How to apply:** after adding such a resource, add it to keep.xml, then verify in 10 s:
- `./gradlew :androidApp:assembleRelease` → `grep -iE "<name>" androidApp/build/outputs/mapping/release/resources.txt` must say "reachable from keep xml file", not "is not reachable".
- `aapt2 dump resources <apk> | grep raw/` (`~/Android/Sdk/build-tools/37.0.0/aapt2`); paths inside the APK are obfuscated (`res/JK.wav`), so do not grep for `res/raw`.
- Release APK is signed with "DrinkWater2 Test" ≠ debug key: installing it on the Pixel 9 needs uninstall of the debug build (back up with run-as tar first; run-as does not work on the release build). Playback check: `dumpsys audio | grep "u/pid:.*/<pid> " | grep state:started`.
- The Pixel 9's notification stream volume is 0 (user setting) and `cmd media_session volume --set` did not change it: reminder notification sound cannot be heard/measured there without the user raising it.
