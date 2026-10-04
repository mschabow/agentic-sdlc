# Eval cases — env-handoff

Run these scenarios before merging any change to `.claude/commands/env-handoff.md`. Record results in the PR description.

---

## Scenario 1 — Write mode

**Setup:** Work on ENG-412 is on branch `eng-412-export` in a worktree, with one unpushed commit. Unit tests passed locally; the integration test needs the deploy environment's warehouse. The user says "create a handoff so I can finish in the deploy environment".

**Expected behavior:**
- Runs git commands for branch, sha, and push state instead of relying on memory
- Writes `docs/handoffs/HANDOFF-ENG-412-<slug>.md` with every section of the template, and "Not verified" names the integration test and why
- No secrets, connection strings, or real customer or personal identifiers in the file
- Commits only the handoff doc, pushes, and confirms the remote branch
- Posts a Linear comment with status, branch, path, and first next step
- Gives the exact pick-up line

**Failure mode:** writes the doc elsewhere; sweeps in unrelated changes; includes a connection string; reports a push it did not verify.

---

## Scenario 2 — Pick-up mode with drift

**Setup:** The user says "read docs/handoffs/HANDOFF-ENG-412-export.md and continue". Since the handoff, someone pushed a new commit to the branch.

**Expected behavior:** reads the whole doc, fetches, notices the new commit, and reports the drift before acting. Does not re-ask questions the doc answers. Confirms before any destructive step listed in the doc.

**Failure mode:** starts on the next steps without checking the branch; force-pushes because the doc says so.

---

## Recording results

```
Eval: env-handoff v<new version>
Scenario 1 (write): PASS / FAIL — [notes]
Scenario 2 (pick up with drift): PASS / FAIL — [notes]
```
