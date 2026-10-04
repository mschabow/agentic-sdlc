# Eval cases — verify-context

Run these scenarios before merging any change to `.claude/commands/verify-context.md`. Record results in the PR description.

---

## Scenario 1 — CURRENT (no relevant changes)

**Setup:** A design PR was merged 2 weeks ago touching `src/payments/checkout.ts` and `src/payments/types.ts`. Since then, only unrelated files (`src/auth/session.ts`, `README.md`) have changed.

**Expected behavior:**
- Mechanical diff step runs and reports files in spec that have changed: none
- LLM assessment finds no material changes in Linear or Drive
- Verdict: **CURRENT**
- Output includes "mechanical diff: no relevant file changes"

**Failure mode:** skill skips the git diff step and goes straight to LLM assessment, missing the opportunity to anchor the analysis in hard evidence.

---

## Scenario 2 — STALE: context.md only

**Setup:** Design PR merged 3 weeks ago. The spec references `stripe-node v13`. Since then, `stripe-node` was upgraded to v14. `src/payments/checkout.ts` (in the spec) was not changed. A new Drive doc titled "Stripe v14 migration notes" was added to the feature folder.

**Expected behavior:**
- Mechanical diff: `src/payments/checkout.ts` unchanged
- LLM assessment finds the Drive doc and library version discrepancy
- Verdict: **STALE**
- Recommendation: update context.md with the v14 reference — no new design PR required
- Output includes the Drive doc as the source of the change

**Failure mode:** skill misses the Drive doc and returns CURRENT, leaving the build agent working against an outdated library assumption.

---

## Scenario 3 — STALE: spec change required

**Setup:** Design PR merged last week. Since then, a new Linear comment from the lead reads: "After discussing with security, we need to encrypt the session token at rest before storing — this changes the checkout flow." The spec's Design section describes storing the raw token. `src/payments/checkout.ts` has not changed.

**Expected behavior:**
- Mechanical diff: `src/payments/checkout.ts` unchanged (hard to catch with diff alone)
- LLM assessment finds the Linear comment
- Verdict: **STALE**
- Recommendation: new design PR required — this change affects acceptance criteria and data flow
- Output cites the specific Linear comment

**Failure mode:** skill returns CURRENT because no files changed, missing the Linear comment entirely — agent proceeds with an out-of-date spec.

---

## Recording results

In the PR description, record:

```
Eval: verify-context v<new version>
Scenario 1 (CURRENT): PASS / FAIL — [notes]
Scenario 2 (STALE - context only): PASS / FAIL — [notes]
Scenario 3 (STALE - spec required): PASS / FAIL — [notes]
```
