---
name: feedback-ask-when-uncertain
description: "User explicitly wants to be consulted the moment something is uncertain, instead of proceeding on a guess and letting the mistake surface later"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6cbd5958-fb0d-4789-b5ef-c4357246df40
  modified: 2026-08-28T02:11:14.439Z
---

When uncertain about a design/layout/behavior detail — especially something I can't directly verify (no way to render Compose UI myself, ambiguous Figma measurement, conflicting signals) — stop and ask the user immediately instead of picking the most-likely guess and proceeding.

**Why:** during the audio_editor "Generate" redesign, several rounds of guessing (icon color from a screenshot instead of the exported SVG, divider gap eyeballed instead of computed, `weight` vs fixed sizing applied without checking the sibling relationship first) produced visible bugs the user had to catch one by one, escalating to "bạn làm UI kém thế" / "sai nhiều thế". The user then said directly: "Nếu bạn thấy nghi ngờ thì trao đổi ngay với tôi để tìm hướng đúng."

**How to apply:** the moment a decision hinges on something I cannot verify from the data at hand (can't render the UI, Figma metadata is ambiguous/missing, two plausible interpretations of a requirement), pause and ask a concrete question before writing code — don't ship a guess and wait for the user to catch it visually. This is stricter than the general "ask clarifying questions" habit: it means treating uncertainty itself as a stop signal, not just genuine ambiguity in the request. See [[feedback-figma-full-property-audit]] and [[feedback-compose-fillmaxwidth-propagation]] for the concrete failure pattern this addresses.
