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
| Library viability | GitHub repo API | `api.github.com/repos/<owner>/<repo>` → stars, `pushed_at`, `archived`, `license.spdx_id` | Old artefacts may live on JCenter/Bintray (dead). Check where the artefact is published, not only the code |

## Not usable without a key (2026-10-01)
- Unsplash (`/napi/*` → "Authorization required"), Pexels (401), Pixabay
  (Cloudflare challenge). Their licences also forbid building a "similar or
  competing service", so bundling them as app presets needs a legal check anyway.
- Play Store ratings, YouTube view counts: no open API. Quote them only if the
  user supplies the numbers.

## Write-up template (repo docs)
| Pick | Source link | Licence | Metric (what, period) | Value | Why chosen / dropped |
|---|---|---|---|---|---|
