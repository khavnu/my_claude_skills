---
name: PptReader HSLF/Escher technical knowledge
description: Key findings for rendering .ppt binary files via Apache POI HSLF on Android — Escher records, coordinate system, color extraction, class hierarchy
type: project
---

## Coordinate System — CRITICAL
- PPT master units: 1 unit = 1/576 inch. Slide width always = 5760 mu (10 inch).
- Slide height: detect via `HSLFSlideShow.getPageSize()` reflection (java.awt.Dimension not on Android). `getHeight()` returns points → multiply by 8 for master units. Fallback: 3240 (16:9).
- 1 point = 8 master units (since 1pt = 1/72 inch, 1 mu = 1/576 inch → 576/72 = 8 mu/pt).
- Slide width = 720pt, slide height = slideH / 8 pt.

**`getAnchor()` via reflection ALWAYS FAILS on Android** — throws `InvocationTargetException` (null message) because HSLF's `getAnchor()` internally uses java.awt classes unavailable on Android. DO NOT rely on it as the primary path. Keep it in code as forward-compat, but the Escher fallback is the REAL primary.

## EscherClientAnchorRecord — CRITICAL FIELD MAPPING for PPT
PPT binary format stores ClientAnchor as **8 bytes = 4 shorts**: top, left, right, bottom in master units.
Apache POI's Excel field names map to PPT coordinates as:
- `getFlag()` → **top** (y1)  ← POI calls this "flag" from Excel; in PPT it is the TOP coordinate
- `getCol1()` → **left** (x1)
- `getDx1()` → **right** (x2)
- `getRow1()` → **bottom** (y2)

**Verified by cross-checking adjacent shapes:** title.row1 (bottom) == subtitle.flag (top) — they are contiguous, proving flag=top, col1=left.

The fields `getDy1()`, `getDx2()`, `getDy2()` etc. correspond to Excel cell-offset bytes that DON'T EXIST in the 8-byte PPT record → they return 0. Using `dx1/dy1/dx2/dy2` gives `height=0` → `posStyle=null` → full-width rendering.

**CORRECT usage for PPT ClientAnchorRecord:**
```kotlin
val y1 = (client.flag.toLong() and 0xFFFF)   // top
val x1 = (client.col1.toLong() and 0xFFFF)   // left
val x2 = (client.dx1.toLong() and 0xFFFF)    // right
val y2 = (client.row1.toLong() and 0xFFFF)   // bottom
```

## EscherChildAnchorRecord — for shapes inside groups
`getDx1()/getDy1()/getDx2()/getDy2()` ARE correct for ChildAnchorRecord (x1, y1, x2, y2 in master units). The group is FLATTENED in rendering — children use slide-absolute coordinates.

## Groups — FLATTEN, never nest
`HSLFGroupShape` children have slide-absolute coordinates from HSLF. Rendering children inside a positioned group div causes double-offset. Always flatten: render each child directly at slide level (same as PptConverter does).

## Escher OPT Record — Fill Color
- Property 0x0181 = `FILL__FILLCOLOR`. Stores color as `0x00BBGGRR` (BGR little-endian), NOT standard RGB.
- To decode: R = `cv and 0xFF`, G = `(cv shr 8) and 0xFF`, B = `(cv shr 16) and 0xFF`.
- `getFillColor()` returns `java.awt.Color` which does NOT exist on Android → `NoClassDefFoundError`. Always read via Escher OPT directly.
- Property 0x01BF = fill flags. `0x00100010` = fFilled=true (shape has fill). `0x00100000` = fFilled=false (transparent).
- Property 0x0183 = `FILL_BACKCOLOR` (gradient back color).

## Class Hierarchy — Critical!
- `HSLFAutoShape extends HSLFTextShape` — in Kotlin `when` blocks, `is HSLFAutoShape` MUST come BEFORE `is HSLFTextShape`, otherwise AutoShapes are caught by the TextShape branch and the AutoShape case is unreachable.

## Background Color (per slide)
Priority order:
1. `slide.background` (HSLFBackground shape) → `getShapeFillColor(slide.background)`
2. `slide.masterSheet?.background` → `getShapeFillColor(masterSheet.background)` ← **this is where template colors live**
3. `slide.colorScheme.backgroundColourRGB` — filter both 0 (black/unset) and 0xFFFFFF (white/default)
4. Master colorScheme fallback

**Key insight:** The orange background in a PPT template is stored in `HSLFSlideMaster.background` (an HSLFBackground shape), NOT in `master.shapes`. `master.shapes` contains transparent placeholder outlines.

## Master Shapes
- `slide.masterSheet?.shapes` = layout placeholders (title area, content area, footer). All have `fFilled=false` (transparent, no fill) EXCEPT decorative shapes like footer bars.
- Master placeholder shapes contain text like "Click to edit the outline text format" — NEVER render master shape text. Render master shapes as fill-only colored divs.
- Only render master shapes that return a non-null fill color from Escher.

## Android Limitations (java.awt missing)
- `java.awt.Color` → NoClassDefFoundError → use Escher OPT property 0x0181 instead
- `java.awt.Dimension` → use reflection: `getPageSize()` → `getHeight()`
- `java.awt.geom.Rectangle2D$Double` → **`slide.getShapes()` throws `NoClassDefFoundError: java.awt.geom.Rectangle2D` for slides containing HSLFTable** (table constructor uses java.awt internally). Catch at the `slide.shapes.iterator()` level and fall back to `renderShapesViaEscher()`.
- `getSpContainer()` is protected → access via reflection walking the class hierarchy

## renderShapesViaEscher — Escher fallback for slides with HSLFTable
When `slide.getShapes()` throws on Android, use this pattern to render shapes directly from the Escher tree:
1. Get `PPDrawing` via reflection: `slide.getPPDrawing()` (protected, walk class hierarchy)
2. Call `ppDrawing.getDgContainer()` (public) → `EscherContainerRecord`
3. Find top-level `SpGrContainer` (id=0xF003) inside DgContainer
4. For each child:
   - `SpContainer` (0xF004): skip if it contains `EscherSpgrRecord` (0xF009, group header); else call `HSLFShapeFactory.createShape(container, slide)` → renders normally
   - Nested `SpGrContainer` (0xF003, table/group): iterate its child `SpContainer`s (0xF004), skip group header, call `createShape()` on each cell → produces `HSLFTextBox`, NOT `HSLFTable` → bypasses java.awt entirely
5. `HSLFShapeFactory.createShape` signature: `createShape(EscherContainerRecord, ShapeContainer)` — pass `slide` as the `ShapeContainer` argument

## CSS Rendering
- Slide container: `position:absolute;top:0;left:0;right:0;bottom:0;overflow:hidden;container-type:size;color:$contrastColor;background-color:$bgColor`
- `contrastColor()`: luminance = 0.299*r + 0.587*g + 0.114*b. If < 128 → white text default, else black.
- Font size: PPT points → `(fontSize / 720.0 * 100).coerceIn(2.5, 9.0)` → cqw/vw. MUST use `Locale.US` in format string.
- `cqw` = container query width (Android 13+ WebView). Emit both `vw` and `cqw` for compatibility.
- Text shape div: `word-break:break-word` to prevent horizontal overflow.
- Do NOT add hardcoded `padding` to text divs — PPT shapes have their own internal margins.

## Per-slide picture deduplication
- `renderedPictureHashes.clear()` must run per-slide (not once per document). Same background image appears on multiple slides — without per-slide reset it only renders on slide 1.

## Locale — Critical!
All CSS `%.2f` format calls MUST use `java.lang.String.format(java.util.Locale.US, ...)`. Kotlin `"%.2f".format()` uses system locale — some locales use comma as decimal separator which breaks CSS.
