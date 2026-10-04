# Linear Ticket Template

Tickets are the control plane. Every ticket carries distilled context — never raw documents or full transcripts. The ticket plugin enforces this structure so tickets stay uniform and clean.

There are two ticket types per feature. Create the design ticket first; create implementation tickets only after the design PR is merged.

**Post-ship changes:** use the same two-ticket pattern if the change affects the design (acceptance criteria, interfaces, or data flow) — open a design ticket first, revise `spec.md`, get it reviewed, then create implementation tickets. For bug fixes with no design implication, open an implementation ticket directly.

---

## Title

`[Feature/Area] — concise outcome statement`

## Type

`Design ticket | Implementation ticket`

- **Design ticket:** output is `spec.md` + `context.md` committed to the repo as a merged PR.
- **Implementation ticket:** output is working code. Requires the design PR to be merged before starting.

## Routing *(implementation tickets only — design tickets are always human-led)*

`agent-ready | human-required | competitive multi-agent`

Design tickets have no routing label. They are always driven interactively by a human engineer using Claude Code as a tool. Never assign a design ticket to an autonomous agent.

- **agent-ready:** atomic, self-contained, scoped to specific files/modules, with explicit testable acceptance criteria.
- **human-required:** high ambiguity, novel architecture, security-critical, or cross-cutting change.
- **competitive multi-agent:** exploratory work where comparing independent implementations is worth the cost. Coordinate with lead before starting.

## Context (distilled)

2–6 sentences summarizing what this work is and why, distilled from source transcripts and documents. No raw transcript paste. No Slack content — if information exists only in Slack, capture it in a Google Doc or Linear comment first.

## Decisions

- Decision 1 (one line each, with date if known)
- Decision 2

## Sources

- **Drive folder:** link to the feature subfolder in Drive (e.g. `Drive / Payments Platform / checkout-redesign/`) — see [drive-conventions.md](drive-conventions.md) for folder structure
- **Linear PRD:** link to the parent Linear project or PRD document
- **GitHub SPEC:** link to `designs/<feature>/spec.md` in the repo (added once the design PR is merged)

## Acceptance criteria

- Observable outcome 1
- Observable outcome 2

For design tickets: criteria describe the artifacts (e.g. "spec.md merged to repo", "context.md contains no Slack references").
For implementation tickets: criteria are mirrored verbatim in the linked spec and must stay in sync.

## Out of scope

- Explicitly excluded items, to keep the context pass tight

---

## Conventions

1. One design ticket and one or more implementation tickets per feature; the GitHub design folder parallels the ticket (e.g. ticket "Feature One" ↔ repo `designs/feature-one/`).
2. The design ticket is created first. Implementation tickets are created from the approved spec after the design PR is merged.
3. The ticket links to the SPEC; the SPEC links back to the ticket.
4. When the build deviates and the SPEC is updated, add a one-line note to the ticket's Decisions section.
5. If routing changes during implementation (e.g. agent-ready → human-required), update the label and note the reason in Decisions.
