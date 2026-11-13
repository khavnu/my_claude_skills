---
name: feedback-connected-test-multi-device
description: "connectedAndroidTest / installDebug act on EVERY connected device and uninstall the app afterwards, so always pin ANDROID_SERIAL; the user keeps comparison phones plugged in"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 87fb5981-5bf1-470a-9072-56ede1d33a2e
  modified: 2026-10-13T07:24:33.992Z
---

On 2026-10-13 the user plugged in a Huawei INE-LX2r (serial K3VDU19124000916) to compare against the app they had already installed there. A `./gradlew :app:connectedDebugAndroidTest` run without a pinned device hit both phones. On the Huawei the install failed (INSTALL_FAILED_VERSION_DOWNGRADE), but Gradle's cleanup still uninstalled `com.tmedilab.sounditor.music.audio.editor`, and the user lost their comparison build. Verified afterwards with `adb -s K3VDU19124000916 shell pm list packages`: no Sounditor left.

**Why:** the Gradle connected tasks treat every adb device as a target and uninstall the app on each of them after running, even on a device where the install failed.
**How to apply:**
- Before any `connected*Test`, `installDebug` or `adb` command, run `adb devices`.
- If more than one device shows up, `export ANDROID_SERIAL=47231FEAQ001B9` (the Pixel 9) in the same shell command, or use `adb -s`.
- Never touch the other phones unless the user asks; they are the user's reference devices.
Related: [[reference-device-rotation-testing]].
