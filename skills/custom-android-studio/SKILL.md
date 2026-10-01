---
name: custom-android-studio
description: Use when Android Studio itself misbehaves on this Linux machine (not the app under development) — terminal typing lag or missing characters with a Vietnamese IME (Unikey/ibus-bamboo), IDE input/rendering issues on Wayland, or re-applying local Studio customizations after installing a new Studio version.
---

# Custom Android Studio (Linux, Wayland)

Local Studio installs: `~/App/android-studio` (Narwhal 4, 2025.1.4) and `~/App/android-studio-newest` (2026.1.x).
Per-version config: `~/.config/Google/AndroidStudio<ver>/` · logs: `~/.cache/Google/AndroidStudio<ver>/log/idea.log`.
Find `<ver>` from `dataDirectoryName` in `<install>/product-info.json`.

## Fix: Vietnamese IME lag in the terminal (Wayland)

**Symptom:** in the Studio terminal, typed letters do not appear until Space commits the word (e.g. type `h` → nothing shows for a moment). Narwhal 4 is fine, 2026.1+ is not.

**Cause:** the session is Wayland (`$XDG_SESSION_TYPE`), and Studio ships `-Dawt.toolkit.name=auto`, so the newer JBR picks the native Wayland toolkit (`sun.awt.wl.WLToolkit`). The IME preedit text is not rendered there. Older Studio (Narwhal) ran on XWayland.

**Not the cause:** terminal engine. Switching Reworked → Classic did not help; Reworked + XToolkit types smoothly (verified 2026-09-30).

**Fix:**
```bash
VER=AndroidStudio2026.1.4   # adjust to the installed version
f=~/.config/Google/$VER/studio64.vmoptions
cp "$f" "$f.bak" 2>/dev/null
grep -q 'awt.toolkit.name=XToolkit' "$f" 2>/dev/null || echo '-Dawt.toolkit.name=XToolkit' >> "$f"
```
The user vmoptions file is appended after the bundled one, and for `-D` options the last one wins.
Fully quit Studio (`File → Exit`) and reopen.

**Verify:**
```bash
grep 'toolkit:' ~/.cache/Google/$VER/log/idea.log | tail -1
# expect: toolkit: sun.awt.X11.XToolkit   (WLToolkit = fix not applied)
```
Then ask the user to type Vietnamese in the terminal — only they can confirm the feel.

**Revert:** `mv "$f.bak" "$f"` (or delete the line) and restart.

## Gotchas
- Claude Code often runs INSIDE the Studio terminal → restarting Studio kills the session. Make every file change first, then tell the user to restart, and verify in the next session.
- A new Studio version = a new config dir → the vmoptions line must be added again.
- Check the IME actually in use with `ibus engine` (the user's machine reports `Unikey` even when they say ibus-bamboo).
- Terminal engine is the `terminalEngine` option (`REWORKED` | `CLASSIC`) in `options/terminal.xml`. 2026.1 hides Classic in Settings, but the option is still read. Edit only while Studio is closed, because Studio may write its in-memory value back on exit.
