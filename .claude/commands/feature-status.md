---
name: feature-status
version: 1.0.0
description: Show the build status of a product feature, story by story and surface by surface (backend, web, Slack, jobs), across every slice, wave and platform ticket. Gathers status from Linear, GitHub and the specs, flags user journeys that have no surface, and publishes or updates one shareable status page. Use when the user asks "where are we", "what's built", "feature status", "build status", or wants a progress view for a feature or project.
changelog:
  - "1.0.0 (2026-10-07): First version, written from the People Planning slice 1 and wave A builds."
---

You are producing a build status view for one product feature. It answers four questions:
- what a user can do today;
- what is in progress;
- what is missing;
- what stands between the build and real users.

Report facts you have read. Never guess a status.

## 1 — Scope

Work out the feature from the request or the current repo. Find:
- **The Linear project:** where the tickets live.
- **The repo:** the code.
- **The specs:** `designs/<feature>*/spec.md`. A feature can have several, such as slice 1 and slice 2 wave A.
- **The integration branches:** for example `slice1`, `slice2-wave-a`, and `main`.

If any of these is ambiguous, ask once and then go on.

If a status page for this feature already exists, update it instead of creating a new one. Find it with the Artifact tool's `list` action, matching on the title or on a link recorded in the spec.

## 2 — Gather (in parallel)

- **Linear:** list every issue in the project, with id, title, status, labels, `parentId` and priority. A design ticket (title starts with "Design:") is the parent of its build tickets.
- **GitHub:**
  - open PRs: number, title, base branch, draft flag, and CI state from `gh pr checks`;
  - merged PRs: number, title, base branch, merge date;
  - for each integration branch, its head and how many commits it is ahead of the branch it merges into, from `git rev-list --count`.
- **Specs:** for each spec, collect:
  - the user stories (`### US<n>: <title>`);
  - the build order;
  - the pre-deploy gates;
  - the out-of-scope list;
  - the status line.
- **Running work (optional):** any active builds or workflows in this session, such as background tasks or open worktrees.

## 3 — Map stories to tickets and surfaces

For each user story:
1. **Tickets:** match it to its tickets through each ticket's acceptance criteria (the `US<n>.<m>` references) or its title.
2. **Surfaces:** decide which surfaces it has:
   - **Backend:** API, jobs, data.
   - **Web:** an SPA screen.
   - **Slack:** a bot flow, or another channel such as email.

   Use the spec's Screens or Surfaces section and each ticket's scope. If the scope is unclear, check the merged PR's changed files: `frontend/` means web, `slack/` means Slack, everything else is backend.
3. **Status per surface,** from the ticket and PR state:
   - **Built:** the ticket is Done and the PR is merged into the feature's integration branch.
   - **In progress:** the ticket is In Review, has an open PR, or is building now.
   - **Not started:** a ticket exists in the Backlog.
   - **Gap:** an actor must use this surface to finish their job, and no ticket covers it. Examples: a Slack button that links to a screen nobody built, or an admin who could only act through curl. Gaps matter most. Call each one out by name.
4. **Not applicable:** mark a surface "n/a" only when the spec says the story doesn't use it.

## 4 — Summarise the gates

List what stands between the build and people using it:
- **Merge:** sign-off reviews and any human-required approvals that are still open.
- **Deploy:** the pre-deploy gates and infrastructure.
- **Pilot:** missing screens or journeys from the gaps above, and pending decisions (tickets labelled `human-required` that ask a question).

## 5 — Publish

Build or update one page. Keep the same URL across updates, and set the page title to `<Feature> Build Status`. The page has these parts, in order:
1. **Header:** the snapshot time (UTC) and the sources.
2. **Four summary cards:** each release band (slice or wave) as one line of status plus one sentence, then "Deployed" and "Biggest gap".
3. **A table for each release band:** rows are features or stories; columns are each relevant surface plus Tickets. Each cell shows its status as both a shape and a word (✓ Built, ◐ In progress, ○ Not started, ✕ Gap). Never use colour alone.
4. **The backlog:** the next wave and the platform or tooling tickets.
5. **"What stands between this and people using it":** the gates from step 4.

Then reply in chat, in no more than 8 lines:
- the link;
- what is built;
- what is moving;
- the single biggest gap;
- anything that needs the user's decision.

Don't repeat the whole table in chat.

## Rules

- Read only. Don't change tickets, PRs or branches while building the status view.
- Say so whenever a source couldn't be read (Linear disconnected, `gh` failing), and mark the affected cells "unknown". Never guess a status.
- Treat a ticket marked Done whose PR isn't merged as a discrepancy, and list it.
- Keep names consistent with the spec's glossary.
