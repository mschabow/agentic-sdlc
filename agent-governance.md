# Agent Governance

This document covers how agents participate safely across the workflow: identity, permissions, the agent constitution, and the human override.

## Agent identity

Every agent that creates tickets, opens PRs, or posts comments must have a **distinct identity** in both Linear and GitHub. Never share a human's credentials with an agent.

- Distinct identity means every action is attributable in the audit log.
- If a run goes wrong, it is immediately clear which agent caused it and which human is responsible for that agent.
- Agent accounts should be named to make their non-human status obvious (e.g. `claude-code[bot]`, not a generic service account).

## Permissions and scope

Agents operate under the same structural controls as human engineers:

- **GitHub:** scoped permissions only; subject to branch protection, required reviews, and required CI on every PR. Agents cannot self-approve their own PRs.
- **Linear:** assignable and @-mentionable like any team member; cannot alter workspace settings, manage members, or modify access controls.
- These constraints are enforced by configuration, not by assumption.

## AGENTS.md — the agent constitution

Each repo contains an `AGENTS.md` at the root. This is the first thing Claude Code reads at the start of the build phase, before any other context gathering.

`AGENTS.md` covers:
- Build and test commands
- Branch naming and PR naming conventions
- Code style and linting expectations
- Directory conventions and what not to touch
- Anything a new agent needs to work correctly in this specific repo without asking

Keep `AGENTS.md` consistent with any agent guidance configured in the Linear workspace. Conventions stated in one place and contradicted in the other create the agentic equivalent of a merge conflict.

## Routing options

Tickets are routed at creation time using one of three labels:

| Label | When to use |
|---|---|
| `agent-ready` | Atomic, bounded, pattern-following work with explicit testable criteria |
| `human-required` | High ambiguity, novel architecture, security-critical, or cross-cutting change |
| `competitive multi-agent` | Exploratory work where comparing independent agent implementations is worth the CI cost |

For `competitive multi-agent`: assign the ticket to multiple agents, each working in a separate branch. Compare the resulting PRs. A human selects and merges the best; runners-up are closed. Coordinate with the lead before starting — this multiplies CI usage and request quota.

If routing changes during implementation (e.g. an `agent-ready` ticket turns out to require human judgment), update the label and note the reason in the ticket's Decisions field.

## Skills — canonical source and lifecycle

The canonical versions of all workflow skills (`/grill-with-docs`, `/verify-context`, `/decompose`, etc.) live in this process repo under `.claude/commands/`. This is the single source of truth — not individual code repos.

**Full lifecycle details:** see [skill-eval-framework.md](skill-eval-framework.md). Summary:

- Every skill file carries a version header (semver) and changelog.
- Every skill has companion eval cases at `.claude/evals/<skill-name>.md`.
- Before propagating a skill change, run the eval and record the result in the PR.
- A PR that modifies a skill without an eval result is not mergeable.
- Propagate to global install after merge: `cp .claude/commands/<skill>.md ~/.claude/commands/`
- Pin specific skill versions in individual repos via `/setup-project` when isolation is needed; document pins in AGENTS.md.

**Why evals matter:** a skill regression is a silent production incident. It degrades every feature built while the bad version is active. Evals catch regressions before propagation.

## Routing instrumentation

The `agent-ready` label is a prediction. Track its accuracy.

When a human intervenes on an `agent-ready` ticket (mid-run redirect, takeover, rewrite of an agent PR), record it in the ticket's Decisions field:

```
2026-06-15: Human override. Reason: [what the agent got wrong]. Routing should have been: [human-required / different criteria].
```

The lead reviews override events monthly and tightens routing criteria when a pattern appears. Target override rate: < 10% of `agent-ready` tickets per month. See [skill-eval-framework.md](skill-eval-framework.md) for the full instrumentation process.

## Human override — always available

Any agent run can be interrupted, redirected mid-task, or taken over by a human at any point. The recommended place to catch problems is at the **plan stage** — reading the agent's proposed approach before it starts writing code is far cheaper than catching a wrong direction at the PR stage.

Humans own intent, judgment, and approval. Agents own generation, execution, and reporting. The spec is the contract that lets them hand off cleanly.
