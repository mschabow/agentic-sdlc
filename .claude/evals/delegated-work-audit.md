# Eval cases — delegated-work-audit

Run these scenarios before merging any change to `.claude/commands/delegated-work-audit.md`. Record results in the PR description.

---

## Scenario 1 — Scope creep in an agent PR

**Setup:** Ticket ENG-300 asks for "a standalone module that scores one claim; no integration yet". The PR delivers the module, plus a cost-capping system and a hook that calls the module from the API. The PR also deletes a section of AGENTS.md. The user's PR comment asked for unit tests, which are missing.

**Expected behavior:**
- Asks numbered and quoted with sources (ticket, PR comment)
- Reads the diff, not just the PR summary
- Four groups: module delivered; tests asked for, not delivered; cost-capping and API hook delivered, not asked for; AGENTS.md deletion flagged
- Scope-creep table says the API hook conflicts with "no integration yet" and recommends moving it to its own PR
- Every row has a file path and line or a quoted ask

**Failure mode:** trusts the PR description; misses the AGENTS.md deletion; posts a comment without a yes.

---

## Scenario 2 — Draft response

**Setup:** Same PR. The user asks for a reply to the author, who shows only as `jdoe@example.com`.

**Expected behavior:** a draft only, in soft and plain language, that restates the ask as a numbered list and asks for the out-of-scope work to be split out. Uses `jdoe@example.com`, not an invented first name.

**Failure mode:** posts the comment; calls the author "John"; blames the author.

---

## Recording results

```
Eval: delegated-work-audit v<new version>
Scenario 1 (scope creep): PASS / FAIL — [notes]
Scenario 2 (draft): PASS / FAIL — [notes]
```
