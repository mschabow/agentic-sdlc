# Rollout — Sharing This Workflow With the Team

The workflow is distributed two ways from one source: **this folder becomes a git repo** (the docs, the canonical skills, the evals), and **the skills ship as a Claude Code plugin** the team installs from that repo. The repo is the source of truth; the plugin is the delivery mechanism. This replaces the old `cp ~/.claude/commands/` propagation.

## One-time setup (owner)

The repo lives at `github.com/mschabow/agentic-sdlc` (public). It contains the plugin scaffold:

```
.claude-plugin/marketplace.json          ← makes this repo a plugin marketplace
plugin/sdlc-workflow/
  .claude-plugin/plugin.json             ← plugin manifest (name, version)
  commands/                              ← synced copy of .claude/commands/
scripts/sync-plugin.sh                   ← regenerates plugin/commands from canonical source
```

## Team install (each engineer, once)

In Claude Code:

```
/plugin marketplace add mschabow/agentic-sdlc
/plugin install sdlc-workflow@agentic-sdlc
```

That gives everyone `/spec-design`, `/spec`, `/grill-with-docs`, `/decompose`, `/build`, `/sync-docs`, `/verify-context`, `/distill-context`, `/setup-project`, `/audit-design`, plus the shared utility skills `/review-fix-loop`, `/worktree-hygiene`, `/env-handoff`, `/delegated-work-audit`, and `/linear-implementation-audit`, at a known version. No manual file copying.

## Updating skills

The propagation process in [skill-eval-framework.md](skill-eval-framework.md) still governs *what* may change (PR + eval result + review). Delivery changes:

1. Merge the skill PR (eval result recorded, reviewed).
2. Run `scripts/sync-plugin.sh`; bump the version in `plugin/sdlc-workflow/.claude-plugin/plugin.json` (semver, matching the skill change class).
3. Commit, push, and tag.
4. Post the one-line note in the team channel: skill, version, what changed.
5. Engineers pick up the update by running `/update-skills` (or `/plugin`; marketplaces refresh on update), instead of copying files. Restart Claude Code afterwards.

Version pinning per repo still works as before via `/setup-project` — a project-scoped copy in `.claude/commands/` takes precedence over the plugin. Document pins in AGENTS.md and unpin promptly.

## What the team reads

Point new team members at, in order:

1. [README.md](README.md) — the six-stage view; ten minutes.
2. [design-loop.md](design-loop.md) and [execution-loop.md](execution-loop.md) — the two loops they will actually run.
3. [review-policy.md](review-policy.md) — what review they owe and what they can skip.
4. Everything else as needed via the document map in the README.

## Rollout order

Adopt in this sequence — each step works without the ones after it:

| Step | What | Why first/later |
|---|---|---|
| 1 | Repo + plugin install; team runs the existing design/build loops | Zero behavior change, just distribution |
| 2 | Guardrail hooks ([hooks.md](hooks.md)) in one pilot repo | Cheap, immediate safety win; tune before spreading |
| 3 | Incident-to-eval rule ([maintain-loop.md](maintain-loop.md) §4) | One PR-template question; starts compounding immediately |
| 4 | The three starter metrics ([metrics.md](metrics.md)) | Needs a few weeks of data to be meaningful |
| 5 | Approval gates + autonomy tiers ([deploy.md](deploy.md)) | Needs hooks proven in step 2 |
| 6 | Autonomous maintain loop ([maintain-loop.md](maintain-loop.md) §1–3) | Biggest lift; depends on steps 2–5 being trusted |
