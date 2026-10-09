---
name: setup-project
description: Bootstrap a new code repo with the canonical workflow skills, an AGENTS.md scaffold, and a setup checklist. Run once in a new repo before any feature work begins.
version: 1.1.0
changelog:
  - "1.1.0 (2026-10-09): AGENTS.md scaffold has a `## Tickets` section (Linear or GitHub Issues) that the workflow skills read; GitHub Issues examples for branch and PR naming; checklist covers both trackers."
  - "1.0.0 (initial): Repo bootstrap."
---

You are setting up a new code repository to use the spec-driven agentic development workflow.

## Step 1 — Locate the process repo

Ask the human for the path to the process repo (the repo containing this skill). You need it to copy the canonical skills.

## Step 2 — Copy workflow skills

Copy all files from `<process-repo>/.claude/commands/` into `.claude/commands/` in the current repo. Create `.claude/commands/` if it doesn't exist.

Skills to copy:
- `spec-design.md` ← entry point for design phase
- `build.md` ← entry point for build phase
- `spec.md`
- `grill-with-docs.md`
- `verify-context.md`
- `distill-context.md`
- `decompose.md`
- `sync-docs.md`
- `audit-design.md` ← run on demand, not part of the per-feature loop
- `setup-project.md`

Confirm each file was copied successfully.

## Step 3 — Scaffold AGENTS.md

Create `AGENTS.md` at the repo root with this template:

```markdown
# AGENTS.md — [Repo Name]

This file is the first thing Claude Code reads at the start of any build phase.
Keep it accurate and minimal. See the process repo's agent-governance.md for context.

## Build and test commands

- Install: `<fill in>`
- Test: `<fill in>`
- Lint: `<fill in>`
- Build: `<fill in>`

## Tickets

<Linear | GitHub Issues>. For GitHub Issues: tickets are issues in `<owner>/<repo>`; a ticket ID is the issue number (`#12`); read and update with `gh issue view`, `gh issue comment`, and `gh issue create`.

Labels: `<fill in — e.g. design, build, bug, chore, agent-ready, human-required>`

## Branch naming

`<feature-area>/<ticket-id>-<short-description>` — e.g. `payments/PAY-42-add-webhook` (GitHub Issues: `sync/12-google-push-channel`)

## PR naming

`[Ticket ID] Short description of change` — e.g. `[PAY-42] Add Stripe webhook handler` (GitHub Issues: `[#12] Add Google push channel`, with `Closes #12` in the PR body)

## Directory conventions

- Designs live in `designs/<feature-name>/` (spec.md + context.md)
- Tests live in `<fill in>`
- Do not modify files in `<fill in>`

## Code style

- `<fill in — linter, formatter, key conventions>`

## What not to touch without lead sign-off

- `<fill in — migrations, auth, billing, etc.>`
```

## Step 4 — Create designs folder

Create a `designs/` folder at the repo root with a `.gitkeep` so it is tracked. This is where all `spec.md` and `context.md` files will live.

Also create an `adr/` folder (`.gitkeep`) and an empty `glossary.md` at the repo root — `/grill-with-docs` writes to both during design sessions.

## Step 5 — Output the manual checklist

Print the following checklist for the human to complete:

---

**Manual setup steps remaining:**

- [ ] Fill in all `<fill in>` placeholders in `AGENTS.md`
- [ ] Pick the ticket tracker and fill in the `## Tickets` section of `AGENTS.md`. The workflow skills read it.
  - Linear: configure the Linear MCP in Claude Code settings for this repo
  - GitHub Issues: create the labels from the Tickets section (`gh label create <name>`), and make sure `gh` acts as the repo owner's account in this repo
- [ ] Connect the Google Drive connector and confirm `_evergreen/` folder is accessible
- [ ] Create the feature subfolder in Google Drive for the first ticket (`Drive / <Project Area> / <Feature Name>/`)
- [ ] Set up branch protection in GitHub: require PR review + CI passing before merge
- [ ] Confirm agents cannot self-approve PRs (branch protection → require review from someone other than the PR author)
- [ ] Add the agent's GitHub identity to the repo with appropriate scoped permissions
- [ ] Verify CI runs on every branch (not just main)
- [ ] Linear only: sync `AGENTS.md` conventions with Linear's workspace/team agent guidance

---

Setup complete. Run `/spec-design` to begin the first feature's design phase.
