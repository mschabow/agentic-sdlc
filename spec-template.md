# SPEC Template

The SPEC is the locus of rigorous review and a living artifact. It lives in the repo (e.g. `designs/<feature>/spec.md`) alongside its distilled context file, so both are version controlled and prior designs can be recovered and reused.

**Spec approval happens as a GitHub PR.** The spec is submitted for review as a pull request; lead approval on that PR is the gate before any implementation tickets are created.

---

## Feature: <name>

**Linear ticket:** <link>
**Status:** Draft | In review | Approved | Implemented | Updated post-build
**Last updated:** <date>

## Problem statement

What this feature does and why, in plain language. 2–4 sentences.

## Design

The specific design being implemented: components touched, interfaces, data flow, and any diagrams. Diagrams should be committed as Mermaid or other diagrams-as-code so they are readable and editable by agents. This is where lead review effort concentrates.

## Context file

Link to `context.md` — the pass-2 distilled context this spec was refined against. The build consumes only that file plus the repo.

**Context file rules:**
- Sources may be Google Docs, Linear, and specific code files.
- Slack must not be a source. If relevant information exists only in Slack, capture it in a Google Doc, Linear comment, or ADR before building the context file.

## Acceptance criteria

Mirror of the acceptance criteria in the linked Linear ticket. These two must stay in sync — if one changes, update the other.

1. Criterion 1
2. Criterion 2

## Draft test list

Produced during the design phase for each acceptance criterion above. Reviewed as part of the design PR. The Pass 2 build agent uses this as the frozen baseline — it implements these tests first, then builds to pass them. Additional tests may be added during the build for edge cases; spec-derived tests may not be silently deleted or weakened.

If a criterion cannot be turned into a concrete test case here, the criterion is too vague — sharpen it before the design PR is approved.

| Criterion | Test case | Input | Expected outcome |
|---|---|---|---|
| Criterion 1 | Test 1a | ... | ... |
| Criterion 1 | Test 1b | ... | ... |
| Criterion 2 | Test 2a | ... | ... |

## Out of scope

Explicit exclusions.

## Deviation log

If the build deviated from this spec, record what changed and why, and update the Design and Acceptance criteria sections to match the implemented code. Never preserve inaccurate information.

| Date | Deviation | Sections updated |
|---|---|---|
| | | |

---

## Conventions

1. Code comments in the implementation link back to this spec.
2. Spec approval (lead review via GitHub PR) gates the creation of implementation tickets.
3. The spec and `context.md` are updated together when reality diverges from plan.
4. Acceptance criteria here and in the Linear ticket are identical; treat any divergence as a bug to fix immediately.
5. The draft test list is reviewed alongside acceptance criteria in the design PR. If the build reveals a test case was wrong, the correction must be noted in the PR and this section updated — never silently changed.
