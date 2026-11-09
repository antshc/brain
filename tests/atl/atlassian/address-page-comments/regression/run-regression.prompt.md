---
mode: agent
description: Run the atlassian Address page comments live regression (twg targeted edits, orphaned comments, replies, rerun gate) against a user-supplied test space and report the case checklist.
argument-hint: <Confluence test space key or numeric id>
---

# Run Address page comments regression

Run [README.md](./README.md)'s scenario. Paths are relative to the repository root.

## Input

- **space** — `${input:space:Confluence test space key or numeric id}`. Missing → ask the user; **MUST NOT** pick a space yourself. A page is created there.

## Steps

1. *Run `preflight-atlassian` skill to resolve site, credentialed twg command, and token availability from `.atlassian.json.user` config* **Action: Resolve**; keep `configPath`, `twg`, `site`, `accountId`. `tokenAvailable` false or empty `accountId` → stop and report.
2. From the repository root, with the repo environment active (`source .envrc`):
   ```bash
   python tests/atl/atlassian/address-page-comments/regression/scripts/apc_regression.py run --space "<space>" --twg "<twg>" --account-id <accountId> --site <site> --config "<configPath>"
   ```
   Prints `runDir`, `checklist`, and `pass`/`fail`/`skipped` case ids; exit 1 unless all pass.

## Report

- Print `<runDir>/checklist.md` in full.
- Per failed or skipped case: id, detail from `results.json`, and any `<runDir>/<step>.err`.
- Page URL and `runDir`.
- Ask whether to trash the test page (`<twg> confluence content trash <pageId>`); never delete without a yes.

## Rules

- **MUST NOT** edit cases, the driver, or run artifacts to make a case pass; a failure is the result.
