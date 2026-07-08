---
name: reuse_layout_binding
description: Reuse the same XML layout and ViewBinding across multiple fragments/dialogs that have the same structure, setting dynamic content (title, etc.) programmatically instead of duplicating layouts.
type: feedback
---

When two dialogs/fragments share the same visual structure, do NOT create separate layout files for each.

Instead:
- Use a single shared XML layout with generic IDs (e.g., `tv_title`, `rv_options`)
- Both classes inflate the same Binding (e.g., `DialogFragmentSampleRatePickerBinding`)
- Set dynamic content (title, list data) programmatically in `onViewCreated`

Example: `BitratePickerBottomSheet` and `SampleRatePickerBottomSheet` both use `DialogFragmentSampleRatePickerBinding`. They only differ in `binding.tvTitle.setText(...)` and the data passed to the adapter.

This applies to any dialogs, bottom sheets, or fragments with the same layout structure.
