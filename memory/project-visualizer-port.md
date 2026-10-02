---
name: project-visualizer-port
description: WMusi Now Playing must reuse the user's AudioVisualizer from the music-editor project, moved into a new :visualizer module
metadata:
  type: project
---

2026-10-01 the user asked: reuse the visualizer from `/home/khapv/Work/music_editor/andorid_music_editor` (package `com.tmedilab.sounditor.music.audio.editor`) in Now Playing, and put it "và những thứ liên quan" in its own module `:visualizer`.

Source files (verified 2026-10-01):
- UI: `feature/nowplaying/components/visualizer/{AudioVisualizer.kt, VisualizerStyle.kt, style/RoundedColumnsStyle.kt}` — `AudioVisualizer(modifier, spectrum: Flow<FloatArray>, isActive)`; colors come from the editor theme (`VisualizerBarTop/Bottom/Inactive`) → make them parameters.
- Data: `playback/visualizer/{PcmTapAudioProcessor.kt, SpectrumAnalyzer.kt, RealFft.kt}` (Media3 AudioProcessor tap → FFT → bands 0..1), `domain/repository/AudioSpectrumRepository.kt`, `data/audio/PlaybackSpectrumRepository.kt`; wired in `playback/service/PlaybackService.kt` via `.setAudioProcessors(arrayOf(tap))`.
- Tests: `app/src/test/.../playback/visualizer/{SpectrumAnalyzerTest, PcmTapAudioProcessorTest, RealFftTest}.kt`.

**How to apply:** planned order (decided under [[autonomy-long-task]]): detail screens → Figma sync → `:visualizer` module (port + tests + tap in `:audio` ExoPlayerEngine) → Now Playing milestone using it. Figma's Bars style = RoundedColumnsStyle (user 2026-10-01: "nó có sẵn kiểu bar rồi, bạn thay đổi màu cho phù hợp, bổ sung thêm Wave và Ring") — recolor it to WMusi tokens; Wave and Ring (4.6.5–4.6.12) are new styles to add in the module, read from Figma to leaf nodes.

2026-10-02 updates (user):
- Split into TWO modules: `:visualizer:engine` (PCM tap, FFT, waveform decode + cache, no Compose; `:audio` depends on it) and `:visualizer:ui` (Compose styles). Plan: `docs/features/visualizer/plan.md`.
- 4th style "Waveform" (SoundCloud-like), VIEW ONLY — "mọi thao tác vẫn dưới ControlBox". Design already in Figma: 4.6.18 `250:6612` (overlay on the bottom of the square cover).
- "Now playing -> Now playing style dialog có update 1 chút, nhớ check khi làm đến": at the Now Playing milestone, re-read the style sheet frames (4.6.12 `164:6810`, 4.6.13 `193:6182`, 4.6.14 `193:6384` and any newer) to leaf nodes before coding — do not reuse the 2026-10-02 reading (it had no Waveform tile yet).
- 2026-10-02: a parallel design session commits docs to WMusi (e.g. 53c7188 "Sing back in v1": Now Playing keeps Listen | Sing tabs + lyric peek again). At Now Playing, read `docs/design/now-playing-style.md` and `docs/design/missing-designs.md` fresh — they change during the day. Exclude such foreign docs commits from SDD review ranges.
- Open items for Now Playing (final review 2026-10-02): M3 — the tap publishes when PCM enters the sink, so bars may lead the audible beat by the AudioTrack buffer (~250–750 ms, unmeasured) + Bluetooth latency: measure on a real phone, timestamp snapshots if visible. L8 — nothing injects WaveformRepository yet, so the Hilt graph for it is unchecked until Now Playing does. L6 — FFT runs with no subscriber (~0.4% core), gate on subscriptionCount if it matters.
