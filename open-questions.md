# Open Questions

Unresolved items from the original design session (whiteboard, 2026-06-12). Each needs an owner and a decision; resolve into an ADR or delete.

| # | Question | Origin | Proposed next step |
|---|---|---|---|
| 1 | ~~Two circled nodes near the PR on the whiteboard (read as "Jury" / "Unit", annotated roughly "best suite merged"). Is this a multi-candidate build/selection mechanism, an automated review agent idea, or abandoned?~~ **Resolved:** this is the competitive multi-agent pattern — assign one issue to multiple agents, compare the resulting PRs, merge the best. It is a valid routing option for exploratory work and is now captured in the ticket template (`competitive multi-agent` routing) and [agent-governance.md](agent-governance.md). | Whiteboard, right edge | ✓ Resolved |
| 2 | Skill list item transcribed as "milestones (?)" — actual intended skill unclear | Whiteboard, skills list | Confirm with author and correct the skills list in execution-loop.md |
| 3 | Workaround for the local repo clone requirement (ADR-0002) | Meeting transcript 00:05:32 | Investigate remote-repo context options |
| 4 | Discard criteria for the pass-1 → pass-2 context boundary are drafted but unvalidated | execution-loop.md | Validate against the next two features built with this workflow |
