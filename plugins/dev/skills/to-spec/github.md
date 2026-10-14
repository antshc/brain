# GitHub

Use `gh` for GitHub I/O. Resolve paths to body files from the caller's working directory, not this reference's folder.

## Prerequisites

- Confirm `gh --version`, `gh auth status`, and the intended repository with `gh repo view --json nameWithOwner,defaultBranchRef`. Resolve ambiguous remotes with the user before writing.
- Commands below use `OWNER/REPO` as a placeholder for the confirmed repository. Pass `--repo OWNER/REPO` explicitly on issue and label commands.
- Report authentication, permission, network, and validation failures with the failed operation. Do not substitute local output for successful publication or retry creation blindly after ambiguous results.

## Operations

| Purpose | Command |
|---|---|
| Read issue | `gh issue view NUMBER --repo OWNER/REPO --json number,title,body,labels,state,url` |
| Read all comments | `gh api --paginate repos/OWNER/REPO/issues/NUMBER/comments` |
| List all labels | `gh api --paginate repos/OWNER/REPO/labels --jq '.[].name'` |
| Create missing label | `gh label create ready-for-agent --repo OWNER/REPO --color 0E8A16 --description "Fully specified and ready for agent implementation"` |
| Publish spec | `gh issue create --repo OWNER/REPO --title "TITLE" --body-file SPEC_FILE --label ready-for-agent` |

Check the complete label list first; create `ready-for-agent` only if missing, preserving existing label metadata. Write the full spec to a temporary Markdown body file outside the repository, pass it with `--body-file`, and remove only that temporary file after publication/read-back.

Record the returned URL immediately. Read the issue back and confirm its body and label before reporting success. If creation returned an ambiguous error, inspect recent issues for the intended spec before attempting another create.

## Gotchas

- Issue numbers differ from database IDs; basic issue commands use numbers.
- GitHub issue creation can succeed before a client-side failure. Preserve partial results and report uncertainty rather than creating duplicates.
- Fully qualify references outside the target repository as `OWNER/REPO#NUMBER`.
