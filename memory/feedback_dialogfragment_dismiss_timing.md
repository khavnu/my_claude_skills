---
name: DialogFragment dismiss timing with repeatOnLifecycle
description: Dismissing a DialogFragment in onStart (or via repeatOnLifecycle STARTED) is too early — mDialog gets recreated by onCreateView after dismiss
type: feedback
---

**Rule:** Never dismiss a `DialogFragment` in `onStart()` or inside a Flow collector that fires during `onStart()` (e.g., `collectWhenStarted` / `repeatOnLifecycle(STARTED)`). Always dismiss in `onResume()` or later.

**Why:** `repeatOnLifecycle(STARTED)` with `Dispatchers.Main.immediate` fires synchronously during `ComponentActivity.onStart()`, BEFORE `mFragments.dispatchStart()`. At that point, `DialogFragment.mDialog` is null. Calling `dismissAllowingStateLoss()` sets `mDismissed = true`, but `onCreateView()` (called during `dispatchStart()`) recreates `mDialog`, and `onResume()` shows it anyway — so the dismiss has no visible effect.

**How to apply:**
- If a stale `DialogFragment` must be dismissed after process restart or permission revocation, do it in `onResume()` (after `super.onResume()`)
- The safe dismiss window is: after `super.onResume()` has returned (all fragments have completed their own `onResume()`)
- Pattern used in `AudioConvertActivity`:
  ```kotlin
  override fun onResume() {
      super.onResume()
      if (!hasReadMediaPermission()) {
          viewModel.cancelConvert()
          dismissConvertingDialog()  // safe here — mDialog is already shown
      } else if (viewModel.uiState.value.conversionState == null) {
          dismissConvertingDialog()
      }
  }
  ```
