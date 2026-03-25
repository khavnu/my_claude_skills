---
name: debug
description: Use when encountering Android bugs, crashes, ANR, Flow not emitting, UI not updating, Hilt DI errors, or any unexpected runtime/compile behavior.
---

# Android Systematic Debugging

Never guess. Never patch symptoms. Always find the root cause.

---

# Step 1: Classify the problem

| Symptom | Category |
|---|---|
| App crashes with exception | Crash |
| App freezes / ANR dialog | ANR / Main thread block |
| UI shows stale data / not updating | State / Flow issue |
| Flow never emits | Flow / Coroutine issue |
| Hilt injection fails at runtime | DI misconfiguration |
| Compile error after adding Hilt/KSP | Annotation processing |
| Feature works sometimes, not always | Race condition |
| Memory grows over time | Memory leak |

---

# Step 2: Debugging by category

## Crash
1. Read the full stack trace — find the **first line in your code** (not framework)
2. Identify: NullPointerException, IllegalStateException, ClassCastException, etc.
3. Check: is it a null that should never be null? Is state mutated from wrong thread?
4. Common Android-specific causes:
   - Accessing View after Fragment detached
   - `requireActivity()` called when fragment not attached
   - `savedStateHandle` missing required argument

## ANR / Main Thread Block
1. Check for `runBlocking` on Main dispatcher
2. Check for database/network calls without `withContext(Dispatchers.IO)`
3. Check BroadcastReceiver — `onReceive()` runs on main thread
4. Use Android Profiler → CPU → find what's blocking main thread

## UI Not Updating / Stale State
1. Verify `StateFlow` is collected with `repeatOnLifecycle(STARTED)` — not just `lifecycleScope.launch`
2. Check if `_uiState.update {}` is called from a coroutine that's actually running
3. Check `stateIn` — is `SharingStarted.WhileSubscribed(5000)` dropping upstream too early?
4. Check `distinctUntilChanged` — is it filtering out an update it shouldn't?
5. In Compose: is state read inside the composable scope, or captured outside?

## Flow Not Emitting
1. Is the Flow **collected**? A cold Flow does nothing without a collector.
2. Is `flowOn(Dispatchers.IO)` used? Check the dispatcher chain.
3. Is the coroutine **cancelled** before the emit? Check `Job` lifecycle.
4. Is `callbackFlow` missing `awaitClose`? It will complete immediately.
5. Is `CancellationException` swallowed in a `catch(e: Exception)` block? Always re-throw it.
6. Check upstream: is the source Flow (Room, DataStore) emitting at all?

## Hilt DI Error
1. Read the full error — Hilt errors are verbose but precise
2. Common causes:
   - Missing `@AndroidEntryPoint` on Activity/Fragment
   - Missing `@HiltViewModel` on ViewModel
   - Binding interface without `@Binds` in an `abstract` module
   - Module not installed in the correct component scope
3. After fixing: run `./gradlew kaptDebugKotlin` to regenerate Hilt code

## Race Condition
1. Add logs with timestamps to identify ordering
2. Check: is shared mutable state accessed from multiple coroutines?
3. Use `Mutex` or `StateFlow.update {}` (atomic) instead of direct mutation
4. Check `flatMapLatest` vs `flatMapConcat` — are events being dropped/interleaved?

## Memory Leak
1. Use Android Studio Memory Profiler → Heap Dump → search for leaked object
2. Common causes:
   - `Context` or `View` held in a `companion object` or singleton
   - Listener/callback registered but never unregistered
   - Coroutine launched in `GlobalScope` instead of `viewModelScope`
   - Inner class holding reference to outer Activity

---

# Step 3: Verify the fix

- Reproduce the original bug scenario — confirm it's gone
- Check adjacent code for the same root cause pattern
- Run compile check: see project CLAUDE.md for correct flavor variant

---

# Common Mistakes

| Mistake | Correct approach |
|---|---|
| Catching `Exception` without re-throwing `CancellationException` | `catch (e: CancellationException) { throw e }` before general catch |
| Collecting Flow in `lifecycleScope.launch` | Use `repeatOnLifecycle(STARTED)` |
| Calling `view.something` in a `lifecycleScope` coroutine after `onDestroyView` | Use `viewLifecycleOwner.lifecycleScope` |
| `GlobalScope.launch` for background work | Use `viewModelScope` or `applicationScope` |
| Accessing Room DB on main thread | Wrap with `withContext(Dispatchers.IO)` |
| `runBlocking` in production code | Use `suspend` functions instead |