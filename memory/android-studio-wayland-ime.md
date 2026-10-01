---
name: android-studio-wayland-ime
description: "Vietnamese IME lag in Android Studio 2026.1+ terminal on Wayland — fixed by forcing XToolkit, not by terminal engine"
metadata:
  node_type: memory
  type: reference
  originSessionId: 7c60e0f4-4bb0-49c1-af21-d0dd1aa8ff11
  modified: 2026-09-30T06:28:28.701Z
---

Symptom (2026-09-30): in Android Studio 2026.1.4 (`~/App/android-studio-newest`) terminal, Unikey (ibus) input shows nothing until Space commits the word. Narwhal 4 (`~/App/android-studio`) was fine.

Cause: `awt.toolkit.name=auto` on a Wayland session makes the new JBR pick `sun.awt.wl.WLToolkit`; preedit is not rendered in the terminal.
Fix: append `-Dawt.toolkit.name=XToolkit` to `~/.config/Google/AndroidStudio2026.1.4/studio64.vmoptions` (backup `.bak` alongside), restart.
Verify: `grep 'toolkit:' ~/.cache/Google/AndroidStudio2026.1.4/log/idea.log | tail -1` → `sun.awt.X11.XToolkit`.

Terminal engine (Classic vs Reworked, `terminalEngine` option in `options/terminal.xml`) was NOT the cause; user chose Reworked — confirmed smooth typing with Reworked + XToolkit (2026-09-30). On a Studio upgrade the config dir changes → re-apply the vmoptions line.
Note: user said ibus-bamboo but `ibus engine` reports `Unikey`.
