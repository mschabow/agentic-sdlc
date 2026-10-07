# Handoff: design and build in stages (skeleton, then prototype, then pilot)

**For:** whoever updates the `sdlc-workflow` skills in this repo.
**From:** Matt Schabowsky, with Claude, after building People Planning slice 1 in `cailum-blue/ludicrous-platform` (2026-10-05).
**Ask:** change `/spec-design` (and the steps and templates that feed it) so a feature is planned and built in three end-to-end stages, in this order: a **skeleton**, then a **prototype**, then a **pilot**, with tickets cut by **use case** at every stage. Today a spec is one flat list of criteria that `/decompose` slices into tickets, one capability at a time.

---

## 1. Why: what happened on People Planning slice 1

We ran the full workflow: `/spec-design` → `/decompose` → `/build`, with every ticket built, reviewed and merged by agents. By the usual measures it went well:

- 15 user stories, 86 acceptance criteria and 124 spec tests, split into 21 build tickets (CB-52 to CB-72).
- 1,282 tests passing, every PR code-reviewed and triaged, CI green.
- Every business rule was in place: approval routing, clean evaluation, close/lock/backstop, corrections, audit, Slack flows and Linear drafts.

When we asked "is it useful yet? can we demo it?", the answer was **no**:

| Gap | Why the process didn't catch it |
|---|---|
| The web app has **one screen** (timesheet entry). Approvals, leave, Head of Ops admin, corrections and export are API-only. | The spec listed rules and APIs, but never asked "where does each actor do each thing?" Only one criterion (US6.10) mentioned a screen. |
| Slack messages have "Edit in app" / "Review in app" buttons that open screens which don't exist. | Nothing checked that every link and handoff between surfaces lands somewhere real. |
| You can't sign in locally in a browser: the SPA never sends the dev identity header. | No criterion required the app to run end to end for a human. Tests call the API directly. |
| No seed or demo data. A fresh database is empty. | "Demoable" was not a deliverable. |
| Nothing is deployed. Infra prerequisites and the sign-off review came at the very end. | Deployment was a "pre-deploy gate" at the end, not the first thing proven. |

The root cause is that **we built depth-first, one capability at a time.** Each ticket finished one capability completely (all its rules, edge cases and tests) before the whole thing worked from one end to the other. Users can't see or react to anything until all the work is done. By then, feedback is expensive, because every rule has already been built around assumptions nobody tried in practice. We also discovered a design gap (missing screens) only after paying for full rigor everywhere else.

## 2. The concept: three stages, each cut by use case

Each stage is a complete, end-to-end slice across **every** layer and surface: UI, API, data, jobs and integrations. Each one gets deeper than the last. You don't go deeper until the stage before it works end to end and has been reviewed.

- **Skeleton:** proves the architecture holds and that we can ship it. It should try to deliver a first sliver of business value too, but coverage of the architecture comes first.
- **Prototype:** has enough features to start delivering **core business value**.
- **Pilot:** all features are in place, and the feature is in acceptance testing and refinement with real users.

### 2.1 Vocabulary: use case and journey

- A **use case** is one actor reaching one goal, across every surface that goal touches (for example, "approver rejects a week with a note"). It has a **main path** and **extensions** (alternate and failure paths). Use cases are the unit that tickets are cut by, at every stage.
- A **journey** is an ordered chain of use cases for one actor (for example, "Engineer's week" = record week, then submit week, then correct a locked week). Journeys group use cases: they become the Linear parent issue and the source of the demo script. Tickets are never cut by journey.
- **User stories** still hold the acceptance criteria. Each story belongs to one use case. Each criterion is tagged with its use case, its path and its stage, for example `UC5 · main · [P]`. Skeleton and infra criteria may use `none` for the use case.
- Each criterion has **exactly one owning use case**. Other use cases may depend on it but don't list it. This keeps the "every criterion in exactly one ticket" rule in `/decompose` intact.
- A use case is marked **core** when the feature delivers no business value without it. The core set is agreed in the stage plan.

### 2.2 The three stages

| | **Skeleton** | **Prototype** | **Pilot** |
|---|---|---|---|
| **Purpose** | Prove the architecture holds and that we can ship it; where possible, deliver a first sliver of business value | Start delivering core business value | All features in place; acceptance testing and refinement |
| **Cut by** | One foundation ticket, then thin use-case slices chosen to cover the architecture | Core use cases built for real; every other use case reachable | Remaining use cases, all extensions, cross-cutting concerns; then refinement from acceptance findings |
| **Depth** | The first step or two of each chosen use case. No business rules. Real auth, roles, schema, integrations and deploy, no shortcuts. | **Core** use cases: main path with real rules and the real integrations they need. **Other** use cases: a clickable main path with rules stubbed behind the real interfaces and integrations faked. | Full rules, every extension and edge case, security, audit, retention, all real integrations |
| **Data** | One hard-coded record | A seeded, realistic demo data set and a local user switcher; real data for core use cases where needed | Real users (a small pilot group) and real data |
| **Tests** | One smoke test per slice; deploy succeeds | Journey tests (for example Playwright) for every journey; rule tests for core use cases | The full spec test list: rules, permission matrix, failure modes; acceptance test results |
| **Exit gate** | Deployed and reachable behind real auth; CI/CD works; every row of the skeleton coverage matrix is ticked | Core use cases demonstrably deliver value (walk the demo script with the people who will use it); every other use case is reachable; feedback recorded and the spec updated | **Feature-complete gate** + sign-off review (security, data, ops), then acceptance testing with a pilot group for N weeks, refinement, then the GA decision |
| **Typical share of effort** | ~10% | ~30% | ~60% |

How the stages work together:

- **Code is kept and deepened, never thrown away.** The prototype is the same codebase as the skeleton, just deeper. The pilot deepens the prototype. Non-core use cases in the prototype stub rules behind the real interfaces (for example `clean_now()` always returns true, or approval goes to a fixed approver), so the pilot replaces the stubs rather than the structure.
- **Plan in rolling waves.** Design all three stages at the level of goal, scope and exit gate. Decompose only the **next** stage into tickets. The prototype review will change the pilot, so tickets written early for the pilot are wasted work.
- **Pull the hard, irreversible decisions forward.** Auth, data ownership, schemas and roles, and the deploy target belong in the skeleton, because they are the costly ones to change late. ADRs still come out of `/grill-with-docs` as they do today.
- **The demo kit is part of the prototype's definition of done:**
  - seed data
  - a local user/role switcher
  - fakes for external systems, with a viewer (for example, a fake Slack inbox)
  - a single `make demo` command

### 2.3 Skeleton: foundation plus thin use-case slices

The skeleton is not cut by layer. A layer ticket ("data and roles") can't be shown to anyone and hides integration risk until the end. Instead:

1. **One foundation ticket first.** It owns every shared file: the app shell with an empty nav and router, auth and identity (including the dev identity header), the schema, roles and migration framework, an API router, the job runner, integration client stubs, CI and the deploy pipeline. It ends with one "hello" path deployed. It can be `human-required` where cloud or IAP setup needs a person. Without it, every slice edits the same files, and `/build` puts them in separate waves.
2. **Then thin use-case slices, in parallel.** Each slice is the first step or two of one use case's main path, end to end. Each slice adds only new files (its own migration, route module, screen, handler). It registers itself in nav, router or job wiring through a registry pattern. A slice that needs to change a shared file gets that change moved into the foundation ticket.
3. **Choose slices for coverage first, then for value.** List what the skeleton must prove: every surface, layer, integration, job, auth path, handoff between surfaces and the deploy target. Pick the **fewest** use cases whose thin slices together cover every item, preferring slices that touch the costly decisions (schema, roles, identity). Where several slices would cover the same rows, prefer the one a real user would find useful (for example "see my assignments for this week" over a hello page), and prefer core use cases. The skeleton should try to deliver a first sliver of business value, but coverage is the requirement and value is not a gate. Each slice ticket names the architectural risk it retires and, where it has one, the value it delivers. Usually 3 to 5 slices.
4. **Skeleton coverage matrix.** Rows are the items to prove; columns are the slices. Every row needs at least one tick. A row with no tick fails the stage plan.
5. **Depth cap and real seams.** One step per surface, one hard-coded record, no business rules, no branches, no extensions. Each slice uses the real auth, roles, schema and deploy path, even if trivially. Anything beyond a "hello" path is tagged `[P]`.
6. **Criteria ownership.** Skeleton criteria cover only reachability and wiring ("the screen loads the record over the authenticated API"). The workflow behaviour of the same use case belongs to the prototype. No criterion is tagged in two stages.

### 2.4 Prototype: core value, everything reachable

- **Core use cases** are built for real on their main path: real rules, real integrations they need, rule tests. This is where the feature starts to deliver value.
- **Every other use case** gets a clickable main path with rules stubbed and integrations faked. This keeps the slice-1 lesson: a missing screen or a Slack button that leads nowhere shows up here, even outside the core.
- Per journey: a **spine** ticket first (shared routes, screens, endpoints and schema the use cases extend), then one ticket per use case, then a **journey-test** ticket last (the end-to-end test and a check that every handoff lands on a real screen).

### 2.5 Pilot: build-out, then acceptance testing and refinement

The pilot has two phases with a gate between them:

1. **Build-out to feature complete.** Remaining use cases' real rules, every extension (one ticket per use case covering its extensions, split only if it fails the size check), and cross-cutting concerns as their own tickets (audit, permission matrix, retention, real integrations). Journey tests are re-run, not rewritten.
2. **Feature-complete gate and sign-off review** (security, data, ops). Real users and real data only after this.
3. **Acceptance testing and refinement.** A pilot group uses it for real for N weeks. Findings become refinement tickets, decomposed as they arrive, tagged `[PL]`. Then the GA decision.

### Slice 1, retold in stages (worked example)

Use cases (sketch): **Engineer** UC1 Record my week, UC2 Submit week, UC3 Request leave, UC4 Correct a locked week. **Approver** UC5 Review timesheets, UC6 Approve leave. **Head of Ops** UC7 Manage people, UC8 Manage engagements and assignments, UC9 Assign roles, UC10 Export period. **System** UC11 Close/lock/backstop, UC12 Daily check-in. Core (to confirm): UC1, UC2, UC5, UC10.

- **Skeleton:** the foundation ticket (Cloud Run behind IAP, sign-in that creates a pending person, the `people_planning` schema and roles, CI and deploy), then four slices:

  | Slice | What it proves |
  |---|---|
  | UC1 "See my week" | Web app, IAP sign-in, schema, Cloud Run deploy |
  | UC12 daily check-in | A job sends a Slack DM whose link opens UC1's screen: a handoff works |
  | UC8 Head of Ops sees one Linear issue | The Linear read and a role-gated screen |
  | UC5 approver's one-item digest opens the queue | A second actor and routing by role |

  Gate: a teammate opens the deployed URL and sees their own week; every coverage row is ticked. Value sliver: UC1 already shows engineers what they're assigned to this week, and UC12's DM reminds them to log time, which is useful before any timesheet rules exist.
- **Prototype:**
  - Core, built for real: timesheet entry and submit (UC1, UC2), the approvals queue and Slack digest with real approval routing (UC5), export (UC10).
  - Reachable, stubbed: leave request and approval, Head of Ops admin (people, engagements, assignments, roles), corrections, daily check-in.
  - The demo kit: seeded crew, user switcher, fake Slack inbox, `make demo`.

  Gate: walk the demo script with an LAA, two engineers and Head of Ops; one real week is recorded, approved and exported. Expected outcome: "approvals in Slack only" turns out not to be enough, and the missing screens show up **here**, not after 1,282 tests.
- **Pilot:**
  - Build-out: clean evaluation; close/lock/backstop and corrections; leave rules; append-only audit, the grants matrix and permission-matrix tests; Linear signals, escalation and offboarding; retention; pre-deploy gates (timezones, Slack scopes).
  - Feature-complete gate and the sign-off review.
  - Acceptance: one engagement's team uses it for four weeks; findings become refinement tickets; then the GA decision.

## 3. What to change in the skills

All paths are relative to this repo. `.claude/commands/` is the canonical source, and `plugin/sdlc-workflow/commands/` is currently a byte-identical copy. Update both, or make one generated from the other. Bump each skill's `version` and `changelog` in its front matter, and run the eval gate in [skill-eval-framework.md](../skill-eval-framework.md).

### 3.1 `/spec` (`.claude/commands/spec.md`)

- Derive user stories from use case paths instead of "split by capability". Each story names its use case and path (`Use case: UC5 / main`).

### 3.2 `/spec-design` (`.claude/commands/spec-design.md`)

1. **Step 0, lightweight path check: no change.** A lightweight change, or one that extends a feature already in pilot, skips staging. Add one line: "If this design adds to an existing feature that is already at pilot or GA, stages are optional. Ask the human."
2. **New step 3.5, use cases and the surface map** (right after `/spec`, before context pass 1).
   - List the use cases: ID, primary actor, goal, trigger, surfaces, main path steps, extensions.
   - Build an **actor × use case × surface** matrix, with a column for each handoff and the use case it lands in.
   - Define each journey as a chain of use cases.
   - Flag: any use case that has no surface; any handoff that points at nothing or at a use case with no prototype slice; any actor who can't complete their job without curl.
   - Resolve each flag in `/grill-with-docs`. The use cases and the matrix go into spec.md.
3. **New step 5.3, the stage plan** (after `/grill-with-docs`, before the draft test list).
   - Mark the **core** use cases.
   - Tag every acceptance criterion with use case, path and stage: `[S]` skeleton, `[P]` prototype or `[PL]` pilot.
   - Choose the skeleton slices and fill in the skeleton coverage matrix.
   - Write each stage's goal, scope, exit gate and (for the prototype) the demo script outline, built from the journeys.
   - Rules for the agent:
     - The skeleton is the foundation plus the fewest thin slices whose coverage matrix ticks every row, including the deploy. Among slices with equal coverage, prefer core use cases and slices with some real user value.
     - The prototype builds every core use case's main path for real, and gives every other use case a reachable main path.
     - A pilot criterion can't be the only thing that makes a use case's main path reachable. If it is, move the reachability part to the prototype.
     - Use the effort split (~10/30/60%) as a sanity check, not a rule.
   - Present the plan to the human and revise it until approved.
4. **Step 5.5, draft test list:** group the list by stage. Skeleton tests are smoke tests, prototype tests are journey tests plus rule tests for core use cases, and pilot tests are the remaining rule tests. Only the **next** stage's tests are the frozen baseline for `/build`. Later stages stay drafts until their stage starts.
5. **Step 6, spec.md:** add the new sections described in 3.4.
6. **Step 8, commit or PR:** the approval covers the whole stage plan. Tell the human that the next step is `/decompose` **for the skeleton stage only**.
7. **New closing step, between stages:** document a short **stage review** loop to run after each stage's build:
   1. Run the exit gate (coverage check for the skeleton; the demo for the prototype; feature-complete and sign-off, then acceptance, for the pilot).
   2. Record what was learned in the spec's deviation log, and update later stages' criteria.
   3. Re-run `/grill-with-docs` on anything that changed.
   4. Then `/decompose` the next stage (or the next pilot phase).

   This can be a new `--next-stage` mode of `/spec-design`, or its own small skill (`/stage-review`). The second option is probably cleaner.

### 3.3 `/decompose` (`.claude/commands/decompose.md`)

- Add an input: **which stage** to decompose (and for the pilot, which phase: build-out or refinement). The default is the earliest stage that isn't done yet. Only criteria tagged with that stage get covered, and the rule "every criterion is in exactly one ticket" applies **within** the stage. One use case appearing in tickets of two stages is not duplication, because the criteria differ.
- **Skeleton:** one foundation ticket, then one ticket per thin use-case slice, all blocked by the foundation ticket. Slices must not edit files the foundation created, except to register themselves. Refuse to finish if any coverage row has no tick.
- **Prototype and pilot: cut by use case.** One actor reaching one goal, across every surface that goal touches. Never split a use case into a UI ticket and an API ticket.
  - Group use cases under a **journey parent issue**.
  - Each journey gets a **spine** ticket first and a **journey-test** ticket last (blocked by all the journey's use-case tickets).
  - If two use-case tickets would edit the same existing file, merge them or move the shared part into the spine.
  - **Size check:** about one screen state and one or two endpoints per ticket. If a ticket's tests can't be derived from its own criteria, split or merge it.
  - **Pilot build-out:** one ticket per use case covering its extensions, split only if it fails the size check. Cross-cutting concerns (audit, permission matrix, retention) are their own tickets, cut by concern and tagged with the use cases they touch.
  - **Pilot refinement:** tickets come from acceptance findings and are decomposed as they arrive.
- Every stage ends with a `human-required` **stage review** ticket that holds the exit gate. The pilot also has a `human-required` **feature-complete** ticket between build-out and acceptance. The next stage's (or phase's) tickets are blocked by it.
- Each stage's tickets go in a Linear **milestone** (`<feature> — Skeleton | Prototype | Pilot`).
- The prototype stage always includes a **demo kit** ticket (seed, user switcher, fakes with viewers, `make demo`), scheduled early because it unblocks the journey tests. On slice 1 this ended up as CB-82, built after the fact.

### 3.4 Templates and docs

- [spec-template.md](../spec-template.md): add these sections:
  - **Use cases**: ID, primary actor, goal, trigger, surfaces, main path, extensions (each with a stage), core yes/no.
  - **Surfaces and journeys**: the actor × use case × surface matrix with handoff targets, and each journey as a chain of use cases.
  - **Stages**: a table with each stage's goal, scope, exit gate and demo script, plus the skeleton coverage matrix.
  - Use case, path and stage tags on every acceptance criterion and test row.

  Change the Status values to `Draft | In review | Approved | Skeleton | Prototype | Pilot | GA | Updated post-build`.
- [ticket-template.md](../ticket-template.md): add `Stage:`, `Journey:` and `Use case:` fields. Note that use-case tickets cut across layers.
- [design-loop.md](../design-loop.md):
  - Update the sequence diagram to include the use cases, surface map and stage plan steps.
  - Add the stage review loop after `/decompose` → `/build`, and the pilot's feature-complete gate.
  - Add the invariant: *no stage's tickets are created until the previous stage's exit gate is recorded.*
- [execution-loop.md](../execution-loop.md): one integration branch per stage (e.g. `<feature>/skeleton`). The stage merges to `main` when its exit gate passes, so `main` gets the skeleton and the prototype early instead of one giant merge at the end.
- [README.md](../README.md) and [lightweight-design.md](../lightweight-design.md): one paragraph each pointing at the stages.

### 3.5 Evals

Add eval cases to the skill eval suite:

1. **Surface gap:** a spec where approvals happen in Slack but a button links to an app screen. Expected: the surface map flags the missing screen.
2. **Skeleton coverage:** a staged plan whose skeleton coverage matrix has an unticked row (for example, deploy). Expected: rejected.
3. **Decompose scope:** `/decompose` given a staged spec. Expected: tickets only for the current stage, cut by use case, grouped under journey parents with a spine and a journey-test ticket, ending in a stage-review ticket.
4. **Shared file:** a staged spec with two use cases on one screen. Expected: a spine ticket or a single merged ticket, not two tickets editing the same file.
5. **Core vs reachable:** a prototype plan that stubs a core use case's rules. Expected: flagged.
6. **Lightweight passthrough:** a lightweight change. Expected: no staging questions.

## 4. Open questions for the skill owner

1. **Names.** "Skeleton / prototype / pilot" is the user's language. "Walking skeleton" is the common industry term. Keep the user's words in the skills and mention the industry term once.
2. **How many stages.** Should small features merge skeleton and prototype into one stage? Suggestion: allow it when the feature adds no new surface or service.
3. **Who approves exit gates.** Suggestion: the skeleton is approved by the tech lead; the prototype by the product owner plus representative users; the pilot's feature-complete gate by the lead sign-off review (security, data, ops); GA by the product owner after acceptance.
4. **Who decides "core".** Suggestion: the product owner, during the stage plan in `/spec-design`.
5. **Applying this to an existing feature.** People Planning slice 1 is already at "pilot depth, prototype breadth". Do we backfill a prototype stage, i.e. the missing screens, before its pilot? Suggestion: yes. Record it as a spec amendment through the stage review flow.

## 5. Definition of done for this handoff

- `/spec`, `/spec-design`, `/decompose`, the spec and ticket templates and `design-loop.md` updated as described above, with versions bumped and changelogs written.
- A stage-review skill or mode exists.
- The eval cases in 3.5 pass.
- The plugin copy is in sync with `.claude/commands/`, and `/update-skills` has been run on one machine to confirm the new versions load.
