---
name: pattern-compose-state-capture-in-coroutine
description: "Trong LaunchedEffect/coroutine, đọc thẳng MutableState (by remember), không dùng plain val snapshot — val bị đóng băng tại compose-time"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7a06c041-77f3-4d2b-bda6-d2b571aa7db1
---

Khi một `LaunchedEffect`/coroutine đọc state SAU một `delay(...)` (hoặc bất kỳ suspend point nào), phải đọc **thẳng** biến `by remember { mutableStateOf() }`, KHÔNG được thay bằng một `val Boolean/Int...` thường được tính từ các state đó.

**Why:** plain `val x = !stateA && !stateB` là một snapshot Boolean tính tại thời điểm compose. Coroutine capture nó → giá trị bị đóng băng tại lúc launch, sau `delay` vẫn stale. Ngược lại, `by remember { mutableStateOf }` desugar thành một `MutableState` delegate (cùng instance qua các recomposition); coroutine capture delegate đó, và mỗi lần đọc biến = đọc `.value` **tại thời điểm chạy** → thấy giá trị mới nhất.

**Rule gốc:** chỉ `State` (instance ỔN ĐỊNH) mới đọc live trong coroutine. Mọi giá trị thường (Boolean/Int…), dù bọc `remember {}` hay `remember(keys) {}`, đều bị đóng băng khi coroutine capture. Riêng `remember(keys) { mutableStateOf(...) }` còn tệ hơn: mỗi lần key đổi tạo **instance State mới**, coroutine giữ instance cũ → vẫn stale.

**Cách gộp 1 biến dùng chung cho cả UI + coroutine (đều live):**
- `val x by rememberUpdatedState(!a && !b)` ← **ưu tiên** cho biểu thức rẻ; đúng use-case chính thức của `rememberUpdatedState` (giữ value tươi để đọc trong effect dài). Impl = `remember { mutableStateOf(v) }.apply { value = v }` → 1 instance ổn định, refresh value mỗi recompose.
- `val x by remember { derivedStateOf { !a && !b } }` (KHÔNG key) ← khi phép tính đắt / input đổi dày.

**How to apply:**
- Watchdog `delay(TIMEOUT); if (isVideoLoading) { flag }` — chỉ đúng khi `isVideoLoading` là `rememberUpdatedState`/`derivedStateOf` (State). Nếu là plain `val` thì phải đọc thẳng 2 state trong coroutine.
- plain val truyền xuống UI (`isLoading = ...`) thì OK — vì đọc trong composition, recompose lại khi state đổi. Bẫy chỉ xảy ra khi đọc trong coroutine sau suspend point.
- Chốt tại `VideoToAudioEditorScreen.kt`: `val isVideoLoading by rememberUpdatedState(...)` dùng chung UI + watchdog.

Gặp lần đầu ở `VideoToAudioEditorScreen.kt` (ticket #232, video-playability watchdog). Liên quan [[pattern_compose_flicker_fix]].
