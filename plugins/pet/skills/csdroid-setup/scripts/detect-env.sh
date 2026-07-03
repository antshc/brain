#!/usr/bin/env bash
# Detect CSDROID_HARNESS_ROOT and CSDROID_WORKSPACE_ROOT and persist them to
# "$(git rev-parse --show-toplevel)/.csdroid.env" as export lines.
# Idempotent: if the env file already exists, source it and skip detection.
set -euo pipefail

ENV_FILE="$(git rev-parse --show-toplevel)/.csdroid.env"

if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  echo "CSDROID_HARNESS_ROOT=$CSDROID_HARNESS_ROOT"
  echo "CSDROID_WORKSPACE_ROOT=$CSDROID_WORKSPACE_ROOT"
  echo "(existing .csdroid.env — skipped detection)"
  exit 0
fi

# Harness root: main working tree of the current repo, then climb to the outermost repo.
CSDROID_HARNESS_ROOT=$(cd "$(git rev-parse --git-common-dir)/.." && pwd)
while parent=$(cd "$CSDROID_HARNESS_ROOT/.." && git rev-parse --show-toplevel 2>/dev/null); do
  CSDROID_HARNESS_ROOT=$parent
done

# Workspace root: the workspace/ source repo if present, else the harness root.
if [ -d "$CSDROID_HARNESS_ROOT/workspace" ] && \
   git -C "$CSDROID_HARNESS_ROOT/workspace" rev-parse --show-toplevel >/dev/null 2>&1; then
  CSDROID_WORKSPACE_ROOT=$(cd "$CSDROID_HARNESS_ROOT/workspace" && git rev-parse --show-toplevel)
else
  CSDROID_WORKSPACE_ROOT=$CSDROID_HARNESS_ROOT
fi

cat > "$ENV_FILE" <<EOF
export CSDROID_HARNESS_ROOT="$CSDROID_HARNESS_ROOT"
export CSDROID_WORKSPACE_ROOT="$CSDROID_WORKSPACE_ROOT"
EOF

echo "CSDROID_HARNESS_ROOT=$CSDROID_HARNESS_ROOT"
echo "CSDROID_WORKSPACE_ROOT=$CSDROID_WORKSPACE_ROOT"
