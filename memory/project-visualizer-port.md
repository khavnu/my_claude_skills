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
