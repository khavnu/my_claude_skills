---
name: pattern-compose-flicker-fix
description: "Pattern ngăn Compose UI flicker khi layout transition có delayed side effect (e.g. scroll reanchor sau zoom), và cách test nó frame-by-frame"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6d36b2f7-8c22-4d44-997e-921e55c911e1
---

## Pattern: Placement-phase offset pin để prevent flicker

**Vấn đề:** State A thay đổi → layout re-measure ngay → side effect B (e.g. scrollTo) chỉ fire qua `LaunchedEffect` sau khi layout publish → gap 1 frame render sai vị trí.

**Fix:**
```kotlin
var committedZoom by remember { mutableFloatStateOf(zoomScale) }

Box(modifier = Modifier.offset {
    val needsPin = committedZoom != zoomScale && !isDragging
    if (needsPin) IntOffset(x = scrollState.value - anchorTargetPx(), y = 0)
    else IntOffset.Zero
})

LaunchedEffect(scrollState.maxValue) {
    scrollState.scrollTo(anchorTargetPx())
    committedZoom = zoomScale  // release pin sau khi scrollTo xong
}
```

- `committed*` = sentinel state: track xem zoom/state nào đã được side effect "commit" thật sự
- `.offset {}` chạy ở **placement phase** (sau layout, trước draw) → override visual position mà không cần recompose
- Shared local function `anchorTargetPx()` → pin và scrollTo luôn agree về target

**Why:** Dùng trong `WaveformView` (commit 453f6e23) để fix zoom flicker.

---

## Pattern: Test UI flicker bằng frame-by-frame clock

`waitForIdle()` skip hết intermediate frames → **luôn pass dù có bug**. Để catch flicker:

```kotlin
composeRule.mainClock.autoAdvance = false
composeRule.runOnUiThread { state.value = newValue }

repeat(FRAMES_TO_CHECK) { frame ->
    composeRule.mainClock.advanceTimeByFrame()
    assertEquals("frame $frame", expectedPosition, actualPosition, TOLERANCE_PX)
}
```

**How to apply:** Bất kỳ bug nào liên quan đến "render sai trong 1-2 frame đầu tiên sau state change" đều cần pattern này để test và reproduce.

---

## Pattern: `internal` constant để test dùng chung

Khi test cần reproduce cùng một phép tính với production code, expose constant là `internal` thay vì `private`:

```kotlin
// WaveformView.kt
internal const val START_ANCHOR_PADDING_FRACTION = 0.15f
```

Test import trực tiếp → pin và test luôn dùng cùng inset → không hardcode magic number trong test.
