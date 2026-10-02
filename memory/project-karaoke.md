---
name: project-karaoke
description: WMusi Sing/Karaoke — contract-first with fakes; waiting for the user's public API document of the AudioSeparation lib
metadata:
  type: project
---

2026-10-02: Sing integrates the user's lib `/home/khapv/AndroidStudioProjects/AudioSeparation` (stem split batch + stream, lyrics embedded/LRCLIB/whisper + wav2vec2 align, BatchStemPlayer + StreamStemPlayer). Approach agreed with the user: domain Repositories + scenario-driven fakes now, swap in the lib later ("lib xong chỉ cần gắn vào"). Survey: `docs/features/karaoke/lib-survey.md`; draft contract: `docs/features/karaoke/contract.md` (5 open questions to the user).

**Why:** the lib is still being built; UI and flow should not wait for it.

**How to apply:** the public API doc arrived (`AudioSeparation/audio_stem_split/public_api.md`) and `contract.md` is reconciled, with an API-gap table A–I for the lib author. The user then said "nếu đã đủ để tạo fake data rồi thì cứ làm với fake data trước" and "Làm lần lượt". So the next milestone after Now Playing is **Sing on fakes**: domain interfaces + `:sing:fake` + contract tests, the Listen|Sing tab, and screens 5.1–5.5. Pick defaults for the 10 product questions and log them. `:sing:engine` waits for the lib to close A–I. Now Playing ships Sing hidden behind `isSingAvailable` (ruling N1) until then.
