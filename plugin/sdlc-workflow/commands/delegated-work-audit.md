---
name: delegated-work-audit
version: 1.1.0
description: Compare what a teammate or agent delivered in one or more PRs against what was asked in tickets, PR comments, and instructions. Use when the user asks "did this deliver what I asked for", wants an asked-versus-delivered table, or suspects scope creep in someone's PRs.
changelog:
  - "1.1.0 (2026-10-09): Works with GitHub Issues as well as Linear: picks the tracker from AGENTS.md's `## Tickets` section, or uses GitHub Issues when there is no such section and no Linear MCP (deferred tools count as Linear). Linear behaviour is unchanged."
  - "1.0.0 (2026-10-03): Added to the sdlc-workflow plugin so it ships to every account from one source."
---

# Delegated work audit

The user leads engineers who build with agents. Agent-built PRs often deliver more than was asked, or something different. This skill compares the ask to the delivery and helps the user respond.

## Ticket tracker

Before you read or write a ticket, find out which tracker this repo uses:

- **GitHub Issues** if AGENTS.md has a `## Tickets` section that says GitHub Issues.
- **Linear** if that section says Linear. If the Linear tools are not available, stop and ask. Do not fall back to GitHub Issues.
- **No `## Tickets` section:** look for Linear MCP tools, including deferred ones (search for "linear" with ToolSearch). If they exist, use Linear, even if they need authentication first. If there are none, use GitHub Issues and say so in one line.

With Linear, the Linear steps in this skill apply unchanged.

With GitHub Issues, a ticket ID is the issue number (`#12`), and each "Linear" step in this skill means the GitHub issue. Read an issue with `gh issue view 12 --comments`. Search with `gh issue list --search "<terms>" --state all`.

`gh` must act as the account that owns the repo. If the active `gh` account is a different one (for example a work account on a personal repo) and no hook sets `GH_TOKEN`, prefix each `gh` command with `GH_TOKEN=$(gh auth token --user <owner>)`. Never run `gh auth switch`; it changes the account for every other session.

## Step 1: Collect the asks

Find every place the work was specified. Quote each ask with its source.

- The tickets and their acceptance criteria (Linear, or `gh issue view <n> --comments` for GitHub Issues; a PR's `Closes #<n>` names its issue).
- The user's PR comments and review responses (`gh pr view <n> --comments`).
- Any instruction file the user points to (for example a saved review comment).
- Slack or chat messages the user pastes.

Number the asks (A1, A2, ...). If two sources disagree, show both and ask the user which one governs. Do not pick one silently. If the user's own PR comment differs from the ticket, say so; that is useful to them.

## Step 2: Read what was delivered

For each PR, read the diff, not just the PR summary (`gh pr diff <n>`). For stacked PRs, note the base of each and read them in order.

Record what the code actually does. Check the PR description against the diff, and flag claims in the description that the diff does not support.

Also record deletions. Flag removed docs, config, `CLAUDE.md`, `AGENTS.md`, skills, or tests, since those are easy to miss.

## Step 3: Sort into four groups

Every ask and every delivered item goes in exactly one group:

1. **Delivered as asked.**
2. **Delivered but not fully correct.** Say what is off.
3. **Asked for, not delivered.**
4. **Delivered, not asked for.**

Present this as a table with the ask on the left (id, source, quote) and the delivery on the right (PR number, file, what it does, verdict). Put group 4 in its own table, since those items have no ask.

Every row needs evidence: a file path and line, or a quoted ask. If you could not confirm something, write "not verified" instead of guessing.

## Step 4: Check for scope creep

This is usually the user's main concern. For each group 4 item, state:

- What it adds (for example: a cost-capping system, sampling, agentic hooks, hashing, versioned history).
- Whether it conflicts with a stated constraint. Common ones: "standalone module, no integration yet", "each step pulls only the data it needs", "write results to a separate database", "nothing agentic in this PR".
- What it costs: extra review time, extra surface to maintain, risk to the parts that were asked for.
- A recommendation: keep, move to its own PR, or remove.

Also judge size against the ask. If a PR is much heavier than the request, say that directly and show the simplest design that would have met the ask.

## Step 5: Diagram what was built

When the user asks how the delivered system works, draw it as Mermaid in a markdown file. Keep it simple: one diagram for the data flow, with at most about ten nodes. If the first diagram is confusing, split it into two smaller ones instead of adding detail. Where it helps, show the asked-for design next to the built design.

## Step 6: Draft the response

Draft only. Never post a PR comment, review, or message without the user's explicit yes.

Rules for the draft:

- Soft language. The reader is a junior teammate. Describe the gap and the next step; do not assign blame.
- Lead with what was done well, in one or two lines, if that is true.
- Restate the ask as a short numbered list so there is no doubt about scope. If the work should be several PRs, say what goes in each.
- For out-of-scope work, ask for it to be split out or held, and say why in one sentence.
- Include a suggested design when the user asks for one.
- Use plain, short sentences.

If you have questions before the draft is final, ask the user one at a time, each with background and your recommendation.

## Names

Use the names the user uses. If a system shows only an email or handle, write the email or handle. Never expand an email prefix into a first name.

## Output

1. A two or three sentence summary: does the work meet the ask, and what is the biggest gap.
2. The asked-versus-delivered table.
3. The not-asked-for table with recommendations.
4. The diagram, if requested.
5. The draft comment, if requested.
