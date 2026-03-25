---
name: new-feature
description: Scaffold a new Android feature with proper MVVM structure — Activity/Fragment, ViewModel, UiState, Hilt DI wiring.
---

# New Android Feature Scaffold

You are scaffolding a new Android feature following Clean Architecture + MVVM.

The user will describe what feature they want. Ask for any missing information before generating code:
- Feature name
- Entry point: Activity or Fragment?
- Does it need a BottomSheet dialog?
- What data does it need from Repository?

---

# Files to generate

For a feature named `MyFeature`, create:

```
feature/my_feature/
├── MyFeatureActivity.kt         # or MyFeatureFragment.kt
├── MyFeatureViewModel.kt
└── model/
    └── MyFeatureUiState.kt
```

And register in:
- `AndroidManifest.xml` (if Activity)
- Hilt module if new Repository binding is needed

---

# Templates

## UiState

```kotlin
data class MyFeatureUiState(
    val isLoading: Boolean = false,
    // add fields here
)
```

## ViewModel

```kotlin
@HiltViewModel
class MyFeatureViewModel @Inject constructor(
    private val repository: SomeRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(MyFeatureUiState())
    val uiState: StateFlow<MyFeatureUiState> = _uiState.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = MyFeatureUiState()
    )
}
```

## Activity

```kotlin
@AndroidEntryPoint
class MyFeatureActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMyFeatureBinding
    private val viewModel: MyFeatureViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMyFeatureBinding.inflate(layoutInflater)
        setContentView(binding.root)
        subscribeObservers()
    }

    private fun subscribeObservers() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { renderState(it) }
            }
        }
    }

    companion object {
        fun open(context: Context) {
            context.startActivity(Intent(context, MyFeatureActivity::class.java))
        }
    }
}
```

## Fragment → Activity BottomSheet communication

Always use `activityViewModels()` — never `setFragmentResult`.

```kotlin
@AndroidEntryPoint
class MyBottomSheet : ThemeBottomSheetDialog() {
    private val viewModel: MyFeatureViewModel by activityViewModels()
}
```

---

# Rules

- UiState must be a `data class` with default values
- ViewModel exposes `StateFlow`, never `LiveData`
- Activity/Fragment only observes state — no business logic
- If passing data to Activity, use `companion object { fun open(context, id) }` pattern
- Always run the compile check command defined in project CLAUDE.md after generating (fallback: `./gradlew compileDebugKotlin`)