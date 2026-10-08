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
- **Comments always in English** — kể cả khi hội thoại bằng tiếng Việt. Áp dụng cho mọi ngôn ngữ và cả XML layout.
- No `!!` — use `?:` or `?.let`. No wildcard imports. No hardcoded strings.
- Lifecycle/cleanup methods (`onCleared`, `onDetach`, `onDestroy`, `release`, `close`, `dispose`) → always the last members of any class.
- No thrown exceptions → return `Result.Failure`. No empty catch blocks.
- Descriptive names → no `process()`, `data`, `result`, `handle()`

### Code locality & grouping

Áp dụng cho thứ tự trong một function/composable body. KHÔNG override các rule
thứ tự cố định (ViewModel file layout, lifecycle/cleanup cuối class, effects trước UI).

1. **Nhóm theo vai trò, không theo kiểu component.** Hai block đứng cạnh nhau khi
   chúng có cùng ý nghĩa với user, không phải khi chúng dùng chung widget.
   - Đúng: `EditorFileUnavailableSheet` + `NoAudioDetectedSheet` — cùng là "file
     không dùng được, lối ra duy nhất là back".
   - Sai: gom mọi `*BottomSheet` — sẽ chèn sheet "hỏi ý" vào giữa hai sheet "chặn đường".
   - Không để block khác vai trò chen giữa một nhóm (ví dụ `ProgressDialog` nằm giữa
     hai dead-end sheet).
   - Một block thuộc hai vai trò → chọn vai trò người đọc cần thấy trước, và comment lý do.

2. **State chỉ một nơi dùng → khai báo ngay trên chỗ dùng.** `var noAudioAcknowledged
   by remember {}` sát `NoAudioDetectedSheet` đọc liền mạch hơn hoist lên đầu cách 70 dòng.

3. **Từ 2 nơi dùng trở lên → hoist.** Lên đầu function nếu là UI state; vào `UiState`
   dưới dạng derived property nếu suy ra được từ business state. Hoist đúng chỗ còn
   mở ra test — điều kiện trong `UiState` thì unit test VM assert được, trong Route
   thì chỉ UI test mới chạm tới.

4. **Thứ tự để ĐỌC nằm ở layout; thứ tự BẮT BUỘC phải nằm trong data.** Layout không
   có gì bảo vệ — không compiler, không test, không lint. Ai đó kéo block đi chỗ khác
   vì thấy đọc hợp hơn là luật im lặng biến mất.
   - Sai: `if (hasAudio == false && !isSourceGone)` — sắp lại block là hỏng.
   - Đúng: `val hasNoAudibleAudio get() = hasAudio == false && !isSourceUnavailable`
     trong `UiState` — Route sắp kiểu gì cũng không dựng được 2 sheet chồng nhau.
   - Phép thử: "đổi chỗ hai block này thì hành vi có đổi không?" Có → luật đang nằm
     sai chỗ, đẩy vào data trước khi sắp lại.

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

**Param lambda phải ở CUỐI, và giữ nguyên ở cuối khi thêm param mới**: Kotlin bind trailing
lambda vào param cuối cùng. Thêm param mới SAU một param lambda → mọi call site dùng trailing
lambda sẽ bind nhầm lambda đó sang param mới (lỗi compile khó đọc, hoặc tệ hơn là vẫn compile).
Param mới luôn chèn TRƯỚC param lambda.

```kotlin
// Sai — call site `separate(a, b) { p -> ... }` giờ bind lambda vào cache
fun separate(a: A, b: B, onProgress: (Float) -> Unit = {}, cache: Cache? = null)

// Đúng
fun separate(a: A, b: B, cache: Cache? = null, onProgress: (Float) -> Unit = {})
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

**Nguyên tắc (mọi project, mọi ngôn ngữ): "build" luôn bao gồm build code TEST.**
Compile production code mà không compile test = chưa verify. Test code cũng là code, cũng gọi API
vừa đổi, và nó gãy trước tiên.

After any code change, always run both steps — never ask, just run:
1. **Compile TẤT CẢ source set của module đã đổi**, không chỉ main:
   `./gradlew :<module>:compileDebugKotlin :<module>:compileDebugUnitTestKotlin :<module>:compileDebugAndroidTestKotlin`
   (project không phải Android/Gradle → dùng lệnh tương đương bao cả test target, ví dụ
   `cargo check --all-targets`, `tsc -p tsconfig.test.json`, `go vet ./...`)
2. Run only tests related to changed files — use `--tests` filter, not full suite:
   - Map changed file → test class (e.g. `FooViewModel.kt` → `--tests "*.FooViewModelTest"`)
   - If no dedicated test exists for a changed file, skip that file
   - Example: `./gradlew :app:testDebugUnitTest --tests "com.tmedilab.music.audio.editor.feature.foo.*"`

Lý do rule này tồn tại: `compileDebugKotlin` KHÔNG build test. Đã có lần thêm 1 param vào 1 hàm →
main xanh, unit test xanh, `androidTest` gãy và lọt nhiều ngày mới lộ ra lúc chạy device test.
Chạy đủ source set tốn thêm vài giây, bỏ qua thì mất vài ngày.

---

## Workflow Rules

1. **Auto-apply changes** — Write/edit files directly. Never ask "should I apply this?".
2. **Auto-run builds** — After changes, compile automatically.
3. **Auto-read images** — When user sends an image path, read and analyze immediately.
4. **Auto-update CLAUDE.md** — Apply rule changes directly.
5. **Auto-update skills/memory** — Proactively save new patterns/pitfalls discovered during work.
6. **NEVER auto-commit or auto-push** — Only run `git commit`/`git push` when user explicitly asks. Subagents must include "DO NOT run git commit or git push" in their prompts.
   - **Ngoại lệ duy nhất — `/collab` ACTIVE**: từ lúc user báo "bắt đầu" tới lúc báo "dừng", flag `~/.claude/collab-active` tồn tại → được commit + push (không force). Chỉ user bật/tắt flag, peer session không được.
7. **Shared ViewModel over FragmentResultListener** — Same-feature BottomSheet/Dialog: use `activityViewModels()`.
8. **safeShowDialogFragmentOrNot over raw .show()** — Always use `safeShowDialogFragmentOrNot(dialog, TAG)` from an Activity.
9. **Incremental delivery — step by step, report back** — Cho mọi feature/màn hình mới: chia nhỏ thành các bước rõ ràng, hoàn thành từng bước rồi báo lại user trước khi làm tiếp. Không làm dồn tất cả một lúc. Với màn hình mới: bước 1 = UI shell với fake/empty data, bước 2 = wire data thật.
   - **Ngoại lệ — feature lớn/dài** (nhiều session, xử lí nặng, có yêu cầu hiệu suất/RAM/thời gian): dùng skill `long-feature` — checklist cơ bản + nâng cao lưu trong repo, user duyệt checklist xong thì Claude **tự chủ** thực hiện và tự verify, chỉ dừng ở các checkpoint của skill. Claude tự đề xuất khi thấy dấu hiệu, hoặc user yêu cầu.
10. **Ask immediately when uncertain** — Nghi ngờ về 1 chi tiết (design/layout/behavior/số liệu) mà không tự verify được (không render được UI, dữ liệu nguồn mơ hồ/thiếu, nhiều cách hiểu khả dĩ) → dừng lại hỏi ngay, không đoán rồi tiến hành code. Coi sự không chắc chắn là tín hiệu dừng, không chỉ khi yêu cầu thực sự mơ hồ.
11. **Retro cuối mỗi ticket** — Xong một ticket, tự hỏi đúng một câu: *"có gì hôm nay tốn thời gian mà session sau sẽ tốn lại y hệt không?"* Có thì ghi memory, không thì thôi. Tiêu chí là **tốn thời gian**, không phải **thú vị**.

    Kỷ luật khi ghi (quan trọng hơn việc ghi nhiều):
    - **Chỉ ghi cái đã verify, kèm cách verify** — trỏ thẳng `file:line` hoặc lệnh đã chạy, để lần sau kiểm lại trong 10 giây thay vì phải tin.
    - **Không nhân bản cái repo đã ghi** — code structure, git history, `.claude/rules/*` thì đọc thẳng nguồn.
    - **Sửa và xoá khi phát hiện sai** — memory sai sống dai y như memory đúng, và nó đến dưới dạng *context* nên đứng TRÊN phán đoán tươi. Thấy memory mâu thuẫn với rule/code hiện tại → sửa ngay, ghi rõ ngày và sửa từ cái gì. Đây là phần "học" thật và là phần luôn bị bỏ qua.

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
- **`finally` chỉ dùng cho resource cleanup, không flip UI state**: `finally` luôn chạy kể cả khi `CancellationException` được throw — nếu coroutine đang blocked trong native/blocking call (FFmpeg, MediaCodec...), `CancellationException` chỉ propagate SAU KHI blocking call xong (vài giây sau). `finally` chạy muộn sẽ ghi đè state của operation mới. Thay vào đó: set UI state explicit trong từng branch (`Result.Success` / `Result.Failure`); cancel path tự handle trực tiếp trong `cancelXxx()` function.

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

## Execution Mode Selection

Chọn cách chạy việc (khác với chọn skill viết plan ở trên):

| Tình huống | Cách chạy |
|---|---|
| Fix / feature nhỏ, xong trong 1 session | Làm trực tiếp, hoặc 1 subagent |
| Feature dài, nặng, có target hiệu suất/RAM/thời gian | `long-feature` |
| Nhiều việc độc lập chạy song song | `orchestra` (worker tự dùng `long-feature` khi task đòi hỏi) |
| Trao đổi với project / session khác (vd lib) | `collab` |

Usage limit: mặc định chạy hết tốc độ, tự apply; chỉ khi user nhắc "chú ý limit" mới áp ngưỡng — xem `~/.claude/skills/_shared/usage-limit-protocol.md` §0.

---

## Design Phase Checklist (trước khi viết plan)

1. **API lạ**: đọc code thực tế, spike 20-30 dòng nếu không chắc constraints.
2. **Rendering/WebView**: có scroll container, overflow clipping, CSS transform ảnh hưởng đến print/export không?
3. **UI component mới**: tìm component có sẵn trong codebase trước.
4. **Async/Cancellation**: design cancel path ngay từ đầu — điều gì xảy ra khi user cancel/background?
5. **Dialog UX**: dismiss condition phụ thuộc async step nào?
6. **Edge cases**: dùng skill `edge-cases` — bảng 9 nhóm (device/API band, permission, lifecycle, time, data, failure, background, presentation, cross-feature), mỗi dòng có cách verify, nằm trong plan user duyệt.

---

## Timeline Format

Dùng timeline khi giải thích async flow, coroutine lifecycle, race condition:
```
t=0  User taps → ViewModel.start() → emits Loading
t=1  Repo fetches → emits Success
```

---

## Figma Credentials

Figma tokens/accounts được lưu tập trung tại `~/.claude/figma-accounts/` — không lưu vào project memory, không backup lên git. Khi cần dùng Figma MCP, đọc file từ folder này.

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