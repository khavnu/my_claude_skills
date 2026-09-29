---
name: project-audio-editor-theming-status
description: "audio_editor \"Generate\" redesign — Trim done per Figma, Copy/Result/sheets waiting on designer; EditorDarkColorScheme applied to all 3 activities"
metadata: 
  node_type: memory
  type: project
  originSessionId: 6cbd5958-fb0d-4789-b5ef-c4357246df40
  modified: 2026-08-27T09:23:31.795Z
---

Branch `update/edit_audio_theme` (as of 2026-08-27). Figma: `xPC3QxMt965PxCNFaZCrEs` ("Generate"), node `86:1235` = "0.1 Trim". **File only contains the Trim frame + one player frame — no designs exist for Copy, Result, or any dialog/sheet. User is discussing with the designer to get those; do not invent styling for them.**

**Done (compiles, user-verified on device):**
- `EditorDarkColorScheme` in `ui/theme/Theme.kt` (charcoal ramp `Charcoal10-50`, `GrayBlue60/70`, `BadgeOrange`, outline roles in `Color.kt`) — passed explicitly at all 3 activities (`Trim/Copy/ResultAudioActivity`); `AppLightColorScheme` still the `MusicEditorTheme` default (legacy `outline=White10`, `outlineVariant=White20` added so shared components keep old look on it).
- PositiveButton (Save) + `ic_play_result`/`ic_pause_result`: gradient → solid primary (`#4E757A`); `PositiveButtonGradientStart/End` consts now unused by the button.
- EditAudioBar badge: pill `RoundedCornerShape(50)`, `tertiary` bg, centered ABOVE icon (`BADGE_BOTTOM_GAP=4dp`).
- Mode cards (EditModeSelector): selected = transparent bg + primary border + `onPrimary` text; unselected = `surfaceContainer` + `outline` border.
- WaveformBarsView disabled bars → `outlineVariant`.
- Icons re-colored per design SVGs (downloaded, exact): `ic_volume_small`/`ic_speed_small` fill `#E8EAEF`, `ic_customize` stroke `#E8EAEF`, trim mode icons `#282C45→#3A3F52` + `audio_editor_icon_disabled #838491→#65687C`; `ic_fade_small` already matched.
- Sheets: `surfaceBright → Charcoal40 #232534` (container of all AppBottomSheet); ResultWaveformBottomSheet text + ResultWaveformPanel playhead `AccentOrange → tertiary`.

**Result screen DONE** (design node `86:1737` "0.3 Save successfully"): PositiveButton back to GRADIENT primary→`PositiveButtonGradientEnd #619298` (user chose "gradient theo design"; affects Save too — matches its node); NegativeButton got optional `containerColor`/`borderColor` params (Result passes surfaceContainerHigh+outline; sheet callers keep translucent defaults); file card bg `Charcoal60 #252737` (new token), 4 new action icons `ic_share/ringtone/alarm/notification_result` in :app (converted from design SVGs; ringtone deliberately diverges from home-menu icon per user); top-bar divider; subtitle split with vertical 1×16 divider.

**Dialogs pass DONE** (template = Speed sheet node `86:1960` in "0.4 Speed" frame): sheets already matched via roles; only real fixes = `AppDivider` default White5→White10, `FormatChip` bg both states = `surfaceContainerHighest`. Slider thumb/track NOT changed (user: "slider không thay đổi gì" — design shows thumb primary+white border 3dp, inactive 15%; revisit if designer insists).

**EditAudioBar**: vertical divider 1×30 White10 added 45dp left of Settings glyph (design "Line 839" x=256 vs glyph x=301) + "Setting" label added under icon (labelMedium/onSurface, top padding 4dp aligns labels).

**Still waiting on designer:**
- Copy screen design (currently theme-only). Figma so far only has: 0.1 Trim, 0.3 Save successfully, 0.4 Speed (+player frame).
- Two 1-role-2-value approximations vs Figma: stepper value box uses `surface #1D202C` (design `#222535` = `surfaceContainerHighest`); ruler text uses `onSurface #65687C` (design `#7C8494` = `onSurfaceVariant`).

**Still deferred from earlier:** `AppBackground` `customBackground` (EditorBackground color/bitmap/uri) and mapping MusicPlayer `AppTheme` → scheme.

**How to apply:** when designer answers, fetch new Figma nodes via figma-reader flow; wget (not curl) for asset SVG downloads.
