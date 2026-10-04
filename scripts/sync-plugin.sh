#!/usr/bin/env bash
# Sync canonical skills from .claude/commands/ into the distributable plugin.
# Run after any skill change merges, then bump plugin/sdlc-workflow/.claude-plugin/plugin.json
# version to match the highest-impact skill change (see skill-eval-framework.md).
set -euo pipefail
cd "$(dirname "$0")/.."
rsync -a --delete .claude/commands/ plugin/sdlc-workflow/commands/
echo "Synced $(ls plugin/sdlc-workflow/commands | wc -l | tr -d ' ') command files into plugin/sdlc-workflow/commands/"
echo "Remember: bump the version in plugin/sdlc-workflow/.claude-plugin/plugin.json before tagging."
