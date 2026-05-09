#!/bin/bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Arguments ─────────────────────────────────────────────────────────────────

if [[ -z "$1" || -z "$2" || -z "$3" ]]; then
  echo "Usage:" >&2
  echo "  $0 review-prs <repo-dir> <github-user> <owner/repo> [max-executions]" >&2
  echo "  $0 review-pr  <repo-dir> <pr-url>                   [max-executions]" >&2
  exit 1
fi

# ── Main ──────────────────────────────────────────────────────────────────────

cd "$1" # <repo-dir>
python3 "$SCRIPT_DIR/brain_tools/ralph.py" "$@"
