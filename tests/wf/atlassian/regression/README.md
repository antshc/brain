# ATL Confluence round-trip regression

Proves Markdown → Confluence → Markdown → Confluence keeps every capability of the `atlassian` skill's Map Markdown, Publish page, and Fetch page tactics (`atl.py map-markdown`, `publish-page`, `fetch-page`), using the real CLI against a real Confluence space. Run it with [run-regression.prompt.md](./run-regression.prompt.md); the user supplies the test space and may supply a parent page for subpage isolation.

## Scenario

| Step | Real call | Artifact in the run directory |
|---|---|---|
| 1. Init | `scripts/regression.py init --space <space>` | `page.md`, `assets/`, `run.json`, `checklist.md` (all unchecked) |
| 2a. Publish healthy child | Publish page from `page.md` into `<space>`, under the supplied parent when available | `publish-1.json` |
| 2b. Publish degradation child | In parallel, publish the same fixture with a distinct title and asset directory | `publish-degraded-base.json` |
| 3. Comment | twg inline comment on `regression anchor phrase`, twg footer comment | `comments.log` |
| 4. Fetch healthy / degrade | In parallel, fetch the healthy child and inject a valid unsupported `mention` into the degradation child | `fetched-1.md`, `degrade.json`, `degraded-adf.json` |
| 5. Fetch degraded | Fetch the degraded child and retain its warning | `fetched-degraded.md`, `fetch-degraded.err` |
| 6. Republish checks | In parallel, republish the healthy fetch and confirm `adf:error` rejects the degraded fetch | `publish-2.json`, `publish-degraded.err` |
| 7. Fetch healthy again | Fetch the healthy child | `fetched-2.md`, `fetched-2.md.assets/` |
| 8. Verify | `scripts/regression.py verify --run <runDir>` + live pytest | `checklist.md` ticked, `results.json` |

A failed normal step stops that dependency branch; verify still runs, marking every capability that needed the missing artifact `SKIPPED`. The degraded republish in step 6 is expected to fail; a successful publish leaves its capability failed.

## Capabilities

[scripts/capabilities.py](./scripts/capabilities.py) is the single catalogue: one id, title, and check per capability, grouped by area — Publish, Fetch, Structure, Marks, Inline, Lists, Blocks, Tables, Diagrams, Attachments, Comments, Republish, Degradation. The checklist and both test suites read it. [fixtures/round-trip-page.md](./fixtures/round-trip-page.md) holds one instance of every lossless capability; the degradation phase injects raw ADF after the lossless checks.

Not covered from Markdown: Confluence smart links (`inlineCard`) and Draw.io macros authored in Confluence — the converter reads them but has no Markdown source form.

## Known Confluence behaviors

- `bash` code blocks are stored as `shell`; the converter reads `shell` back as `bash` (B03).
- A code span inside a link (`` [`Foo.Bar`](url) ``) is unsupported: Confluence's v2 ADF read intermittently drops the `code` mark from such text, so it cannot round-trip. The Markdown lint rejects it on publish; fetch renders existing linked code as a plain link and reports `code inside link omitted`. The fixture therefore has no instance of it.

## Runs

`runs/<runId>/` (gitignored). Each run gets unique healthy and degradation child titles so runs never collide in one space. With a parent page, both children are created under it; without one, they are created at the space root. Pages are kept until the user asks to trash them.

## Tests

- Offline (CI): `python3 -m pytest tests/wf/atlassian/regression` — runs the fixture through the real converter, simulates lossless and degraded fetch-page output, and proves every check passes on healthy evidence and fails when evidence is removed.
- Live: `ATL_REGRESSION_RUN=tests/wf/atlassian/regression/runs/<runId> python3 -m pytest tests/wf/atlassian/regression -k integration` — one test per capability against a real run; skipped when the variable is unset.
