# Deploy — Stage 5

**Stage 5** covers everything between a pushed branch and running code: implementation PR review, approval gates, CI/CD execution, and the controls that keep autonomous runs safe. It adopts the playbook's deploy-stage practices on top of our existing PR gate.

## The implementation PR gate

Unchanged from [review-policy.md](review-policy.md): every implementation PR — agent or human — passes the same structural gate (branch protection, required review, required CI), with differentiated review depth. Agents cannot self-approve ([agent-governance.md](agent-governance.md)).

Additions from the playbook:

1. **Bidirectional AI review.** `/review-agent` reviews incoming PRs (Stage 4); the authoring agent also addresses review comments on its own PRs when @-mentioned. Humans spend their attention on intent and risk, not mechanical findings.
2. **Findings ranked by severity.** Review output separates Important from Nit; nit volume is capped so review stays readable (see [workflows/review-agent.md](workflows/review-agent.md)).

## Approval gates

Privileged actions — deploy, release, production config — are wrapped in ask/block gates per [hooks.md](hooks.md). Gate approvals are logged and become part of the audit trail.

## CI/CD integration

When Claude runs non-interactively in the pipeline (scheduled jobs, PR-triggered actions, Stage 6 responses):

1. **Sandboxed execution with scoped credentials.** The pipeline identity can do exactly what its job needs — nothing else.
2. **Deployment tooling through MCP.** Deploy, status, and rollback are exposed as MCP tools with explicit scopes, not as raw shell access to production.
3. **Rollback rehearsed in advance.** A deploy path an agent can trigger must have a rollback path a human has actually run.

## Per-environment autonomy tiers

| Environment | Agent may | Gate |
|---|---|---|
| Dev | Build, test, deploy freely | Guardrail hooks only |
| Staging | Deploy after ask-gate approval | Named approver |
| Production | Propose only — PR or pre-approved runbook | All privileged actions gated; human executes or approves |

## Managed settings

For org-wide consistency, the platform/lead level owns a managed settings baseline that individual repos inherit and cannot weaken:

- Deny: secrets access, arbitrary network, unsandboxed commands.
- Allow: git, build, test, lint.
- Managed hooks and MCP servers only; minimum Claude Code version enforced.

Repo-level settings may tighten this baseline, never loosen it. The baseline is version-controlled in this process repo and distributed with the plugin ([rollout.md](rollout.md)).

## Evidence

Stage 5 leaves a record: PR findings and fixes, gate approvals with timestamps, deployment logs. Together with the artifact chain (intent card → spec → context → diff → test evidence), this answers "who asked for what, what the agent produced, who approved it."
