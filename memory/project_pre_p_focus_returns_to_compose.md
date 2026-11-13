---
name: pre-p-focus-returns-to-compose
description: "Below Android 9 a cleared/returned focus goes to the first focusable view (ComposeView -> first text field): search box self-focuses, keyboard won't close; fixed by a focusable content frame in AdsActivity."
metadata:
  type: project
---

Ticket 2106 (2026-11-10, Vivo 1606 API 23): after Play as audio / Floating window the Videos search box got focus by itself and Done / Back could not close the keyboard. Cause: pre-P `View.clearFocus()` and a window regaining focus re-focus the first focusable view; ComposeView forwards that to its first text field. Fix `2351516a0`: in `AdsActivity.setShellContent`, below P, `findViewById<ViewGroup>(android.R.id.content).isFocusableInTouchMode = true` so the frame takes it.

**Why:** it looks like a screen bug (keyboard code in ListHeader looked fine) and never shows on API 28+ devices or emulators.

**How to apply:** a text field that focuses itself / a keyboard that reopens only on Android 6-8 → this mechanism, not the screen. Verify on Vivo 1606: `dumpsys input_method | grep mInputShown` + uiautomator `edt_search focused=`. A floating video window can sit on the IME Done key: move it before tapping.
