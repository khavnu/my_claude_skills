---
name: wmusi-strings-xml-pitfalls
description: mergeDebugResources NPE with no line number = unescaped ' or " in strings.xml (often from a Python heredoc eating backslashes)
metadata:
  type: reference
---

Verified 2026-10-06 (Folders v2 step 2):
- `:app:mergeDebugResources` failing with "Failed to compile values resource file ... merged.dir/values/values.xml. Cause: java.lang.NullPointerException" gives no line. Get the real error with
  `$ANDROID_HOME/build-tools/37.0.0/aapt2 compile app/src/main/res/values/strings.xml -o /tmp/x/` → prints "unescaped apostrophe in string" with the line.
- Cause there: strings added via a Python `'''...'''` literal turned `\'` into `'` and `\"` into `"`. Use `’` (the file's convention, e.g. "Couldn’t") and write `\"` through a raw string / Edit tool.
- adb-driven checks: a Long snackbar (Undo) lasts ~10 s; tapping Undo in a separate tool call usually misses it. Do show → tap Undo in ONE bash call.
