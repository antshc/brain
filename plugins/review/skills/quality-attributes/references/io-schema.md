# I/O Schema — quality-attributes axis

The axis agent consumes an **input** payload and returns an **output** payload. Both are JSON.

## Input

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
  "spec": null
}
```

`spec` is unused by this axis; it may be `null`.

## Output

```json
{
  "axis": "quality-attributes",
  "violations": [
    {
      "file_path": "src/Foo.cs",
      "line_number": 42,
      "label": "bug",
      "finding": "<issue>. <why it matters>. <smallest safe fix>.",
      "evidence": "Error handling — confirmed issue"
    }
  ],
  "passed": [
    { "rule": "Backward compatibility", "conclusion": "no issue found", "scope": "PublicApi.Serialize" },
    { "rule": "Evidence filter", "conclusion": "dropped speculative finding", "scope": "src/Bar.cs:88" }
  ],
  "counts": { "candidates_total": 8, "after_filter": 3, "filtered_out": 5, "passed": 6 }
}
```

## Rules
- `label` is one of `bug | suggest | nit`.
- `line_number` is the new-file line on the right side of the diff.
- One finding per `violations` entry — never combine unrelated issues.
- `evidence` for this axis names the quality area and its conclusion (e.g. `Error handling — confirmed issue`).
- `passed` includes each checklist item concluded **no issue found**, plus each candidate dropped by a review rule (with the filtering rule named in `rule`).
- `counts.after_filter` must equal `len(violations)`; `counts.filtered_out` must equal the number of dropped candidates.
