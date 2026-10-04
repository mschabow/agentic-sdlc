# Metrics

**All stages.** The workflow is measured so that drift shows up in numbers before it shows up in incidents. Leading indicators predict; lagging indicators confirm. The control-band monitor ([maintain-loop.md](maintain-loop.md)) watches a subset of these automatically.

## Leading indicators

| Metric | What it tells you | Stage |
|---|---|---|
| Time from idea to committed intent card | Whether intake is capturing work or losing it | 1 |
| Time from design ticket open to design PR merged | Whether the design phase is a gate or a bottleneck | 2 |
| First-pass CI success rate for agent PRs | Whether spec + context discipline is actually working — the single best signal of context quality | 3–4 |
| /verify-context STALE rate | How often artifacts drift between tickets; high rate means specs are too broad or too slow to update | 3 |
| Share of review comments resolved without a human pushing code | Whether the authoring agent can close its own loop | 5 |
| Skill eval pass rate trend | Whether skill changes are improving or degrading the toolchain | 4 |
| Routing override rate (existing — target < 10%/month) | Whether `agent-ready` predictions are accurate | 3 |

## Lagging indicators

| Metric | What it tells you |
|---|---|
| Rework cycles per change (spec revisions after build starts) | Design-phase quality |
| Defects and vulnerabilities escaping to production | End-to-end gate effectiveness |
| Repeat incident rate | Whether incident-to-eval is working — this number should approach zero |
| DORA: deployment frequency, lead time, change failure rate, MTTR | Overall delivery health |

## Practice

1. Start with three: **first-pass CI success for agent PRs**, **routing override rate**, and **repeat incident rate**. Add others when a question needs them.
2. Metrics feed the monthly routing review ([skill-eval-framework.md](skill-eval-framework.md)). A metric nobody reviews is deleted.
3. Metrics measure the workflow, not individuals. Never use per-person agent statistics in performance conversations — it poisons the override log, which depends on people honestly recording interventions.
