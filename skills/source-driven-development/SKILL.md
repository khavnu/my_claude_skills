---
name: source-driven-development
description: Use when implementing unfamiliar Android/Jetpack APIs, upgrading library versions, or when correctness depends on a specific version (Compose BOM, Navigation3, Room, CameraX, Media3, Hilt). Grounds every decision in official docs, not training-data memory.
---

# Source-Driven Development (Android)

Confidence is not evidence. Training data contains outdated Jetpack patterns that look correct but break against current library versions. Always verify.

---

## When to Apply

**Apply when:**
- Using an API you haven't used in *this* codebase before
- Compose BOM upgrade — APIs shift between BOM versions
- Navigation3 (new, sparse training data, changes frequently)
- CameraX or Media3 (complex lifecycle contracts)
- Room migration API or new TypeConverter pattern
- WorkManager enqueue/observe patterns
- Hilt `@AssistedInject` / `@AssistedFactory` wiring
- Any `@Experimental` or `@OptIn` API

**Skip when:**
- Pure Kotlin logic (loops, data transforms, sealed classes)
- Renaming or extracting code that already works
- Patterns already used identically elsewhere in *this* codebase (existing code = verified source)

---

## Four-Step Process

### 1. DETECT
Read the actual version from the project before writing a single line.

```bash
grep -E "compose-bom|navigation3|room|hilt|camerax|media3|work" \
  gradle/libs.versions.toml
```

Also check: `build.gradle.kts` for `compileSdk`, `targetSdk`, `minSdk` — some APIs are gated.

Never assume the version from the user's description. Check the file.

### 2. FETCH
Find the official source for that specific version. Priority order:

1. **`developer.android.com`** — Jetpack, Compose, CameraX, WorkManager, Room
2. **`kotlinlang.org`** — Coroutines, Flow, kotlinx.datetime
3. **GitHub release notes** — `androidx/androidx`, library-specific changelogs
4. **Existing code in this codebase** — if the pattern is used elsewhere, follow it

**Never** cite Stack Overflow, Medium, or AI summaries as the basis for an API decision.

If you cannot find official documentation for a specific pattern, say so explicitly:
> "I couldn't find official docs for X. Here's my best understanding based on [source] — verify before shipping."

### 3. IMPLEMENT
- Write code that matches documented patterns exactly
- If the codebase uses an older pattern that conflicts with current docs, **surface the conflict** to the user rather than silently changing it
- For `@OptIn` APIs: state which annotation is required and why

### 4. CITE
When the implementation is non-obvious, include the source inline:

```kotlin
// Navigation3: NavEntry requires both decorators to restore VM + saveable state
// https://developer.android.com/reference/kotlin/androidx/navigation3/...
NavDisplay(
    entryDecorators = listOf(
        rememberSaveableStateHolderNavEntryDecorator(),
        rememberViewModelStoreNavEntryDecorator(),
    ),
    ...
)
```

In explanations to the user, always name the source:
> "Per the Room 2.6 migration guide: …"

---

## Android Version-Sensitivity Hotspots

These APIs change enough between versions that training data is unreliable:

| API | Why it changes |
|---|---|
| Compose `collectAsStateWithLifecycle` | Lifecycle-ktx version dependency |
| Navigation3 `NavDisplay` / `NavEntry` | API still stabilizing |
| `hiltViewModel()` in Compose | Scoping changed across Hilt versions |
| CameraX `ImageAnalysis.Analyzer` | Contract changed in 1.3+ |
| WorkManager `setExpedited` | Requires foreground service on API 31+ |
| Room `AutoMigration` | Added in 2.4, syntax changed in 2.5 |
| `rememberLauncherForActivityResult` | Subtle lifecycle contract |

---

## Quick Check Before Implementing Any New API

```
1. What version is in libs.versions.toml?
2. Is there existing usage of this API in the codebase I can follow?
3. If not — did I fetch official docs for this exact version?
4. Am I using @OptIn? If yes — is the annotation correct for this version?
```

If any answer is "I'm not sure" → fetch before coding.