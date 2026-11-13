---
name: splash-resets-status-bar-color
description: "API 31-34 status bar band (#252753) after cold start = core-splashscreen copying the theme's statusBarColor over enableEdgeToEdge(); fixed by android:statusBarColor transparent in BaseAppTheme."
metadata:
  node_type: memory
  type: project
  originSessionId: 3eb82f20-c3e8-4cda-8e47-e6cee19550cd
  modified: 2026-11-09T02:05:13.801Z
---

core-splashscreen 1.0.1 `SplashScreen.Impl31.applyAppSystemUiTheme()` (SplashScreen.kt:479 in the sources jar) and `SplashScreenViewProvider.remove()` write `window.statusBarColor` / navigationBarColor / light appearance from the post-splash theme, AFTER `FullScreenActivity.enableEdgeToEdge()`. With no `android:statusBarColor` in AppTheme the AppCompat default `?colorPrimaryDark` (#252753) painted a band behind the status bar on API 31-34 until a recreate (Change theme) — API 35+ ignores statusBarColor, so the API 36 emulator never shows it. Found on Pixel 4 XL API 33, 2026-11-09; fix = `<item name="android:statusBarColor">@android:color/transparent</item>` in `values/themes.xml` BaseAppTheme.

**Why:** cost a long search: grep for statusBarColor in Kotlin finds nothing; the writer is inside the library.

**How to apply:** any system-bar color/appearance that differs between cold start and after a recreate on API 31-34 → check the theme attrs the splash library copies (statusBarColor, navigationBarColor, windowLightStatusBar/NavigationBar, enforce*Contrast), not app code. Verify on an API 31-34 device with a cold start (`am force-stop` then launch), sampling pixel colors of the status bar band.
