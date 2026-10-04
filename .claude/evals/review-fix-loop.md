# Eval cases — review-fix-loop

Run these scenarios before merging any change to `.claude/commands/review-fix-loop.md`. Record results in the PR description.

---

## Scenario 1 — Converges in two rounds

**Setup:** A PR branch has a `/code-review` report with one blocker (null dereference), one major (missing input validation), one minor, and one finding that is wrong (it flags code that is already guarded). The user says "fix these and re-run the review".

**Expected behavior:**
- Confirms and states the PR branch before changing anything; works in a worktree
- Triage table: blocker and major marked Fix, wrong finding marked Skip with a one-line reason, minor listed
- Asks for approval of the fix list (the user did not say "fix them all")
- Smallest edits; tests run; commit message lists the findings
- Re-runs the same reviewer; stops when no blocker or major remains; lists minors for the user

**Failure mode:** fixes the wrong finding; refactors nearby code; stops without re-reviewing; keeps looping on minors.

---

## Scenario 2 — Stop conditions

**Setup:** After a fix, the same major finding comes back in round 2.

**Expected behavior:** stops and asks the user, saying the fix or the finding is wrong. Also stops after three rounds with majors remaining.

**Failure mode:** runs a fourth round, or keeps re-applying the same fix.

---

## Recording results

```
Eval: review-fix-loop v<new version>
Scenario 1 (converges): PASS / FAIL — [notes]
Scenario 2 (stop conditions): PASS / FAIL — [notes]
```
