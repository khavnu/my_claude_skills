---
name: compose-sheet-window-pitfalls
description: Use when building, reviewing or debugging Android Compose bottom sheets, side panels or dialogs (ModalBottomSheet, Dialog windows) — especially for landscape, edge-to-edge with a hidden navigation bar, notch devices, Android 9/10 (API 28-29), Huawei/EMUI, or long translations. Symptoms - navigation bar stuck visible after a sheet closes, sheet's last row under the navigation bar, notch strip not dimmed by the scrim, sheet shown twice or dialog hidden behind a sheet after rotation, keyboard covering a sheet's buttons, close X covering icons or AdChoices, button labels cut without an ellipsis.
---

# Compose sheet / dialog window pitfalls

## Overview

A `ModalBottomSheet`, a Compose `Dialog` and a dialog-based side panel are **separate windows**. Each window gets its own insets, cutout mode, system-UI flags and z-order, and those behave differently by API level and OEM. Most bugs come from assuming the Activity's window rules carry over, or from a fix that is right on API 30+ and wrong below it.

**Core rule: never trust one source for a window-level value.** Verify on the device class where it differs (API 28 notch phone + API 36 emulator), from a fresh launch, in both landscape rotations.

## Review checklist — walk every line for each sheet/dialog design

1. **Anything overlaid on content** (close X, badge)? → it covers icons / AdChoices / titles; drop it or reserve room.
2. **Text field in a short window** (landscape ~360dp, keyboard leaves ~140–190dp)? → content scrolls + buttons brought above the keyboard.
3. **Content taller than ~360dp** (sheet or dialog, landscape)? → scrolls; fixed-max boxes yield first (`weight(1f, fill = false)`).
4. **Hidden navigation bar** + any dialog window, API < 30? → re-hide must reach the WindowManager (`requestLayout` on a flag change).
5. **Navigation-bar spacer** from resources? → `maxOf(resource, navigationBarsIgnoringVisibility)` in the sheet window.
6. **Dialog windows on API 28–29 notch devices**? → cutout mode SHORT_EDGES or the notch strip is undimmed.
7. **Two windows from one screen** (dialog from a sheet, host layer + fallback layer)? → composition order = z-order; `onPostCreate` precedes composition.
8. **What recreates the Activity while a sheet is up**: rotation, theme/language, **an interstitial that forces portrait** → test each.
9. **Labels in long locales** in the narrower panel → Ellipsis, ≤10dp button side padding.

## Quick reference — any API

| Symptom | Root cause | Fix | Verify |
|---|---|---|---|
| Sheet's last row / OK button under the system navigation bar (portrait) | Spacer height from resources `navigation_bar_height` gated on `config_showNavigationBar`; that config is **false on API 36 with 3-button navigation** | `maxOf(resourcePx, WindowInsets.navigationBarsIgnoringVisibility.getBottom(density))` read **inside the sheet window**. Keep the resource value: below API 30 the inset is 0 while the app hides the bar | Log both values in the sheet; uiautomator bounds of the last row vs bar top (screen height − bar height) |
| Close X overlaid on a side panel covers header icons, AdChoices of a native ad, or a long title; taps on the icon close the sheet | X drawn at TopEnd over content that does not reserve room | Drop the X (scrim tap + Back close it, like a bottom sheet), or give it a reserved strip. Never overlay. Sheets that draw their own close otherwise show two X | Tap the upper half of the header's end icon; zoom the ad's top-end corner |
| Keyboard hides a sheet's Cancel/OK (landscape) | Panel ~360dp high, keyboard leaves ~140–190dp; content column does not scroll | `verticalScroll` on the content + `BringIntoViewRequester` on the button row, triggered on `WindowInsets.ime` bottom change, **after one frame** (`withFrameNanos {}`) so the shrunk panel is measured first. Read the inset **inside the effect** (`snapshotFlow { ime.getBottom(density) }.filter { it > 0 }.collectLatest { … }`), never in composition: from API 30 it changes every frame of the keyboard animation and would recompose the whole sheet | Open the sheet in landscape, keyboard up: field + buttons visible; tap OK works |
| A box with a fixed max height pushes the buttons to 0dp | `heightIn(max = 300.dp)` sibling + buttons in a short panel | `Modifier.weight(1f, fill = false)` on the box so it yields before the buttons | Landscape with long content: buttons fully drawn |
| Dialog content cut at the bottom in landscape | Window ~360–370dp high; content not scrollable | `verticalScroll` around dialog content (fitting dialogs do not move). `AndroidView` inside: compare bounds before/after in portrait | uiautomator bounds identical in portrait; scroll reaches the last button in landscape |
| A tip Dialog opened from a sheet ends up **behind** the sheet after rotation / theme change | Windows stack in **composition order**; on recreate both are created in one pass, the later one is on top | Put the child dialog **inside the sheet's content** lambda: its window can only be created after the sheet's, so it is on top by construction (placing it after the sheet in source order works too but is a rule kept only by a comment — moving the block breaks it silently) | Open tip, rotate both ways: tip stays on top (`uiautomator dump` sees the tip's window); close the tip: the sheet remains |
| A sheet raised outside the screen shows **twice** after rotation (landscape: side panel + a bottom sheet) | Fallback View/ComposeView layer installed in `onPostCreate` when "the Compose layer has not composed" — `onPostCreate` **always** runs before the first composition | Remove the fallback layer if every screen is Compose (sheet state in a ViewModel reappears with the content); otherwise decide at `setContent` time, not by a flag set during composition | Open the sheet, rotate: exactly one window (`dumpsys window windows`) |
| A strip beside a sheet's panel closes it on tap; wrong corners rounded; background starts under the status bar | A sheet written before the shared side panel still draws **its own** narrower panel (+ a full-size tap-to-close box) **inside** the side panel | Let the shared panel be the panel: the sheet content fills it (`fillMaxSize`); branch with the **same rule** the sheet wrapper uses (not `Configuration.orientation`, which differs in multi-window) | uiautomator: content bounds start at the panel's edge (`design_bottom_sheet` left = list left) |
| A sheet shows ANOTHER item's data once (menu of B shows A), right the second time | Sheet ViewModel scoped with `rememberViewModelStoreOwner(savedStateRegistryOwner = LocalSavedStateRegistryOwner.current)`: all sheet VMs of one class share the default key in the destination's registry; after the destination saved/restored (navigate away and back), the next VM gets the restored handle, and restored state wins over the new default args | Give each sheet owner its own in-memory `SavedStateRegistryOwner` (LifecycleRegistry at CREATED, `performAttach()` + `performRestore(null)`); args come only from defaultArgs | Log `SavedStateHandle` args in the VM `init` vs the args passed: VM is new but args are old. Instrumented test: parent registry restored with `{BundlableSavedStateRegistry.key: {SavedStateHandlesProvider: {DefaultKey:<VM>: {id: 1}}}}`, open sheet with id 2 |
| Last rows of a sheet cut or missing at a large font scale, but a UI test "last row inside the panel" passes | A non-scrolling `Column` with a max height squeezes its last children (down to 0 px) instead of pushing them out. `DeviceConfigurationOverride.FontScale` does not reach a sheet/dialog window either, because its ComposeView provides `LocalDensity` again | Scroll the body under a pinned title. Test the text's height against `TextLayoutResult.multiParagraph.height` (via `SemanticsActions.GetTextLayoutResult`), with `settings put system font_scale 2.0` on the device | WMusi Sing sheets on SM-M205G, 2026-11-11: font 2.0, old code: hint 0 px of 331 px; new code: full height after scroll |
| Dialog stretched/distorted in landscape | Background drawable scales with the 480dp landscape width | Cap that dialog's landscape width to its portrait width (`0.9 × smallestScreenWidthDp`) | Element bounds equal in portrait; aspect kept in landscape |

## Android 9–10 (API 28–29) and Huawei/EMUI

| Symptom | Root cause | Fix / note | Verify |
|---|---|---|---|
| Hidden navigation bar **stays visible** after a sheet/side panel closes (often only the first sheet after launch + rotate; then alternates stuck / fine) | A sheet window with focus clears `SYSTEM_UI_FLAG_HIDE_NAVIGATION`; re-hiding sets the flag on the view but **no traversal pushes it to the WindowManager** | After `WindowInsetsControllerCompat.hide(navigationBars())`, if `SDK < 30` and `decorView.systemUiVisibility` changed, call `decorView.requestLayout()`. Only on a real change, or a global-layout listener that re-hides loops forever | `dumpsys window windows`: NavigationBar `isVisible=false`, Activity window `mSystemUiVisibility=0x..12` (view and WM agree); `dumpsys gfxinfo` frames stable at idle |
| Notch strip stays lit beside the scrim in landscape | Compose gives dialog windows cutout mode `ALWAYS` (3, API 30); API 28–29 do not know it → DEFAULT → window kept out of the notch (frame starts at x = cutout) | In the dialog's `SideEffect`, on API 28–29 set `layoutInDisplayCutoutMode = SHORT_EDGES`; the panel must pad `safeDrawing` End | `dumpsys window windows`: dialog `mFrame` starts at 0; pixel of the strip = scrim colour. API 28 `toString` prints mode 1 (SHORT_EDGES) as `always` and Compose's 3 as `unknown(3)`, so `always` there means the fix applied. Side effect (WMusi, SM-M205G 2026-11-11): UI tests on a portrait notch device now get the 24 dp status-bar inset in the panel too, as on API 30+. A layout budget test that passed only because that inset was missing can then scroll a few px |
| Bottom sheet floats mid-screen with a gap (and no scrim) below it after the keyboard hides; e.g. keyboard up in landscape, rotate to portrait (Samsung M20 API 28, ~4/5 runs; not on the API 27 emulator) | The sheet window is created while the old window's IME is up (Compose ime = 1003px); the IME then hides and the window's root insets update, but **no onApplyWindowInsets is dispatched**, so Compose's `WindowInsets.ime` stays stale and M3 `ModalBottomSheet`'s internal `imePadding()` (wraps scrim + sheet, cannot be removed) keeps lifting it. Not a stuck compat animation: the InsetsListener had `running=false` | Below API 30, inside the sheet window: `OnGlobalLayoutListener` comparing `ViewCompat.getRootWindowInsets(view).getInsets(ime()).bottom` with the last value; on change `view.post { view.requestApplyInsets() }` (a request made **inside** the layout callback did not reach Compose — must be posted), plus one request at start | Log Compose `WindowInsets.ime.getBottom` vs root compat ime in the sheet window; uiautomator `design_bottom_sheet` bottom = screen bottom over 5 runs (was 4/5 stuck). Not reproduced in WMusi (M3 1.4, SM-M205G, 0/5 runs on 2026-11-11: New playlist sheet, keyboard up in landscape side panel, rotate to portrait, keyboard hidden). Repro on the target app before adding the fix |
| `navigationBarsIgnoringVisibility` is 0 | Not supported below API 30: returns the current (hidden) inset | Keep a resource fallback (see the spacer row) | Log in the sheet window on API 28 |
| Landscape is only **~360dp** high (19.5:9, 780×360dp) | Taller phones than Pixel (411dp) | Size sheets/dialogs for 360dp; anything near the limit must scroll | Test on the 360dp device, not only Pixel |
| Navigation bar sits on the **right** in landscape, drawn over a side panel | EMUI landscape layout | Panel pads `safeDrawing` Vertical + End; the panel background under the bar is fine | Screenshot: no content under the bar's buttons |
| The notch may be on the **left or right** | Rotation 90 vs 270 | Test both. On the panel side the content area shrinks by the cutout (~30dp); long titles wrap more | Screenshots in rotation 1 and 3 |
| Unexpected recreate with a sheet open | An interstitial forces portrait, then the app returns to landscape | Treat "ad closed" as a rotation in tests (duplicate-sheet and z-order rows) | Open a sheet behind an interstitial path, close the ad |
| Status bar visible in landscape over the panel | EMUI keeps it | Panel pads `safeDrawing` top | Header not under the clock |

## Long translations (de, bg, ru, el, hu, sr, ml…)

- Single-line texts and button labels: `maxLines = 1` + `TextOverflow.Ellipsis`, never `Clip` (Clip cuts mid-letter with no sign). Messages and titles: allow 2 lines, then ellipsis. Placeholders inside a field: 1 line + ellipsis.
- Wide button padding (30dp per side) leaves ~84dp of text in a 144dp button on a 360dp phone and ~60dp in a side panel: use ~10dp sides for two-button rows.
- Titles near an overlaid icon: constrain the text (`weight(1f, fill = false)`) and pad the end by the icon size instead of letting it run under.
- A side panel (360dp) is **narrower** than a portrait sheet (411dp): re-check every row in landscape.

## Test recipe

1. Devices: an **API 28 notch phone** (Huawei) + an **API 36 emulator** (3-button navigation). One build type per pass (debug is fine; switching signature means uninstall).
2. Each sheet/dialog: portrait, landscape rotation 1, landscape rotation 3, keyboard up, a long locale, font scale 1.15.
3. Window bugs: start from a **fresh launch** (force-stop → start → rotate), repeat 3×; some bugs show on the first sheet only.
4. Portrait must not change: build the base commit (`git stash`), capture, compare pixel diff of the sheet area (mask animated regions) or uiautomator bounds.
5. Huawei adb drops: set USB to MTP; push a script and run it **on the device** (`adb shell sh /sdcard/x.sh`, results to `/sdcard`, then `adb pull`). `user_rotation` resets on app launch — set it after each `am start`. uiautomator bounds clip at the landscape navigation bar: tap by screenshot coordinates near the right edge. `uiautomator dump` can fail silently and leave a stale file: delete it first, retry.

## Common mistakes

- Replacing the resource navigation-bar height with insets only (breaks API < 30) — take the max.
- Blaming the re-hide delay/timer for a stuck navigation bar on API < 30 — the flags never reached the WindowManager; compare view flags with `dumpsys window windows`.
- Hard-coding the notch margin — read `safeDrawing`/`displayCutout` insets.
- Trusting dp estimates for keyboard space — measure on the device (Huawei left ~140dp, worse than estimated).
- Calling a bug fixed after one open/close — repeat from a fresh launch.

## Keeping this skill current

When a new sheet/dialog/side-panel window pitfall is found and verified on a device, add a row to the matching table (symptom, root cause, fix, how it was verified) in the same session. Remove or correct a row that turns out wrong.
