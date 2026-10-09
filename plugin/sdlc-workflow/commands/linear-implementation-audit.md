---
name: linear-implementation-audit
version: 1.1.0
description: Check open Linear tickets (or GitHub issues) against the code to find what is done, partly done, not started, or obsolete, then update the tickets one at a time with approval. Use when the user asks which open tickets are already implemented or wants a backlog reconciled with the repo.
changelog:
  - "1.1.0 (2026-10-09): Works with GitHub Issues as well as Linear: picks the tracker from AGENTS.md's `## Tickets` section, or uses GitHub Issues when there is no such section and no Linear MCP (deferred tools count as Linear). Linear behaviour is unchanged."
  - "1.0.0 (2026-10-03): Added to the sdlc-workflow plugin so it ships to every account from one source."
---

# Linear implementation audit

Linear drifts from the code. Tickets stay open after the work ships, or stay open after a decision made them pointless. This skill checks each open ticket against the repo and brings the tracker back in line. It works the same way on GitHub Issues; the name stays for existing installs.

This is different from restructuring a milestone or project. If the user wants tickets moved, re-parented, or re-labelled, that is a milestone cleanup task (use `linear-milestone-cleanup` if it is available). This skill only asks one question per ticket: does the repo already do this?

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

## Step 1: Set the scope

Confirm which tickets to check: a project, a milestone, an initiative, or a label. Pull every open ticket in that scope with its description, acceptance criteria, comments, created date, and last-updated date.

With GitHub Issues the scope is a milestone, a label, or all open issues: `gh issue list --state open --limit 500 [--milestone <m>] [--label <l>] --json number,title,body,labels,milestone,createdAt,updatedAt`. Read comments with `gh issue view <n> --comments`.

State the count. If it is over about 40, propose working in batches by milestone.

## Step 2: Check each ticket against the code

For each ticket, look for evidence in the repo:

- Search the code for the feature, module, table, or endpoint the ticket names.
- Search git history and PRs for the ticket id (`git log --all --grep=<ID>`, `gh pr list --search <ID> --state all`). For a GitHub issue, also search for `#<n>` and for PRs that link it (`Closes #<n>`).
- Check all branches and worktrees, not only `main`. Note where the work lives if it is unmerged.
- Compare against each acceptance criterion, not just the title.

For large scopes, use parallel subagents, one per batch of tickets. Each returns the verdict and its evidence.

## Step 3: Classify

Give each ticket one verdict:

- **Done**: every acceptance criterion is met on the main branch.
- **Done, unmerged**: met on a branch or open PR. Name it.
- **Partly done**: list which criteria are met and which are not.
- **Not started**: no evidence found.
- **Obsolete**: the work no longer makes sense. Give the reason, such as an architecture change or a superseding ticket.
- **Needs a decision**: you cannot tell, or it depends on someone outside the team.

Show a table: ticket, title, age, verdict, evidence (file path, PR number, or commit). Old tickets deserve extra suspicion; show the created date so the user can judge relevance.

Every verdict needs evidence. If you found nothing, write "no evidence found" instead of assuming not started. Only the user can declare a ticket obsolete for business or contract reasons; propose it and let them decide.

## Step 4: Walk through the changes

Do not bulk-update. A past bulk change in this workspace cancelled tickets by mistake.

Go in this order: done, then partly done, then obsolete, then needs a decision. For each ticket, show the proposed change and wait for a yes, a no, or an edit. The user may answer for several at once (for example "558 and 585: close as obsolete"); apply exactly what they say.

Proposed changes by verdict:

- **Done**: close it, with a comment that cites the PR or commit (GitHub: `gh issue close <n> --comment "..."`).
- **Done, unmerged**: leave open, add a comment naming the branch or PR.
- **Partly done**: update the description to show what remains, or split the remainder into a new ticket. Ask which.
- **Obsolete**: close with the reason in a comment (GitHub: `gh issue close <n> --reason "not planned" --comment "..."`). If the user has an `Unanswered` or similar terminal state for questions, use the state they name. If closing has contract or client implications, offer a follow-up ticket for the user to discuss it with the right person.
- **Needs a decision**: add a comment with the open question, and assign or tag as the user directs.

If the user asks for a writing style on ticket updates (for example a plain-language or ADHD-friendly skill), use it for every comment and description in the run.

## Step 5: Follow-ups

When the audit shows missing work that no ticket covers (for example "integrate and test the full chain"), propose a new ticket with a title, a short description, and acceptance criteria. Create it only after a yes. Ask who owns it; do not assign by guessing.

## Rules

- Never delete tickets. Close or cancel with a comment.
- Record decisions that kill a body of work in the project's decision log, if one exists, before closing the tickets. Otherwise the reasoning is lost.
- Use emails or handles exactly as the tracker shows them. Never turn an email prefix into a first name.
- If a tracker write fails, retry once, then report it and move on. List failed updates at the end.

## Final report

- Counts per verdict.
- Tickets changed, with links.
- Tickets created.
- Tickets still waiting on a decision, and from whom.
- Updates that failed.
