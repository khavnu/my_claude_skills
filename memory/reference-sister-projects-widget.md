---
name: reference-sister-projects-widget
description: Where the user's other apps keep widget-pin device workarounds (not music_editor)
metadata:
  type: reference
---

Widget pin (`requestPinAppWidget`) device workarounds live in **/home/khapv/Work/music_player/green_ba_music_player** `feature/widgets/chooser/WidgetChooserActivity.kt` + `PinWidgetBroadcastReceiver.kt` — NOT in /home/khapv/Work/music_editor (no widget code on any branch, verified 2026-10-07 with grep + `git log --all -S requestPinAppWidget`). Other pin users: calculator (`ui/widget/FragmentWidget.kt`), weather (`feature/customize/widgets/WidgetsFragment.kt`).

Known workarounds there: success callback as a BroadcastReceiver (ticket 1429); `successCallback = null` on Huawei INE-LX2r / CLT-L29 (ticket 526) — applied to WMusi `AppWidgetManagerWidgetPinner.dropsSuccessCallback` (commit 92ca3a9). Related: [[wmusi-widget-emulator]].
