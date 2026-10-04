---
name: update-skills
version: 1.0.0
description: Bring this machine's installed skills up to date after a skill change merges. Refreshes the plugin marketplaces, updates installed plugins to their latest versions, verifies what is now installed, and finds stale duplicate copies of plugin skills (loose files in ~/.claude, claude.ai-synced skills, repo-pinned copies) that can shadow the current version. Run after any skill PR merges, or when a slash command seems to run old instructions.
changelog:
  - "1.0.0 (2026-10-03): Initial version."
---

You are updating the skills installed on this machine and removing stale copies that could shadow them. Follow these steps in order. Ask before you move or delete anything.

Argument: an optional `plugin@marketplace` to update only that plugin. With no argument, update every installed plugin.

## 1 — Inventory what's installed

Read `~/.claude/plugins/installed_plugins.json` and `~/.claude/plugins/known_marketplaces.json`. For each installed plugin, note its version, `gitCommitSha`, `installPath`, and its marketplace's `installLocation`.

Report this as a table: plugin, installed version, installed commit.

## 2 — Check each marketplace before updating

For each marketplace that is a git checkout (`installLocation` contains `.git`):
- Run `git -C <installLocation> fetch origin` and `git -C <installLocation> status -sb`.
- If the checkout has uncommitted changes or is not on the default branch, stop and tell the human. The update pulls into this directory and would conflict with their work. Recommend developing in a separate clone.
- Note how many commits it is behind `origin/<default-branch>`.

For marketplaces this repo owns (the plugin source is `.claude/commands/`), compare `plugin/<plugin>/.claude-plugin/plugin.json` on `origin/<default-branch>` against the installed version. If commands changed since the installed commit but the version did not change, warn the human: `claude plugin update` will not pick up the change until the version is bumped. The fix is a PR that runs `scripts/sync-plugin.sh` and bumps the version — never push it to the default branch directly.

## 3 — Update

For each marketplace in scope, run:

```bash
claude plugin marketplace update <marketplace>
```

Then for each plugin in scope, run:

```bash
claude plugin update <plugin>@<marketplace>
```

Re-read `installed_plugins.json` and report a before/after table: plugin, old version, new version, new commit. Spot-check one changed command in the new `installPath` to confirm the new content is present.

## 4 — Find stale duplicates

Build the list of command and skill names the installed plugins provide (the `.md` files in each `installPath/commands/` and the folders in `installPath/skills/`). Then look for other copies of those names:

- **Loose user copies:** `~/.claude/commands/*.md`, flat `~/.claude/skills/*.md`, and `~/.claude/skills/<name>/SKILL.md`. These load in every project and can shadow the plugin version.
- **claude.ai-synced skills:** `~/.claude/skills/synced/*/<name>/` and `~/.claude/plugins/synced/`. These come from skills uploaded in claude.ai settings. Note how many synced folders exist — more than one usually means more than one account or org.
- **Repo copies:** `.claude/commands/` and `.claude/skills/` in the current working directory, if it is a git repo. A repo bootstrapped by `/setup-project` may pin a skill version on purpose.
- **Retired names:** copies of skills the plugin has renamed or removed (check the plugin's changelogs, e.g. `design` → `spec-design`, `grill-me` → `grill-with-docs`).

For each copy, compare it with the installed plugin version and classify it as **identical**, **different**, or **retired name**. Report a table: location, name, status, recommended action.

## 5 — Clean up, with approval

Ask the human which copies to clean up. Then:

- **Loose user copies:** move them to `~/.claude/backup-stale-skills-<YYYY-MM-DD>/` rather than deleting them. Keep the `commands/` and `skills/` structure inside the backup folder.
- **claude.ai-synced skills:** do not delete these locally — they re-sync. Tell the human to remove or update them in claude.ai settings for each account, and list the exact skill names. Mention they only need to keep them if they use the skills in the claude.ai web app or Cowork, where plugins don't load.
- **Repo copies:** do not change them here. If a repo copy is different and not deliberately pinned, suggest a PR in that repo to remove it or update it.

## 6 — Finish

Tell the human:
- What was updated (versions) and what was moved (backup path).
- Anything left for them to do (claude.ai settings, version-bump PR, repo cleanup).
- Restart Claude Code, or start a new session — open sessions keep the old skills.
