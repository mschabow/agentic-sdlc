---
name: worktree-hygiene
version: 1.0.0
description: Report the state of every git branch and worktree in a repo (unpushed, unmerged, stale, merged) and clean up on request. Use when the user asks "did we commit and push", "what branch is this on", "any unpushed work", or wants to prune worktrees or combine branches.
changelog:
  - "1.0.0 (2026-10-03): Added to the sdlc-workflow plugin so it ships to every account from one source."
---

# Worktree hygiene

The user runs many agent sessions in parallel, each in its own git worktree. Work gets stranded: unpushed commits, merged branches that were never deleted, worktrees nobody remembers. This skill answers "where is everything?" and cleans up safely.

Standing rule: all agentic work happens in a git worktree, not on a plain branch in the main checkout. When starting new work, create a worktree. Use this layout unless the repo already has another: `.claude/worktrees/<ticket-id>-<slug>` with a branch of the same name. This is the layout the EnterWorktree tool creates and that `/spec-design` and `/build` use. A `/build` collector branch is `feat/<parent-id>-<slug>`, in `.claude/worktrees/<parent-id>-<slug>`. Some worktrees may sit beside the repo instead (`../<name>`, the `/spec-design` fallback); `git worktree list` finds both.

## Report mode (default)

Run this for any status question. It changes nothing.

### Gather

```
git fetch --all --prune
git worktree list --porcelain
git branch -vv
git branch -r --merged origin/main
git stash list
gh pr list --state all --limit 100 --json number,headRefName,state,title
```

Use the repo's real default branch if it is not `main`. For each worktree also run `git -C <path> status --porcelain` and `git -C <path> log @{u}..HEAD --oneline` (if there is no upstream, the whole branch is unpushed).

### Present

Answer the user's actual question first, in one sentence (for example: "Yes, committed and pushed; `feat/x` is at `abc123` on origin").

Then one table, one row per branch or worktree:

| Branch | Worktree path | Uncommitted | Unpushed commits | PR | Merged to main | Last commit | Verdict |

Verdicts:

- **Active**: recent work or an open PR. A `/build` collector branch (`feat/<parent-id>-<slug>`) stays active until its PR to the default branch merges.
- **Unpushed work**: commits or changes that exist only on this machine. List these first; they are the ones at risk.
- **Safe to remove**: merged, or the remote branch is gone and nothing is unpushed.
- **Unknown**: no PR, not merged, old. Say what it contains (ticket id from the name, last commit message) so the user can decide.

Also list stashes, and remote branches with no local copy that are already merged.

Keep in mind that a squash merge leaves a branch looking unmerged. Check the PR state before calling a branch unmerged.

## Cleanup mode

Only when the user asks to prune, clean up, or delete.

1. Run the report first.
2. Propose the exact list to remove: worktrees, local branches, remote branches. Wait for a yes. The user may remove items from the list.
3. Never remove anything with uncommitted changes or unpushed commits unless the user names that item and confirms it. Offer to push or stash it first.
4. Remove in this order:
   - `git worktree remove <path>` (no `--force` unless the user confirmed that item).
   - `git branch -d <branch>`. Use `-D` only for a branch whose PR was squash-merged or that the user confirmed.
   - `git push origin --delete <branch>` for remote branches, only if the user asked for origin cleanup.
   - `git worktree prune` at the end.
5. Never delete the default branch, the currently checked-out branch, or a branch with an open PR.
6. Report what was removed and what was kept, with the reason for each kept item.

## Combine mode

When the user asks to put several branches or worktrees onto one branch (for example "have ONE KPI branch"):

1. Show which branches would be combined and what each contains.
2. Create a new branch in a new worktree from the up-to-date default branch, or from the base the user names.
3. Merge each source branch in, oldest first. Stop on a conflict and show it; do not resolve conflicts by discarding one side without asking.
4. Run the tests on the combined branch.
5. Leave the source branches in place until the user confirms the combined branch is good. Then offer cleanup mode.

## After a merge

When the user says a branch was merged or deleted on origin: fetch with prune, switch the main checkout to the default branch and pull, then offer to remove the local branch and its worktree.

If a stacked branch needs to move onto the default branch after its parent merged, propose the rebase command and wait for a yes before any force push. Use `--force-with-lease`, never plain `--force`.

## Other checks

- When asked which GitHub user is active, run `gh auth status`. The user has both a personal and a work account; a push with the wrong one fails or lands in the wrong place.
- Before a push, state the remote and branch it will go to.
