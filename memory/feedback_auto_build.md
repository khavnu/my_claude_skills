---
name: Auto-apply code changes and run gradle builds
description: Always apply code changes and run gradle builds automatically without asking for user confirmation. User reviews after completion.
type: feedback
---

# Auto-apply code changes and run gradle builds

Always apply ALL of the following automatically, without asking for confirmation:

1. **Code changes** — Write, Edit, create files directly. Do not ask "should I apply this?". User will review after completion.
2. **Gradle build commands** — Run `./gradlew :app:compileLiteDebugKotlin` (or relevant variant) automatically after changes. Do not prompt "should I run the build?".

This applies to all projects.
