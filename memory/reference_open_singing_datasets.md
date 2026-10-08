---
name: reference-open-singing-datasets
description: Where open-licensed SUNG audio with lyrics was found per language (2026-10-07 survey) and where it was not — saves re-searching Commons
metadata:
  type: reference
---

Found (all in `lyrics-corpus/sung/`, built by `sung/build_sung.py`, report `FleursCtcReport` with `SONGS=sung`):
- **de, en** — JamendoLyrics MultiLang (HF `jamendolyrics/jamendolyrics`; mp3 under `subsets/<lang>/mp3/`, the top-level
  `mp3/` entries are symlinks; line CSVs `annotations/lines/`). CC BY*, many NC/ND. Also fr, es.
- **ru** — MulJam v2.0 (github zhuole1025/LyricWhiz, `MulJam_v2.0/preconstructed-split/{test,valid}.meta`: id,file,lang,start,end,text);
  audio `https://prod-1.storage.jamendo.com/?trackid=<id>&format=mp31` (no key). Hard songs, weak line times. Also de/en/fr/es/it.
- **ja** — PJS corpus (CC BY-SA 4.0, Google Drive id 1hPHwOkSe2Vnq6hXrhVtzNskJjVMQmvN_), a cappella; lyrics are kana only —
  kanji text = Voice Actress Corpus `balance_sentences.txt` (voice-statistics GitHub); first sung time from `.lab` (HTK 100 ns).
- **ru (clean)** — GTSinger (HF `GTSinger/GTSinger`, CC BY-NC-SA, a cappella; `processed/Russian/metadata.json` has words +
  durations; take `Control_Group`). TRAP: several "songs" are the same lyrics under typo'd/numbered titles — dedupe pairs
  before counting wrong accepts (2026-10-07 report showed 2 fake ones). Also de/ja/fr/es/it/ko/zh/en.
- **tr** — MTG turkish-makam-acapella-sections-dataset (GitHub, CC BY-NC-ND), word TextGrids; classical şarkı, Silero VAD
  misses most of it — not representative of pop.
- **pt** — Commons "Portuguese-language songs" (1930s Carmen Miranda etc.) + Hino Nacional choirs; lyrics via LRCLIB `/api/get/<id>`.

NOT found (Commons, 2026-10-07): **da** ("Songs of Denmark" = Erik Damskier PIANO), **ro**, **fi** (Maamme 1929 choirs: VAD
hears no singing), **tr** (Takabeg = band; İstiklal 2013 = orchestra+choir mush), **hi** (one NCERT song). Next options if
needed: Jamendo API `lang` filter + lyrics (needs a client_id the user must create), or CC-NC research corpora.
CC-NC approved by the user 2026-10-07. Vocadito / SingStyle111 have none of our languages.
Commons API rate-limits bursts (429) — `sung/commons.py` backs off. Whisper is NOT a singing detector for old/choir
recordings. Related: [[project-lyrics-device-run-recipe]].
