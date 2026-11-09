# address-page-comments live regression

Proves the twg mechanics `address-page-comments` relies on, against a real Confluence space: targeted edits keep untouched nodes, inline-comment highlights, draw.io diagrams, media, attachments, and every other ADF-only construct, a removed highlight turns its thread orphaned, replies land in the right place, and the rerun gate sees every answer. Run it with [run-regression.prompt.md](./run-regression.prompt.md); the user supplies the test space.

Scripted, not agent-driven: [scripts/apc_regression.py](./scripts/apc_regression.py) follows the skill's steps with fixed edits and replies, so a failure points at twg or `comment_state.py`, never at agent judgment.

## Scenario

| Step | Real call | Artifact in the run directory |
|---|---|---|
| 1. Publish | `atl.py publish-page run` on [fixtures/page.md](./fixtures/page.md): three comment-target paragraphs plus every construct from the round-trip fixture (TOC, marks, status, headings, lists, panels, code, breakouts, tables, expands, two draw.io diagrams, image, file) | `page.md`, `publish.json`, `run.json` |
| 2. Seed | twg inline comments on `retry limit`, `Legacy export`, `rotate daily`; one footer comment | `seed.json` |
| 3. Gate 1 | twg `attachments list`, `comments list`, `content get --draft --format html` + `comment_state.py` | `attachments-before.json`, `before.html`, `gate-1.json` |
| 4. Edit | twg `content update --edits-file`: `replaceNode` (three → five), `deleteNode` (legacy export), `appendNodeToEnd` (owner) | `edits.json`, `update.json`, `after.html` |
| 5. Gate 2 | as step 3 on the edited body | `gate-2.json` |
| 6. Reply | twg `comments reply` on three threads; one footer page answer linking the orphan; read back each | `replies.json` |
| 7. Gate 3 | as step 3, plus attachments list | `final.html`, `gate-3.json`, `final-comments.json`, `attachments-after.json` |
| 8. Verify | `scripts/apc_regression.py verify` (runs automatically after `run`) | `checklist.md`, `results.json` |

A failed step writes `<step>.err` and stops; verify still runs, marking every case whose artifact is missing `SKIPPED`.

**One account:** seeded reviewer comments and agent replies share the configured account, so the driver relabels seeded comments to `regression-reviewer` before `comment_state.py` classifies them. The skill's own agent run is not covered.

## Cases

[scripts/cases.py](./scripts/cases.py) is the single catalogue:

| Id | Case |
|---|---|
| G1 | First gate lists every seeded thread with its anchor |
| E1 | Targeted edit update succeeds |
| E2 | `replaceNode` changes text and keeps the annotation |
| E3 | Untouched node is byte-identical after the edit |
| E4 | `deleteNode` removes the node and its annotation |
| E5 | `appendNodeToEnd` adds the requested paragraph |
| G2 | Removed highlight makes its thread orphaned with page reply target |
| R1 | Thread replies post and read back |
| R2 | Orphaned thread answered in a page comment linking it |
| G3 | Rerun gate detects every answer and skips |
| R3 | No seeded comment resolved |
| P1 | Page carries diagrams, media, tables, lists, panels, and other ADF-only constructs |
| P2 | Everything outside the edited nodes is byte-identical after edits and replies |
| P3 | Attachments (image, file, draw.io) unchanged after edits and replies |

Diagrams render with the configured `diagramRenderer`; `drawio` needs the `drawio` CLI and `drawioExtensionKey` (see the `atlassian` skill's Publish page reference), `mmdc` always.

## Runs

`runs/<runId>/` (gitignored). Each run creates a page titled `APC Comments Regression <runId>`. Pages are kept until the user asks to trash them.

## Tests

- Offline (CI): `python3 -m pytest tests/atl/address-page-comments` — every case passes on healthy artifacts, fails on a broken one, skips on a missing one.
- Live: see [run-regression.prompt.md](./run-regression.prompt.md).
