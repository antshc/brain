# GitHub setup

## Setup labels

Run from the tracker repository: the current repository for a single repo, the docs/harness root for a wrapping repo. GitHub issues are the only backlog backend for this workflow; local documents are not a tracker.

1. Confirm CLI authentication with `gh auth status`; resolve the tracker with `gh repo view --json nameWithOwner --jq .nameWithOwner`. Stop and report failures.
2. Resolve `./scripts/create_labels.py` from this installed skill's base directory, not the caller CWD. Run `python3 <resolved-script-path>` with the tracker repository as CWD. The helper creates missing labels and preserves existing ones.
3. Check `gh api --paginate repos/{{trackerRepository}}/labels?per_page=100 --jq .[].name` for every baseline label below. If a label is absent, report incomplete setup rather than success.

| Label | Color | Purpose |
|---|---|---|
| `hitl` | `fbca04` | Requires human implementation/review |
| `spec` | `5319e7` | Spec with implementation context |
| `bug` | `d73a4a` | Failure requiring investigation |
| `wayfinder:map` | `0e8a16` | Map issue |
| `wayfinder:research` | `1d76db` | Research decision |
| `wayfinder:experiment` | `5319e7` | Experiment decision |
| `wayfinder:grilling` | `fbca04` | Grilling decision |
| `wayfinder:task` | `d93f0b` | Manual-work decision |

**Returns:** the resolved tracker repository and confirmed label names.

## Gotchas

GitHub authentication, repository permissions, or missing `gh` must surface as setup errors. Do not claim setup succeeded or substitute a Jira/local tracker. Existing labels are intentionally not recolored or rewritten.
