# GitHub

Use `gh` for GitHub I/O. Resolve paths to body files from the caller's working directory, not this reference's folder.

## Prerequisites

- Confirm `gh --version` and `gh auth status`. Resolve `TRACKER_REPOSITORY` from the supplied issue destination or `gh repo view --json nameWithOwner --jq .nameWithOwner` at the caller's repository root.
- Resolve `SOURCE_REPOSITORY` (`owner/repo`) from agreed context or the source checkout's `origin`. A `workspace/` folder with exactly one checkout selects that checkout; multiple candidates or ambiguous remotes require clarification. Without a separate source checkout, use the caller's repository. Confirm its identity with `gh repo view SOURCE_REPOSITORY --json nameWithOwner,defaultBranchRef`.
- Resolve `BASE_BRANCH` from agreed context; otherwise confirm the source repository's default branch as the intended base. Verify the branch exists in the source repository before publication. Ask only for unresolved routing; keep tracker and source distinct even when they are the same repository.
- Commands below use resolved placeholders. Pass `--repo TRACKER_REPOSITORY` explicitly on issue and label commands.
- Report authentication, permission, network, and validation failures with the failed operation. Do not substitute local output for successful publication or retry creation blindly after ambiguous results.

## Operations

| Purpose | Command |
|---|---|
| Read issue | `gh issue view NUMBER --repo TRACKER_REPOSITORY --json number,title,body,labels,state,url` |
| Read all comments | `gh api --paginate repos/TRACKER_REPOSITORY/issues/NUMBER/comments` |
| List all labels | `gh api --paginate repos/TRACKER_REPOSITORY/labels --jq '.[].name'` |
| Create missing source label | `gh label create "repo:target:SOURCE_REPOSITORY" --repo TRACKER_REPOSITORY --color 0e8a16 --description "Source repository for this spec's tickets"` |
| Create missing base label | `gh label create "repo:base:BASE_BRANCH" --repo TRACKER_REPOSITORY --color c5def5 --description "Base branch for this spec's feature branch"` |
| Publish spec | `gh issue create --repo TRACKER_REPOSITORY --title "TITLE" --body-file SPEC_FILE --label "repo:target:SOURCE_REPOSITORY,repo:base:BASE_BRANCH"` |

Check the complete label list first; create only missing labels, preserving existing label metadata. The required labels are `repo:target:<owner/repo>` and `repo:base:<branch>`; no `spec` label is required. Write the full spec to a temporary Markdown body file outside the repository, pass it with `--body-file`, and remove only that temporary file after publication/read-back.

Record the returned URL immediately. Read the issue back and confirm its complete body and both exact routing-label values before reporting success. If creation returned an ambiguous error, inspect recent issues for the intended spec before attempting another create; a failed lookup is not proof of absence.

## Gotchas

- Issue numbers differ from database IDs; basic issue commands use numbers.
- Substitute resolved placeholders as argument values, not shell interpolation of user text; use `--body-file` for multiline content.
- GitHub issue creation can succeed before a client-side failure. Preserve partial results and report uncertainty rather than creating duplicates.
- Fully qualify references outside the target repository as `OWNER/REPO#NUMBER`.
