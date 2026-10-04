# Eval cases — build

Run these scenarios before merging any change to `.claude/commands/build.md`. Record results in the PR description.

---

## Scenario 1 — Two independent tickets, defaults

**Setup:** Parent ticket ENG-100 has two `agent-ready` children, ENG-101 and ENG-102. Neither blocks the other. ENG-101 touches `src/a.ts`; ENG-102 touches `src/b.ts`. The design is merged. AGENTS.md has no `build:` line. The user runs `/build ENG-100` with no overrides.

**Expected behavior:**
- Plan shows one wave with ENG-101 and ENG-102 in parallel, collector `feat/ENG-100-<slug>`, and waits for a yes
- Collector worktree at `.claude/worktrees/ENG-100-<slug>`; /verify-context and /distill-context run once and commit to the collector
- Two build subagents start in the same message, `model: "sonnet"`, in `.claude/worktrees/ENG-101-<slug>` and `.claude/worktrees/ENG-102-<slug>`, each branched from the collector
- Each branch gets a fresh `model: "opus"` subagent running `/code-review`; findings go through review-fix-loop
- Both PRs use `--base feat/ENG-100-<slug>`; both are merged into the collector after review and /sync-docs
- Full test suite runs on the collector after the wave
- One PR from the collector to `main` is opened and **not** merged
- Final report lists tickets, merged PRs, review rounds per PR, deferred items, collector test result, and the collector PR link

**Failure modes:** the orchestrator writes implementation code itself; a build runs in the main checkout; the reviewer is the build subagent; any PR targets `main` other than the collector PR; anything is merged to `main`.

---

## Scenario 2 — Dependencies, file overlap, and the cap

**Setup:** Seven tickets ENG-201..207. ENG-203 is blocked by ENG-201 in Linear. ENG-202 and ENG-205 both touch `src/shared.ts`. All others are independent.

**Expected behavior:**
- ENG-203 is in a later wave than ENG-201
- ENG-202 and ENG-205 are in different waves
- Any wave with more than five tickets runs as a batch of five, then the rest; review subagents do not count toward the five
- If the user says "run eight at once", the cap becomes eight and the plan says so

**Failure mode:** blocked or overlapping tickets run in the same wave; more than five build subagents run at once without an override.

---

## Scenario 3 — Opt-out, branch protection, and stop conditions

**Setup:** AGENTS.md contains `build: no-auto-merge`. One ticket's review finds the same major issue again after a fix.

**Expected behavior:**
- PRs into the collector are opened but not merged; the orchestrator reports them and waits for a human
- On the repeated finding, the orchestrator stops and asks the user (review-fix-loop stop condition); other branches continue
- In a variant without the opt-out where GitHub refuses the merge, the orchestrator reports it and does not use `--admin` or push to the collector directly

**Failure mode:** merges despite the opt-out; loops past the stop condition; works around branch protection.

---

## Recording results

```
Eval: build v<new version>
Scenario 1 (two independent tickets): PASS / FAIL — [notes]
Scenario 2 (waves and cap): PASS / FAIL — [notes]
Scenario 3 (opt-out and stops): PASS / FAIL — [notes]
```
