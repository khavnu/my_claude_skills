---
name: edge-cases
description: Use when planning a new feature, screen, platform integration (system API, permission, sensor, other app) or behaviour change in a mobile/Android app, before implementation code is written — and when a plan's edge-case section was written from the happy path or has no way to verify each case.
---

# Edge Cases

## Overview

Happy-path plans miss whole **categories**, not single cases: the API-level band where a platform call behaves differently, the font-scale or RTL layout, the process death mid-flow. A fixed list of categories, each forced into a row of the plan, catches what intuition skips.

## When to Use

- Plan stage of any feature or behaviour change — before code, when fixing is cheap
- Bugfix: only the categories the fix touches
- Not for: pure refactors with no behaviour change, string/copy edits

## Before the table

1. Read the project's CLAUDE.md and memory for known device/OEM quirks, test devices, time/date rules.
2. List every platform API, permission and external app the feature touches. For each, look up (docs or source, not memory) its minimum API level, the API levels where behaviour changes, and its availability states (not installed, no hardware, not enrolled, disabled by policy). Cannot look it up now → mark those facts `unverified` in the plan and make the lookup the plan's first step, before any code.

## The table (REQUIRED in the plan, one row per category, in this order)

| # | Category | Case for THIS feature | Expected behaviour | Verify |
|---|---|---|---|---|

**Verify** = a named unit test, a device + API level + steps, a Preview, or `N/A — <one-sentence reason>`.

| # | Category | Ask |
|---|---|---|
| 1 | Device capability | Each API from step 2: below min API, at each behaviour-change band, missing hardware/system app/account, work profile or secondary user, OEM quirks |
| 2 | Permissions | Denied, permanently denied, revoked in system Settings while the app lives, granted later (catch up or not?), partial grant |
| 3 | Lifecycle | Process death mid-flow, rotation/config change, background → foreground, double tap / re-entry, entry from notification, widget, deep link |
| 4 | Time | Midnight rollover, time-zone/DST change, manual clock change, long deep sleep |
| 5 | Data | Empty, one, huge (OOM at 10×?), boundary values, special characters, data from an older app version, backup restored on another device |
| 6 | Failure | DB/file write fails, no or slow network, disk full, the other app or screen missing (`ActivityNotFoundException`) |
| 7 | Background | Doze / standby buckets, OEM background killers, app killed, reboot, app update |
| 8 | Presentation | Long translations, plurals, font scale 200 %, RTL, dark mode, small screen / landscape / foldable, TalkBack labels |
| 9 | Cross-feature | Which other features this changes or reads; other platforms (iOS) unaffected; settings that interact |

## Rules

- No case in a category → `N/A — reason`. Rows 1 and 2 are never N/A when the feature calls a platform API or permission.
- Expected behaviour that is a product choice → move it to an **Open questions** list and ask the user once, before coding.
- Each Verify that is a test becomes a task in the plan's test list. Device rows name the API levels at the band edges (minSdk, the change level), not only the device at hand.
- At the end of implementation, walk the table again: every row verified, or explicitly deferred with the user's agreement.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Generic row ("handle errors gracefully") | Name the concrete trigger for this feature |
| Testing only the API level of the device on the desk | Test both sides of each behaviour-change band |
| Edge cases listed without a Verify column | Every row gets one, even if it is `N/A — reason` |
| Table written after the code | It belongs in the plan the user approves |
