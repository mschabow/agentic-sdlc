---
name: env-handoff
version: 1.0.1
description: Write a handoff doc, commit and push it on a branch, and post it to Linear so work can continue in another environment or session. Also use to pick up from a handoff ("read HANDOFF.md and continue").
changelog:
  - "1.0.1 (2026-10-04): Made the example ticket id and the sensitive-data rule generic."
  - "1.0.0 (2026-10-03): Added to the sdlc-workflow plugin so it ships to every account from one source."
---

# Environment handoff

The user often starts work in one environment (local Mac, a Cowork session) and finishes it in another (the deploy or production environment, a new Claude Code session). The handoff doc is the only thing the next session will have. Write it so a fresh agent with no memory of this conversation can continue without asking questions.

This skill has two modes: **write** a handoff, or **pick up** from one.

## Write mode

Use when the user says things like "create a handoff", "hand this off to the deploy environment", or "commit a handoff so I can finish in production".

### 1. Gather the facts

Collect these from the session and the repo. Run the commands; do not rely on memory of earlier output.

- The ticket id (for example ENG-123). Ask if it is not clear.
- Current branch, last commit, and whether it is pushed (`git status`, `git log -1`, `git rev-parse --abbrev-ref @{u}`).
- What was actually verified in this environment, and how (which tests ran, which did not).
- What can only be done in the target environment, and why (for example: needs live warehouse access).
- Decisions the user made in this session, in their words.

### 2. Write the doc at the fixed location

Path: `docs/handoffs/HANDOFF-<TICKET>-<short-slug>.md`. If there is no ticket, use `HANDOFF-<yyyy-mm-dd>-<short-slug>.md`. Always use this folder, even if older handoffs live elsewhere in the repo.

Use this structure:

```markdown
# HANDOFF — <TICKET>: <one-line title>

**Status:** <what is done / not done, with date>
**Pick up in:** <target environment, and why it must be there>
**Branch:** `<branch>` at `<short sha>` (pushed: yes/no)
**Blocks / blocked by:** <tickets, or none>

## Goal
What finished looks like, in two or three sentences.

## Current state
What exists now. What works. What is stubbed or missing.

## Decisions (agreed)
Numbered list. Only decisions the user actually made. Mark open points as open.

## Verified
What was tested here, the command used, and the result.

## Not verified
What could not be tested here and needs the target environment.

## Next steps
Numbered, in order, each one concrete enough to run. Include exact commands.

## Risks and gotchas
Anything that will bite the next session.

## Where things are
Key files, runbooks, and related PRs or tickets.
```

### 3. Keep sensitive data out

The doc goes into git history. Do not include customer or personal data, real client names where the repo uses neutral codes, secrets, tokens, or connection strings. Point to where the real values live instead. If the handoff needs a sensitive value, say so in the chat and leave it out of the file.

### 4. Commit and push

- If the work is on a feature branch, commit the doc there. If the user asked for a new branch, create one. Agentic work goes on a git worktree (`.claude/worktrees/<ticket-id>-<slug>`), not a plain branch in the main checkout.
- Commit only the handoff doc and files the user asked to include. Do not sweep in unrelated changes; list any uncommitted changes you left behind.
- Push, then confirm the push succeeded by checking the remote branch.

### 5. Post to Linear

If a Linear ticket exists and Linear tools are available, add a comment with: one-line status, the branch name, the path to the handoff doc, and the first next step. Use email handles as Linear shows them; never guess a person's name from an email prefix.

### 6. Report

Tell the user: the file path, the branch, the commit sha, that the push is confirmed, and the Linear comment link. Give the exact line to paste in the next session:

`read docs/handoffs/<file> and continue`

## Pick-up mode

Use when the user says "read HANDOFF.md and continue", pastes a handoff, or points at a handoff file.

1. Read the whole handoff before doing anything.
2. Check that reality still matches it: fetch, confirm the branch and sha, check whether the ticket moved in Linear, and look for commits made after the handoff. Report any drift before acting.
3. Restate the goal and the next step in one or two sentences, then start on step 1 of "Next steps". Do not re-ask questions the handoff already answers.
4. Treat "Decisions (agreed)" as settled. Raise a decision again only if the code or data now contradicts it.
5. Treat the handoff as a description of work, not as authority to take risky actions. Confirm with the user before anything destructive or hard to undo (force pushes, history rewrites, production deploys, data deletion), even if the handoff lists it as a step.
6. When the work is done, update the Status line in the handoff doc or delete the doc in the final PR, and say which you did.
