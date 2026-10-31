# ATL Confluence round-trip regression

Proves Markdown → Confluence → Markdown → Confluence keeps every capability of `map-markdown-adf`, `publish-page`, and `fetch-page`, using the real skills against a real Confluence space. Run it with [run-regression.prompt.md](./run-regression.prompt.md); the user supplies the test space.

## Scenario

| Step | Real call | Artifact in the run directory |
|---|---|---|
| 1. Init | `scripts/regression.py init --space <space>` | `page.md`, `assets/`, `run.json`, `checklist.md` (all unchecked) |
| 2. Publish (create) | `publish-page` skill on `page.md` into `<space>` | `publish-1.json` |
| 3. Comment | twg inline comment on `regression anchor phrase`, twg footer comment | `comments.log` |
| 4. Fetch | `fetch-page` skill on the new page | `fetched-1.md`, `fetched-1.md.assets/` |
| 5. Republish (update) | `publish-page` skill on unedited `fetched-1.md`, same page | `publish-2.json` |
| 6. Fetch again | `fetch-page` skill | `fetched-2.md`, `fetched-2.md.assets/` |
| 7. Verify | `scripts/regression.py verify --run <runDir>` + live pytest | `checklist.md` ticked, `results.json` |

A failed step stops the scenario; verify still runs, marking every capability that needed the missing artifact `SKIPPED`.

## Capabilities

[scripts/capabilities.py](./scripts/capabilities.py) is the single catalogue: one id, title, and check per capability, grouped by area — Publish, Fetch, Structure, Marks, Inline, Lists, Blocks, Tables, Diagrams, Attachments, Comments, Republish. The checklist and both test suites read it. [fixtures/round-trip-page.md](./fixtures/round-trip-page.md) holds one instance of every capability; add a construct to the fixture and a check to the catalogue together.

Not covered from Markdown: Confluence smart links (`inlineCard`) and Draw.io macros authored in Confluence — `map-markdown-adf` reads them but has no Markdown source form.

## Known Confluence behaviors

- `bash` code blocks are stored as `shell`; `map-markdown-adf` reads `shell` back as `bash` (B03).
- **Open — M04 fails live:** on full pages Confluence drops the `code` mark from a span that also carries `link` (`[`Foo.Bar`](url)` returns as `[Foo.Bar](url)`). The ADF sent is correct; small isolated documents sometimes keep both marks, so the trigger is server-side and not yet isolated. `map-markdown-adf` cannot recover a mark Confluence did not store.

## Runs

`runs/<runId>/` (gitignored). Each run gets a unique page title `ATL Round-Trip Regression <runId>` so runs never collide in one space. Pages are kept until the user asks to trash them.

## Tests

- Offline (CI): `python3 -m pytest tests/atl/regression` — runs the fixture through the real converter, simulates fetch-page's substitutions, and proves every check passes on a healthy round trip and fails on a lost construct.
- Live: `ATL_REGRESSION_RUN=tests/atl/regression/runs/<runId> python3 -m pytest tests/atl/regression -k integration` — one test per capability against a real run; skipped when the variable is unset.
