---
name: sync-docs
version: 1.0.0
description: Compare implementation changes on the current branch against design docs (spec.md, context.md). Surface discrepancies with solution options (pros/cons + recommended fix) and flag missing implementation details in docs. Resolve each issue interactively before advancing to the PR. Run as the last step of /build before opening a PR.
changelog:
  - "1.0.0 (2026-09-01): Added to the canonical skill set. Was already referenced by /build's description and by audit-design's Step 3 format; now has a matching file so both references resolve to something real."
---

You are reconciling the implementation on the current branch against its design documentation. Work through every discrepancy and gap before the PR is opened.

Subagent handoff rule: if you delegate any read or search work, pass only the files being analysed — not the full session transcript.

---

## Step 1 — Locate the design docs

Find the feature's design folder. Try in order:
1. Read context.md in the current working directory or `designs/<feature>/`
2. Check the Linear ticket (already pulled in this session) for the `designs/` path
3. If still not found, ask: "Where is the designs folder for this feature?"

Read `spec.md` and `context.md` in full. Note any other documents linked or referenced inside them (Drive docs, ADRs, etc.) — fetch those too.

---

## Step 2 — Get the implementation diff

Run:
```
git diff <feature-branch>..HEAD
```
Where `<feature-branch>` is the parent branch this implementation branch was cut from (recorded in step 2b of /build). If unknown, use `main`.

Also run:
```
git diff <feature-branch>..HEAD --name-only
```
to get the full file list, then read each changed file in full (not just the diff hunk) so you understand the complete shape of what was built.

---

## Step 3 — Identify discrepancies

Compare the implementation against spec.md and context.md. Flag every place where the code diverges from, contradicts, or goes beyond what the docs describe. Categories to check:

- **Behaviour**: does the code do what the acceptance criteria say? Any criteria silently dropped or changed?
- **Interfaces**: API shapes, function signatures, data schemas — do they match the spec?
- **Data flow**: pipelines, event sequences, error paths — do they match the sequence diagrams or descriptions?
- **Dependencies**: libraries, versions, services used — do they match context.md?
- **Scope**: anything built that the spec does not mention (may be intentional or accidental scope creep)

For each discrepancy found, record:
- **What**: one-sentence description of the divergence
- **Where in code**: file + line range
- **Where in docs**: spec.md section or context.md section that conflicts

---

## Step 4 — Surface discrepancies to the human

Present each discrepancy one at a time in this format:

---

**Discrepancy N of M — [short title]**

> [One-sentence description of the conflict]

**In code** (`file.py:12–34`): [what the code does]
**In docs** (`spec.md §X`): [what the doc says]

**Options:**

| | Option | Pros | Cons |
|---|---|---|---|
| A | Update docs to match code | Docs stay truthful; no code churn | May hide a spec violation; future devs see no intent |
| B | Revert/change code to match docs | Preserves original intent; keeps spec honest | Requires rework; may be the right call if spec was deliberate |
| C | *(custom — describe below)* | — | — |

**Recommended:** [A or B] — [one sentence rationale]

Which do you choose? (A / B / C — if C, describe the fix):

---

Wait for the human's response before moving to the next discrepancy. If they choose C, confirm the approach before applying. Apply the chosen fix (doc update or code change) immediately, then continue.

---

## Step 5 — Identify missing doc details

After resolving all discrepancies, scan for implementation detail that is present in the code but absent from the docs and would matter to a future maintainer or reviewer. Focus on:

- Non-obvious design choices made during implementation (e.g. why a particular algorithm, retry strategy, or error handling approach was chosen)
- Constraints discovered during implementation not captured in context.md (e.g. library limitation, performance boundary, auth edge case)
- Acceptance criteria that were refined or clarified during the build but the refinement is not written down
- New dependencies or version pins not reflected in context.md

For each gap, present it like this:

---

**Missing detail N of M — [short title]**

> [What is in the code that is not documented anywhere]

**Suggested doc addition** (`context.md §Constraints` or `spec.md §Acceptance Criteria`):
```
[Draft text to add]
```

Add this detail, skip it, or rewrite the draft? (Add / Skip / Rewrite):

---

Wait for the human's response. Apply additions immediately. If they skip, note it as explicitly deferred.

---

## Step 6 — Commit doc updates

If any spec.md or context.md changes were made, commit them to the current branch:
```
git add designs/<feature>/spec.md designs/<feature>/context.md
git commit -m "docs: reconcile spec and context with implementation"
```

---

## Step 7 — Report

Print a summary:

```
sync-docs complete
  Discrepancies resolved: N
  Doc gaps filled:        N
  Explicitly deferred:    N (list them)
  Docs committed:         yes / no
```

The branch is now ready for the PR.
