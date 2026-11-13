---
name: project_fingerprint_lyrics_license_blocked
description: "Fingerprint ID (AcoustID/MusicBrainz) and full-text lyrics search (Genius/Musixmatch) both blocked on commercial license — verified 2026-10-12, user said stop for now"
metadata:
  node_type: memory
  type: project
  originSessionId: f3d6b4db-0990-4904-8a79-1c1052bbf9b2
  modified: 2026-10-12T01:36:39.022Z
---

2026-10-12: user asked to evaluate Google Search, then fingerprint ID, as extra online lyrics sources. Verified license
terms directly from each service (not from training memory, since pricing/terms change) before proposing anything. Result:
user said "thế thôi" (stop) once the commercial-license gap was clear. Full detail: `docs/features/lyrics-speed/ideas.md`
ý tưởng 5 và 6.

**Why this matters for next time:** none of these four services have a free commercial tier for this use case. Don't
re-propose any of them without first telling the user that gap exists.

- **Chromaprint** (the fingerprinting library itself, runs on-device): LGPL-2.1, free for commercial use — this ONE piece
  is fine. `fpcalc` binary (official v1.5.1, no sudo needed) sits at `/home/khapv/tools/chromaprint/fpcalc`, reusable.
- **AcoustID API** (fingerprint → song ID): free tier is **non-commercial only** (acoustid.org/webservice, their own
  wording). Commercial needs a quote from acoustid.biz — not obtained.
- **MusicBrainz API** (song ID → title/artist): same split, free for **non-commercial only**; commercial needs a separate
  arrangement (musicbrainz.org/doc/MusicBrainz_API). Also rate-limited to 1 req/s, IP-banned above that.
- **Genius API**: does not serve full lyrics text at all (only metadata + a URL to the song page); their own ToS forbids
  scraping that page. No legal path to full lyrics via Genius, commercial or not.
- **Musixmatch API**: free tier caps at 30% of a song's lyrics (not enough to align against); full lyrics require a paid
  commercial license, price not public, not requested.

Google Search as a source was also evaluated and rejected on the same call: no official lyrics API, would mean scraping a
second site (Genius/Musixmatch/etc.) whose own ToS forbids it, plus Google's own ToS against automated SERP scraping.

Not shipped: `onlineProvider` in `DefaultLyricsRepository.kt` is still LRCLIB alone ([[reference_open_singing_datasets]] is
the unrelated test-corpus note; this one is about the app's live lyrics source).
