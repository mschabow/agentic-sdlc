# Hooks — Deterministic Guardrails and Approval Gates

**Stages 3 and 5.** Hooks are scripts that run before or after Claude Code acts. They allow, ask, or block — deterministically, as code, not as review-time discipline. They are the playbook practice we adopted to enforce rules at edit time instead of discovering violations at PR time.

Hooks complement, never replace, the existing gates: CI still validates context files and runs the frozen suite; PR review still happens per [review-policy.md](review-policy.md). Hooks catch what those gates catch — earlier and cheaper.

## Two hook classes

| Class | Stage | Runs | Purpose |
|---|---|---|---|
| **Build-time guardrails** | 3 | On file edit / tool use during a session | Keep agents inside the rails while they work |
| **Approval gates** | 5 | Before a privileged action (deploy, release, protected change) | Pause until a named human approves, or block with the approval route |

## Build-time guardrails (Stage 3)

Standard set for every repo, installed at `.claude/hooks/` and referenced from `.claude/settings.json`:

1. **Protected paths.** Block edits to generated code, frozen packages, migration history, and anything listed under "what not to touch" in AGENTS.md. The hook is the enforcement; AGENTS.md is the documentation. Both must list the same paths.
2. **Spec-derived test protection.** Block deletion or modification of tests in the spec-derived suite unless the diff also touches `spec.md` (invariant 5 of [execution-loop.md](execution-loop.md), enforced as code).
3. **Auto-format and lint after edits.** Run the repo formatter per file. Keeps formatting noise out of diffs and out of review.
4. **Secrets.** Block any edit that introduces credential patterns. No secret reaches a diff.
5. **Fast checks only.** Guardrail hooks run per-file checks in under a second or two. Heavy validation belongs in CI.

## Approval gates (Stage 5)

Gates wrap privileged actions with a human decision:

- **Ask gates** pause the session until a named approver responds (e.g. release authorization, changes behind a change-management window).
- **Block gates** deny the action and print why plus the approval route (e.g. "production config is change-managed; open a design ticket or get lead sign-off").

Rules:

1. Every gate decision is logged with timestamp, actor, and approver. The log is part of the audit trail, alongside the artifact chain.
2. Gates are enforced consistently — same behavior for agent and human sessions.
3. An agent can never approve its own gate. Approvers are humans named in the gate config.
4. Gate configs are version-controlled in the repo and changed by PR, same as skills.

## Per-environment autonomy tiers

Hook strictness follows the environment (detail in [deploy.md](deploy.md)):

| Environment | Autonomy | Gates |
|---|---|---|
| Dev | Free — guardrails only | None |
| Staging | Middle — guardrails + ask gates on deploy | Deploy requires named approver |
| Production | Gated — all privileged actions gated | Deploy, config, data changes all gated; rollback path rehearsed |

## Ownership and change process

- The standard guardrail set lives in this process repo and ships with the plugin ([rollout.md](rollout.md)).
- Repo-specific hooks (protected paths, gate approvers) are configured per repo during [setup.md](setup.md) and documented in AGENTS.md.
- Hook changes follow the same PR + eval discipline as skills ([skill-eval-framework.md](skill-eval-framework.md)): a bad hook silently degrades every session.
