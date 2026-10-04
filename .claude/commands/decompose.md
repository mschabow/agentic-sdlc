---
name: decompose
description: Interactively break an approved spec's acceptance criteria into atomic, independently testable implementation tickets. Run after the design PR is merged. Produces ticket stubs ready for Linear, each with routing label and criteria that are a verifiable subset of the spec's acceptance criteria.
---

You are helping decompose an approved feature spec into implementation tickets. This is an interactive process — propose, discuss, and refine until the breakdown is agreed.

1. Read spec.md for this feature (find it in designs/<feature>/ or the path in the Linear ticket).
2. Present the feature-level acceptance criteria from the spec so the human can see what needs to be covered.
3. Propose an initial decomposition: a set of implementation tickets that together satisfy all the spec's acceptance criteria.

For each proposed ticket include:
- **Title:** `[Feature/Area] — concise outcome statement`
- **Scope:** specific files, modules, or components touched
- **Acceptance criteria:** a subset or refinement of the spec's criteria — testable independently, without other tickets being complete first
- **Routing:** `agent-ready` or `human-required` (use the criteria from the ticket template)
- **Dependencies:** list any tickets that must be merged before this one can begin (minimize these — they are a sequencing risk)

4. Flag any proposed ticket whose acceptance criteria cannot be verified until another ticket is complete. These need to be either merged into the blocking ticket, resequenced, or their criteria restated so they can be verified independently.

5. Iterate — adjust scope, split, merge, or reorder tickets based on discussion — until every spec acceptance criterion is covered by exactly one ticket, no criterion is left unassigned, and no criterion appears in more than one ticket.

6. When the breakdown is agreed, output the final ticket list in this format so it can be created in Linear:

---
**Ticket [N]: [Title]**
Type: Implementation ticket
Routing: [agent-ready | human-required]
Scope: [files/modules]
Acceptance criteria:
- [criterion]
Dependencies: [ticket numbers, or "none"]
---

After outputting the ticket list, confirm with the human that all spec acceptance criteria are covered before closing the session.
