---
name: feedback-sweep-same-pattern-screens
description: "For a \"state X missing / broken on screen Y\" ticket, grep every screen with the same pattern and fix them together — fixing only the reported screen got tickets 2080 and 2101 reopened."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 043a86db-918e-4a0d-9fdc-1525c32e6db3
  modified: 2026-11-12T01:40:47.900Z
---

Tickets 2080 (search empty) and 2101 (landscape empty state) were each reopened because the first fixes covered only the screens QA named; the same pattern lived in sibling screens (Home "View all" lists, All directories music/video, video folder detail).

**Why:** QA reports screens one by one; the root is a shared pattern (an empty flag counted before filtering, a portrait-only `padding(top = 120.dp)` empty block). The user asked why the earlier fixes missed it (2026-11-11) and agreed to the sweep.

**How to apply:** before fixing, grep the pattern app-wide and list each hit with handled/missing, e.g.
- landscape empty: `grep -rn "padding(top = 120.dp)" app/src/main/java` and check ~14 lines above for `Landscape|EmptySimpleFitting|SearchEmpty`
- search empty: screens with a search box whose empty flag is `isAllEmpty` / counts before the query
Fix all missing ones in the same ticket and name them in the report. Device paths: video "All directories" is the LAST row of the Videos > Folders list (scroll, let the fling stop before tapping); the system "Alarms" folder is an empty folder on every device.
