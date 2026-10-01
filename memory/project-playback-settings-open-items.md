---
name: project-playback-settings-open-items
description: Playback settings milestone done on emulator; real-device checks (headphones, Bluetooth, listening, shake) deliberately left to the user's manual test
metadata:
  type: project
---

Playback settings milestone (docs/features/playback-settings/checklist.md) is done on the emulator as of 2026-10-01. Left open on purpose, not forgotten: N2 (wired unplug), N3/C3 (Bluetooth resume, 10 connects + 3 during a call), N4/N5 listening (gapless, fade), N7 (shake 10× / walk 5 min) — all need a real Pixel 9.

**Why:** user 2026-10-01: "Bỏ qua phần nghe thử trên máy thật nhé, tôi sẽ manual test sau".

**How to apply:** don't re-propose these as pending work; if the user reports results, record them in the checklist's N table. Shake threshold (2.7 g, 2 jolts / 500 ms) may need tuning after N7. Also still open from earlier: BackgroundSoakTest lacks @ManualRunOnly (shows as one failure in a full :audio run) — mentioned to the user, not fixed. See [[wmusi-device-verify]].
