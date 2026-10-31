---
mode: agent
description: Run the atl Confluence round-trip regression (publish-page, fetch-page, map-markdown-adf) against a user-supplied test space and report the capability checklist.
argument-hint: <Confluence test space key or numeric id>
---

# Run ATL round-trip regression

Run [README.md](./README.md)'s scenario end to end with the real skills. All paths below are relative to the repository root; `<runDir>` is absolute.

## Input

- **space** — `${input:space:Confluence test space key or numeric id}`. Missing → ask the user; **MUST NOT** pick a space yourself. Pages are created there.

## Steps

1. *Run `preflight-atlassian` skill to resolve site, credentialed twg command, and token availability from `.atlassian.json.user` config* **Action: Resolve**; keep `twg`. `tokenAvailable` false → stop, report missing `apiToken`.
2. `python3 tests/atl/regression/scripts/regression.py init --space <space>` → keep `runDir`, `mdPath`, `title`. Tell the user the checklist path `<runDir>/checklist.md` (every item unchecked).
3. *Run `publish-page` skill to create a Confluence page from a local Markdown file* with `mdPath`, `spaceId: <space>`; redirect its `run` stdout to `<runDir>/publish-1.json`. Keep `pageId`.
4. Comments, from `<runDir>`, appending both outputs to `comments.log`:
   - `<twg> confluence content comments create --id <pageId> --comment-type inline --text-selection "regression anchor phrase" --body "Regression inline comment"`
   - `<twg> confluence content comments create --id <pageId> --comment-type footer --body "Regression footer comment"`
5. *Run `fetch-page` skill to fetch the Confluence page as Markdown* for `<pageId>` with `--md-path <runDir>/fetched-1.md`.
6. *Run `publish-page` skill to update the Confluence page from Markdown* with `mdPath: <runDir>/fetched-1.md`, `pageId`; redirect its `run` stdout to `<runDir>/publish-2.json`. **MUST NOT** edit `fetched-1.md` first — this step is the Confluence → Markdown → Confluence path under test.
7. *Run `fetch-page` skill to fetch the Confluence page as Markdown* for `<pageId>` with `--md-path <runDir>/fetched-2.md`.
8. Verify, always, even after a failed step:
   - `python3 tests/atl/regression/scripts/regression.py verify --run <runDir>`
   - `ATL_REGRESSION_RUN=<runDir> python3 -m pytest tests/atl/regression -k integration -q`

A step fails → save its stderr to `<runDir>/<step>.err`, skip the remaining Atlassian steps, run step 8.

## Report

- Print `<runDir>/checklist.md` in full.
- Per failed or skipped item: id, detail from `results.json`, and the step artifact to inspect.
- Page URL and `runDir`.
- Ask whether to trash the test page (`<twg> confluence content trash <pageId>`); never delete without a yes.

## Rules

- **MUST NOT** edit fixtures, checks, or fetched files to make an item pass; a failure is the result.
- Diagrams render with the configured `diagramRenderer`; `mermaid` is refused by `publish-page` — report it and stop.
