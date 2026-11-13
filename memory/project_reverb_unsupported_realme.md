---
name: project-reverb-unsupported-realme
description: "Reverb on Realme C55 (Android 15) cannot work through audiofx — insert refused, aux created but HAL never starts it; do not retry the aux route (ticket 2109)."
metadata:
  node_type: memory
  type: project
  originSessionId: 043a86db-918e-4a0d-9fdc-1525c32e6db3
  modified: 2026-11-11T07:55:14.221Z
---

Ticket 2109 (2026-11-11), fixed in `aae90d652`: Reverb picker no longer opens when `PresetReverb` cannot be built; reverb enabled only for a non-NONE preset.

Verified on Realme C55 (RMX3710, API 35) with logcat + `dumpsys media.audio_policy` / `media.audio_flinger`:
- Insert `PresetReverb(prio, playerSession)`: AudioFlinger refuses, `status: -38` → `presetReverb == null` → "Unsupported".
- Aux `PresetReverb(prio, 0)` + `ExoPlayer.setAuxEffectInfo`: needs `MODIFY_AUDIO_SETTINGS` (else `no permission for AUDIO_SESSION_OUTPUT_MIX`, status -1). After the permission is ADDED by an update, audioserver keeps denying until a device REBOOT. Then it is created and attached, but the AIDL HAL logs `Auxiliary Preset ReverbV2 skip process in state: IDLE` — never STARTed, no audible reverb. Abandoned.
- The QA's reference app (DDmusic) offers Reverb on the same device with no audible effect either (user listened).
- Effect CPU budget is device-wide and low on this ROM (~100 MIPS): reverb = 47 MIPS; another app's idle EQ/Bass/Virtualizer (`musicplayer.playmusic.audioplayer`) made APM refuse ours (`setEffectEnabled(true) CPU Load limit exceeded`). Check `dumpsys media.audio_policy | grep -A30 "Total Effects CPU"`.

**Why:** a future "make reverb work on device X" request will look like an easy aux-effect fallback; on this device it costs a new permission + a reboot and still produces nothing.

**How to apply:** for a device reporting "Unsupported" reverb, first read `dumpsys media.audio_policy` and the AudioFlinger createEffect status before proposing any engine change. Only when the user asks to keep data (default: uninstall + debug, see [[feedback-debug-builds-on-devices]]): installing over a QC release build keeps data/widgets only with the same key; compare `apksigner verify --min-sdk-version 28 --print-certs` digests first (release f913d4…, debug 5b843f…).
