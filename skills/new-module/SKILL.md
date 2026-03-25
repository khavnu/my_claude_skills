---
name: new-module
description: Create a new Android Gradle module with the correct convention plugin, package structure, and Hilt setup.
---

# New Android Module

You are creating a new Gradle module following the project's multi-module convention.

Ask the user if not clear:
- Module name and purpose
- Module type: feature / library / core / data / domain

---

# Convention Plugin mapping

| Module type | Convention plugin |
|---|---|
| App entry point | `AndroidApplicationConventionPlugin` |
| Feature module | `AndroidFeatureConventionPlugin` |
| Library (no Compose) | `AndroidLibraryConventionPlugin` |
| Library (with Compose) | `AndroidLibraryComposeConventionPlugin` |
| Uses Hilt | `AndroidHiltConventionPlugin` |
| Uses Room | `AndroidRoomConventionPlugin` |

Always use convention plugins — never duplicate Gradle config manually.

---

# build.gradle.kts template

```kotlin
plugins {
    alias(libs.plugins.android.library)       // or android.feature
    alias(libs.plugins.android.hilt)
}

android {
    namespace = "com.example.feature.myfeature"
}

dependencies {
    implementation(project(":domain"))
    implementation(project(":core:common"))
}
```

---

# Package structure

```
:feature:my-feature
└── src/main/java/com/example/feature/myfeature/
    ├── MyFeatureActivity.kt
    ├── MyFeatureViewModel.kt
    └── model/
        └── MyFeatureUiState.kt
```

---

# Rules

- Namespace must match the module path
- Domain layer must be pure Kotlin — no Android dependencies
- New modules must be registered in `settings.gradle.kts`
- Always run the compile check command defined in project CLAUDE.md after creating (fallback: `./gradlew compileDebugKotlin`)