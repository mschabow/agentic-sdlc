# Skill Evaluation and Versioning Framework

Skills are the executable core of this workflow. A bad skill update silently degrades every project. This document defines how skills are versioned, tested before propagation, and rolled back when they regress.

## Principles

- Skills are treated like library dependencies: versioned, with a changelog, with tests that run before a new version ships.
- The canonical source is `.claude/commands/` in this process repo. No other version of a skill is authoritative.
- A skill regression is a production incident — it affects every feature being built on the workflow.

## Version header

Every skill file must include a version header in its frontmatter:

```yaml
---
name: verify-context
version: 1.2.0
description: ...
changelog:
  - "1.2.0 (2026-06-18): Added mechanical git diff step before LLM assessment"
  - "1.1.0 (2026-05-02): Added context staleness threshold table"
  - "1.0.0 (2026-04-15): Initial version"
---
```

Version follows semver: patch for wording/clarity, minor for new behavior, major for restructured flow.

## Eval cases

Each skill has a companion eval file at `.claude/evals/<skill-name>.md`. An eval file contains:

1. **Inputs** — a realistic prompt or scenario the skill would receive
2. **Expected output** — what a correct response looks like (key elements, not exact text)
3. **Failure modes** — what a bad response looks like and how to detect it

Before merging a skill change, run the eval manually (or via automated runner if available) and record the result in the PR description:

```
Eval: verify-context v1.2.0
Input: [brief description of scenario used]
Result: PASS — mechanical diff step fired correctly on a changed file; LLM verdict was STALE with correct attribution
```

A PR that changes a skill without an eval result is not mergeable.

### Minimum eval cases per skill

| Skill | Minimum eval scenarios |
|---|---|
| `/verify-context` | CURRENT verdict (no changes); STALE - context only; STALE - spec change required |
| `/distill-context` | Over-limit context reduced correctly; Slack reference caught and rejected |
| `/grill-with-docs` | One-at-a-time mode resolves full decision tree; batch mode groups correctly; qualifying decision produces an ADR in `adr/`; contested term gets pinned to `glossary.md` |
| `/spec` | Single-story output; multi-story split surfaced |
| `/decompose` | All criteria covered exactly once; dependent ticket flagged |
| `/sync-docs` | Discrepancy correctly attributed to code vs. docs; missing detail surfaced and added on "Add" |
| `/build` | Two independent tickets run as parallel Sonnet subagents in separate worktrees, each reviewed by a fresh Opus subagent, PRs into the collector, nothing merged to main; waves respect blockers, file overlap, and the cap; `build: no-auto-merge` and stop conditions honoured |
| `/review-fix-loop` | Converges when no blocker/major remains; stops on a repeated finding or after three rounds |
| `/worktree-hygiene` | Report lists unpushed work first and treats squash-merged branches as merged; cleanup waits for a yes |
| `/env-handoff` | Write mode produces a complete, pushed doc with no sensitive data; pick-up mode reports drift before acting |
| `/delegated-work-audit` | Scope creep and deletions flagged with evidence; reply drafted, never posted |
| `/linear-implementation-audit` | Each verdict has evidence; updates proposed one at a time, never in bulk |
| `/audit-design` | Vibe-coded feature correctly flagged with no matching `designs/` folder; dangling code identified with correct evidence; retroactive spec.md/context.md drafted and marked as such |

Eval files live at `.claude/evals/` alongside the skill commands.

## Incident-derived evals

Every production incident attributable to the workflow — bad routing, stale context, a skill regression, a hook that failed to block — adds a permanent eval case to `.claude/evals/`, named for the incident (e.g. `incident-2026-08-14-stale-context.md`). Code bugs add tests in the affected repo instead; see [maintain-loop.md](maintain-loop.md) for the full rule.

Incident evals are never deleted. They run with the standard eval set before any skill change propagates, so a fixed failure class stays fixed.

## Propagation process

**Never propagate a skill directly via `cp`. Always follow this sequence:**

1. Open a PR in this process repo modifying the skill file.
2. PR description must include: what was wrong with the prior version, what changed, and eval results (as above).
3. A second person reviews the PR — same standard as a design PR.
4. After merge, update the global install:
   ```bash
   cp .claude/commands/<skill>.md ~/.claude/commands/
   ```
5. Post a one-line note in the team channel: skill name, version, and what changed.

For a patch (wording fix, no behavior change), step 3 may be async — comment approval is sufficient. For minor or major, synchronous lead review is required.

## Version pinning

If a project must be isolated from a skill update (mid-build, freeze period), run `/setup-project` to copy the current skills into `.claude/commands/` at the repo root. Project-scoped skills take precedence over global ones.

Document the pin in `AGENTS.md`:

```
# Skill version pins
verify-context: 1.1.0 (pinned 2026-06-01, unpin after current sprint)
```

Unpin promptly — pinned versions accumulate debt.

## Routing instrumentation and feedback loop

The `agent-ready` label is a prediction. Track whether the prediction was correct.

**When a human intervenes on an `agent-ready` ticket** — redirects the agent mid-run, takes over implementation, or closes an agent PR and rewrites it — record the event in the ticket's Decisions field:

```
2026-06-15: Human override. Reason: agent missed cross-cutting auth middleware dependency not in spec. Routing should have been human-required.
```

**Monthly routing review:** the lead reviews all human overrides from the past month. If a class of ticket is consistently requiring intervention, tighten the `agent-ready` criteria in [ticket-template.md](ticket-template.md) and [agent-governance.md](agent-governance.md) to exclude it.

Track the override rate as a simple metric: overrides / total `agent-ready` tickets per month. Target < 10%. Above 20% is a signal the routing criteria need revision.

### What triggers a routing criteria update

- A ticket type appears in override records 3+ times in a month
- A new framework, library, or architectural pattern is introduced that agents handle poorly
- A post-mortem attributes a bug to incorrect routing

Routing criteria updates go through the same PR process as skill updates.
