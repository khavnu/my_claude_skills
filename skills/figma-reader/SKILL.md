---
name: figma-reader
description: Use when given a Figma URL or node to implement as Android/Compose UI — before writing any UI code, to avoid hardcoded colors, wrong typography tokens, or duplicating existing composables.
metadata:
  author: khapv
  version: "2.3"
---

# Figma Reader — Design Token Mapper

Use this skill **before writing any UI code from a Figma link**. The goal: every color, typography, and spacing value from Figma maps to a named token in the project — zero hardcoded hex, zero magic numbers, zero duplicated composables.

---

## Step 1 — Discover project tokens

### 1a. Theme tokens

Locate and read the project's theme files:

```
ui/theme/Color.kt        — named Color constants
ui/theme/Type.kt         — TextStyle definitions per typography scale key
ui/theme/Theme.kt        — colorScheme mapping (which token → which role)
```

If not at these paths, search for `Color.kt`, `Type.kt`, `Theme.kt` (or `Colors.kt`, `Typography.kt`). If still not found, **ask the user** — do not guess.

Build two lookup tables from what you find:

**Color table**
```
Figma token name  →  colorScheme key         (for semantic roles)
Figma token name  →  Color.kt constant name  (for accents/overlays)
```

**Typography table**
```
Figma style name  →  MaterialTheme.typography.<key>
```

---

## Step 2 — Read Figma

Call `get_design_context` for the **requested node(s) only**. Nodes outside the requested scope that appear in the output must be flagged — never implemented silently.

> **Scope guard:** If `get_design_context` returns sibling or parent nodes not in scope, note them as "out of scope — skip" and ask before touching them.

For each value in the output:

| Figma output type | Action |
|---|---|
| Color token name (e.g. `surface/surface`) | Look up in color table → use `colorScheme.*` or raw token |
| Typography style name (e.g. `headline/small`) | Look up in typography table → use `MaterialTheme.typography.*` |
| Auto-layout direction (`flex-col` / `flex-row`) | See **Layout mapping** section below |
| Spacing / size (e.g. `gap-[16px]`, `h-[54px]`) | Convert px → `.dp` |
| Opacity / alpha (e.g. `opacity-[50%]`, layer alpha) | See **Alpha/Opacity** section below |
| Border / stroke (e.g. `border-[1px]`, `outline-[2px]`) | Convert px → `.dp`; apply color via border pattern in Appendix |
| Icon node | See **Icon handling** section below |
| Value not in any table | **Flag it, ask the user** — never estimate |

---

## Step 2.5 — Present layout overview + confirm decomposition

Before searching for existing composables or writing any code, present the layout structure to the user and wait for confirmation.

### Format

```
Layout overview — <ScreenName>

<ScreenName>
├── <SectionA>     ← brief description
├── <SectionB>
│   ├── <SubComponent>
│   └── <SubComponent>
└── <SectionC>

Câu hỏi trước khi implement:
1. <SectionX> — reusable composable dùng lại × N lần, hay tách riêng?
2. <SubComponent> — đã có sẵn trong codebase chưa?
3. Design show trạng thái [default / ...]. Cần handle thêm không?
   • loading / skeleton  • empty  • error  • selected / disabled

Confirm rồi tôi bắt đầu.
```

Tất cả câu hỏi — bao gồm states — gửi trong **một message duy nhất**. Không hỏi states trước rồi mới present tree.

### Rules
- Show the tree BEFORE any code or search
- Each node = one composable (or "absorbed into parent" if trivial — say so)
- Flag reuse candidates explicitly: "× 2", "× N", "already in feature X?"
- Ask all open questions in one message — not one by one
- Do not start Step 2.6 until user confirms or corrects the tree

---

## Step 2.6 — Search existing composables (report + confirm)

After layout tree is confirmed (Step 2.5), list the distinct UI components needed. For each component, run the search below, then **stop and report to the user before writing any code**.

### Search process

1. **Extract semantic purpose** — not the Figma node name, but what it *does*. "Song_Cell_Active" → "selectable list item with thumbnail and title".

2. **Search by semantic keyword:**
   ```bash
   grep -r "ListItem\|TrackItem\|SongItem\|MediaItem" app/src/main --include="*.kt" -l
   ```
   Also scan:
   ```
   ui/component/            — shared reusable composables
   feature/*/components/    — feature-scoped composables
   ```

3. **Read candidate files** — capture function name, signature, and params.

### Report format (mandatory — do this before writing any code)

For each component needed, output:

```
Component: <semantic description>

Candidates found:
  <file path>
    → <function signature> — <what's present / what's missing>
  (none found)

Assessment: <which candidate is closest and why, or "no match">
Proceed with reuse / extend / create new — or do you have a suggestion?
```

The user may know about components the search missed. Always ask before deciding.

### Decision (after user confirms)

| User says | Action |
|---|---|
| Reuse as-is | Import and call existing composable |
| Extend it | Add optional param to existing file |
| Create new | Co-locate in nearest `components/` folder |

**Never skip the report step, even if you found no candidates** — "no match found" is itself useful signal.

---

## Step 3 — Write code

Rules that apply to every project:

- **No raw `Color(0xFF...)`** — every color must come from a named token
- **No hardcoded sp/dp** that already has a named constant in the project
- **No hardcoded strings** — `stringResource(R.string.*)`
- **`modifier` is the first parameter** in every `@Composable`
- **Color role → `colorScheme.*`**, accent/overlay not tied to a role → raw Color token

---

## Step 4 — Validate completeness (no extra tool call needed)

After writing the code, scan the `get_design_context` output that is already in context. For every **leaf node** (Text, Icon, Image, Shape), check whether it has been implemented.

**Why this step exists:** Absolutely-positioned nodes (e.g. `top-[202px]` outside a flex container) don't appear in the visual flow hierarchy — they're easy to miss when scanning for "main" components.

Checklist:
- [ ] List every leaf node from the context output (type + content)
- [ ] Mark each: ✅ implemented | ❌ missing
- [ ] For any ❌: add to code before reporting done

Cost: ~0 extra tool calls — context is already loaded from Step 2. Only a new `get_design_context` call is needed if the screen has sub-nodes not fetched in the initial call.

---

## Alpha / Opacity handling

When Figma shows a layer or element with opacity:

| Situation | What to use |
|---|---|
| Project has a named opacity token (e.g. `White50`) that matches | Use the raw token — `White50` not `White.copy(alpha = 0.5f)` |
| No matching opacity token exists | Use `Modifier.alpha(value)` for the whole composable, or `color.copy(alpha = value)` inline |
| Text color at reduced opacity | Prefer the opacity token (e.g. `onSurface` with `White30` overlay) — ask user if unclear |

**Never** use `Color(0xFF...).copy(alpha = ...)` — the base color must still come from a named token.

---

## Gradient handling

When Figma shows a gradient background (`bg-gradient-to-b`, `bg-gradient-to-r`, etc.):

| Figma | Compose |
|---|---|
| `bg-gradient-to-b from-[A] to-[B]` | `Brush.verticalGradient(listOf(colorA, colorB))` |
| `bg-gradient-to-r from-[A] to-[B]` | `Brush.horizontalGradient(listOf(colorA, colorB))` |
| `from-[A] from-[X%] to-[B]` | `Brush.verticalGradient(0f to colorA, X to colorB)` |

Apply via `Modifier.background(brush)`. Colors in gradient still follow the same token lookup (Step 2) — resolve to named tokens, not hardcoded hex.

---

## Icon handling

When a Figma node is an icon (vector, SVG-like shape):

1. **Search existing drawables first** — `grep -r "ic_<name>" app/src/main/res/drawable/` — or browse `res/drawable/` visually if icon name is ambiguous.
2. **If found** → use `painterResource(R.drawable.ic_<name>)` inside `Icon(painter = ...)`.
3. **If not found** → ask the user to export and add the SVG as a vector drawable. Do **not** recreate icons in code.
4. **Size** → always read the Figma node size, convert to `.dp`, pass via `Modifier.size(N.dp)` — do not rely on icon intrinsic size.
5. **Tint / color** → treat as a Color value and apply the same color token lookup (Step 2). Pass via `tint =` param.

---

## Layout mapping

| Figma auto-layout | Compose |
|---|---|
| `flex-col` | `Column` |
| `flex-row` | `Row` |
| `flex-wrap` | `FlowRow` |
| `w-full` / fill container | `Modifier.fillMaxWidth()` |
| `h-full` / fill container (vertical) | `Modifier.fillMaxHeight()` |
| `flex-1` / fill remaining space | `Modifier.weight(1f)` |
| `items-center` | `verticalAlignment = Alignment.CenterVertically` (Row) / `horizontalAlignment = Alignment.CenterHorizontally` (Column) |
| `justify-between` | `Arrangement.SpaceBetween` |
| `justify-center` | `Arrangement.Center` |

---

## Universal: Spacing & Sizing

Figma MCP output (React/Tailwind-style) → Compose:

| Figma value | Compose |
|---|---|
| `gap-[N px]` | `Arrangement.spacedBy(N.dp)` |
| `px-[N px]` | `padding(horizontal = N.dp)` |
| `py-[N px]` | `padding(vertical = N.dp)` |
| `p-[N px]` | `padding(N.dp)` |
| `rounded-[N px]` | `RoundedCornerShape(N.dp)` |
| `h-[N px]` | `Modifier.height(N.dp)` |
| `w-[N px]` | `Modifier.width(N.dp)` |
| `size-[N px]` | `Modifier.size(N.dp)` |

---

## Universal: Typography mapping pattern

Figma style names map 1-1 to `MaterialTheme.typography.*` — no need to check weight/size, those are already defined in `Type.kt`.

Pattern: `{category}/{scale}` → `{category}{Scale}` (camelCase)

| Figma style name | MaterialTheme.typography.* |
|---|---|
| `headline/large` | `headlineLarge` |
| `headline/medium` | `headlineMedium` |
| `headline/small` | `headlineSmall` |
| `title/large` | `titleLarge` |
| `title/medium` | `titleMedium` |
| `title/small` | `titleSmall` |
| `body/large` | `bodyLarge` |
| `body/medium` | `bodyMedium` |
| `body/small` | `bodySmall` |
| `label/large` | `labelLarge` |
| `label/medium` | `labelMedium` |
| `label/small` | `labelSmall` |

> If Figma uses different naming conventions, build the table from `Type.kt` definitions discovered in Step 1.

---

## Common token traps (reference when writing in-scope code)

Existing code can look reasonable but still be wrong against Figma. Only check sections explicitly requested — do not self-expand scope.

| Looks reasonable in code | May actually be wrong in Figma |
|---|---|
| `onSurfaceVariant` on subtitle text | Often `onSurface` (grey) instead |
| `bodySmall` on metadata text | Often `bodyMedium` |
| `primary` on playhead/accent | May be `AccentOrange` or other raw token |
| `titleMedium` on a bold label | May be `headlineSmall` (SemiBold 14sp) |
| Divider added or sized by intuition | Always read from Figma node: check if divider exists, and read its exact width (may be absent, full-width, or inset) |

---

## Output after every Figma apply

After applying changes from Figma, always produce a structured diff table — one section per block. This lets the user spot errors by scanning, without opening the file.

Format:
```
SectionName
  field      : old style → new style  |  old color → new color
  field      : unchanged              |  old color → new color
```

- List every `Text`/`Icon` that was in scope (changed OR explicitly verified unchanged)
- If a section was skipped (not in scope), do not include it
- Post this BEFORE the compile result

---

## Checklist before writing UI code

- [ ] Theme files read — color and typography tables built for this project
- [ ] Scope confirmed — only requested nodes in scope; out-of-scope nodes flagged
- [ ] Layout tree + states + questions presented in one message (Step 2.5), confirmed by user
- [ ] Existing composables scanned after layout confirmed (Step 2.6) — reuse or extend before creating new
- [ ] Every Figma color token resolved to a named Compose token
- [ ] Every Figma typography style resolved to `MaterialTheme.typography.*`
- [ ] Auto-layout direction mapped to Row/Column/FlowRow correctly
- [ ] All sizes converted to `.dp` — no raw pixel math
- [ ] Opacity values resolved to token or `.alpha()` — no `Color(0xFF...).copy(alpha=...)`
- [ ] Icon nodes → existing drawable found or user asked to export
- [ ] No unmapped values slipped through — flagged and confirmed with user
- [ ] `modifier` first in every `@Composable`
- [ ] Strings in `strings.xml`

## Checklist after writing UI code (Step 4)

- [ ] All leaf nodes from Figma context listed and verified implemented
- [ ] No absolutely-positioned nodes skipped

---

## Appendix: music_editor design system

> Apply this section only when the project uses the `music_editor` shared design system (Navy surface hierarchy + WhiteX opacity tokens).

### Color — semantic roles

| Figma token name | colorScheme key |
|---|---|
| `primary/primary` | `MaterialTheme.colorScheme.primary` |
| `primary/on-primary` | `MaterialTheme.colorScheme.onPrimary` |
| `background/background` | `MaterialTheme.colorScheme.background` |
| `background/on-background` | `MaterialTheme.colorScheme.onBackground` |
| `surface/surface` | `MaterialTheme.colorScheme.surface` |
| `surface/on-surface` | `MaterialTheme.colorScheme.onSurface` |
| `surface/on-surface-variant` | `MaterialTheme.colorScheme.onSurfaceVariant` |
| `surface/surface-container` | `MaterialTheme.colorScheme.surfaceContainer` |
| `surface/surface-container-high` | `MaterialTheme.colorScheme.surfaceContainerHigh` |
| `surface/surface-container-highest` | `MaterialTheme.colorScheme.surfaceContainerHighest` |
| `surface-bright` | `MaterialTheme.colorScheme.surfaceBright` |
| `error` | `MaterialTheme.colorScheme.error` |

### Color — raw tokens (accents + opacity overlays)

| Figma token name | Color.kt token |
|---|---|
| `white/5` … `white/80` | `White5` … `White80` |
| `black/10`, `black/70`, `black/90` | `Black10`, `Black70`, `Black90` |
| `accent/orange` | `AccentOrange` |
| `accent/pink` | `AccentPink` |
| `gray/80` | `Gray80` |
| `gray/60` | `Gray60` |

### Border pattern

| State | Width | Color token |
|---|---|---|
| Selected / active | `2.dp` | `MaterialTheme.colorScheme.primary` |
| Unselected / inactive | `1.dp` | `White10` |
| Error | `1–2.dp` | `MaterialTheme.colorScheme.error` |

### Surface hierarchy (darkest → lightest)

```
background           Navy10  ← page background
surface              Navy30  ← cards, bottom sheets
surfaceContainer     Navy15  ← chip bg, input fields
surfaceContainerHigh Navy40  ← bottom bar, elevated panels
```
