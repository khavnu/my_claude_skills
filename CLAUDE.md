# CLAUDE.md

## User Profile
- **Language**: Respond in Vietnamese. English only for code, technical terms, library names.
- **Skill level**: Senior Android engineer — skip basics, get to the point.
- **Decision style**: When asked "bạn thấy sao?" → give assessment + recommendation, then wait. Never implement during evaluation.
- **Tech stack**: Kotlin, Jetpack Compose, Clean Architecture + MVVM, Coroutines + Flow, Hilt, Room, DataStore, Retrofit, Media3.

---

## Code Quality

- Constants belong to the class they configure — sentinel values go in that class's `companion object`.
- Truncation must show `…`: `if (text.length > N) text.take(N - 1) + "…" else text`
- `modifier` is always the first argument — definitions and call sites, all `@Composable` functions. **New code only.**
- Comments explain **why**, not what.
- No `!!` — use `?:` or `?.let`. No wildcard imports. No hardcoded strings.
- Lifecycle/cleanup methods (`onCleared`, `onDetach`, `onDestroy`, `release`, `close`, `dispose`) → always the last members of any class.
- No thrown exceptions → return `Result.Failure`. No empty catch blocks.
- Descriptive names → no `process()`, `data`, `result`, `handle()`

### Lambda & Higher-order function naming

**Higher-order function params**: không dùng `block` — quá generic. Dùng tên semantic:
- `(T) -> T` transformation → `transform`
- `(T) -> Unit` side-effect → `action`
- `(T) -> Boolean` filter → `predicate`
- `StateFlow.update {}` helper → `update`

```kotlin
// Sai
fun updateDraft(block: (DraftState) -> DraftState)

// Đúng
fun updateDraft(transform: (DraftState) -> DraftState)
```

**Named `let` lambda params**: luôn đặt tên explicit khi có nested lambda hoặc `it` gây ambiguity — không dùng implicit `it`:

```kotlin
// Sai — `it` trong let là gì? draft hay state?
state.draft?.let { state.copy(draft = transform(it)) }

// Đúng
state.draft?.let { oldDraft ->
    state.copy(draft = transform(oldDraft))
}
```

Convention: `old{Type}`, `current{Type}`, hoặc tên domain ngắn (`draft`, `file`, `preset`).

---

## Build Verification

After any code change, always run `./gradlew :<module>:compileDebugKotlin` (check project CLAUDE.md for flavor). Never ask — just run.

---

## Workflow Rules

1. **Auto-apply changes** — Write/edit files directly. Never ask "should I apply this?".
2. **Auto-run builds** — After changes, compile automatically.
3. **Auto-read images** — When user sends an image path, read and analyze immediately.
4. **Auto-update CLAUDE.md** — Apply rule changes directly.
5. **Auto-update skills/memory** — Proactively save new patterns/pitfalls discovered during work.
6. **NEVER auto-commit or auto-push** — Only run `git commit`/`git push` when user explicitly asks. Subagents must include "DO NOT run git commit or git push" in their prompts.
7. **Shared ViewModel over FragmentResultListener** — Same-feature BottomSheet/Dialog: use `activityViewModels()`.
8. **safeShowDialogFragmentOrNot over raw .show()** — Always use `safeShowDialogFragmentOrNot(dialog, TAG)` from an Activity.
9. **Incremental delivery — step by step, report back** — Cho mọi feature/màn hình mới: chia nhỏ thành các bước rõ ràng, hoàn thành từng bước rồi báo lại user trước khi làm tiếp. Không làm dồn tất cả một lúc. Với màn hình mới: bước 1 = UI shell với fake/empty data, bước 2 = wire data thật.

---

## Scope Discipline

Only fix what was asked. If a related issue is spotted, mention it — do not fix silently.

## Multi-Fix Discipline

When applying multiple fixes from a review list: after each fix, pause and ask *"Does this fix make any remaining item obsolete?"* Never tick items blindly — fixes interact.

---

## Problem-Solving Approach

Top-down before implementing:
1. **Function** — what does this serve, what does the caller need?
2. **Pseudo code** — branches, edge cases, interface shape
3. **Implement** — only then write real code

For refactors/extractions: ask *"does this abstraction hide complexity, or just move code?"* If the caller still needs to know all internals → don't extract.

---

## Solution Format

**Non-trivial tasks** (new feature, architecture change, complex bug fix):
1. **Solution** — approach + why over alternatives.
2. **Weaknesses** — trade-offs, assumptions.
3. **Edge Cases** — crashes, wrong behavior, silent failures.

**Trivial tasks**: just make the change.

---

## Code Review Format

**Strengths** → **Issues** (Critical / High / Medium / Low) → **Summary table**.
Always include file:line references.

| Severity | Meaning |
|---|---|
| Critical | Crash, data loss, security |
| High | Memory leak, OOM, incorrect behavior |
| Medium | Performance, fragile coupling |
| Low | Code smell, readability |

---

## Architecture & Structure

**Modules:** `:app` (nav/DI) → `:domain` (pure Kotlin) → `:data` (impl) → `:core:common` / `:core:designsystem`

**Feature package:** `feature/{name}/{Name}Screen.kt`, `{Name}ViewModel.kt`, `components/`

**Feature có tabs — cấu trúc bắt buộc:**
```
feature_name/
├── FeatureScreen.kt          — Route + Screen (slim)
├── FeatureViewModel.kt       — scan/permission/loading/error relay only
├── FeatureUiState.kt
├── components/               — shared UI của feature
└── tabs/
    ├── tab_a/
    │   ├── TabAContent.kt    — self-contained, hiltViewModel() bên trong
    │   └── TabAViewModel.kt
    └── tab_b/
        ├── TabBContent.kt
        ├── TabBViewModel.kt
        └── navigation/       — nested NavDisplay nếu tab có sub-navigation
            ├── BrowserScreen.kt
            └── BrowserViewModel.kt
```
- **Tab tự chứa**: VM riêng, KHÔNG nhận search/filter state từ parent — tab tự handle.
- **Navigation co-located**: nested nav của tab nào → `tabs/tab_name/navigation/`, không tạo `*navigation/` ngang hàng feature root.
- **VM single responsibility**: VM cha chỉ orchestrate shared state; shared data → singleton `*State` inject vào nhiều VM.
- **Plan phải có section Package Structure** trước khi liệt kê implementation steps.

**ViewModel file layout:** ViewModel class first → `UiState` data class → `Event` sealed interface at the bottom. Never declare supporting types above the ViewModel class.

**Naming:** `*Screen`, `*ViewModel`, `*Repository` (interface in domain), `Default*Repository` (impl in data), `*Scanner` (interface in data/mediastore), `MediaStore*Scanner` (impl), `*UseCase`, `*Mapper`, `*Extension`

**Domain modeling:**
- Pure Kotlin — zero Android imports
- `kotlinx.datetime.Instant`, không dùng `java.util.Date` / `java.time`
- No UseCase wrapping single repo call — chỉ tạo UseCase khi multi-repo, business rules, hoặc reused across VMs
- Domain trả `DomainError`/enum — không có user-facing string (`R.string`, `UiText`); mapping → string sống ở presentation
- `sealed interface` thay `open class`; tất cả `val`, không `var`

**Thin delegation là anti-pattern** — class chỉ delegate 1-1 không thêm logic → xoá, inject trực tiếp. Chỉ tạo wrapper khi có transformation hoặc business logic thực sự.

**Libraries:** Timber (no `Log.d`), Coil, Hilt+KSP, Room+KSP, DataStore (no SharedPreferences), Compose Navigation, `collectAsStateWithLifecycle()`.

**Dependencies:** Always add to `libs.versions.toml`. Prefer KSP over KAPT.

---

## Onboarding

Before writing code on any project: read project CLAUDE.md → follow existing patterns (consistency over perfection).

---

## Large Data

Default to streaming (SAX/sequential). DOM only if < 5MB or random access required. Ask "Will this OOM at 10× data size?"

---

## Flow & Concurrency

- **Bridge sync callback → Flow**: `channelFlow { syncFn(onProgress = { trySend(it) }) }.flowOn(io)` — never `flow {}` + `emit` from non-suspend lambda.
- **Multiple raw callbacks** (`onSuccess`/`onError`/`onProgress`) → replace with sealed class.
- StateFlow for UI state. One-time events → `Channel` + `receiveAsFlow()`, **never SharedFlow**.
- Justify operator choice: `map` vs `mapLatest`, `flatMapConcat` vs `flatMapLatest`.
- **Domain interface dùng `fun observeX(): Flow<T>`**, không phải `val x: StateFlow<T>` — ẩn impl detail, dễ test hơn.
- **Sealed scan state**: thay vì `isLoading + data + error` riêng lẻ, model thành `sealed interface XyzScanState { Scanning, Ready(data), Error }` trong `domain/model/`.
- **Shared singleton state**: nhiều VM cần cùng một hot state → `MutableStateFlow` trong `@Singleton` + `@ApplicationScope`, không dùng cold Flow (cold Flow = mỗi subscriber trigger một scan mới).
- **Dispatcher owned by data source, not repository**: data source tự wrap blocking work — `withContext(ioDispatcher)` cho suspend fn, `flowOn(ioDispatcher)` cho Flow. Repository chỉ orchestrate, không biết dispatcher. Never hardcode `Dispatchers.IO` — inject via qualifier để swap `UnconfinedTestDispatcher` trong tests.

---

## ViewModel Pattern

**File layout** (enforce trước khi viết):
1. ViewModel class — luôn đầu tiên
2. UiState data class
3. Event sealed interface

Never declare UiState/Event above the ViewModel class.

**State pattern:**
- `private data class ViewModelState` → `private val _state = MutableStateFlow(ViewModelState())` → public `val uiState = _state.map { it.toUiState() }.stateIn(WhileSubscribed(5_000))`
- `toUiState()` = lightweight field mapping only — no filter/sort/search
- `_state.update {}` for thread-safe mutation, never expose MutableStateFlow

**Rules:**
- `@HiltViewModel` + `@Inject constructor`
- Never inject `Context` — delegate Context-dependent work to Repository/data layer
- Import domain layer only, never data layer
- Input validation in Repository, not ViewModel
- Intermediate Flow pipelines → keep as `Flow`, không `stateIn` ở giữa pipeline

---

## Repository Pattern

**Conventions:**
- Reactive reads → `fun observeX(): Flow<T>` (not suspend)
- One-shot reads → `suspend fun getX(): T?`
- Writes that can fail → `suspend fun save(): Result<T>`
- Fire-and-forget → `suspend fun delete()` (no Result)

**Result & Error:**
- `Result<T>` = `Success(data)` | `Failure(DomainError)`
- `OperationError`: `Empty`, `AlreadyExists`, `NotExists`
- Feature-specific → `sealed class {Feature}Error : DomainError`
- Never throw → catch at boundary, return `Result.Failure`
- Input validate first (trim + isEmpty) → `OperationError.Empty`

**Mappers:** co-located với entity — `toDomain()` / `toEntity()` extension functions

---

## Compose Patterns

**Route vs Screen split:**
- `{Feature}Route` — owns `hiltViewModel()`, navigation callbacks, `remember` UI-only state (dialogs, tooltips)
- `{Feature}Screen` — pure UI: nhận `UiState` + callbacks, không biết ViewModel

**Rules:**
- `remember` = UI-only state | ViewModel = business state
- Modifier order: `size → clip → background → padding → interaction`
- testTag format: `"{Feature}_{Component}"` cho non-text nodes
- Reuse shared `LoadingView`, `EmptyView`, `ErrorView` thay vì tự tạo

---

## Test Strategy

Mỗi task phải declare: **test-first** | **test-after** | **no test needed**

```
Plan → Pseudo code → Test-first (business logic) → Implement → Test-after (UI) → Simplify
```

Pseudo code bắt buộc trước khi viết test — xác định interface, input/output, edge cases.

**Test-first:** ViewModel, Repository, UseCase
**Test-after:** Composable, Navigation (implement → test multi-state/interactions)
**Skip test:** simple delegation, static UI

**Unit test stack:** JUnit4 + MockK + Turbine + `kotlinx-coroutines-test`
- `MainDispatcherRule(UnconfinedTestDispatcher)` — reuse across all VM tests
- Turbine: `flow.test { awaitItem(); cancelAndIgnoreRemainingEvents() }`
- Test names: backtick `` `when X then Y` ``; body: Given / When / Then comments
- Mock only direct dependencies, one assertion focus per test

**UI test stack:** `createComposeRule()` + MockK relaxed ViewModel
- `setContent { AppTheme { Screen(uiState, callbacks) } }`
- `waitForIdle()` sau state changes; `AppTheme {}` wrapper luôn bắt buộc

**Integration test (DB):** `Room.inMemoryDatabaseBuilder()` — never mock DB/DAO; close DB in `@After`

---

## Production Mindset

Before finalizing: thread safety, memory leaks, concurrent access, race conditions, silent failures at scale.

---

## Anti-Patterns

Actively detect and fix: Flow where suspend suffices, business logic in UI, state duplication, scope misuse causing leaks.

---

## Planning Skill Selection

Khi nhận yêu cầu viết plan, tự chọn skill phù hợp — không hỏi lại — và announce rõ lý do:

| Tình huống | Skill | Lý do chọn |
|---|---|---|
| Yêu cầu mơ hồ / chưa rõ intent | `superpowers:brainstorming` trước, rồi mới plan | Plan sai scope còn nguy hơn không plan — brainstorm để clarify intent, constraints, edge case trước khi commit vào hướng cụ thể |
| Feature/bug/refactor rõ ràng, implement 1 lần | `superpowers:writing-plans` | Scope đã xác định → cần breakdown steps, test strategy, package structure; implement ngay sau khi plan được approve |
| Spec cần track dài hạn, revisit nhiều lần, hoặc user dùng từ "spec / design doc / tài liệu" | `openspec-propose` | Spec là living document — cần versioning, diff giữa các lần thay đổi, và khả năng apply/archive độc lập với implementation |

**Announce format:** *"Using `[skill]` vì [lý do 1 câu]"* — sau đó thực thi luôn.

---

## Design Phase Checklist (trước khi viết plan)

1. **API lạ**: đọc code thực tế, spike 20-30 dòng nếu không chắc constraints.
2. **Rendering/WebView**: có scroll container, overflow clipping, CSS transform ảnh hưởng đến print/export không?
3. **UI component mới**: tìm component có sẵn trong codebase trước.
4. **Async/Cancellation**: design cancel path ngay từ đầu — điều gì xảy ra khi user cancel/background?
5. **Dialog UX**: dismiss condition phụ thuộc async step nào?

---

## Timeline Format

Dùng timeline khi giải thích async flow, coroutine lifecycle, race condition:
```
t=0  User taps → ViewModel.start() → emits Loading
t=1  Repo fetches → emits Success
```

---

## Secrets Policy

**Không bao giờ lưu API key, token, secret, password vào memory** — kể cả dưới dạng reference. Nếu cần nhớ token, chỉ ghi "token đã được set" không ghi giá trị thực.

---

## Periodic Backup

Cuối session, backup tự động (không hỏi):
```bash
rsync -av --delete ~/.claude/CLAUDE.md /home/khapv/Claude_Usage/my_claude_skills/CLAUDE.md
rsync -av --delete ~/.claude/settings.json /home/khapv/Claude_Usage/my_claude_skills/settings.json
rsync -av --delete ~/.claude/skills/ /home/khapv/Claude_Usage/my_claude_skills/skills/
rsync -av --delete --exclude="*token*" --exclude="*secret*" --exclude="*key*" --exclude="*credential*" --exclude="*password*" ~/.claude/projects/*/memory/ /home/khapv/Claude_Usage/my_claude_skills/memory/
```