# Ticket trackers: Linear or GitHub Issues

Work repos use Linear. Some repos, such as personal projects, have no Linear and use GitHub Issues. The workflow skills support both. Linear behaviour does not change.

## How a skill picks the tracker

1. If AGENTS.md has a `## Tickets` section that says GitHub Issues, use GitHub Issues.
2. If that section says Linear, use Linear. If the Linear tools are not available, stop and ask. Do not fall back to GitHub Issues.
3. If there is no `## Tickets` section, look for Linear MCP tools, including deferred tools and tools that still need authentication. If they exist, use Linear. If there are none, use GitHub Issues and say so.

Rule 3 keeps a work repo on Linear when the Linear MCP is only deferred or signed out. Add a `## Tickets` section to every GitHub Issues repo so the choice never depends on which tools a session has.

Example `## Tickets` section (from `mschabow/calendar-sync-app`):

```markdown
## Tickets

Tickets are GitHub Issues in `mschabow/calendar-sync-app`. There is no Linear. When a workflow skill asks for a ticket ID, use the issue number (`#12`). Read and update tickets with `gh issue view`, `gh issue comment`, and `gh issue create`.

Labels: `design` (spec work), `build` (implementation), `bug`, `chore`.
```

`/setup-project` adds this section to new repos.

## GitHub Issues conventions

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
| Labels such as `agent-ready` | The labels AGENTS.md lists. If a label does not exist, write it as a line in the body (`Routing: agent-ready`) |
| Project or milestone | A milestone or a label |

- Branches: `<area>/<issue>-<slug>`, for example `sync/12-google-push-channel`. Drop the `#` in branch, worktree, and file names.
- PR titles: `[#<issue>] Title`, with `Closes #<issue>` in the body.
- The design PR has `Closes #<design-issue>`, so the design issue closes when the design merges.
- `/decompose` creates the implementation issues with the `build` label after a yes, and adds them as a task list to the design issue. The `Parent:` and `Blocked by:` body lines are what the skills read; native GitHub relations (`gh issue create --parent`, `--blocked-by`) are added as well where `gh` supports them.
- `/build` implementation PRs go into a collector branch. GitHub closes an issue only when a PR merges into the default branch, so the collector-to-main PR repeats one `Closes #<issue>` line for each ticket built, plus the parent if it is still open.

AGENTS.md wins over these defaults when it says something different.

## The `gh` account

`gh` must act as the account that owns the repo. On a machine where the active `gh` account is a work account, personal repos need the personal account's token. Unless a hook already sets `GH_TOKEN`, run each command as:

```bash
GH_TOKEN=$(gh auth token --user <owner>) gh issue view 12
```

Never run `gh auth switch`. It changes the account for every other session on the machine.

## Keeping the skills in sync

Each skill that reads or writes tickets has a `## Ticket tracker` section with these rules. Skills that create, close, or comment on tickets carry the full table; skills that only read carry a short version. When you change a rule here, change it in those sections too.
