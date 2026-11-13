---
name: project-online-theme-images
description: "Theme \"download images online\" feature — DEFERRED by the user 2026-10-19; Pexels chosen but its API guidelines forbid wallpaper-like use, open questions recorded"
metadata:
  node_type: memory
  type: project
  originSessionId: a262b834-fb52-4207-97e1-f64b8d6db760
  modified: 2026-10-19T00:52:00.246Z
---

2026-10-16/19: user wants Theme › Image to also fetch images online and picked **Pexels**, then said "chúng ta sẽ làm chức năng này sau" (deferred, 2026-10-19). Nothing built.

Verified 2026-10-16 (WebFetch https://www.pexels.com/api/documentation/ and /license/):
- API guidelines: "You may not copy or replicate core functionality of Pexels (including making Pexels content available as a wallpaper app)" → access termination. License: no redistribution "on other stock photo or wallpaper platforms". A browse-and-apply theme background is close to that.
- Limits 200 req/h, 20,000 req/month by default; attribution "Photo by X on Pexels" + link expected; `src.portrait` = 800×1200.

**Why:** the restriction can get the key revoked after release; the user has not chosen between (1) emailing Pexels for approval first (my recommendation), (2) building anyway with mitigations, (3) CC0/PD sources (Commons, Openverse CC0, NASA).
**How to apply:** when the feature resumes, ask those two open questions first — which option, and whether a server/proxy exists to hold the API key (else the key ships in the APK and the 20k/month quota can be abused). Bundled preset images are separate and verified PD/CC0 (docs/design/theme.md).
