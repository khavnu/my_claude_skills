---
name: ios-qa-tickets-status
description: "Status of the iOS QA ticket list (73 tickets, screenshots image 18-22) mapped onto the Android port, as of 2026-10-01"
metadata:
  node_type: memory
  type: project
  originSessionId: 27ccde43-719f-4759-8157-77c6314d8ec6
  modified: 2026-10-01T06:55:05.971Z
---

On 2026-10-01 the user gave the old iOS QA ticket list. Store/purchase tickets (#93 #104 #107 #109 #111) are excluded. The rest were mapped against the Android code; the top ones were reproduced on the physical Pixel 9.

Fixed and committed on `fixbugs`:
- #96: install day is never moved by a clock set back.
- #11: a blocked reminder channel counts as denied; the prompt opens the channel's own page.
- #42: core-splashscreen on all APIs; the splash is held until the first screen.
- #77: Home hides defaults while loading, and the splash waits for Home's first state.
- #58: an invisible longest-quote bubble reserves the tip height (done in HomeHeader; the user wanted QuoteBubble untouched).
- #87: SUPERSEDED 2026-10-07 by Android ticket #16 (user decision): fl oz labels AND the custom-cup field now take two decimals (`FL_OZ_LABEL_DECIMALS` in `domain/model/Volume.kt`); cups stay whole ml, so e.g. 8.26 saves as 244 ml and reads 8.25 (off ≤ 0.01, accepted). Was: one decimal, exact round-trip.

Deferred by the user:
- #72: clock set back hides later days in History. Keep as is "until requested"; option 2, extending History to the latest day that has data, was explained.
- #101: RTL; see [[rtl-deferred]].
- #20/#88: late or lost alarms. The "lost" part was fixed on 2026-10-02 (649db13); "late": exact alarms + Watercat banner built 2026-10-02 (Realme still windows them). See [[reminder-alarm-lateness-deferred]].
- #100: Arabic digits; not tested (needs the Arabic layout added to the user's Gboard).

Still open, never discussed in detail: #33 (records list not lazy, one Lottie per row), #70 (goal 507 fl oz is about the 15000 cap), #65 (grammar, e.g. "1 times / day"), #80 (fl oz rows vs total: 58% of days are off by up to 0.4 fl oz; recommended making the total the sum of the rounded rows), #44 (tiny custom cups give 0; recommended a minimum cup size), #5, #112, plus the device-only checks (tablet, font size).

**Why:** a later session will be asked to "continue the QA list"; re-mapping 68 tickets cost three agents and a device session.
**How to apply:** start from this list; verify any claim in code before acting (agent mappings over-estimated twice: M2, M9).
