#!/usr/bin/env bash
# Detect HARNESS_ROOT and persist it to "$HARNESS_ROOT/.agent.env" as an export line.
# Works from the harness root or any of its worktrees.
# Idempotent: if the env file already exists, source it and skip detection.
set -euo pipefail

# Main working tree of the current repo (resolves through linked worktrees).
CURRENT_MAIN=$(cd "$(git rev-parse --git-common-dir)/.." && pwd)

# Harness root: climb from the current repo to the outermost enclosing repo.
HARNESS_ROOT=$CURRENT_MAIN
while parent=$(cd "$HARNESS_ROOT/.." && git rev-parse --show-toplevel 2>/dev/null); do
  HARNESS_ROOT=$parent
done

ENV_FILE="$HARNESS_ROOT/.agent.env"

if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  echo "HARNESS_ROOT=$HARNESS_ROOT"
  echo "(existing .agent.env — skipped detection)"
  exit 0
fi

cat > "$ENV_FILE" <<ENVEOF
export HARNESS_ROOT="$HARNESS_ROOT"
ENVEOF

echo "HARNESS_ROOT=$HARNESS_ROOT"
