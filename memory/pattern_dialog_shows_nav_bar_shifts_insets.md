---
name: pattern-dialog-shows-nav-bar-shifts-insets
description: "App hides the nav bar, but every sheet/side panel (dialog window) shows it; in landscape the 3-button bar sits on a side edge, so anything padded by default TopAppBar/navigationBars insets jumps sideways (#477, #446)"
metadata:
  node_type: memory
  type: project
  originSessionId: 4c307939-5ce3-4bb7-9648-f0eb7c5763c4
  modified: 2026-10-28T09:10:18.863Z
---

Verified 2026-10-28 on the Pixel 9 AVD with 3-button nav (`cmd overlay enable-exclusive --category com.android.internal.systemui.navbar.threebutton`; restore with `...navbar.gestural`).

**Symptom:** a button in the screen behind a sheet (Save in `AppTopBar`) moves while the sheet opens or closes, mostly in landscape. #477: QC saw Save "jump" when rotating with a sheet open.

**Cause:** `hideNavigationBars()` hides the bar for the Activity window only. A `ModalBottomSheet`/`SidePanel` is its own dialog window and shows the bar, so the Activity gets nav-bar insets for as long as the sheet is open. `TopAppBarDefaults.windowInsets` includes the horizontal system-bar insets, so the actions moved in by the bar width (~126px on the AVD). Fixed in `AppTopBar` with `.exclude(WindowInsets.navigationBars)` (commit ea2cf7e1), same idea as `safeDrawingWithoutNavBar`.

**Trap that cost time:** I first blamed the 500ms `AdaptiveSheet` rotation delay from #472 (the bare screen does show during it), and the user had to correct me. Before blaming the delay, check if the element changes position: measure its bounds with no sheet, then from a screenshot with the sheet open. uiautomator only dumps the dialog window while it is open.

**Still exposed (not fixed, out of scope on 2026-10-28):** direct `TopAppBar` callers with default insets — `NowPlayingScreen`, `LibrarySelectScreen`, `AddAudioToPlaylistScreen`, `SelectPlaylistAudioScreen`. Inside the sheet itself the bar overlaps content unless the sheet pads for it (#446 `ResultWaveformBottomSheet`). Related: [[pattern-coloros-window-added-mid-rotation]].
