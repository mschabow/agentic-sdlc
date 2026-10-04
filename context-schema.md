# context.md Schema

`context.md` is the sole hand-off artifact from Pass 1 to Pass 2. Its quality determines build quality. This document defines the required structure, size contract, and discard rules. Both the `/distill-context` skill and the CI validation script enforce these rules.

## Size limit

**300 lines maximum.** If you cannot fit the necessary context in 300 lines, the spec is too broad — split the feature or reduce the scope of the implementation ticket before proceeding.

CI rejects any `context.md` that exceeds this limit.

## Required sections

Every `context.md` must contain exactly these four sections, in this order:

```
## Key decisions
## Constraints
## Relevant code
## External references
```

CI rejects `context.md` if any required section heading is missing or renamed.

### Key decisions

Design choices and their rationale, sourced from Google Drive or Linear. Each entry is one or two sentences: the decision, and why it was made.

- Include: choices with non-obvious rationale (architectural trade-offs, rejected alternatives, deadline-driven cuts)
- Exclude: decisions that are self-evident from the spec itself

### Constraints

Hard limits the build must respect: performance budgets, security requirements, backwards compatibility rules, feature flags, infrastructure constraints, dependency versions.

- Include: anything that would cause an agent to make a wrong assumption if it weren't stated
- Exclude: general good-practice advice — the build agent is expected to apply standard engineering judgment

### Relevant code

Specific files, functions, interfaces, or data structures the implementation must interact with. Enough for the build agent to locate the entry points without a broad codebase search.

Format: file path + brief annotation.

```
src/payments/checkout.ts — CheckoutSession interface (lines 42–67); add new field here
db/migrations/ — migration naming convention: YYYYMMDD_description.sql
```

- Include: exact paths and line ranges for the primary contact points identified in spec.md
- Exclude: general architectural descriptions — those belong in the spec

### External references

Library versions, API endpoints, data schemas, or documentation URLs the build depends on.

```
stripe-node v14.x — use PaymentIntent, not Charge (Charge API deprecated)
https://docs.stripe.com/api/payment_intents — authoritative reference for this build
```

- Include: only what the agent will need to look up during implementation
- Exclude: background reading, general documentation

## Discard rules

Apply these before presenting `context.md` for human confirmation. If any of the following appear, remove them:

| Discard | Reason |
|---|---|
| Slack references | Not a permitted source — capture in Drive or Linear first |
| Superseded documentation | Causes the agent to implement against the wrong version |
| Conflict narratives | Keep the resolution, not the debate |
| Exploratory dead ends | Pollute the agent's reasoning with rejected paths |
| Content not cited by the spec | If spec.md doesn't reference it, the build doesn't need it |
| General advice or conventions | These belong in AGENTS.md, not context.md |

## Source traceability

Every item in `context.md` must trace to one of:

- A specific Google Drive document (link or filename)
- A specific Linear ticket or comment (ticket ID)
- A specific file in the repo (path)

Untraceable content — paraphrased recollections, summaries of summaries — must be removed or re-sourced.

## CI validation

The script `ci/validate-context.sh` runs on every branch that touches a file matching `designs/*/context.md`. It checks:

1. File exists and is not empty
2. Line count ≤ 300
3. All four required section headings are present
4. No Slack URLs or "slack.com" references

See `ci/validate-context.sh` for the exact checks. Run it locally before pushing:

```bash
ci/validate-context.sh designs/<feature>/context.md
```
