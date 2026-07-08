---
name: Prefer shared ViewModel over FragmentResultListener
description: When a fragment is an internal UI component of an activity feature, use activityViewModels() to communicate instead of FragmentResultListener
type: feedback
---

# Prefer shared ViewModel over FragmentResultListener

When a BottomSheetFragment/Dialog is an **internal UI component** of a host activity (same feature), always use `activityViewModels()` to communicate state — never use `setFragmentResult` + `FragmentResultListener`.

## Pattern to use

```kotlin
// In BottomSheetFragment
private val viewModel: HostActivityViewModel by activityViewModels()

binding.btnConfirm.setOnSingleCLickListener {
    viewModel.selectSampleRate(selected) // call directly, type-safe
    dismiss()
}
```

## Why

- Type-safe: no Bundle packing/unpacking, no string keys
- Single source of truth: ViewModel holds all state
- Cleaner: removes REQUEST_KEY, KEY_SELECTED constants, and listener registration/cleanup in Activity
- Data flow is explicit and traceable

## When FragmentResultListener is appropriate

Only when fragments are **truly decoupled** (e.g. different features, different modules) and cannot share a ViewModel.

## Applied in

`AudioConverterActivity` + `SampleRatePickerBottomSheet` + `BitratePickerBottomSheet` (2026-03-13)
