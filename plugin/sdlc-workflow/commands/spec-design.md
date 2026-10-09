---
name: spec-design
version: 1.5.1
description: "Entry point for the design phase. Orchestrates the full design loop for a feature: pulls the design ticket, checks if lightweight path applies, runs /spec, does a broad context pass, runs /grill-with-docs, produces spec.md + context.md with a draft test list, and guides to the design PR. Works with Linear or GitHub Issues. Run this at the start of any design ticket."
changelog:
  - "1.5.1 (2026-10-09): Commit-only path closes the GitHub design issue (after a yes) once the approval is recorded, since there is no PR to close it."
  - "1.5.0 (2026-10-09): Works with GitHub Issues as well as Linear. New Ticket tracker section; step 0 accepts `#12` as the ticket ID; steps 1, 3 and 4 read from the tracker; the design PR uses `[#<issue>]` and `Closes #<issue>` with GitHub Issues. Linear behaviour is unchanged."
  - "1.4.0 (2026-10-07): Step 8 asks whether the design needs a PR for lead review or a commit only. PR stays the recommendation for shared or restricted areas or ADRs needing sign-off; the commit-only path records the approval route in spec.md's Status line before /decompose. Pushing is confirmed with the human either way."
  - "1.3.0 (2026-10-01): New step 0 — the design phase always starts in a fresh git worktree named after the ticket, branched off a freshly fetched origin/<default-branch>, with the base verified before anything else. Lightweight path check moves to step 0.5."
  - "1.2.0 (2026-09-01): Renamed from /design to /spec-design to avoid any ambiguity with Claude Code's built-in Design-canvas skill. Step 5 now runs /grill-with-docs (replaces /grill-me) — same interview, plus glossary and ADR maintenance."
  - "1.1.0 (2026-06-18): Added lightweight path check (step 0); added draft test list production after /grill-me (step 5.5); added --batch option for /grill-me; added test list to design PR checklist"
  - "1.0.0 (initial): Full design loop without lightweight path or draft test list"
---

You are orchestrating the full design phase. Follow these steps in order — do not skip any.

## Ticket tracker

Before you read or write a ticket, find out which tracker this repo uses:

- **GitHub Issues** if AGENTS.md has a `## Tickets` section that says GitHub Issues.
- **Linear** if that section says Linear. If the Linear tools are not available, stop and ask. Do not fall back to GitHub Issues.
- **No `## Tickets` section:** look for Linear MCP tools, including deferred ones (search for "linear" with ToolSearch). If they exist, use Linear, even if they need authentication first. If there are none, use GitHub Issues and say so in one line.

With Linear, the Linear steps in this skill apply unchanged.

With GitHub Issues, do each "Linear" step in this skill with `gh`:

| Linear | GitHub Issues |
|---|---|
| Ticket ID `ENG-123` | Issue number `#12` |
| Pull a ticket | `gh issue view 12 --comments` |
| Search tickets | `gh issue list --search "<terms>" --state all` |
| Create a ticket | `gh issue create --title "<title>" --body-file <file> --label <label>` |
| Post a status update or comment | `gh issue comment 12 --body-file <file>` |
| Close a ticket | `gh issue close 12 --comment "<reason>"`; add `--reason "not planned"` for obsolete work |
| Status (Backlog, In Review, Done) | Open with no PR, open with an open PR, closed |
| Parent and children | A `Parent: #<n>` line in the child's body, and a task list of the children in the parent's body |
| `blocked by` / `blocks` | A `Blocked by: #<n>` line in the issue body |
| Labels such as `agent-ready` | The labels AGENTS.md lists (`gh label list`). If a label does not exist, write it as a line in the body (`Routing: agent-ready`). Do not create labels without a yes. |
| Project or milestone | A milestone or a label (`gh issue list --milestone <m>` or `--label <l>`) |

Unless AGENTS.md says otherwise, branches are `<area>/<issue>-<slug>` (for example `sync/12-google-push-channel`), PR titles are `[#<issue>] Title`, and the PR body has `Closes #<issue>`. Drop the `#` in branch, worktree, and file names (`12-google-push-channel`).

`gh` must act as the account that owns the repo. If the active `gh` account is a different one (for example a work account on a personal repo) and no hook sets `GH_TOKEN`, prefix each `gh` command with `GH_TOKEN=$(gh auth token --user <owner>)`. Never run `gh auth switch`; it changes the account for every other session.

## 0 — Start in a fresh worktree

Before anything else, find the ticket tracker (see Ticket tracker) and ask: "What is the ticket ID for this design?" (`ENG-123` in Linear, `#12` in GitHub Issues). Then create an isolated git worktree for the design work, named after the ticket (e.g. `eng-123-<short-slug>`, or `12-<short-slug>` for a GitHub issue):

- **Preferred:** use the EnterWorktree tool with the ticket-based name.
- **Fallback:** run `git fetch origin`, then `git worktree add -b <branch> ../<worktree-name> origin/<default-branch>`, and switch to that directory. Find the default branch with `git symbolic-ref refs/remotes/origin/HEAD` (or `gh repo view --json defaultBranchRef`).

Do all remaining steps inside this worktree. Never do design work in the main checkout or on an existing feature branch.

Verify the base is current before continuing:
- `git fetch origin`, then confirm `git rev-parse HEAD` matches `git rev-parse origin/<default-branch>`. If the worktree is behind (e.g. EnterWorktree branched off a stale local ref), reset the new, still-empty branch to `origin/<default-branch>`.
- Confirm the expected app directories are present (the top-level layout described in AGENTS.md or the README). If any are missing, stop and tell the human — the worktree is on the wrong base or repo.

Report the worktree path, branch name, and base commit to the human.

## 0.5 — Lightweight path check

Before starting, ask: "Is this a lightweight change?" Run through the checklist from [lightweight-design.md]:

- Touches ≤ 3 files and no shared interfaces
- Acceptance criteria can be stated in ≤ 5 lines
- No new data flow, no new component boundaries
- No architectural decision is being made
- No other team or system depends on the change

If **all five** are true, ask the human: "This looks like a lightweight change. Should I produce an intent card instead of a full spec?" If yes, follow the lightweight path in [lightweight-design.md] and stop here. If no, continue with the full design loop below.

If any condition is false, proceed with the full design loop without asking.

## 1 — Pull the ticket

Pull the ticket from step 0 from the tracker (the Linear MCP, or `gh issue view <n> --comments`): title, description, sources, and any linked PRD.

If the Drive feature subfolder doesn't exist yet (check the ticket's Sources field), ask the human to create it now per [drive-conventions.md] before continuing.

## 2 — Read AGENTS.md

Read AGENTS.md at the repo root. Note build commands, branch naming, and any restricted areas.

## 3 — /spec

Run the /spec skill in full: ask "What do you want to build or change?", explore the codebase for contact points and side effects, check the tracker and Drive, ask clarifying questions one at a time, and produce user stories with acceptance criteria.

Wait for human confirmation before proceeding.

## 4 — Context pass 1

Do a broad context gather anchored on the /spec draft:
- Codebase: full files for the contact points identified in /spec, plus surrounding context for side effects
- Google Drive: the feature subfolder and `_evergreen/`
- The tracker: ticket history, linked PRD, related tickets
- Web search and Context7/MCPs for current library and API documentation relevant to the spec

Slack is not a context source. If anything important lives only in Slack, ask the human to capture it in Drive first.

Summarise what the context pass confirmed, challenged, or added to the /spec draft.

## 5 — /grill-with-docs

Run the /grill-with-docs skill on the current spec draft. Let the context pass findings drive the questions.

**Mode:** Ask the human: "Prefer batch questions (all at once, grouped) or one at a time?" Use `/grill-with-docs --batch` for batch mode. Default to one-at-a-time if the human doesn't specify.

Work through every branch of the decision tree until all ambiguities are resolved. Along the way, `/grill-with-docs` pins contested terminology to `glossary.md` and writes an ADR to `adr/` for any decision that's hard to reverse, surprising, and a genuine tradeoff — that's in addition to, not instead of, resolving the spec's open questions.

Wait for the human to confirm the decision tree is fully resolved.

## 5.5 — Draft test list

Before writing spec.md, produce a draft test list from the resolved acceptance criteria. For each criterion, write one or two concrete test cases: what is called, what input is used, and what the expected observable outcome is.

This list is reviewed as part of the design PR. It becomes the frozen baseline for the Pass 2 build agent — the agent will implement these tests first, then build to pass them.

Example format:
```
Criterion: "User receives an email confirmation within 30 seconds of checkout"
  Test 1: trigger checkout → assert email_sent event in queue within 30s
  Test 2: trigger checkout with invalid email → assert no event queued, error returned to caller
```

Present the draft test list to the human. Revise until approved. If a criterion cannot be turned into a testable case, that criterion is too vague — return to /grill-with-docs to sharpen it.

## 6 — Draft spec.md

Draft spec.md using the spec template, incorporating output from /spec, the context pass, /grill-with-docs, and the draft test list. The design section must be precise enough to serve as an agent's implementation contract.

Include the draft test list as a section in spec.md (see spec template).

Present the draft for human review. Revise until approved.

## 7 — Build context.md

Produce context.md following the schema in [context-schema.md]: required sections (Key decisions, Constraints, Relevant code, External references), 300-line max, no Slack references.

`glossary.md` and any ADRs from step 5 are separate artifacts, not part of context.md — reference them from context.md's External references section instead of duplicating their content.

Run `ci/validate-context.sh` locally before presenting it.

Present context.md for human confirmation. Revise until approved.

## 8 — Commit, and open a design PR if one is needed

Ask: "Does this design need a PR for lead review, or should I commit only?" Recommend a PR when the design touches shared or restricted areas (per AGENTS.md) or includes ADRs that need sign-off. Commit-only is reasonable when the human is the approver, or when approval happens in a separate review session.

Either way, commit spec.md, context.md, and any ADR or glossary changes on the worktree branch from step 0 (rename it first if it doesn't match the AGENTS.md branch naming convention). Ask before pushing.

**If a PR is needed:** push and open the design PR with a description that:
- Summarises the feature
- Links the ticket. With GitHub Issues: title the PR `[#<issue>] <title>` and put `Closes #<issue>` in the body
- Confirms the draft test list is included in spec.md
- Links any ADRs written during /grill-with-docs, and notes any glossary terms pinned
- Notes this is a design-only PR

Tell the human: the next step is lead review of the design PR. After it merges, run `/decompose` to create implementation tickets.

**If commit-only:** record in spec.md's **Status** line who approves the design and how (e.g. "Approved by <name> in sign-off review"). Tell the human: run `/decompose` once that approval is recorded. Note that `/decompose` assumes a merged design, so its PR check should be skipped by pointing it at the committed branch.

With GitHub Issues, a design PR closes the design issue through `Closes #<issue>`. Commit-only has no PR, so close it yourself once the approval is recorded in spec.md and the commit is pushed. Ask first, then run `gh issue close <issue> --comment "Design approved by <who>. Committed on <branch> at <short sha>. Next: /decompose."`. If the approval is still pending, leave the issue open and tell the human to close it when the approval is recorded.
