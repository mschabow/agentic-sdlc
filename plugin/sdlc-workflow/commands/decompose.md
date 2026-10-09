---
name: decompose
description: Interactively break an approved spec's acceptance criteria into atomic, independently testable implementation tickets. Run after the design PR is merged. Produces ticket stubs ready for Linear, or creates them as GitHub issues in repos that use GitHub Issues, each with routing label and criteria that are a verifiable subset of the spec's acceptance criteria.
version: 1.1.0
changelog:
  - "1.1.0 (2026-10-09): Works with GitHub Issues as well as Linear. New step 7 creates the agreed tickets as GitHub issues (after a yes), labelled `build` with routing, `Blocked by` and `Parent` lines, and links them from the design issue. Linear behaviour is unchanged: the skill still outputs stubs only."
  - "1.0.0 (initial): Interactive decomposition into ticket stubs."
---

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

You are helping decompose an approved feature spec into implementation tickets. This is an interactive process — propose, discuss, and refine until the breakdown is agreed.

1. Read spec.md for this feature (find it in designs/<feature>/ or the path in the design ticket). With GitHub Issues, also get the design issue number: from spec.md if it names one, otherwise ask.
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

6. When the breakdown is agreed, output the final ticket list in this format so it can be created in the tracker:

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

7. **GitHub Issues only: create the issues.** With Linear, stop after step 6. With GitHub Issues, ask: "Create these N issues in `<owner>/<repo>`?" and create them only after a yes.
   - Create them in dependency order, so each `Blocked by` line can use a real issue number.
   - Title: the ticket title. Labels: `build` (or the implementation label AGENTS.md names), plus `agent-ready` or `human-required` if the repo has that label. If it does not, put `Routing: <value>` in the body.
   - Body: Scope, Acceptance criteria as a checklist, `Blocked by: #<n>` for each dependency (or `Dependencies: none`), `Parent: #<design-issue>`, and the path to spec.md.
   - Command: `gh issue create --title "<title>" --body-file <file> --label build [--label agent-ready]`. If `gh issue create --help` lists `--parent` and `--blocked-by`, pass them as well, but keep the body lines: the other skills read those.
   - Then append a task list of the new issues (`- [ ] #<n> <title>`) to the design issue's body, so /build can find the children: read it with `gh issue view <design-issue> --json body -q .body`, add the list, and write it back with `gh issue edit <design-issue> --body-file <file>`.
   - Report each issue number and URL. If a create fails, retry once, then report it and continue.
