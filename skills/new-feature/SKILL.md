---
name: new-feature
description: Scaffold a new Android feature with proper MVVM structure — Composable Route+Screen, ViewModel, UiState, NavKey, Hilt wiring. Uses Compose + Navigation3.
---

# New Android Feature Scaffold

Follow Clean Architecture + MVVM. Project uses **Jetpack Compose + Navigation3** — no Activity/Fragment for features.

Ask for missing info before generating:
- Feature name
- NavKey params needed (if any)
- What data from Repository?
- Does it need a BottomSheet?

---

## File Structure

```
feature/{name}/
├── {Name}Screen.kt       # Route + Screen composables
├── {Name}ViewModel.kt    # ViewModel + ViewModelState (co-located)
└── {Name}UiState.kt      # UiState data class + UiEvent sealed interface
```

NavKey goes in `navigation/NavKey.kt` (no params) or alongside the feature if params needed.

---

## Templates

### NavKey (`navigation/NavKey.kt`)
```kotlin
@Serializable
data class MyFeature(val id: Long) : NavKey   // with params

@Serializable
data object MyFeature : NavKey                 // no params
```

### UiState (`MyFeatureUiState.kt`)
```kotlin
data class MyFeatureUiState(
    val isLoading: Boolean = false,
    // fields here
)

sealed interface MyFeatureEvent {
    data object NavigateBack : MyFeatureEvent
}
```

### ViewModel (`MyFeatureViewModel.kt`)
```kotlin
@HiltViewModel
class MyFeatureViewModel @Inject constructor(
    private val repository: SomeRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(ViewModelState())
    val uiState: StateFlow<MyFeatureUiState> = _state
        .map { it.toUiState() }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), ViewModelState().toUiState())

    private val _events = Channel<MyFeatureEvent>()
    val events: Flow<MyFeatureEvent> = _events.receiveAsFlow()
}

private data class ViewModelState(
    val isLoading: Boolean = false,
) {
    fun toUiState() = MyFeatureUiState(isLoading = isLoading)
}
```

### Screen (`MyFeatureScreen.kt`)
```kotlin
@Composable
fun MyFeatureRoute(
    onBack: () -> Unit,
    viewModel: MyFeatureViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    MyFeatureScreen(uiState = uiState, onBack = onBack)
}

@Composable
fun MyFeatureScreen(
    uiState: MyFeatureUiState,
    onBack: () -> Unit,
) {
    // pure UI — no ViewModel here
}
```

### NavEntry (in `CamScannerNavigation.kt`)
```kotlin
is MyFeature -> NavEntry(key) {
    MyFeatureRoute(
        onBack = { backStack.removeLast { } },
    )
}
```

---

## Rules

- `Route` = hiltViewModel() + navigation lambdas + `remember` UI state (dialogs)
- `Screen` = pure UI, receives UiState + callbacks only
- UiState/Event declared at **bottom** of ViewModel file — never above the class
- `modifier` is always first param in every `@Composable`
- One-time events → `Channel` + `receiveAsFlow()`, never `SharedFlow`
- No `!!`, no hardcoded strings, no `Log.d` (use Timber)
- Compile after generating: `./gradlew :app:compileDebugKotlin`