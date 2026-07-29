#!/usr/bin/env bash
set -euo pipefail

repo="$(gh repo view --json nameWithOwner -q .nameWithOwner)"

create_label_if_missing() {
  local name="$1"
  local color="$2"
  local description="$3"

  if gh label list --repo "$repo" --json name -q '.[].name' | grep -Fxq "$name"; then
    echo "exists:  $name"
    return 0
  fi

  gh label create "$name" \
    --repo "$repo" \
    --color "$color" \
    --description "$description"

  echo "created: $name"
}

create_label_if_missing "hitl" "fbca04" "Requires human implementation"
create_label_if_missing "spec" "5319e7" "Spec task with implementation context"