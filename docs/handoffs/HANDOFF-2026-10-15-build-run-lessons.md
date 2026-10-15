# HANDOFF — 2026-10-15: encode lessons from a long /build run in /build and /decompose

**Status:** Not started. Lessons collected and agreed on 2026-10-15; no skill file has been edited yet.
**Pick up in:** a new Claude Code session in this repo (`mschabow/agentic-sdlc`). The work is editing skill markdown; no special environment needed.
**Branch:** `skills/build-run-lessons` (worktree `.claude/worktrees/build-run-lessons` of the clone at `/Users/schabowsky/agentic-sdlc`), branched from `origin/main` at `4fac9ee`. This doc is its only commit.
**Blocks / blocked by:** none. No ticket exists for this work.

## Goal

`/build` and `/decompose` (in `plugin/sdlc-workflow/commands/`) carry the eight lessons below, so the next multi-wave build run does not repeat the stops and slowdowns of the first one. Finished = one PR to `main` in this repo, each lesson mapped to a concrete edit, merged by Matt, then `/update-skills` run on his machine.

## Where the lessons come from

The People Planning slice 2 wave B build (repo `cailum-blue/ludicrous-platform`, design ticket CB-215, tickets CB-218 to CB-228) ran `/build` as a Workflow script: Sonnet build agents in per-ticket worktrees, Opus review agents, a collector branch `feat/CB-215-wave-b` that PRs into the integration branch `slice2-wave-a`, six dependency waves, and the full test suite on the collector after each wave. Over two days it stopped four times and ran far slower than planned. Evidence is in that repo: PRs #95–#101 and the CB-215 spec's deviation log (`designs/people-planning-slice2-wave-b/spec.md`, branch `feat/CB-215-wave-b`).

## Current state

- `plugin/sdlc-workflow/commands/build.md` (207 lines). Sections: Defaults, Ticket tracker, 1 Pull the tickets, 2 Plan the waves, 3 Collector branch and worktree, 4 Read AGENTS.md, 5 /verify-context, 6 Pass 1 and /distill-context, 7 Build each wave, 8 Review, sync docs, open the PR, 9 Merge into the collector, 10 Collector PR to main, 11 Final report.
- `plugin/sdlc-workflow/commands/decompose.md` (77 lines).
- `plugin/sdlc-workflow/commands/review-fix-loop.md` (83 lines), used by `/build` step 8.
- Repo-level references `/build` leans on: `execution-loop.md`, `review-policy.md`, `ticket-template.md`, `workflows/`.
- Nothing has been changed yet.

## Decisions (agreed)

Matt agreed that the skills should change (2026-10-15, "do we need to update our sdlc skill as well?" → yes, with a separate session). The eight lessons, each with what happened:

1. **Test cost.** Before planning waves, find out what PR CI actually runs compared with the repo's full suite. A build subagent runs the full suite once only when CI does not cover the ticket's tests. Fix rounds run fast checks only. The collector's full suite after each wave is the gate. Agents waiting on a long test log check it every ~2 minutes.
   *Happened:* every build and every fix round ran the 25–50 minute full suite, serially per ticket, and agents polled the log about every 10 minutes. Parallel stacks on one laptop pushed a 25-minute suite to 43–51 minutes. The repo's PR CI (`make test-integration`) did not run the app's 3,394 API tests, which only the full suite covers; the skill never asked.
2. **CI must cover the collector.** Before the first PR, check that CI triggers on the collector's branch pattern (for example `feat/*`). If not, propose adding it as the collector's first commit.
   *Happened:* CI ran only for `main` and `slice*`; the first two PRs into the collector had no checks at all.
3. **Baseline before wave 1.** Run the full suite once on the collector base before building anything, and fix pre-existing failures first.
   *Happened:* two date-dependent tests on the base branch (a hard-coded "Tue, Oct 13" hint; leave dates of Oct 12–14) broke on the run date and each stopped the run mid-flight.
4. **Integration-branch base.** Let the collector start from, and PR into, an integration branch instead of always the default branch. Let the design live on a committed design branch rather than only a merged design PR.
   *Happened:* the app's code exists only on `slice2-wave-a`, and the design was committed without a PR; both had to be overridden by hand.
5. **human-required tickets.** Offer three choices instead of always dropping them: drop (current behaviour), build with agents and hold the merge for sign-off, or build and merge with the requester's approval.
   *Happened:* the three foundation tickets were human-required and every other ticket depended on them, so the default would have built nothing. Matt chose "build and merge".
6. **Escalations vs notes.** The PR / `/sync-docs` step stops the run only for a discrepancy with acceptance criteria, interfaces or data flow that the spec's deviation log does not already record. Pre-existing failures, environment issues and documented interpretation choices go in the PR body.
   *Happened:* CB-218's PR agent escalated a pre-existing frontend test failure, which stopped the whole run.
7. **Workflow mode.** Document running `/build` as a Workflow script: fixes go to a fresh agent in the same worktree (workflow agents cannot be messaged); merges wait for PR CI; a ticket can resume from its review stage without rebuilding (for example a `built` flag in the args); a stop for a decision ends the run before the next wave, and the restart skips finished work. Include a reference outline of the script.
8. **/decompose screens check.** Check that every item in the spec's Screens or Surfaces table is covered by an acceptance criterion, and flag screens with none.
   *Happened:* the deal form, the win review dialog and the grid view toggle had no criteria, so their UI tickets could not be verified until three criteria were added during `/decompose`.

Open: whether lesson 1's "full suite once per ticket" should become "never per ticket" when a repo's CI covers the API tests. Decide while editing, from what the skill can detect.

## Verified

- The skill sources are in this repo: `plugin/sdlc-workflow/commands/build.md`, `decompose.md`, `review-fix-loop.md` (read 2026-10-15 at `4fac9ee`).
- The lessons' "what happened" facts were checked against ludicrous-platform: CI triggers in `.github/workflows/people-planning.yml`, the `test-integration` target in its `Makefile`, the failing tests and their fixes (PRs #97, #99, #98, #100), and the CB-220 review finding (PR #101).

## Not verified

- No edits made, so nothing to test. Skill changes are checked by reading them and, if this repo has a skill eval harness (`skill-eval-framework.md`, `ci/`), by running it.

## Next steps

1. `cd /Users/schabowsky/agentic-sdlc/.claude/worktrees/build-run-lessons && git fetch origin && git status`. Confirm the branch is `skills/build-run-lessons` and rebase on `origin/main` if it moved.
2. Read `plugin/sdlc-workflow/commands/build.md`, `decompose.md`, `review-fix-loop.md`, `execution-loop.md` and `review-policy.md` in full.
3. Edit `build.md` for lessons 1–7: Defaults (test cost, polling), step 1 (human-required choices), step 2 (CI coverage check, baseline suite), step 3 (integration-branch base and design branch), step 7 (fast checks in fix rounds), step 8 (escalations vs notes), and a new "Running as a Workflow" section for lesson 7. Keep edits to the sentences that change; match the file's voice.
4. Edit `decompose.md` for lesson 8.
5. Check `README.md`, `execution-loop.md` and `workflows/` for statements the edits contradict, and update them.
6. Run the repo's checks if any exist (look in `ci/` and `scripts/`).
7. Commit, push, and open a PR to `main` titled "[skills] /build and /decompose: lessons from a six-wave build run". The body lists the eight lessons, each with the file and section changed. Do not merge it.
8. After Matt merges: run `/update-skills` so the installed plugin picks the change up. On 2026-10-14 the skill list also showed unscoped `build` and `decompose` entries besides `sdlc-workflow:*`; `/update-skills` reports stale duplicates like these.

## Risks and gotchas

- **Do not edit the marketplace clone** at `~/.claude/plugins/marketplaces/agentic-sdlc`. `/update-skills` pulls there; edits would be overwritten or block the pull. Work only in `/Users/schabowsky/agentic-sdlc` and its worktrees.
- **GitHub account:** this repo is under the personal account `mschabow`, not `cailum-blue`. If `gh` acts as the work account, prefix commands with `GH_TOKEN=$(gh auth token --user mschabow)`. Never run `gh auth switch`.
- `.claude/worktrees/` is not in this repo's `.gitignore`, so `git status` in the main clone shows `.claude/` as untracked. Ignore it, or add the line in this PR.
- The ludicrous-platform build run that produced these lessons may still be running when you start. Its state does not affect this work.
- Keep client names and personal data out of the skill text; describe the lessons generically ("an integration branch", "date-dependent tests").

## Where things are

- Skills: `plugin/sdlc-workflow/commands/build.md`, `decompose.md`, `review-fix-loop.md`, `env-handoff.md`, `update-skills.md`.
- Process docs: `execution-loop.md`, `review-policy.md`, `design-loop.md`, `ticket-template.md`, `workflows/`.
- Evidence (in `cailum-blue/ludicrous-platform`): PRs #95, #96 (wave 1 stop), #97, #99 (date-test fixes on `slice2-wave-a`), #98 (collector CI trigger), #100, #101 (CB-220 and the US26.5 allowlist), branch `feat/CB-215-wave-b`, `designs/people-planning-slice2-wave-b/spec.md` deviation log.
