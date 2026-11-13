---
name: api24-java-util-crash-android6
description: "No coreLibraryDesugaring (minSdk 23): Map.merge/computeIfAbsent/getOrDefault/stream/Optional/java.time crash on Android 6 with NoClassDefFoundError $$ExternalSyntheticLambda, debug and release alike."
metadata:
  type: project
---

Ticket 2102 (2026-11-10): every audio play crashed on Vivo 1606 (API 23) with `NoClassDefFoundError: PlayerStateMapper$$ExternalSyntheticLambda1` — `HashMap.merge(id, 1, Int::plus)` takes a `java.util.function.BiFunction` (API 24). Fixed in ce91ec670 with an `SDK_INT >= N` branch (the user wants a version `if` with a why-comment, not a silent rewrite).

**Why:** app/build.gradle.kts has no `isCoreLibraryDesugaringEnabled`, unit tests run on the JVM (API 24+ available) and lint runs with abortOnError=false, so nothing catches it before an Android 6 device.

**How to apply:** when a crash shows only on Android 6, grep first: `grep -rnE "\.merge\(|computeIfAbsent|getOrDefault\(|putIfAbsent\(|removeIf|\.stream\(\)|java\.util\.Optional|java\.time\." --include=*.kt --include=*.java app/src/main` (ConcurrentHashMap.putIfAbsent is API 1, fine). Android 6 has no crash buffer: read the main logcat. adb is at ~/Android/Sdk/platform-tools/adb (not on PATH).
