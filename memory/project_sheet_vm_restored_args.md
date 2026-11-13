---
name: project_sheet_vm_restored_args
description: Sheet VMs (rememberViewModelStoreOwner) must not use the destination's SavedStateRegistry — a restored handle overrides new args (ticket 2059)
metadata:
  type: project
---

Fixed 2026-11-05 (ticket 2059, uncommitted at time of writing): `rememberSheetViewModelStoreOwner` (`feature/base/compose/SheetViewModelScope.kt`) now gives each sheet its own in-memory `SheetSavedStateRegistryOwner`. Before, it passed the Nav entry's `LocalSavedStateRegistryOwner`: every sheet VM of one class shares the default key `DefaultKey:<class>`, and after a Player round trip the next sheet of that class got the EARLIER sheet's args once (`SavedStateHandle.createHandle`: restored state is the single source, default args ignored — lifecycle 2.11 `SavedStateHandle.android.kt:209`).

**Why:** cost a long session to find; symptom looks like a stale VM but the VM is new (log showed `VM new … songId=390` while the sheet passed 389).
**How to apply:** suspect this when a sheet shows another item's data exactly once. Regression test: `SheetViewModelScopeTest.argsOfAnEarlierSheetSavedByTheDestinationDoNotReplaceNewArgs` (androidTest; restored bundle must be wrapped in `androidx.lifecycle.BundlableSavedStateRegistry.key`, or the test passes trivially). Repro script: menu A → play another song → Player → back → menu B. See [[reference_emulator_screenshot_capture]].
