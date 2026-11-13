---
name: pattern-workmanager-ten-minute-not-a-cap
description: Plain OneTimeWorkRequest is NOT cut at 10 minutes on Android 16 (foreground or background); 10 min is the minimum guarantee
metadata:
  type: project
---

On 2026-10-20 an emulator running Android 16 ran a probe CoroutineWorker for 13 minutes as a plain `OneTimeWorkRequest`, with no `setForeground` and no `setExpedited`. It finished SUCCEEDED in one attempt both with the app in the foreground and with the app in the background after pressing Home. Logcat showed: `JobServiceContext: Letting … SystemJobService continue to run past min execution time`.

**Why:** a `/code-review` finding said the video workers (`WorkManager*Runner`) would be cut at 10 minutes and retried forever. The probe disproved it for normal conditions, so the finding was downgraded in `.reviews/review-video-compress.md`. Not covered: an exhausted job quota, the Restricted bucket, Doze, and running on battery (the probe ran on a charging emulator under instrumentation).

**How to apply:**
- Don't claim "jobs die at 10 minutes" without re-measuring.
- Probe shape: a CoroutineWorker class in androidTest, enqueued from an instrumented test that polls `WorkInfo` every 30 s for 14 min. Pass `-e foreground false` to skip launching the activity.
- The test function needs an explicit `runBlocking<Unit>`, or JUnit rejects the class as invalid.
