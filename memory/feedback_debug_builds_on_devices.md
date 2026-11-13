---
name: feedback-debug-builds-on-devices
description: Device checks use debug builds; uninstall ANY installed version (release, other signature, freshly installed by someone) without asking; update tests only when the user asks.
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3eb82f20-c3e8-4cda-8e47-e6cee19550cd
  modified: 2026-11-03T09:50:18.569Z
---

While working, verify on devices with the DEBUG build (`./gradlew :app:installDebug`). If the device holds a release (or other-signature / old) build, `adb uninstall com.amapps.media.music` first — allowed, no need to ask. Do not run `assembleRelease` unless the user asks for a release build.

Applies to any version on any test device, including one that someone else installed minutes ago (2026-11-06 I held back on the Pixel 9 for that reason; the user said not to). Upgrade tests (install over an old version to keep data) happen only when the user asks for one.

**Why:** user, 2026-11-06: "Khi làm việc bạn được phép gỡ bản release hoặc bất kì version nào trong máy, không cần hỏi lại tôi. Khi nào cần test update tôi sẽ báo bạn". Earlier, 2026-11-03 (landscape side-panel fixes on the Huawei): release builds cost minutes each round and were only used to avoid an uninstall; the user prefers fast debug iterations and accepts losing the device's app data.

**How to apply:** after an uninstall expect the first-run flow again (media permission, UMP consent, default language). This supersedes the "install -r a release to keep data" approach noted in [[reference-huawei-notch-device-test]]; release builds stay the rule only for perf/R8 checks when the user asks.

Broken again 2026-11-11 (ticket 2111, Z Flip 3 holding QA's 2.91.03 release): I started `assembleRelease` + `install -r -d` "to keep QA's data", and the same day on the Realme to keep 12 widgets. User stopped it: "bạn được quyền build debug, gỡ các bản trước đó; khi nào tôi yêu cầu mới cần build release, update". The QA data / widget placements on a device are NOT a reason to pick release — uninstall and install debug. My memory [[project-reverb-unsupported-realme]] suggesting a same-key install-over to keep data is only for when the user asks for it.
