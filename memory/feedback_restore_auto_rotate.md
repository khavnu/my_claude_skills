---
name: feedback-restore-auto-rotate
description: "Never toggle the device's auto-rotate around builds/tests: no lock/unlock per run, no restore afterwards — leave whatever state it is in."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3eb82f20-c3e8-4cda-8e47-e6cee19550cd
  modified: 2026-11-05T08:53:13.901Z
---

Do not switch auto-rotate on and off around a build or a test. If it is enabled, leave it enabled; if it is disabled, leave it disabled. No "lock portrait at the start of every run" step in helper scripts, no "turn it back" step at the end, no report line about it.

**Why:** user, 2026-11-04: "Không cần bật - mở lại, cứ để như bình thường"; again 2026-11-05 (stronger): "đừng thay đổi Auto rotate mỗi lần build và test xong ... nếu bạn Enable rồi thì cứ để như vậy, nếu bật Disable thì cứ để disable — đừng tắt bật lại làm gì". My ad-hoc capture scripts that day ran `cmd window user-rotation lock 0` on every launch and the portrait-guard `set_rotation` writes `accelerometer_rotation 0` on every `launch` / `ad` step.

**How to apply:** touch rotation settings only when a test needs a specific orientation (landscape checks, sensor rotation), and then leave the result as it is. A script that does not test rotation must not lock/unlock it. Corrected 2026-11-05 from "only no restore step" to "no toggling at all". See [[reference-huawei-notch-device-test]] for the rotation commands.
