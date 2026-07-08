---
name: Compose modifier param position
description: modifier must always be the first argument in Composable functions and call sites — new code only, no refactoring old code
type: feedback
originSessionId: f46c96e3-a23f-4c10-af4b-dff7573a84d7
---

Always put `modifier: Modifier = Modifier` as the first parameter in every `@Composable` function, and `modifier = ...` as the first named argument at every call site (including Compose built-ins: `Image`, `Slider`, `Text`, `Icon`, etc.).

**Why:** User convention — absolute consistency, even when modifier is optional.

**How to apply:** New code only. Do not refactor existing code to follow this rule.

```kotlin
// CORRECT — definition
fun MyButton(
    modifier: Modifier = Modifier,
    label: String,
    onClick: () -> Unit,
)

// CORRECT — call site
Image(
    modifier = Modifier.size(20.dp),
    painter = painterResource(R.drawable.ic_foo),
    contentDescription = null,
)
```
