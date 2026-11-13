---
name: pattern-compose-test-hangs
description: "Compose UI tests that hang forever (no assertion error) — waveform with null samples, and performScrollTo on a zero-height scroll viewport; always wrap connected runs in `timeout`"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 87fb5981-5bf1-470a-9072-56ede1d33a2e
  modified: 2026-10-13T11:53:49.243Z
---

Seen 2026-10-13 while writing landscape layout tests (FadeScreenTest, ConvertScreenTest):
- A screen whose waveform gets `waveformSamples = null` shows `WaveformLoading`, an infinite animation → `waitForIdle` never returns and `connectedDebugAndroidTest` runs until the shell timeout. Feed `WaveformSamples(FloatArray(200) { 0.5f })` in test state (same root as [[pattern-blocking-jni-timeout-detached]]: null samples = loading, not error).
- `performScrollTo()` on a node inside a `verticalScroll` whose viewport is ~0dp (portrait layout squeezed into an 800x360 test page, before the landscape branch exists) loops forever. The RED step for a scroll test therefore hangs instead of failing — run only the non-scroll tests for RED, and run the scroll test after implementing.

**Why:** a hang looks like a slow build; I lost ~10 min twice before noticing.
**How to apply:** run connected tests as `timeout 300 ./gradlew ... > log; echo exit $?`; exit 124 = hang → suspect the two causes above first. Never `pkill -f connectedDebugAndroidTest` from the same shell — it matches its own command line and kills the shell (exit 144).
