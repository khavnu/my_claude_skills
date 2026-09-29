---
name: project-karaoke-idea-explored
description: "Karaoke feature explored 2026-09-03 — not committed; ASR rejected for Vietnamese sung vocals, alignment/tap-to-sync preferred"
metadata: 
  node_type: memory
  type: project
  originSessionId: e0e87c8a-7800-4c48-8018-92b52653531d
  modified: 2026-09-03T02:20:38.566Z
---

Explored on 2026-09-03 as an idea only — user closed with "chỉ trao đổi thôi, việc của chúng ta vẫn
là separate và player". Do NOT start building this; it is not on the roadmap. Recorded because the
conclusions took real reasoning and would otherwise be re-derived.

Scope discussed: beat + scrolling lyrics only. **No mic recording** — user ruled that out, which
removes the AAudio/Oboe monitoring-latency problem entirely.

**Karaoke needs alignment, not ASR.** Transcription (audio → text) and forced alignment (known text
+ audio → timestamps) are different problems with very different difficulty. Karaoke has the lyrics
problem solved the moment the user supplies text.

**Why ASR is the wrong tool here specifically for Vietnamese:** Vietnamese is tonal and tone is
phonemic (ma/má/mà/mả/mã/mạ are distinct words), but **singing replaces the tone contour with the
melody** — the primary discriminative feature is gone from the signal, not merely degraded. Listeners
compensate from context and familiarity; ASR cannot. Whisper is already notably weaker on Vietnamese
than English even on clean speech, and on-device tiers (tiny/base) are weaker still. The user's
"80-90% accuracy is enough" premise is wrong twice: karaoke needs better than that (90% word accuracy
≈ one wrong word per line, and users read ahead), and 80-90% is not achievable on Vietnamese singing.
Forced alignment is far less affected — it never has to tell `má` from `mà`, only when the syllable
lands.

**ASR does not solve the copyright concern that motivated it.** Lyrics are a separate copyrighted work
from the recording; machine-transcribing them still creates a copy. What actually lowers exposure is
on-device + user's own file + never stored or transmitted — which the project's existing offline-first
architecture already satisfies. Not legal advice; flagged for real counsel if ever built.

**Recommended order if it is ever revived:** (1) user pastes plain lyrics + **tap-to-sync** (zero ML,
days of work, and it generates ground-truth timing data on the project's own separated vocals stems);
(2) forced alignment on the vocals stem to automate the tapping; (3) ASR only ever as a draft to be
edited, never as the source of truth. Note "user pastes lyrics" is NOT the same as ".lrc licensing" —
the user initially conflated them; pasting involves no fee, no API, no shipped database.

Karaoke is also a **batch** use case, not streaming: users loop sections to practise, and every seek
outside the loaded range rebuilds the player. It should use the existing `save()` full-length
assembly, not [[project-streaming-phase2-shipped]]'s on-demand path.
