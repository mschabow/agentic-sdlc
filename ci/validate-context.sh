#!/usr/bin/env bash
# validate-context.sh — CI check for context.md schema compliance
#
# Usage: ci/validate-context.sh <path-to-context.md>
# Exit 0 = pass, exit 1 = fail (with error details printed to stdout)
#
# Checks:
#   1. File exists and is not empty
#   2. Line count <= 300
#   3. All four required section headings present
#   4. No Slack references (slack.com or slack:// URLs)
#
# Run locally before pushing:
#   ci/validate-context.sh designs/<feature>/context.md

set -euo pipefail

FILE="${1:-}"
ERRORS=()
PASS=true

# ── helpers ──────────────────────────────────────────────────────────────────

fail() {
  ERRORS+=("$1")
  PASS=false
}

# ── 0. argument check ─────────────────────────────────────────────────────────

if [[ -z "$FILE" ]]; then
  echo "Usage: ci/validate-context.sh <path-to-context.md>"
  exit 1
fi

# ── 1. exists and non-empty ───────────────────────────────────────────────────

if [[ ! -f "$FILE" ]]; then
  echo "FAIL: file not found: $FILE"
  exit 1
fi

if [[ ! -s "$FILE" ]]; then
  echo "FAIL: file is empty: $FILE"
  exit 1
fi

# ── 2. line count ─────────────────────────────────────────────────────────────

LINE_COUNT=$(wc -l < "$FILE")
MAX_LINES=300

if (( LINE_COUNT > MAX_LINES )); then
  fail "Line count $LINE_COUNT exceeds maximum of $MAX_LINES. Reduce scope or split the ticket."
fi

# ── 3. required section headings ─────────────────────────────────────────────

REQUIRED_SECTIONS=(
  "## Key decisions"
  "## Constraints"
  "## Relevant code"
  "## External references"
)

for SECTION in "${REQUIRED_SECTIONS[@]}"; do
  if ! grep -qF "$SECTION" "$FILE"; then
    fail "Missing required section: '$SECTION'"
  fi
done

# ── 4. no Slack references ────────────────────────────────────────────────────

if grep -qiE "(slack\.com|slack://|https://[a-z-]+\.slack\.com)" "$FILE"; then
  SLACK_LINES=$(grep -niE "(slack\.com|slack://|https://[a-z-]+\.slack\.com)" "$FILE" | head -5)
  fail "Slack references found (not a permitted source). Capture content in Drive or Linear first.
  Lines:
$(echo "$SLACK_LINES" | sed 's/^/    /')"
fi

# ── result ────────────────────────────────────────────────────────────────────

echo ""
echo "context.md: $FILE"
echo "Lines: $LINE_COUNT / $MAX_LINES"
echo ""

if $PASS; then
  echo "PASS — all checks passed."
  exit 0
else
  echo "FAIL — ${#ERRORS[@]} issue(s) found:"
  echo ""
  for i in "${!ERRORS[@]}"; do
    echo "  $((i + 1)). ${ERRORS[$i]}"
    echo ""
  done
  exit 1
fi
