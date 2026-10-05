---
name: project-karaoke
description: WMusi Sing/Karaoke — contract-first with fakes; API doc received, Sing-on-fakes milestone next
metadata:
  type: project
---

2026-10-02: Sing integrates the user's lib `/home/khapv/AndroidStudioProjects/AudioSeparation` (stem split batch + stream, lyrics embedded/LRCLIB/whisper + wav2vec2 align, BatchStemPlayer + StreamStemPlayer). Approach agreed with the user: domain Repositories + scenario-driven fakes now, swap in the lib later ("lib xong chỉ cần gắn vào"). Survey: `docs/features/karaoke/lib-survey.md`; draft contract: `docs/features/karaoke/contract.md` (5 open questions to the user).

**Why:** the lib is still being built; UI and flow should not wait for it.

**How to apply:** the public API doc arrived (`AudioSeparation/audio_stem_split/public_api.md`) and `contract.md` is reconciled, with an API-gap table A–I for the lib author. The user then said "nếu đã đủ để tạo fake data rồi thì cứ làm với fake data trước" and "Làm lần lượt". So the next milestone after Now Playing is **Sing on fakes**: domain interfaces + `:sing:fake` + contract tests, the Listen|Sing tab, and screens 5.1–5.5. Pick defaults for the 10 product questions and log them. `:sing:engine` waits for the lib to close A–I. Now Playing ships Sing hidden behind `isSingAvailable` (ruling N1) until then.

**Update 2026-10-03:** Sing on fakes is DONE and on main (4c27f70). Plan, rulings S1–S8 and the decision log are in `docs/features/sing/`. The checklist for the real engine is the ":sing:engine checklist" section in `docs/features/karaoke/contract.md`. Next milestone: `:sing:engine` against the lib. Step 1 is splitting `SingViewModel` into SingHandOver + SongEndedCountdown (plan, deferred section). The debug scenario picker is removed together with `:sing:fake` (P14).

**:sing:engine scope (user, 2026-10-05):**
- Composite build: `includeBuild("../AudioSeparation")`.
- Models are bundled in the APK. No Play Asset Delivery and no download.
- Separation: STREAM 2-stem QUANTIZE only (38 MB) to start.
- Lyrics: embedded (`lyrics:core`) + LRCLIB online (`lyrics:online`) only. No whisper or wav2vec2 yet.
- 4/5-stem, recognition and alignment come later.
