---
name: review
description: Review Android code for bugs, architecture issues, performance problems, and adherence to project conventions.
---

# Android Code Review

You are doing a senior-level code review. Be critical but constructive.

If the user hasn't specified which file(s) to review, ask them first.

---

# Review checklist

## Architecture
- [ ] Does the code follow Clean Architecture layers? (data → domain → presentation)
- [ ] Does the ViewModel contain business logic that belongs in a UseCase?
- [ ] Does the Repository implementation depend on the correct data sources?
- [ ] Are domain models leaking into the data layer (or vice versa)?

## ViewModel & State
- [ ] Is UI state exposed as `StateFlow`, not `LiveData` or raw mutable fields?
- [ ] Is `MutableStateFlow` properly encapsulated (private `_state`, public `state`)?
- [ ] Does the ViewModel avoid direct Android SDK dependencies?
- [ ] Are heavy operations off the main thread?

## Fragment / Activity communication
- [ ] Are internal BottomSheets using `activityViewModels()` — not `setFragmentResult`?
- [ ] Is data passed to Activities via `companion object { fun open(...) }` — not raw Intent extras?

## UI
- [ ] Is UI logic inside ViewModel, not Fragment/Activity?
- [ ] Are Flows collected with `repeatOnLifecycle(Lifecycle.State.STARTED)`?
- [ ] Are there unnecessary recompositions (if Compose)?

## Code quality
- [ ] Are functions longer than 50 lines? If so, should they be split?
- [ ] Is naming meaningful and consistent with project conventions?
- [ ] Are there magic numbers/strings that should be constants?
- [ ] Are comments explaining *why*, not *what*?

## DI
- [ ] Are dependencies injected via constructor (`@Inject constructor`) — not created manually?
- [ ] Is Hilt properly wired (`@HiltViewModel`, `@AndroidEntryPoint`, `@Binds`/`@Provides`)?

## Performance
- [ ] Are there blocking calls on the main thread?
- [ ] Are there memory leaks (e.g. holding Context in ViewModel)?
- [ ] Is `distinctUntilChanged()` used where appropriate to avoid redundant updates?

## Flow & Concurrency
- [ ] Is `CancellationException` always re-thrown?
- [ ] Is the correct operator used? (`collect` vs `collectLatest`, `map` vs `mapLatest`, `flatMapConcat` vs `flatMapLatest`)
- [ ] Is Flow used where a simple `suspend` function would suffice?
- [ ] Are there nested Flow collectors that could cause backpressure or leaks?
- [ ] Is `StateFlow` used for UI state and `SharedFlow` for one-time events?

## Error Handling
- [ ] Are exceptions caught and mapped to domain error types at the repository boundary?
- [ ] Are exceptions silently swallowed anywhere (empty `catch` block)?
- [ ] Is `sealed Result<T>` or a sealed state used instead of throwing exceptions to the UI?
- [ ] Are all `Fail`/`Error` states handled in the UI?

---

# Output format

**Bugs:** (critical issues that will cause crashes or wrong behavior)

**Architecture issues:** (violations of Clean Architecture / MVVM)

**Improvements:** (non-blocking suggestions for better code)

**Good parts:** (what's done well — always include this)

**Weaknesses:** (trade-offs and scalability concerns of the current design)

**Edge Cases:** (scenarios that could cause crashes, wrong behavior, or silent failures)