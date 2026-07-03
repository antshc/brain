#!/usr/bin/env bash
# Detect CSDROID_HARNESS_ROOT and CSDROID_WORKSPACE_ROOT and persist them to
# "$CSDROID_HARNESS_ROOT/.csdroid.env" as export lines.
# Works from the harness root, the workspace source repo, or any of their worktrees.
# Idempotent: if the env file already exists, source it and skip detection.
set -euo pipefail

# Main working tree of the current repo (resolves through linked worktrees).
CURRENT_MAIN=$(cd "$(git rev-parse --git-common-dir)/.." && pwd)

# Harness root: climb from the current repo to the outermost enclosing repo.
CSDROID_HARNESS_ROOT=$CURRENT_MAIN
while parent=$(cd "$CSDROID_HARNESS_ROOT/.." && git rev-parse --show-toplevel 2>/dev/null); do
  CSDROID_HARNESS_ROOT=$parent
done

ENV_FILE="$CSDROID_HARNESS_ROOT/.csdroid.env"

if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  echo "CSDROID_HARNESS_ROOT=$CSDROID_HARNESS_ROOT"
  echo "CSDROID_WORKSPACE_ROOT=$CSDROID_WORKSPACE_ROOT"
  echo "(existing .csdroid.env — skipped detection)"
  exit 0
fi

# Workspace root:
# - If we started inside a nested repo (current repo != harness), that repo IS the workspace source.
# - Otherwise, look for a source repo under workspace/ (matching the worktree skill's resolution).
# - Else, fall back to the harness root (harness-only layout).
if [ "$CURRENT_MAIN" != "$CSDROID_HARNESS_ROOT" ]; then
  CSDROID_WORKSPACE_ROOT=$CURRENT_MAIN
else
  src_git=""
  if [ -d "$CSDROID_HARNESS_ROOT/workspace" ]; then
    src_git=$(find "$CSDROID_HARNESS_ROOT/workspace" -maxdepth 2 -name .git -type d 2>/dev/null | head -n1 || true)
  fi
  if [ -n "$src_git" ]; then
    CSDROID_WORKSPACE_ROOT=$(cd "$(dirname "$src_git")" && pwd)
  else
    CSDROID_WORKSPACE_ROOT=$CSDROID_HARNESS_ROOT
  fi
fi

cat > "$ENV_FILE" <<EOF
export CSDROID_HARNESS_ROOT="$CSDROID_HARNESS_ROOT"
export CSDROID_WORKSPACE_ROOT="$CSDROID_WORKSPACE_ROOT"
EOF

echo "CSDROID_HARNESS_ROOT=$CSDROID_HARNESS_ROOT"
echo "CSDROID_WORKSPACE_ROOT=$CSDROID_WORKSPACE_ROOT"
