# Mobile spec numbers — quick lookup

Defaults for phone UI. Every value a multiple of 4. Deviate deliberately.

## Spacing (8pt system)
| Token | Value | Use |
|---|---|---|
| XS | 4 | icon↔text, stacked text lines |
| S | 8 | items inside a group |
| M | 12 | chip/tag padding |
| L | 16 | screen margin, card padding, between list items |
| XL | 24 | between content groups |
| 2XL | 32 | between sections |
| 3XL | 48–64 | page top/bottom, very large blocks |
Screen side margin: 16 (20–24 for airy layouts).

## Buttons
| Size | Height | H-padding | Text |
|---|---|---|---|
| Small | 32 | 12 | 13–14 |
| Medium | 40 | 16 | 14–15 |
| Large (primary) | 48 | 20–24 | 16 |
| XL (end-of-screen CTA) | 52–56 | 24 | 16–17 |
- Touch target ≥ 48 dp / 44 pt even when the visual is smaller.
- Gap between adjacent buttons ≥ 8 (usually 12). Icon button 40–48 with 20–24 glyph.
- Full-width = screen width − 2 × margin. Label weight 500–600.
- Disabled: 38–40% opacity, or grey fill + grey text.
- Same row → same height and same radius.

## Corner radius
| Element | Radius |
|---|---|
| Checkbox, small tag, tooltip | 4 |
| Input, small button | 6–8 |
| Button, text field | 8–12 |
| Card | 12–16 |
| Thumbnail | 8–12 |
| Dialog / modal | 16–24 |
| Bottom sheet (top corners) | 16–28 |
| Pill, chip, avatar | full |
- **Nested radius: outer = inner + padding** (card 16 with padding 8 → inner image 8). Equal radii on nested shapes look off.
- Radius is personality: 0–4 formal, 8–12 neutral, 16+/pill friendly. Pick one family, stay consistent.

## Typography (mobile)
| Level | Size | Line-height | Weight |
|---|---|---|---|
| Display | 32–40 | 1.2 | Bold |
| Heading 1 | 24–28 | 1.25 | Bold/Semibold |
| Heading 2 | 20 | 1.3 | Semibold |
| Title | 16–17 | 1.4 | Semibold |
| Body | 15–16 | 1.5 | Regular |
| Body small | 14 | 1.45 | Regular |
| Caption | 12–13 | 1.4 | Regular/Medium |
| Floor | 11 | — | never smaller |
- 1 family (max 2), 2–3 weights. Line length 50–75 chars.
- ≥24: letter-spacing −0.5% to −2%. Small caps labels: +5%.
- Vietnamese: line-height never < 1.2 (display lyric text ≥ 1.3); test "Ướt đẫm, nỗi nhớ quẫn trí".

## Text field
Height 44–48 (Material 56) · H-padding 12–16 · radius matches buttons · border 1, focus 1.5–2 in primary · label gap 4–8 · error text 4–6 below, 12–13, error color · fields 16–20 apart.
Input text 16 matters for **web on iOS Safari** (smaller triggers zoom); native apps are unaffected.

## Icons
16 caption-level · 20 in buttons/lists · 24 default (bars) · 32–48 illustrative/empty states. One stroke weight (1.5–2) app-wide. Icon↔text gap 4–8.

## Avatar
24 stacked/compact · 32 comments · 40 list item · 48–56 messages/contacts · 80–120 profile.

## Lists & cards
1-line item 48–56 · 2-line 64–72 · 3-line 88 · card padding 16 (12 compact, 20–24 airy) · card gap 12–16 · divider 1 px (0.5 iOS), very low contrast.

## System bars
| | iOS | Android M3 |
|---|---|---|
| Status bar | 44–59 | 24–48 |
| Top bar | 44 (large title ~96) | 64 |
| Bottom nav / tab bar | 49 + 34 safe area | 80 |
Tab/nav items: 3–5. Base frames 390×844 (iPhone), 360×800 (Android).

## Color
- 60 neutral / 30 secondary / 10 accent. Neutral ramp 9–10 steps; each hue 50→900.
- Text ≥ 4.5:1; large (≥18 regular or ≥14 bold) and icons ≥ 3:1. Also check APCA in dark mode.
- Dark background: very dark grey (e.g. #121212), not #000. Text on dark: white at ~87% (primary), 60% (secondary), 38% (disabled).
- Light mode text: not #000 — ~#1A1A1A–#222 primary, ~#666–#757575 secondary.

## Shadows
| Level | y / blur / black opacity |
|---|---|
| Low (card) | 1 / 3 / 8–10% |
| Mid (dropdown, floating button) | 4 / 12 / 10–12% |
| High (modal, sheet) | 8 / 24 / 12–16% |
Soft and faint. In dark mode use a lighter surface instead of a shadow.

## Motion
| Kind | Duration |
|---|---|
| Press / hover feedback | 100–150 ms |
| Toggle, small state change | 150–200 ms |
| Dropdown, toast | 200–300 ms |
| Screen transition, bottom sheet | 300–400 ms |
| Ceiling | 500 ms |
Ease-out to enter, ease-in to exit, ease-in-out to move (or M3 springs).

## One-screen rules
One primary button · max 2 fonts, 3 weights, 1 main accent · same-row controls share height and radius · contrast checked before colors are final.
