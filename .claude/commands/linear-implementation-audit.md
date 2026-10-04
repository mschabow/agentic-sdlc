---
name: linear-implementation-audit
version: 1.0.0
description: Check open Linear tickets against the code to find what is done, partly done, not started, or obsolete, then update the tickets one at a time with approval. Use when the user asks which open tickets are already implemented or wants a backlog reconciled with the repo.
changelog:
  - "1.0.0 (2026-10-03): Added to the sdlc-workflow plugin so it ships to every account from one source."
---

# Linear implementation audit

Linear drifts from the code. Tickets stay open after the work ships, or stay open after a decision made them pointless. This skill checks each open ticket against the repo and brings Linear back in line.

This is different from restructuring a milestone or project. If the user wants tickets moved, re-parented, or re-labelled, that is a milestone cleanup task (use `linear-milestone-cleanup` if it is available). This skill only asks one question per ticket: does the repo already do this?

## Step 1: Set the scope

Confirm which tickets to check: a project, a milestone, an initiative, or a label. Pull every open ticket in that scope with its description, acceptance criteria, comments, created date, and last-updated date.

State the count. If it is over about 40, propose working in batches by milestone.

## Step 2: Check each ticket against the code

For each ticket, look for evidence in the repo:

- Search the code for the feature, module, table, or endpoint the ticket names.
- Search git history and PRs for the ticket id (`git log --all --grep=<ID>`, `gh pr list --search <ID> --state all`).
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

- **Done**: close it, with a comment that cites the PR or commit.
- **Done, unmerged**: leave open, add a comment naming the branch or PR.
- **Partly done**: update the description to show what remains, or split the remainder into a new ticket. Ask which.
- **Obsolete**: close with the reason in a comment. If the user has an `Unanswered` or similar terminal state for questions, use the state they name. If closing has contract or client implications, offer a follow-up ticket for the user to discuss it with the right person.
- **Needs a decision**: add a comment with the open question, and assign or tag as the user directs.

If the user asks for a writing style on ticket updates (for example a plain-language or ADHD-friendly skill), use it for every comment and description in the run.

## Step 5: Follow-ups

When the audit shows missing work that no ticket covers (for example "integrate and test the full chain"), propose a new ticket with a title, a short description, and acceptance criteria. Create it only after a yes. Ask who owns it; do not assign by guessing.

## Rules

- Never delete tickets. Close or cancel with a comment.
- Record decisions that kill a body of work in the project's decision log, if one exists, before closing the tickets. Otherwise the reasoning is lost.
- Use emails or handles exactly as Linear shows them. Never turn an email prefix into a first name.
- If a Linear write fails, retry once, then report it and move on. List failed updates at the end.

## Final report

- Counts per verdict.
- Tickets changed, with links.
- Tickets created.
- Tickets still waiting on a decision, and from whom.
- Updates that failed.
