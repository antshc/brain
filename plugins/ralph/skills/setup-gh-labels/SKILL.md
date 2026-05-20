---
name: setup-gh-labels
description: Create required GitHub issue labels if they do not exist.
---

# Ensure GitHub Labels

## Goal

Create missing GitHub issue labels for AFK/HITL task workflow.

## Labels

| Name | Color | Description |
|---|---:|---|
| `ready` | `0e8a16` | Ready for AFK implementation |
| `hitl` | `fbca04` | Requires human implementation |
| `blocked` | `d73a4a` | Skipped or blocked; not implemented |
| `prd` | `5319e7` | PRD task with implementation context |

## Rules

- Detect repo from current git remote.
- Use `gh` CLI.
- Create only missing labels.
- Do not fail if label already exists.
- Do not overwrite existing label color/description unless explicitly requested.
- Print created labels.
- Print existing labels.
- Return non-zero only on real API/auth/network errors.

## Implementation

```bash
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

create_label_if_missing "ready"   "0e8a16" "Ready for AFK implementation"
create_label_if_missing "hitl"    "fbca04" "Requires human implementation"
create_label_if_missing "blocked" "d73a4a" "Skipped or blocked; not implemented"
create_label_if_missing "prd"     "5319e7" "PRD task with implementation context"
```

## Expected output

```text
exists:  ready
created: hitl
exists:  blocked
created: prd
```

## Done

- All required labels exist in the current GitHub repository.
- Existing labels are preserved.
- Missing labels are created.
