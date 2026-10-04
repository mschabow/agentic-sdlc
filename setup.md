# Setting Up a New Repo

Run this once when creating a new code repository. It takes about 15 minutes end-to-end.

## Prerequisites

Before running `/setup-project`, confirm:

- You have the path to this process repo on your local machine
- The Linear MCP is available in your Claude Code installation
- The Google Drive connector is available in your Claude Code installation
- You have admin access to the new GitHub repo (for branch protection)

## Step 1 — Confirm global skills are installed

All workflow skills should already be available globally at `~/.claude/commands/`. Verify:

```bash
ls ~/.claude/commands/
```

You should see: `spec-design.md`, `build.md`, `spec.md`, `grill-with-docs.md`, `verify-context.md`, `distill-context.md`, `decompose.md`, `sync-docs.md`, `audit-design.md`, `setup-project.md`, `update-skills.md`.

If any are missing, copy them from the process repo:

```bash
cp <process-repo>/.claude/commands/*.md ~/.claude/commands/
```

Global skills are available in every project. You do not need to copy them into each repo to use them.

## Step 2 — Run /setup-project (optional — for version pinning)

If you want to pin a specific version of the skills to this repo (so the project is not affected by future global updates), open Claude Code in the new repo's root directory and run:

```
/setup-project
```

When prompted, provide the path to this process repo. The skill will:
- Copy all workflow skills into `.claude/commands/` (project-scoped copy takes precedence over global)
- Scaffold `AGENTS.md` with placeholders
- Create the `designs/` folder
- Create the `adr/` folder and an empty `glossary.md` at the repo root (both written to by `/grill-with-docs`)
- Print a manual checklist of remaining steps

For most repos, global skills are sufficient — skip this step unless version pinning matters.

## Step 2 — Complete AGENTS.md

Fill in every `<fill in>` in `AGENTS.md`. Do not leave placeholders — an incomplete `AGENTS.md` is worse than none because it gives agents false confidence about conventions that aren't actually defined.

Key sections to fill in carefully:
- **Build and test commands** — the exact commands agents will run; test these manually first
- **What not to touch without lead sign-off** — list anything that can cause data loss, auth issues, billing problems, or production incidents if modified without review

## Step 3 — Configure integrations

| Integration | Where to configure | What to confirm |
|---|---|---|
| Linear MCP | Claude Code project settings | Agent can create and update tickets in this team's workspace |
| Google Drive connector | Claude Code project settings | Agent can read `_evergreen/` and feature subfolders |
| GitHub branch protection | Repo Settings → Branches | PR review required, CI must pass, no self-approval |
| Agent GitHub identity | Repo Settings → Collaborators | Scoped write access only; cannot manage settings or users |
| Linear agent identity | Linear workspace settings | Agent is a workspace member, not a human account |

## Step 4 — Sync AGENTS.md with Linear guidance

Any conventions in `AGENTS.md` must be consistent with the team's Linear workspace/team agent guidance. Check both and resolve any contradictions before the first ticket is picked up.

## Step 5 — Verify

Run a quick smoke test before the first real feature:
1. Create a test design ticket in Linear
2. Run `/spec-design` in the new repo — confirm Claude Code reads `AGENTS.md`, the Linear MCP pulls tickets, and the Drive connector reads `_evergreen/`
3. Confirm the Drive connector can read `_evergreen/`
4. Close the test ticket; do not leave open tickets from setup

## Keeping skills current

When this process repo's skills are updated, propagate the changes:

```bash
cp <process-repo>/.claude/commands/*.md <new-repo>/.claude/commands/
```

Check the PR description for the update in the process repo to understand what changed and whether any behaviour in active features is affected.
