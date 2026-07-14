# I/O Schema — auto orchestrator

The orchestrator builds one shared **input** payload and sends it to each of the three axis
agents (`quality-attributes`, `code-smells`, `requirements-coverage`). Each agent returns an
**output** payload. All payloads are JSON.

## Input (orchestrator → each axis agent)

```json
{
  "pr": { "owner": "OWNER", "repo": "REPO", "number": 1245, "url": "https://github.com/OWNER/REPO/pull/1245" },
  "diff_dir": "bin/review_diff/",
  "changed_symbols": ["Namespace.Type.Method", "Namespace.Type.Property"],
  "existing_comments": [
    { "file_path": "src/Foo.cs", "line_number": 42, "user": "alice", "body": "..." }
  ],
  "lsp_summary": {
    "symbols": [
      { "symbol": "...", "contract": "before -> after", "nullability": "...", "callers": "...", "fan_out": "3 files / 7 callers", "overrides": "no", "risk_flag": "high: contract change" }
    ],
    "risk_flags": ["Namespace.Type.Method — contract change"]
  },
  "spec": { "source": "issue #123", "content": "..." }
}
```

The same payload goes to all three axes. `spec` is consumed only by `requirements-coverage`;
it is `null` when no spec was found.

## Output (each axis agent → orchestrator)

```json
{
  "axis": "quality-attributes | code-smells | requirements-coverage",
  "violations": [
    { "file_path": "src/Foo.cs", "line_number": 42, "label": "bug", "finding": "...", "evidence": "..." }
  ],
  "passed": [
    { "rule": "...", "conclusion": "...", "scope": "..." }
  ],
  "counts": { "candidates_total": 8, "after_filter": 3, "filtered_out": 5, "passed": 6 }
}
```

Field rules per axis live in each axis skill's own `references/io-schema.md`. The orchestrator
treats all three outputs uniformly for aggregation.
