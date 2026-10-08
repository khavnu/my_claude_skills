# Popularity research — sources that work without an API key

Use for taste-dependent picks (see SKILL.md › Workflow › Brief). Research
informs the choice; it does not replace the Review Gate. Record every number
with its source and date in the repo docs, so the next session can recheck it
in seconds instead of trusting it.

| Need | Source | How (verified 2026-10-01) | Gotchas |
|---|---|---|---|
| Free images, "highest rated" | Wikimedia Commons **Featured pictures** (community-voted) | `commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch=incategory:"Featured_pictures_on_Wikimedia_Commons" <topic>&prop=imageinfo&iiprop=url\|size\|extmetadata&iiextmetadatafilter=LicenseShortName` | Filter `LicenseShortName` to CC0 / Public domain for bundling without attribution. BY / BY-SA need credits (and SA terms). Files of people or buildings may carry other rights: flag them for legal |
| "Most viewed" images | Wikimedia **mediarequests** REST API | `wikimedia.org/api/rest_v1/metrics/mediarequests/per-file/all-referers/all-agents/<url-encoded /wikipedia/commons/x/xy/File.jpg>/monthly/<YYYYMMDD>/<YYYYMMDD>` → sum `items[].requests` | Rate-limited (HTTP 429): one request every ~6 s with a descriptive User-Agent, back off on 429. Some files return 404 (renamed); drop or look up the new name |
| Image thumbnails at a given size | Wikimedia imageinfo `iiurlwidth=<px>` | Gives `thumburl`. Ask for height ≥ target (e.g. 1700 px for a 9:20 phone crop) | Download thumbnails, never the 40k-px originals |
| "Most popular" UI patterns / styles (visualizers, charts, loaders, pickers…) | **GitHub search API**, sorted by stars | `api.github.com/search/repositories?q=<topic>&sort=stars&order=desc&per_page=30` across several phrasings, then group repos by the style they ship | Unauthenticated: 10 searches/min. Stars measure developer interest, not end-user taste: state that in the write-up. Check `pushed_at` and the licence before reusing code |
| App popularity + what the UI looks like (Android) | **Play Store details page** | `urllib` GET `play.google.com/store/apps/details?id=<pkg>&hl=en&gl=US` with a browser User-Agent (verified 2026-10-06). Exact installs: regex `\["[0-9,]+\+",\d+,(\d+)`; rating: `"ratingValue":"([\d.]+)","ratingCount":"(\d+)"`. Screenshots: `play-lh.googleusercontent.com/<id>=w526` URLs → fetch `=h400`, paste into one PIL contact sheet, Read it | WebFetch truncates these pages, so use curl/urllib. Installs measure reach/ASO, not UI taste: conclude from the pattern across several apps |
| "Ceiling": what the best apps do (expressive decisions) | **Apple Design Awards** winners + finalists, by category (Delight and Fun · Interaction · Visuals and Graphics · Innovation · Inclusivity · Social Impact) | `curl -A Mozilla/5.0 https://developer.apple.com/design/awards/` → strip tags; the page names the current year's winners and links to 2025, 2024 (verified 2026-10-06). Look up each winner's store page for screenshots | iOS-centric: borrow the *idea*, not the platform chrome. Few music apps per year, so look at the Interaction and Delight categories for transferable ideas |
| Design-system direction | **Material Design blog** `m3.material.io/blog` | Plain GET works (200, 2026-10-06). Read the latest posts for M3 Expressive patterns | Text only; the component pages render client-side, and WebFetch returns only the title for them |
| Library viability | GitHub repo API | `api.github.com/repos/<owner>/<repo>` → stars, `pushed_at`, `archived`, `license.spdx_id` | Old artefacts may live on JCenter/Bintray (dead). Check where the artefact is published, not only the code |

## Not usable without a key (2026-10-01; inspiration sites rechecked 2026-10-06)
- Dribbble search (HTTP 202 with an empty body, a bot challenge), Behance search (HTTP 429).
- Mobbin: the explore page returns 200, but its images are placeholders and the app names are not in the HTML. Treat it as login-only.
- Google Play "Best of" topic pages: the guessed URL `apps/topic?id=campaign_editorial_bestof<year>_apps` returns 404. Untested alternative: ask the user for the link.
- Unsplash (`/napi/*` → "Authorization required"), Pexels (401), Pixabay
  (Cloudflare challenge). Their licences also forbid building a "similar or
  competing service", so bundling them as app presets needs a legal check anyway.
- YouTube view counts: no open API. Quote them only if the user supplies the numbers.

## Write-up template (repo docs)
| Pick | Source link | Licence | Metric (what, period) | Value | Why chosen / dropped |
|---|---|---|---|---|---|
