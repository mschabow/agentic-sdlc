---
name: verify-context
version: 1.2.0
description: Check whether spec.md and context.md are still accurate given changes since the design PR merged. Run at the start of each implementation ticket and before opening a PR. Reports "CURRENT" or "STALE" with specific changes listed.
changelog:
  - "1.2.0 (2026-10-09): Works with GitHub Issues as well as Linear: picks the tracker from AGENTS.md's `## Tickets` section, or uses GitHub Issues when there is no such section and no Linear MCP (deferred tools count as Linear). Linear behaviour is unchanged."
  - "1.1.0 (2026-06-18): Added mechanical git diff step before LLM assessment — provides hard signal from changed files, not just LLM judgment"
  - "1.0.0 (initial): LLM-only staleness assessment"
---

You are verifying that the design spec and context file for this feature are still accurate before implementation proceeds.

## Ticket tracker

Before you read or write a ticket, find out which tracker this repo uses:

- **GitHub Issues** if AGENTS.md has a `## Tickets` section that says GitHub Issues.
- **Linear** if that section says Linear. If the Linear tools are not available, stop and ask. Do not fall back to GitHub Issues.
- **No `## Tickets` section:** look for Linear MCP tools, including deferred ones (search for "linear" with ToolSearch). If they exist, use Linear, even if they need authentication first. If there are none, use GitHub Issues and say so in one line.

With Linear, the Linear steps in this skill apply unchanged.

With GitHub Issues, a ticket ID is the issue number (`#12`), and each "Linear" step in this skill means the GitHub issue. Read an issue with `gh issue view 12 --comments`. Search with `gh issue list --search "<terms>" --state all`.

`gh` must act as the account that owns the repo. If the active `gh` account is a different one (for example a work account on a personal repo) and no hook sets `GH_TOKEN`, prefix each `gh` command with `GH_TOKEN=$(gh auth token --user <owner>)`. Never run `gh auth switch`; it changes the account for every other session.

## Step 1 — Mechanical diff (run first)

Before reading any documents, run a git diff to surface hard evidence of change:

1. Find the merge commit for the design PR. Look for the commit that added `designs/<feature>/spec.md` to the repo.
2. Run: `git diff <design-pr-merge-commit>..HEAD -- <files>` where `<files>` is every file path explicitly mentioned in spec.md (contact points, interfaces, data files).
3. List any files that have changed since the design PR merged. These are **candidate stale signals** — they may or may not be material.

If no files mentioned in spec.md have changed, note "mechanical diff: no relevant file changes" and proceed to Step 2.

If files have changed, list them with their diff summary before proceeding. These will anchor the LLM assessment in Step 2.

## Step 2 — LLM assessment

Now assess materiality using the diff output from Step 1 plus the following sources:

1. Read spec.md and context.md for this feature (find them in `designs/<feature>/` or the path referenced in the ticket).
2. For each file flagged in Step 1: read the diff and assess whether the change affects acceptance criteria, component interfaces, or data flow described in spec.md.
3. Check the tracker (Linear, or `gh issue view <n> --comments`) for any new comments, decisions, or changes to the ticket or linked PRD since the design was approved.
4. Check Google Drive (via connector) for any new or updated documents relevant to this feature since the design was created.

## Step 3 — Verdict

Report one of two verdicts:

---

**CURRENT** — spec.md and context.md accurately reflect the current state. No material changes found. Implementation can proceed.

*(Include: "mechanical diff: X files changed / 0 material" or "mechanical diff: no relevant file changes")*

---

**STALE** — the following changes are material to the design:

For each issue:
- What changed (source: git commit hash / Linear comment or GitHub issue comment / Drive document)
- Which section of spec.md or context.md it affects
- Recommended update

Apply this threshold to determine required action:

| What changed | Action |
|---|---|
| Acceptance criteria, component interfaces, or data flow in spec.md | **New design PR required.** Update spec.md, push as a PR, get lead approval before any implementation begins. |
| context.md only — library version, doc reference, resolved ambiguity that does not change what is being built | **No new review.** Developer updates context.md, commits it, and proceeds. Note the update in the PR description. |

When in doubt, flag to the lead before proceeding.

---

Add a one-line summary of the verdict to the implementation PR description so reviewers can confirm this check was run. Include the mechanical diff result.

Example: `verify-context: CURRENT (mechanical diff: 2 files changed, neither material to spec)`
