---
name: wmusi-drag-reorder-pitfalls
description: Drag-to-reorder lists in Compose — compute from the finger's root Y vs drag start, key rows, and test with frames between moves (one performTouchInput hides the bug)
metadata:
  type: project
---

Found 2026-10-09 (Library tabs 8a5fee5, Queue sheet ab14fd9): the dragged row fell one row behind the finger at every slot swap, so a 3-row drag moved 1–2 rows (user saw it on the Pixel 9).

- Per-event deltas from `pointerInput` are local to the row; when the live reorder relays the row into a new slot they jump. Fix: remember the finger's **root** Y at drag start (`onGloballyPositioned` coords → `localToRoot`), and on every move derive `target = startIndex + round((rootY - startY) / rowHeight)` from the order at drag start, `offset = total - (target - start) * rowHeight`. Unkeyed `forEach` rows also need `key(id)`.
- Row height: take the smallest visible item (a section-opening item also holds its label and is taller).
- Tests: a single `performTouchInput { down; moveBy…; up }` never recomposes between moves, so it passes on the broken code. Inject on the root (`onAllNodes(isRoot())[1]` for a ModalBottomSheet window), one `performTouchInput { moveTo(...) }` per step with `waitForIdle()` / `mainClock.advanceTimeBy(16)` between. Verify fail-before by copying the test into `_review` at origin/main.
- Real-device check on the emulator: `adb shell 'input motionevent DOWN x y; sleep 0.8; input motionevent MOVE …; input motionevent UP …'` (long press), `input swipe x y x y2 2000` (plain drag).
