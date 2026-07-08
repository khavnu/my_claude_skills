---
name: doubt-driven-development
description: Use before implementing non-trivial decisions — architecture choices, cross-module changes, threading/concurrency, irreversible operations (DB migration, data deletion). Subjects the plan to adversarial self-review before writing code.
---

# Doubt-Driven Development

Subject non-trivial decisions to adversarial review **before** implementation. Catching a wrong approach costs nothing. Catching it after 200 lines of code costs a rewrite.

---

## When to Apply

**Apply when the decision involves:**
- Coroutine scope choice (`viewModelScope` vs `lifecycleScope` vs custom)
- Flow operator choice (`flatMapLatest` vs `flatMapConcat`, `map` vs `mapLatest`)
- StateFlow vs SharedFlow vs Channel
- Cross-module boundary changes (domain ↔ data ↔ presentation)
- Hilt scope (`@Singleton` vs `@ViewModelScoped`)
- Room: transactions, migration scripts, TypeConverter correctness
- Irreversible operations: DB migration, file deletion, data transformation
- Concurrency: anything with `Mutex`, `withContext`, parallel coroutines
- New library/API you haven't used in this codebase before

**Skip when:**
- Simple CRUD delegation (ViewModel → Repository → DAO)
- Renaming, formatting, extracting a composable under 20 lines
- The user gave a direct, specific instruction with no design ambiguity
- One-liners with obvious correctness

---

## Five-Step Process

### 1. CLAIM
State the decision and its stakes in one sentence.

> "I plan to use `flatMapLatest` to chain search query → repository call, dropping in-flight requests when query changes."

### 2. EXTRACT
Isolate just the contract: what goes in, what comes out, what side-effects are expected. Strip away the implementation reasoning.

> Input: `StateFlow<String>` (query). Output: `StateFlow<List<Result>>`. Side-effect: cancels in-flight network call on new emission.

### 3. DOUBT
Switch to adversarial mode. Ask: *"What breaks this? What assumption is wrong?"*

Challenge specifically:
- **Threading**: Is this called from the right dispatcher? What if the upstream emits on `Dispatchers.IO`?
- **Lifecycle**: What if the ViewModel is cleared mid-flight?
- **Backpressure**: What if emissions come faster than the consumer processes?
- **State consistency**: Can two coroutines mutate shared state simultaneously?
- **Edge cases**: Empty input, null, error from repository — does the chain handle all of them?
- **Hilt scope**: Will this dependency outlive its consumer? Will it be garbage-collected too early?
- **Room**: Does this query run on a background thread? Is the `@Transaction` actually needed?

Write down at least 2 concrete doubts before proceeding.

### 4. RECONCILE
Classify each doubt:
- **Actionable** → fix it before writing code
- **Trade-off** → acknowledge, document in a comment, proceed
- **Non-issue** → explain why, then dismiss

### 5. STOP
Stop the doubt loop when:
- All doubts are classified
- After 2 cycles maximum (3rd cycle = over-engineering)
- User explicitly says to proceed

---

## Android-Specific Red Flags

These patterns should always trigger a DOUBT cycle:

| Pattern | Risk |
|---|---|
| `GlobalScope.launch` | Leak — never use |
| `flow { emit(...) }` with non-suspend callback | Illegal — use `channelFlow` |
| `collect` inside `LaunchedEffect` without cancellation | Leak on recomposition |
| `_state.value = ...` from multiple coroutines | Race condition |
| `@Singleton` on a class with `Context` | Memory leak |
| Room migration without test | Silent data corruption |
| `!!` on any nullable from external layer | Crash waiting to happen |
| `SharedFlow` for UI state | Missed emissions on resubscribe |

---

## Output Format

Before implementing, output:

```
CLAIM: [one sentence]
DOUBTS:
  1. [specific concern]
  2. [specific concern]
RESOLUTION:
  1. [actionable / trade-off / non-issue + why]
  2. [actionable / trade-off / non-issue + why]
PROCEED: [yes / no + what changes before coding]
```