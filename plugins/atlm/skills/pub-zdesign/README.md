# pub-zdesign — implementation notes

Maintainer-facing notes for the `pub-zdesign` skill. Agent-facing usage lives in
[SKILL.md](SKILL.md).

## Why hand-built ADF

The pipeline builds ADF node dicts directly (see [references/adf-mapping.md](references/adf-mapping.md))
instead of using a generic Markdown → ADF converter:

- zdesign docs lean on nodes generic converters skip — `<details>` expands, `<br>`-joined table
  cells, bold list lead-ins, and diagrams.
- The `ADFBuilder` class does **not** exist in the installed `atlassian-python-api` 4.0.7 (only on
  `master`).

Self-contained at runtime: it implements its own Markdown → ADF conversion, Mermaid-to-PNG
pipeline, and Confluence publish/verify — no dependency on the `markdown-to-adf` or
`publish-confluence-page` skills (their node-mapping tables informed this one).

## Module layout

`scripts/publish_zdesign.py` is a thin CLI entrypoint; the pipeline lives in
`scripts/zdesign_publisher/`, split along its natural seams so each part is unit-testable without
network, filesystem, or subprocess access.

| Module | Seam | Depends on I/O? |
| --- | --- | --- |
| `patterns.py` | shared regexes/marker helpers | no |
| `inline.py` | inline mark parsing (markdown spans → ADF text nodes) | no |
| `blocks.py` | block parsing (headings, lists, tables, quotes, `<details>`, TOC) | no |
| `adf.py` | wires parsed blocks + media fileIds into the ADF doc envelope | no |
| `env.py` | reads `.atlmcp.env`, constructs the `Confluence` client | yes (file read, client ctor) |
| `mermaid.py` | extracts ```mermaid fences (pure); renders via `mmdc` (I/O) | mixed |
| `attachments.py` | uploads PNGs, reads back media-service fileIds | yes (Confluence REST) |
| `cli.py` | arg parsing, page-id resolution, orchestration, publish/verify | yes (Confluence REST) |

## Tests

`tests/` covers every module: the pure ones (`inline`, `blocks`, `adf`, `patterns`,
`extract_mermaid`) directly; the I/O seams (`env`, `mermaid.render_diagrams`, `attachments`, `cli`)
by mocking `subprocess.run` / the `Confluence` client.

```bash
python -m pytest .github/skills/pub-zdesign/tests/ -q
```

## Dependencies

Runtime preconditions (mmdc install, shared libraries) live in [SKILL.md](SKILL.md#preconditions).

- `pip install -r requirements.txt` pins `atlassian-python-api<5` — the 5.x `Cloud` client dropped
  `attach_file`, which `attachments.py` depends on.
- `mmdc` is an npm package, so it is deliberately absent from `requirements.txt`.