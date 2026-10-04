# Lightweight Design Path

**Stage 1 of the [six-stage lifecycle](README.md).** The intent card defined below is the universal Stage 1 artifact: every piece of work — human-initiated or emitted by Stage 6 monitoring, scans, or on-call ([maintain-loop.md](maintain-loop.md)) — enters triage as an intent card. For full-path features the card is brief (What and why + rough criteria) and becomes the input to `/spec-design`, where `/spec` supersedes it. For sub-threshold changes, defined below, the card **is** the design and no spec is written.

Not every change needs a full spec. This document defines a faster path for changes that are small enough that writing a full `spec.md` and `context.md` would cost more than the implementation itself.

## When to use the lightweight path

Use it when **all** of the following are true:

1. The change touches ≤ 3 files and no shared interfaces
2. The acceptance criteria can be stated in ≤ 5 lines
3. The change introduces no new data flow and no new component boundaries
4. No architectural decision is being made — the approach is unambiguous
5. No other team or system depends on the change

If any condition is false, use the full design path. When in doubt, use the full design path — a brief spec is cheaper than discovering mid-build that the scope was wrong.

**Always use the full design path for:**
- Security-critical changes
- Changes to shared interfaces or contracts
- Database schema changes
- New external integrations
- Any change tagged `human-required`

## The intent card

Instead of `spec.md` + `context.md`, a lightweight change produces a single **intent card** committed to the repo at `designs/<feature>/intent.md`.

```markdown
# Intent: <feature name>

**Linear ticket:** <link>
**Type:** Lightweight change
**Last updated:** <date>

## What and why

1–3 sentences. What is changing and why. Plain language.

## Acceptance criteria

- Criterion 1 (observable and testable)
- Criterion 2
- (max 5)

## Files affected

- `path/to/file.ts` — what changes here
- `path/to/other.ts` — what changes here

## Out of scope

- Explicit exclusions to keep the build tight

## Routing

`agent-ready | human-required`
```

The intent card has no Design section, no context.md, and no context pass. The build agent reads only the intent card and `AGENTS.md`.

## Design PR vs. direct implementation ticket

A lightweight change does **not** require a design PR or lead review before the implementation ticket is created. Instead:

- The human creates the intent card
- The human or lead creates the implementation ticket directly in Linear, linking the intent card in the Sources field
- The implementation ticket is routed (`agent-ready` or `human-required`) at creation

If the intent card surfaces ambiguity during the build — the agent asks a question, or the implementation reveals an unexpected dependency — **stop and upgrade to a full design**. Create a design ticket, produce a full spec, and close the lightweight ticket.

## CI for lightweight changes

The `ci/validate-context.sh` script does not apply to intent cards. There is no `context.md` to validate. CI still runs its standard checks (security scans, tests) on the implementation PR.

## Post-ship routing

Lightweight changes follow the same post-ship routing as full-spec changes: bug fix with no design implication → new implementation ticket; behavior change or new constraint → new design ticket (full path, not lightweight).

If a lightweight change repeatedly produces post-ship bugs, that is a signal the change was not actually lightweight — route future changes of this type through the full design path.

## Threshold summary

| Signal | Full design | Lightweight |
|---|---|---|
| Files touched | > 3 or any shared interface | ≤ 3, no shared interfaces |
| Acceptance criteria | Complex or multi-story | ≤ 5 lines |
| Architectural decision | Yes | No — approach is obvious |
| Cross-team impact | Yes | No |
| Security-critical | Yes | No |
| Lead review required before build? | Yes (design PR) | No |
| context.md required? | Yes | No |
| CI context validation? | Yes | No |
