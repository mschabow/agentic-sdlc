# Maintain Loop — Stage 6

**Stage 6** closes the lifecycle: production signals initiate work without waiting for a human to notice. Every autonomous finding is written as an **intent card** ([lightweight-design.md](lightweight-design.md) format) and enters the Stage 1 triage queue in Linear. A human routes it — fix, schedule, or dismiss — using the same post-ship routing decision as any other change ([design-loop.md](design-loop.md)).

Nothing in this stage bypasses the pipeline. Autonomy here means *initiating and diagnosing*, never merging or deploying.

## 1. Control-band monitoring

A deterministic detection script watches a small set of workflow and production metrics (see [metrics.md](metrics.md)). Response tiers live in a version-controlled config (`bands.yaml` in the ops repo):

| Deviation | Response |
|---|---|
| 1σ | Log only |
| 2σ | Claude diagnoses, read-only; writes findings as an intent card into triage |
| 3σ | Claude may act: open a PR or execute a pre-approved runbook — both still pass the Stage 5 gates |

Dismissed findings tune the bands: a dismissal records why, and repeated dismissals of the same class widen the band or fix the metric.

## 2. Scheduled scans

Security and code-health scans run on schedule, without human invocation:

- Findings are validated before reporting; each carries a confidence rating.
- **Bounded finding** (a specific patch): open the suggested fix as a PR through the normal Stage 5 review gate, tagged with the scan ID.
- **Wider finding** (design implication): write an intent card; it takes the full design path.
- Dismissals are recorded with reasons, so the same finding is not re-triaged monthly.

## 3. Claude on-call

Claude joins the incident channel (Slack) as a distinct identity per [agent-governance.md](agent-governance.md):

- Responds in-channel: pulls metrics via MCP, proposes diagnosis, drafts the post-mortem.
- Small fixes arrive as PRs through the review gate. Larger issues become intent cards.
- **Slack provenance rule still applies.** The channel is an interaction surface, not a context source. Before any resulting build starts, the relevant channel history is captured as a transcript in the feature's Drive folder ([drive-conventions.md](drive-conventions.md)). `context.md` never references Slack.

## 4. Incident-to-eval

**Every production incident becomes a permanent eval.** The fix PR is not complete until it adds a regression case:

- A code bug adds a test to the affected repo's suite.
- A workflow failure (bad routing, stale context, skill regression) adds an eval case to `.claude/evals/` in this process repo, per [skill-eval-framework.md](skill-eval-framework.md).
- The PR template asks: "What eval or test now catches this class of failure?" A blank answer blocks merge for incident-fix PRs.

This is the same principle as routing instrumentation ([agent-governance.md](agent-governance.md)): failures are data, and the data tightens the system.

## Invariants

1. Every autonomous finding enters triage as an intent card; a human routes it. No finding self-routes to implementation.
2. Stage 6 agents are read-only below the 3σ tier, and even at 3σ produce only PRs or pre-approved runbook executions — all subject to Stage 5 gates.
3. Slack content reaches a build only via a Drive transcript.
4. An incident fix without a regression eval or test is incomplete.
5. Dismissals are recorded with reasons and reviewed in the monthly routing review.
