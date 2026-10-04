---
name: build
version: 2.0.0
description: "Entry point for the build phase. Orchestrates the full execution loop for one implementation ticket, a list, or a parent ticket with children: pulls the tickets, plans waves, runs /verify-context, does Pass 1 context gather, runs /distill-context, then builds each ticket with a Sonnet subagent in its own worktree, reviews each branch with a fresh Opus /code-review subagent, and merges into one collector branch that gets a single PR to main. Run this at the start of any implementation work."
changelog:
  - "2.0.0 (2026-10-03): Orchestrated build. Accepts one ticket, a list, or a parent with children, and plans dependency waves. Each ticket is built by a Sonnet subagent in its own worktree (at most five at once), reviewed by a fresh Opus /code-review subagent through review-fix-loop, and merged into a collector branch; the orchestrator opens one collector-to-main PR and never merges it. New Defaults section lists the overrides. AGENTS.md can opt out of auto-merge with `build: no-auto-merge`."
  - "1.1.0 (2026-10-01): New step 0 — start in a fresh ticket-named worktree on a verified, current base."
  - "1.0.0 (initial): Single-ticket build loop."
---

You are orchestrating the build phase for one or more implementation tickets. Follow these steps in order.

## Defaults

Unless the user's prompt overrides them, every `/build` run uses these defaults:

1. **Sonnet build subagents, in parallel, each in its own worktree.** Each ticket is built by its own subagent on the Sonnet model, in its own git worktree at `.claude/worktrees/<sub-issue-id>-<slug>`. Tickets in the same wave run in parallel, at most **five** build subagents at once.
2. **Opus review on each branch.** When a build subagent finishes, a fresh subagent on the Opus model runs `/code-review` on its branch. Findings go through the `review-fix-loop` skill.
3. **One collector branch before main.** Every implementation PR targets the collector branch `feat/<parent-ticket-id>-<slug>`, never the default branch. You open one PR from the collector to the default branch and stop. A human merges that PR.

The user can override any default in the prompt, for example "single agent, no subagents", "use Opus for the build", "run eight at once", or "PR straight to main". Apply only the overrides the user states, and repeat them back in the plan (step 2).

A single ticket still uses a Sonnet build subagent and an Opus review subagent.

**You are the orchestrator. You do not write implementation code.** You plan, gather context, spawn subagents, track them, and merge. Code changes, fixes, and rebases are done by build subagents.

## 1 — Pull the tickets

Ask: "Which Linear ticket(s)? Give one ID, a list, or a parent ticket." Accept any of these. For a parent ticket, pull its children. Pull each ticket via the Linear MCP and confirm:

- Each ticket is tagged `agent-ready`. A `human-required` ticket is dropped from the run and handed off to the assigned engineer; tell the user which ones.
- All tickets belong to one feature: one linked design, merged, with spec.md + context.md under `designs/<feature>/`. If the tickets span more than one feature, stop and ask the user to split the run.
- The **parent ticket** for the collector branch: the Linear parent issue of the tickets if they have one, otherwise the design ticket they were decomposed from.

## 2 — Plan the waves

Skip this step if there is only one ticket.

Read the dependencies between tickets:
- Linear `blocked by` / `blocks` relations, and the Dependencies field from `/decompose`.
- Any build order the user gives. The user's order wins over Linear.

Estimate the files each ticket will touch from its acceptance criteria and the Relevant code section of context.md.

Group the tickets into **waves**. A wave holds tickets that have no unmet dependencies and no overlapping files. A ticket that depends on another goes in a later wave than it. Two tickets that touch the same file go in different waves, even when they are independent. If you cannot tell whether two tickets overlap, put them in different waves.

A wave with more than the cap (five by default) runs in batches of five.

Show the plan to the user:

```
Collector: feat/<parent-id>-<slug>  →  PR to <default-branch> (human merges)
Overrides: <none | the ones the user gave>
Wave 1 (parallel): ENG-101, ENG-102, ENG-104
Wave 2 (parallel): ENG-103 (blocked by ENG-101), ENG-105 (shares src/x.ts with ENG-102)
Wave 3: ENG-106
```

Wait for a yes before starting. Apply any changes the user makes to the plan.

## 3 — Collector branch and worktree

Create or reuse the collector branch and do all orchestration work in its worktree. Never work in the main checkout.

- `git fetch origin`. Find the default branch with `git symbolic-ref refs/remotes/origin/HEAD` (or `gh repo view --json defaultBranchRef`).
- If `origin/feat/<parent-id>-<slug>` exists (an earlier run started it), reuse it. Otherwise create it from `origin/<default-branch>`.
- Create the collector worktree at `.claude/worktrees/<parent-id>-<slug>`:
  - **Preferred:** the EnterWorktree tool with that name, then check out or reset to the collector branch.
  - **Fallback:** `git worktree add -b feat/<parent-id>-<slug> .claude/worktrees/<parent-id>-<slug> origin/<default-branch>` (or `git worktree add .claude/worktrees/<parent-id>-<slug> feat/<parent-id>-<slug>` when reusing it).
- Make sure `.claude/worktrees/` is in `.gitignore`. If it is not, add it in the collector's first commit.

Verify the base before continuing:
- For a new collector, confirm `git rev-parse HEAD` matches `git rev-parse origin/<default-branch>`. If the worktree is behind (e.g. EnterWorktree branched off a stale local ref), reset the new, still-empty branch to `origin/<default-branch>`.
- Confirm the expected app directories are present (the top-level layout described in AGENTS.md or the README), along with the merged design under `designs/<feature>/`. If any are missing, stop and tell the human — the worktree is on the wrong base or repo.

Push the collector branch so the implementation PRs have a base. Report the collector worktree path, branch name, and base commit to the human.

All ticket worktrees go in `.claude/worktrees/` at the root of the **main** checkout (`git rev-parse --git-common-dir` gives its `.git`), not inside the collector worktree.

## 4 — Read AGENTS.md

Read AGENTS.md at the repo root. Note build commands, test commands, branch naming, and restricted areas.

Also look for `build: no-auto-merge`. If it is present, you open the implementation PRs into the collector but do not merge them; a human merges them (step 9). This is for repos where someone else owns the merge rules, such as a client-owned org with its own CI/CD.

## 5 — /verify-context

Run the /verify-context skill once for the feature. Check spec.md and context.md for drift since the design PR merged:
- Git log for changes to files referenced in the spec
- Linear for new comments, decisions, or changes to any ticket in the run
- Google Drive for new or updated documents relevant to the feature

Apply the staleness threshold from review-policy.md:
- **STALE — acceptance criteria, interfaces, or data flow affected:** stop. Flag to lead. A spec revision PR is needed before proceeding.
- **STALE — context.md only:** update context.md, commit it to the collector branch, and continue.
- **CURRENT:** continue.

## 6 — Pass 1 and /distill-context

Do a broad context gather anchored on spec.md and context.md, covering every ticket in the run:
- Codebase: full files for the contact points in the spec, plus surrounding context for side effects
- Google Drive: the feature subfolder (linked in the ticket's Sources field) and `_evergreen/`
- Linear: ticket history and any comments since the design PR merged
- Web search and Context7/MCPs for current library documentation relevant to the spec

Slack is not a context source.

Then run the /distill-context skill, Steps 1–4: synthesise Pass 1 into one minimal context.md for the whole run, confirm with the human, and commit it to the collector branch. Push the collector. Do not let /distill-context spawn the build agent; step 7 does that. If the run's context does not fit in 300 lines, stop and propose splitting the run.

Every ticket worktree branches from the collector, so each build subagent gets this context.md.

## 7 — Build each wave

For each wave, in order, and in batches of at most the cap:

1. `git fetch origin`. For each ticket, create its worktree from the current collector tip:
   `git worktree add -b <branch> <main-root>/.claude/worktrees/<sub-issue-id>-<slug> origin/feat/<parent-id>-<slug>`
   Use the AGENTS.md branch naming convention for `<branch>`; if it has none, use `<sub-issue-id>-<slug>`.
2. Spawn one build subagent per ticket, all in the same message so they run in parallel. Use the Agent tool with `model: "sonnet"`. Do not use the Agent tool's own worktree isolation; the worktree from step 1 is the one to use.
3. Give each subagent only: AGENTS.md, spec.md, context.md, its ticket (ID, title, description, acceptance criteria), its worktree path, and its branch. Nothing from Pass 1. Its instructions:

> Work only in `<worktree path>`, on branch `<branch>`. Never touch the main checkout or another worktree. Read AGENTS.md, spec.md, and context.md. Derive the tests for this ticket from its acceptance criteria and the draft test list in spec.md, and freeze them. Do not modify spec-derived tests during the build; add tests for edge cases separately. Implement the ticket against context.md and the repo. Run the test suite. Commit to `<branch>`, but do not push and do not open a PR. Report: what you built, the files changed, the test command and result, and anything you could not do.

As each build subagent finishes, start step 8 for its branch. Do not wait for the rest of the batch. When a batch slot frees up, start the next ticket in the wave.

If a build subagent fails or reports a blocker, do not take over the code. Re-brief it (SendMessage), or stop that ticket and report it to the user. Other tickets in the wave continue.

## 8 — Review, sync docs, open the PR

For each finished branch:

1. **Review.** Spawn a new subagent with `model: "opus"`. It must not be the subagent that wrote the code. It runs `/code-review` on `<branch>` in `<worktree path>`, against `feat/<parent-id>-<slug>` as the base, and returns the findings with severities. Review subagents do not count toward the build cap.
2. **Fix loop.** Run the findings through the `review-fix-loop` skill. You make the decisions the skill would ask the user for: which findings to fix, skip, or defer. You do not stop to ask the user about each finding. Send the fixes to the ticket's build subagent (SendMessage), working in the same worktree. Each new review round uses a fresh Opus subagent. Stop when no blocker or major findings remain.

   **Stop and ask the user** when the loop hits one of review-fix-loop's stop conditions: three rounds with majors remaining, a finding that comes back after a fix, or a fix that would change behaviour or scope beyond the ticket. Other branches continue while you wait.
3. **/sync-docs.** Have the build subagent run /sync-docs on the branch, against the collector as the base. Doc-only gaps: accept the skill's recommended fix. A discrepancy that changes acceptance criteria, interfaces, or data flow: bring it to the user. Commit the doc updates on the branch.
4. **Push and open the PR.** Have the build subagent push the branch and post a status update to its Linear ticket. Open the PR with `--base feat/<parent-id>-<slug>`. Never target the default branch. The PR description includes the /verify-context verdict from step 5, the review rounds and their findings by severity, anything skipped or deferred, the test result, and confirms /sync-docs ran.

## 9 — Merge into the collector

When a PR has passed review (no blocker or major findings) and /sync-docs:

- **Default:** merge it into the collector: `gh pr merge <n> --squash`, or the merge method AGENTS.md names.
- **`build: no-auto-merge` in AGENTS.md:** do not merge. Report the PR and wait for the human to merge it before the next wave.
- **GitHub refuses the merge** (branch protection, required checks, required reviews): report it and wait. Do not work around it — no `--admin`, no disabling protection, no direct pushes to the collector.
- **Merge conflict with the collector:** send the branch back to its build subagent to rebase on the collector and re-run the tests, then re-review the changed parts. Do not resolve code conflicts yourself.

After the PR merges, update the collector worktree (`git pull`).

**After each wave** has fully merged, run the full test suite from AGENTS.md in the collector worktree. If it fails, stop: report the failure and which merges went in, and do not start the next wave. If it passes, start the next wave from the new collector tip.

## 10 — Collector PR to main

When the last wave has merged and the full suite passes on the collector:

- Open one PR from `feat/<parent-id>-<slug>` to the default branch. If one is already open from an earlier run, update its description instead.
- The description lists the tickets built, the PRs merged into the collector, the collector test result, and anything deferred.
- **Never merge this PR.** Stop here. A human reviews and merges it.

## 11 — Final report

For a multi-ticket run, report:

- Tickets built, and tickets dropped or stopped, with the reason.
- PRs merged into the collector, with links. PRs waiting on a human, and why.
- Review rounds per PR, and findings fixed, skipped, or deferred.
- Anything deferred, with an offer to file follow-up tickets (file them only after a yes).
- Test results on the collector after each wave.
- The link to the collector-to-main PR.

For a single ticket, report the same items that apply.

Leave the ticket worktrees in place. Offer to run `worktree-hygiene` cleanup once the collector PR is merged.
