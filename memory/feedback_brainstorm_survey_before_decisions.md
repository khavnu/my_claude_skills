---
name: feedback_brainstorm_survey_before_decisions
description: Early-stage feature brainstorming should stay at options/feasibility level before drilling into implementation decisions
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a09c713c-d65b-4be5-80a4-18124fe14aef
  modified: 2026-08-19T08:54:14.349Z
---

When a feature request is still at the "bạn có ý tưởng gì" (do you have ideas) stage, don't immediately drill into sequential decision-forcing clarifying questions (model variant, service architecture, etc.) per the brainstorming skill's default cadence. User explicitly said "chúng ta sẽ trao đổi phương án khả thi chứ chưa cần bắt tay vào làm" (we're just discussing feasible options, not committing to implementation yet) after two rounds of pointed technical questions.

**Why:** User wants a survey of the feasibility landscape and trade-offs first — enough to decide if the feature is worth pursuing at all — before locking into specific technical choices (on-device vs cloud, which model variant, service vs blocking UI). Forcing early micro-decisions (e.g. "which Demucs variant?") short-circuits that survey.

**How to apply:** When a feature idea is brand new and the user hasn't signaled readiness to commit, first give a concise overview of 2-3 realistic approaches with rough effort/risk trade-offs (matches [[feedback_sdd_commit_granularity]]-style "propose grouping upfront" habit). Only shift into the brainstorming skill's one-question-at-a-time decision drilling once the user signals they're ready to commit to a direction (e.g. explicitly picks an approach or says "let's proceed/plan it").
