---
name: grill-with-docs
version: 1.0.1
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree — while maintaining a running project glossary and recording ADRs for decisions that are hard to reverse, surprising, and a genuine tradeoff. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me". Supports --batch flag for human design sessions. Replaces /grill-me.
changelog:
  - "1.0.1 (2026-10-04): Shortened the description to under 500 characters so claude.ai stores it in full. The attribution moved here: glossary and ADR maintenance are adapted from mattpocock/skills (grill-with-docs / grilling / domain-modeling)."
  - "1.0.0 (2026-09-01): Replaces /grill-me. Same interview mechanic (one-at-a-time / --batch, recommended answers, facts-vs-decisions, decision-tree resolution) plus two additions: glossary maintenance (glossary.md) and ADR creation (adr/) for qualifying decisions, resolved live during the interview rather than as a wrap-up step."
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer. Two things happen alongside the interview, not after it: ambiguous terminology gets pinned into the project glossary, and decisions that qualify get written up as ADRs — both as they're resolved, not as a wrap-up step at the end.

## Mode

**Default (no flag):** Ask questions one at a time. Wait for the answer before continuing. This is the mode for autonomous agent design sessions where the decision tree must be resolved in order.

**`--batch` flag:** If the user runs `/grill-with-docs --batch`, group all open questions by category and present them together. The human can answer several at once, skip questions they've already resolved, and reorder their responses. Use batch mode when the human is driving the design session interactively and one-at-a-time is too slow.

Batch output format:

```
## Open questions — [category]

1. [Question] — Recommended: [answer]
2. [Question] — Recommended: [answer]

## Open questions — [category]

3. [Question] — Recommended: [answer]
```

After the human responds to a batch, identify which questions remain unresolved and present a follow-up batch for those only.

## Rules (both modes)

- If a question can be answered by exploring the codebase, explore the codebase instead of asking.
- Do not re-ask a question that was answered earlier in the session.
- Distinguish facts from decisions: a fact (what an API returns, what a term already means elsewhere in the codebase) is something you research yourself; a decision (which of several valid approaches to take) is the human's to make. Don't block unrelated questions on a fact lookup still in progress.
- Stop when every branch of the decision tree is resolved and confirm: "Decision tree fully resolved. Here is a summary of all decisions made:" followed by a compact list — plus any glossary terms pinned and ADRs written this session.

## Glossary maintenance (glossary.md)

- When a term in the plan is ambiguous, conflicts with existing usage, or is about to be used precisely for the first time, pin it down as a question in the interview rather than letting it slide.
- Keep `glossary.md` (repo root, or the feature's Drive subfolder if the repo has no root glossary yet) a pure glossary: term → one-line canonical definition. No implementation details, no specs, no decisions — those belong in `context.md` ([context-schema.md]). The two files are never the same file and never merge.
- Update `glossary.md` immediately when a term crystallizes during the session, not as a batch at the end.
- Reading `glossary.md` to check existing vocabulary doesn't count as using this skill — only pinning down a *new or contested* term during an active grilling session does.

## ADR creation (adr/)

- Write an ADR only when all three hold: the decision is hard to reverse, it would be surprising to a future reader without documentation, and it represents a genuine tradeoff between real alternatives. Most resolved branches in a grilling session are ordinary decisions, not ADRs — reserve ADRs for this subset.
- File it under `adr/` as `NNNN-title.md` (sequential numbering; see the existing references in [design-loop.md]), using Context / Decision / Consequences as the three sections.
- If the repo has no `adr/` folder yet, create it (`/setup-project` scaffolds this for new repos — see [setup.md]).
- Link any ADR written during the session from `spec.md`'s context section if it affects the feature currently being designed.
