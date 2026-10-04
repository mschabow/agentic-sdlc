---
title: Feature Pipeline v2
description: Fully automated spec → ship loop with retries (2025 edition)
variables:
  phase: spec          # spec → context → code → test → review → done
  feature_slug: login-v2
  max_review_rounds: 3
  review_round: 0
---

# FULLY AUTOMATED FEATURE PIPELINE (2025)

**Current Phase:** `{{phase}}` | Review round: `{{review_round}}/{{max_review_rounds}}`

@if phase == "spec"
  Running Spec Agent...
  /spec-agent

@if phase == "context"
  Running Context Agent...
  /context-agent
  → Set phase = code when done

@if phase == "code"
  Running Code Agent...
  /code-agent
  → Set phase = test when done

@if phase == "test"
  Running Test Agent...
  /test-agent
  → Set phase = review when done

@if phase == "review"
  Running Review Agent...
  /review-agent

  # AUTO-LOOP LOGIC (this is the 2025 secret sauce)
  @if last_yaml.confidence >= 9 or review_round >= max_review_rounds
    → Set phase = done
  @else
    review_round = review_round + 1
    → Append review notes to the original spec
    → Set phase = code
    → "Fixing round {{review_round}}..."

@if phase == "done"
  # FINAL DIFF
  git diff --stat
  git diff HEAD~{{total_commits}} > /diffs/final.patch

  All agents are happy!

  **Ready to merge?** Reply with:
  - yes → I will create PR
  - edit → tell me what to change
  - restart → start over

  Final confidence across all agents: **{{average_confidence}}**/10
