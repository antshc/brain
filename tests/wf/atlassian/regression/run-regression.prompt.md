---
mode: agent
description: Run the atl Confluence round-trip regression (atlassian skill Publish page, Fetch page, Map Markdown) against a user-supplied test space and optional parent page, report the capability checklist, and parallelize independent branches.
argument-hint: <Confluence test space key or numeric id> [<parent page id or URL>]
---

# Run ATL round-trip regression

Run [README.md](./README.md)'s scenario end to end with the real skills. All paths below are relative to the repository root; `<runDir>` is absolute.

## Input

- **space** — `${input:space:Confluence test space key or numeric id}`. Missing → ask the user; **MUST NOT** pick a space yourself. Pages are created there.
- **parentPageId** — optional parent page supplied by the user. Resolve a URL to its numeric page id. When present, create both regression pages as children; otherwise create them at the space root.

## Steps

1. *Run `preflight-atlassian` skill to resolve site, credentialed twg command, token availability, config path, and account id from `.atlassian.json.user` config* **Action: Resolve**; keep `twg`, `configPath`, and `accountId`. `tokenAvailable` false → stop, report missing `apiToken`.
2. `python3 tests/wf/atlassian/regression/scripts/regression.py init --space <space>` → keep `runDir`, `mdPath`, `title`. Tell the user the checklist path `<runDir>/checklist.md` (every item unchecked).
3. Create two child pages in parallel, using separate asset directories:
   - Healthy: *Publish page* on `mdPath` with `spaceId: <space>` and `parentId: <parentPageId>` when supplied; redirect stdout to `<runDir>/publish-1.json`. Keep `healthyPageId`.
   - Degradation baseline: *Publish page* on the same `mdPath` with title `<title> Degradation`, `spaceId: <space>`, `--assets-dir <runDir>/degraded-page.md.tmp`, and the same parent; redirect stdout to `<runDir>/publish-degraded-base.json`. Keep `degradedPageId`.
4. Comments, from `<runDir>`, appending both outputs to `comments.log`:
   - `<twg> confluence content comments create --id <healthyPageId> --comment-type inline --text-selection "regression anchor phrase" --body "Regression inline comment"`
   - `<twg> confluence content comments create --id <healthyPageId> --comment-type footer --body "Regression footer comment"`
5. Run the independent fetch/degrade branches in parallel:
   - Healthy: *Fetch page* `<healthyPageId>` to `<runDir>/fetched-1.md`.
   - Degradation: `python3 tests/wf/atlassian/regression/scripts/regression.py degrade --run <runDir> --publish <runDir>/publish-degraded-base.json --config <configPath> --account-id <accountId>` → redirect stdout to `<runDir>/degrade.json`; it appends a valid Confluence `mention` node and valid text after it, then preserves the exact injected body in `<runDir>/degraded-adf.json`.
6. *Fetch page* `<degradedPageId>` to `<runDir>/fetched-degraded.md`. Redirect stderr to `<runDir>/fetch-degraded.err`; the fetch must exit 0 with a conversion warning.
7. Run final republish branches in parallel:
   - Healthy: *Publish page* `<runDir>/fetched-1.md` to `<healthyPageId>`; redirect stdout to `<runDir>/publish-2.json`. **MUST NOT** edit `fetched-1.md` first.
   - Degraded: attempt *Publish page* `<runDir>/fetched-degraded.md` to `<degradedPageId>`; redirect stderr to `<runDir>/publish-degraded.err`. Failure is expected.
8. *Fetch page* `<healthyPageId>` to `<runDir>/fetched-2.md`.
9. Verify, always, even after a failed normal step:
   - `python3 tests/wf/atlassian/regression/scripts/regression.py verify --run <runDir>`
   - `ATL_REGRESSION_RUN=<runDir> python3 -m pytest tests/wf/atlassian/regression -k integration -q`

A normal step fails → save its stderr to `<runDir>/<step>.err`, skip only the dependent branch, run step 9 when the independent branch finishes. The degraded republish must fail; a zero exit is a regression result.

## Report

- Print `<runDir>/checklist.md` in full.
- Per failed or skipped item: id, detail from `results.json`, and the step artifact to inspect.
- Page URL and `runDir`.
- Ask whether to trash the test page (`<twg> confluence content trash <pageId>`); never delete without a yes.

## Rules

- **MUST NOT** edit fixtures, checks, or fetched files to make an item pass; a failure is the result.
- When a parent page is supplied, the test never edits it: healthy and degraded work stays on dedicated children. The degradation child remains degraded for verification.
- Diagrams render with the configured `diagramRenderer`; `mermaid` is refused by Publish page — report it and stop.
