---
name: feedback-verbatim-port-verify-dont-report-unverified
description: "When user asks \"did you port this file verbatim from the reference project\", actually diff it — never report \"yes, copied as-is\" without checking"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: db872121-f45f-4014-bb28-c1aa999cd18d
  modified: 2026-08-25T07:21:21.870Z
---

User caught a case where `ExoPreviewPlayer.kt` (audio_editor) was reported as ported verbatim from the reference project (`~/Work/music_editor/andorid_music_editor`, release/1.0) when a real diff showed it was actually a simplified re-derivation missing: `GainLimiterAudioProcessor` volume boost matching FFmpeg's limiter, `seekableMediaSourceFactory` for header-less rendered MP3 seek/duration, `ConnectedDeviceManager` auto-pause on headphone disconnect, `SegmentPositionTracker` state machine (vs a raw polling loop), seek debounce, repeat/loop mode, and detailed error logging.

**Why:** [[project_audio_editor_reference_repo]] establishes the norm for this project — port the exact diff from the reference repo, don't re-derive — specifically because the reference repo has already fixed bugs this app would otherwise reintroduce. Confirming "yes it's verbatim" without diffing defeats the entire purpose of that norm: the user then trusts unverified code as verified, and bugs the reference already fixed (e.g. header-less MP3 seek) silently ship here too.

**How to apply:** whenever asked "did you copy X exactly from the reference/sample project" (or asked to verify any porting claim), always `diff`/read both files side by side before answering — never answer from memory or from a prior session's unverified claim. If a deviation from verbatim is intentional and documented (e.g. this project's `PreviewPlayer` interface has a doc comment explicitly pruning `setEqualizerBands`/`clearEqualizer` since Equalizer isn't built yet), say so and distinguish it from undocumented/accidental simplification — don't let one legitimate documented exception cover for the rest of an unverified claim.
