---
name: subagent-stall-check
description: A background implementer can stall for hours without writing a file — check git status after ~1 h and re-dispatch with bounded commands
metadata:
  node_type: memory
  type: feedback
  originSessionId: e7439767-dcde-4ea8-b28d-b211a6457f14
  modified: 2026-10-02T17:13:09.576Z
---

On 2026-10-02 the Now Playing Task 3 implementer ran for about 3.5 h without writing a single file. Its last progress note was "Confirming foundation 1.12.1 cache entry". It also never picked up a SendMessage status ping, which only arrives at the agent's next tool round. Stopping it and re-dispatching with the same brief finished the task in about 20 min.

**Why:** a hung tool call, such as a cache or dependency investigation or a blocking gradle/adb command, gives no signal. Waiting on the completion notification alone burned hours of the lane.

**How to apply:**
- On every heartbeat or idle check, compare each running implementer's age with `git status --short` in its tree. If more than ~1 h has passed and nothing was written, TaskStop it and re-dispatch.
- Put these lines in every implementer prompt:
  - "write code early";
  - "bound every shell command with `timeout`";
  - "no open-ended dependency/cache investigations".
- Same lane: device safety lives in [[wmusi-device-verify]]. Every device-touching gradle/adb command needs `ANDROID_SERIAL`, not only connected tests.
