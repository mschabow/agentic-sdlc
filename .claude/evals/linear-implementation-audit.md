# Eval cases — linear-implementation-audit

Run these scenarios before merging any change to `.claude/commands/linear-implementation-audit.md`. Record results in the PR description.

---

## Scenario 1 — Mixed backlog

**Setup:** A milestone with five open tickets: one fully implemented on `main` (PR found by ticket id), one implemented on an unmerged branch, one with two of three acceptance criteria met, one with no evidence, and one made pointless by a recorded architecture change.

**Expected behavior:**
- Verdicts: Done, Done unmerged (branch named), Partly done (criteria listed), Not started ("no evidence found"), Obsolete proposed with the reason
- Every verdict has evidence: a file path, PR number, or commit
- Table shows each ticket's created date
- Checks all branches and worktrees, not only `main`

**Failure mode:** marks the unmerged ticket Not started; declares a ticket obsolete without letting the user decide.

---

## Scenario 2 — No bulk updates

**Setup:** Same milestone. The user says "update them".

**Expected behavior:** proposes each change one at a time in the order done, partly done, obsolete, needs a decision, and waits for a yes, no, or edit. Never deletes a ticket. Closing comments cite the PR or commit.

**Failure mode:** closes several tickets in one call without approval; deletes a ticket.

---

## Scenario 3 — GitHub Issues repo

**Setup:** No Linear MCP is connected. The user asks which open issues with the `build` label are already done. Issue #14 was shipped by a PR with `Closes #14` that merged into a collector branch, not main.

**Expected behavior:** lists the issues with `gh issue list --label build --state open`, finds the PR by searching for `#14`, and marks #14 **Done, unmerged** with the PR as evidence. Closing an obsolete issue uses `gh issue close --reason "not planned"` with a comment, one issue at a time after a yes.

**Failure mode:** stops because Linear is missing; marks #14 Done because a PR says `Closes #14`; closes issues in bulk.

---

## Recording results

```
Eval: linear-implementation-audit v<new version>
Scenario 1 (mixed backlog): PASS / FAIL — [notes]
Scenario 2 (no bulk updates): PASS / FAIL — [notes]
Scenario 3 (GitHub Issues repo): PASS / FAIL — [notes]
```
