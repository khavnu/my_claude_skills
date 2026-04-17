---
name: android-context-extensions
description: Use when creating or working in a new Android project and need standard reusable Kotlin extension functions for Activity, Fragment, Context, View, and Flow — covers safe dialog show, debounced click, lifecycle-aware Flow collection, keyboard control, permission checks, network check, and animated visibility
---

# Android Context Extensions

Reusable Kotlin extension functions for Android projects. Create these files in `extension/` package on first use.

## ActivityExtension.kt

```kotlin
// Safe show — guards: Activity destroyed, FragmentManager state saved, duplicate tag, lifecycle < RESUMED
fun FragmentActivity.safeShowDialogFragmentOrNot(
    dialogFragment: DialogFragment,
    tag: String,
    onSuccess: () -> Unit = {}
) {
    if (isFinishing || isDestroyed) return
    val fm = supportFragmentManager
    if (fm.isStateSaved) return
    if (fm.findFragmentByTag(tag) != null) return
    if (!lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED)) return
    dialogFragment.show(fm, tag)
    onSuccess()
}

fun AppCompatActivity.dismissDialogByTag(tag: String) {
    (supportFragmentManager.findFragmentByTag(tag) as? DialogFragment)?.dismissAllowingStateLoss()
}

fun Fragment.dismissDialogByTag(tag: String) {
    (childFragmentManager.findFragmentByTag(tag) as? DialogFragment)?.dismissAllowingStateLoss()
}

fun Activity.toggleSoftKeyboard(isShow: Boolean) {
    val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as? InputMethodManager ?: return
    currentFocus?.let { focus ->
        if (isShow) {
            imm.showSoftInput(focus, InputMethodManager.SHOW_FORCED)
        } else {
            imm.hideSoftInputFromWindow(focus.windowToken, 0)
        }
    }
}
```

**Rule:** Always use `safeShowDialogFragmentOrNot` instead of `dialog.show(supportFragmentManager, TAG)`.

**Rule:** Dismiss stale dialogs after process restart in `onResume()`, NOT in `onStart()` or Flow collectors. `DialogFragment.mDialog` is null until `dispatchStart()` completes — dismissing too early has no effect.

---

## FlowExtension.kt

```kotlin
fun <T> Flow<T>.collectWhenStarted(lifecycleOwner: LifecycleOwner, collector: suspend (T) -> Unit) {
    lifecycleOwner.lifecycleScope.launch {
        lifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            collect { collector(it) }
        }
    }
}

fun <T> Flow<T>.collectWhenResumed(lifecycleOwner: LifecycleOwner, collector: suspend (T) -> Unit) {
    lifecycleOwner.lifecycleScope.launch {
        lifecycleOwner.repeatOnLifecycle(Lifecycle.State.RESUMED) {
            collect { collector(it) }
        }
    }
}

// 6-arg combine (standard library only goes to 5)
fun <T1, T2, T3, T4, T5, T6, R> combine(
    flow: Flow<T1>, flow2: Flow<T2>, flow3: Flow<T3>,
    flow4: Flow<T4>, flow5: Flow<T5>, flow6: Flow<T6>,
    transform: suspend (T1, T2, T3, T4, T5, T6) -> R
): Flow<R> = kotlinx.coroutines.flow.combine(flow, flow2, flow3, flow4, flow5, flow6) { args: Array<*> ->
    @Suppress("UNCHECKED_CAST")
    transform(args[0] as T1, args[1] as T2, args[2] as T3, args[3] as T4, args[4] as T5, args[5] as T6)
}
```

**Note:** `collectWhenStarted` fires synchronously via `Dispatchers.Main.immediate` during `ComponentActivity.onStart()`, BEFORE `mFragments.dispatchStart()`. Do not use it to dismiss dialogs — use `onResume()` instead.

---

## ContextExtension.kt

```kotlin
fun Context.hasPermission(permission: String): Boolean =
    ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED

// API-aware: WRITE_EXTERNAL_STORAGE not needed on API 30+
fun Context.hasWriteStoragePermission(): Boolean {
    if (Build.VERSION.SDK_INT > Build.VERSION_CODES.Q) return true
    return ActivityCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) ==
            PackageManager.PERMISSION_GRANTED
}

fun Context.openDetailSettings() {
    startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
        data = Uri.fromParts("package", packageName, null)
        addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_NO_HISTORY or Intent.FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS)
    })
}

fun Context.isNetworkAvailable(): Boolean {
    return try {
        val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val nw = cm.activeNetwork ?: return false
        val caps = cm.getNetworkCapabilities(nw) ?: return false
        caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ||
            caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ||
            caps.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET)
    } catch (_: Exception) { false }
}

fun Context.isTablet(): Boolean = resources.configuration.smallestScreenWidthDp >= 600

fun Context.showShortToast(msg: String) = Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
fun Context.showShortToast(@StringRes res: Int) = showShortToast(getString(res))
fun Context.showLongToast(msg: String) = Toast.makeText(this, msg, Toast.LENGTH_LONG).show()
fun Context.showLongToast(@StringRes res: Int) = showLongToast(getString(res))
```

---

## ViewExtension.kt + DebouncingOnClickListener.kt

```kotlin
// DebouncingOnClickListener.kt — prevents double-tap
class DebouncingOnClickListener(
    private val intervalMillis: Long,
    private val doClick: (View) -> Unit
) : View.OnClickListener {
    override fun onClick(v: View) {
        if (enabled) {
            enabled = false
            v.postDelayed(ENABLE_AGAIN, intervalMillis)
            doClick(v)
        }
    }
    companion object {
        @JvmStatic var enabled = true
        private val ENABLE_AGAIN = Runnable { enabled = true }
    }
}

// ViewExtension.kt
fun View.setOnSingleClickListener(intervalMillis: Long = 300, doClick: (View) -> Unit) =
    setOnClickListener(DebouncingOnClickListener(intervalMillis, doClick))

fun View.showKeyboard() {
    val imm = context.getSystemService(Context.INPUT_METHOD_SERVICE) as? InputMethodManager
    if (imm != null && requestFocus()) imm.showSoftInput(this, InputMethodManager.SHOW_IMPLICIT)
}

fun View.hideKeyboardAndClearFocus() {
    val imm = context.getSystemService(Context.INPUT_METHOD_SERVICE) as? InputMethodManager
    imm?.hideSoftInputFromWindow(windowToken, 0)
    clearFocus()
}

fun View.smoothShow(duration: Long = 300, onEnd: () -> Unit = {}) {
    if (visibility != View.VISIBLE || alpha < 1f) {
        animate().cancel()
        alpha = 0f
        visibility = View.VISIBLE
        animate().alpha(1f).setDuration(duration).withEndAction { onEnd() }.start()
    }
}

fun View.smoothHide(duration: Long = 300, onEnd: () -> Unit = {}) {
    if (visibility == View.VISIBLE && alpha > 0f) {
        animate().cancel()
        animate().alpha(0f).setDuration(duration).withEndAction { visibility = View.GONE; onEnd() }.start()
    }
}

fun View.slideDownHide(duration: Long = 300) {
    animate().translationY(height.toFloat()).setDuration(duration)
        .withEndAction { visibility = View.GONE }.start()
}

fun View.slideUpShow(duration: Long = 300) {
    visibility = View.VISIBLE
    animate().translationY(0f).setDuration(duration).start()
}

fun View.disableClick() { isFocusable = false; isClickable = false }
fun List<View?>.disableClick() = forEach { it?.disableClick() }
```

---

## Quick Reference

| Function | File | Purpose |
|---|---|---|
| `safeShowDialogFragmentOrNot` | ActivityExtension | Safe dialog show with 4 guards |
| `dismissDialogByTag` | ActivityExtension | Dismiss by tag |
| `collectWhenStarted` | FlowExtension | Lifecycle-aware Flow collection |
| `collectWhenResumed` | FlowExtension | Collection only when RESUMED |
| `combine` (6 args) | FlowExtension | Extend standard 5-arg combine |
| `hasPermission` | ContextExtension | Generic permission check |
| `hasWriteStoragePermission` | ContextExtension | API-aware write storage |
| `openDetailSettings` | ContextExtension | Navigate to app permission settings |
| `isNetworkAvailable` | ContextExtension | Network check with SecurityException fallback |
| `isTablet` | ContextExtension | sw >= 600dp |
| `setOnSingleClickListener` | ViewExtension | Debounced click (300ms default) |
| `smoothShow` / `smoothHide` | ViewExtension | Animated visibility |
| `slideDownHide` / `slideUpShow` | ViewExtension | Slide animation |
| `showKeyboard` / `hideKeyboardAndClearFocus` | ViewExtension | IME control |
