---
name: audit-design
version: 1.0.0
description: "Audit an existing codebase against its original docs/specs, auto-update stale docs, clean up dangling/duplicate code, find features that were vibe-coded without a design doc, and run a /grill-with-docs session per feature to draft retroactive spec.md/context.md."
changelog:
  - "1.0.0 (2026-09-01): Added to the canonical skill set. Step 6 now calls /grill-with-docs (renamed from /grill-me) — same interview mechanic, plus it now also pins terminology to glossary.md and can write an ADR for a qualifying retroactive decision. See 'Related' below for how this differs from /doc-ops."
---

You are auditing an existing codebase against the docs/specs it started from: reconciling drift, cleaning up dangling code, and backfilling design docs for whatever was built without one. Work interactively — resolve each finding with the user before applying it, don't batch everything to the end.

**Related:** `/doc-ops` (see [workflows/doc-ops-agent.md]) covers similar ground (stale specs, coverage gaps, ADR staleness) but is read-only — it produces a report and changes nothing, meant to run unattended after a sprint or on a schedule. This skill is interactive and mutates the repo: it updates docs, deletes dead code, and drafts retroactive specs, with the human confirming every change. Run `/doc-ops` for a quick unattended health check; run this skill when you're ready to sit down and actually fix what it would find. The two keep independent detection logic by design, so don't assume a `/doc-ops` report and an `audit-design` finding will always agree on what counts as stale.

Subagent handoff rule: if you delegate any read or search work, pass only the files being analysed — not the full session transcript.

---

## Step 1 — Locate the original docs/specs corpus

Find everything that captures original intent:
- `designs/<feature>/spec.md` and `context.md` for every feature that has one
- `docs/`, `specs/`, `README.md`, ADRs, `AGENTS.md`
- Any Linear PRDs or Drive docs referenced from those files

Read them in full. Build a model of: the intended architecture, the conventions/patterns the docs establish (naming, layering, error handling, data flow style), and the full feature set the docs describe as in scope.

If no docs/specs exist at all, stop and tell the user — this skill audits against a baseline; without one there's nothing to audit against, and they likely just want `/spec-design` run retroactively for the whole app instead.

## Step 2 — Survey the current state of the app

Map what's actually in the codebase now: modules, routes, pages, services, API endpoints, database tables/migrations. For each feature the docs describe, check whether the code actually delivers it in full or is partial/stubbed. Note anything documented but not finished, or finished but clearly cut short (TODOs, stubbed handlers, disabled routes) — carry these into Step 4's cleanup scan.

## Step 3 — Design-consistency check (resolve stale docs interactively)

Compare the current implementation against the docs corpus from Step 1 — a whole-tree comparison, not a branch diff. For every divergence, present it in the same format `/sync-docs` uses:

- **Behaviour**: does the code do what the acceptance criteria in spec.md say?
- **Interfaces**: do API shapes, function signatures, schemas match what's documented?
- **Patterns**: does newer code follow the same conventions (layering, error handling, naming) as the code the docs describe, or has it drifted?
- **Completeness**: anything the docs describe that the code doesn't fully deliver

---
**Discrepancy N of M — [short title]**

> [one-sentence description]

**In code** (`file:line`): [what the code does]
**In docs** (`spec.md §X` or pattern description): [what's documented / expected]

**Options:**

| | Option | Pros | Cons |
|---|---|---|---|
| A | Update docs to match code | Docs stay truthful; no code churn | May paper over a real regression |
| B | Change code to match docs | Preserves original intent | Requires rework; only right if the doc was correct |
| C | *(custom — describe below)* | — | — |

**Recommended:** [A or B] — [one sentence rationale]

Which do you choose? (A / B / C):

---

Wait for the human's answer before moving to the next discrepancy. Apply the chosen fix immediately — edit the doc, or make the code change if they pick B and it's small and unambiguous; for anything larger than a one- or two-line code fix, log it as a follow-up instead of editing live (this skill is an audit pass, not an implementation session). When all discrepancies are resolved, commit doc updates:
```
git add designs/ docs/ AGENTS.md
git commit -m "docs: reconcile docs with current implementation (audit-design)"
```

## Step 4 — Cleanup: find dangling code

Scan for cruft the app has accumulated — things that are no longer clean, whether or not they're documented:

- **Partially implemented features**: stubbed handlers, TODO/FIXME markers guarding real functionality, feature flags permanently off, routes that 404 or return "not implemented"
- **Removed/dead features**: code paths, components, or endpoints with no live caller — nothing imports them, no route points at them, no UI links to them
- **Duplicate processes**: more than one implementation of the same thing — two auth flows, two ways of validating the same input, near-duplicate modules that look copy-pasted and diverged
- **Superseded code**: an old implementation left in place after a newer one replaced it (e.g. `utils.js` and `utils_v2.js` both still referenced somewhere, or neither referenced)

For each finding:

---
**Cleanup item N of M — [short title]**

> [what's dangling, and why it looks that way]

**Where:** `file(s)` — [evidence: no callers found / superseded by X / duplicate of Y]

**Options:** Remove it / Keep it (explain why it's still needed) / Investigate further (flag as follow-up, don't decide now)

---

Wait for the human's answer. On "Remove", delete the file(s)/code immediately. On "Keep", note the reason so the same thing isn't re-flagged pointlessly if this skill runs again. On "Investigate further", log it in the final report as a follow-up, not resolved here.

When all cleanup items are resolved, commit removals separately from the doc updates in Step 3, so they're easy to review or revert on their own:
```
git add -A
git commit -m "chore: remove dangling/duplicate code identified by audit-design"
```

## Step 5 — Identify features added without a design

Scan for "vibe-coded" additions: functionality present in the code with no matching section in the docs corpus and no `designs/<feature>/` folder of its own. These are different from Step 4's cleanup items — they're real, working features, just undocumented. Signals to use:

- Feature footprint (a route, module, UI screen, API endpoint, or table) with no corresponding doc coverage from Step 1
- If git history is available and legible: commits/PRs that added a feature-sized chunk of code without a paired `designs/` change — treat this as supporting evidence, not the primary signal

Produce a candidate list: for each, what it is, roughly where in the code, and why it was flagged. Present the full list to the user and ask them to confirm, add, remove, or merge entries before proceeding — the heuristic will miss things and over-flag things, and they know the codebase's history better than a scan does.

## Step 6 — /grill-with-docs session, per feature

For each confirmed undocumented feature, one at a time:

1. Read that feature's code in full.
2. Invoke the `/grill-with-docs` skill, framed against the code you just read: interview the user about the design intent behind it — why it was built this way, what edge cases it handles, what a spec would have said if one had been written first. Ask one question at a time, give a recommended answer, and resolve every branch, same as `/grill-with-docs` normally does for a forward-looking plan. Any term worth pinning gets added to `glossary.md`; any hard-to-reverse/surprising/genuine-tradeoff decision uncovered this way is written up as an ADR in `adr/`, same as it would be in a forward-looking design session.
3. Explicitly ask, once the intent is understood: "Based on this, should anything about the implementation change?" Capture any yes as a follow-up item — do not implement it here.
4. Draft `spec.md` and `context.md` for the feature in the same shape `/spec` and `/build` produce, under `designs/<feature-slug>/`. Mark them clearly at the top as retroactively authored (e.g. "Written after implementation, from a grill-with-docs session on `<date>` — reconstructs intent, may not reflect the original author's actual reasoning"). Show the draft to the user before writing the file, then write it and commit:
```
git add designs/<feature-slug>/
git commit -m "docs: backfill design docs for <feature-slug> (audit-design)"
```

Move to the next feature only after the current one's docs are drafted, confirmed, and committed.

## Step 7 — Report

Print a summary:

```
audit-design complete
  Docs/specs found:            [list of designs/ folders + docs/specs read]
  Design-consistency findings: N resolved (A: n docs updated, B: n code fixes), N deferred as follow-ups
  Cleanup items:                N removed, N kept, N flagged for follow-up
  Undocumented features found: N confirmed (M grilled this session, K deferred)
  Design docs drafted:         [list of designs/<feature-slug>/ paths written]
  Recommended changes (not applied): [list, from Step 6.3 — needs /sync-docs or a follow-up ticket if the user wants them made]
  Commits made:                 [list the commit messages from Steps 3, 4, and 6]
```

Tell the user what was auto-applied (doc updates, cleanup removals, new docs) versus what's only a recommendation (larger code fixes from Step 3, changes surfaced during grilling in Step 6) — and that `/decompose` or `/sync-docs` are the next steps if they want the remaining recommendations turned into actual work.
