---
name: distill-context
version: 1.3.0
description: Synthesise Pass 1 context into a minimal context.md, then spawn a clean subagent for the build phase with only context.md, spec.md, and AGENTS.md loaded. This is the phase boundary between broad context gathering and predictable building — the current session's noisy Pass 1 context is never seen by the build agent.
changelog:
  - "1.3.0 (2026-10-09): Works with GitHub Issues: a GitHub issue is a valid context source, and the build agent posts its status with `gh issue comment` when the repo uses GitHub Issues. Linear behaviour is unchanged."
  - "1.2.0 (2026-10-03): When /build runs this skill, stop after Step 4. /build spawns the build agents itself (Sonnet, one per ticket, each in its own worktree)."
  - "1.1.0 (2026-06-18): Added schema enforcement step — context.md must conform to context-schema.md (required sections, 300-line limit, no Slack). Added local CI validation before human confirmation."
  - "1.0.0 (initial): Basic distillation and subagent spawn"
---

You are at the boundary between Pass 1 (broad gather) and Pass 2 (clean build). Your job is to distill everything gathered so far into a single, minimal context file, then hand off to a clean build agent.

## Step 1 — Write context.md

Synthesise the Pass 1 context into `designs/<feature>/context.md`. Follow the schema defined in [context-schema.md](../../context-schema.md) exactly.

**Required structure (in this order):**

```
## Key decisions
## Constraints
## Relevant code
## External references
```

Apply these discard criteria ruthlessly — if something does not directly support a decision or constraint in spec.md, it does not belong:

- Discard: anything not directly cited by the spec
- Discard: superseded documentation versions (keep only the current version)
- Discard: conflicting sources that were resolved during Pass 1 (keep the resolution, not the conflict)
- Discard: exploratory dead ends
- Discard: general conventions — those belong in AGENTS.md

**Size limit: 300 lines maximum.** If you cannot fit the necessary context in 300 lines, the spec is too broad. Stop and raise this with the lead.

Every source must trace to Google Drive, a Linear ticket or GitHub issue, or a specific code file. No Slack references.

## Step 2 — Run CI validation locally

Before presenting context.md to the human, run the validation script:

```bash
ci/validate-context.sh designs/<feature>/context.md
```

Fix any reported issues. Do not proceed to Step 3 until the script exits 0.

## Step 3 — Confirm with human

Present context.md to the human for confirmation. Check:
- Does it cover everything the build needs?
- Is anything missing that would cause the build agent to make wrong assumptions?
- Are all sources clean (no Slack)?
- Is anything present that the build doesn't actually need?

Revise until confirmed. Re-run the validation script after any revision that adds lines.

## Step 4 — Commit context.md

Commit `context.md` to the repo alongside `spec.md`. This is the version-controlled hand-off artifact.

## Step 5 — Spawn the build agent

If /build called this skill, stop after Step 4 and return to /build. It spawns one build agent per ticket, each in its own worktree, with the same three files and the same instructions as below. Run this step only when /distill-context is used on its own.

Spawn a subagent with a clean context window. Pass it exactly:
- `AGENTS.md` — repo conventions
- `designs/<feature>/spec.md` — the implementation contract
- `designs/<feature>/context.md` — the distilled context

The subagent's instructions:
> Read AGENTS.md, spec.md, and context.md. Derive the test suite from the acceptance criteria in spec.md — use the draft test list in spec.md as the starting point and freeze it. Do not modify spec-derived tests during the build; add tests for edge cases separately. Implement the feature against context.md and the repo. When the branch is pushed, post a status update to the ticket (Linear, or `gh issue comment` for GitHub Issues). Include the /verify-context verdict in the PR description.

The build agent has no access to Pass 1's context. This is intentional and enforced by the subagent boundary.
