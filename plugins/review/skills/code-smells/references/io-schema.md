# I/O Schema — code-smells axis

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
      { "symbol": "...", "contract": "before -> after", "nullability": "...", "callers": "...", "fan_out": "3 files / 7 callers", "overrides": "no", "risk_flag": "high: wide fan-out" }
    ],
    "risk_flags": ["Namespace.Type.Method — wide fan-out"]
  },
  "spec": null
}
```

`spec` is unused by this axis; it may be `null`.

## Output

```json
{
  "axis": "code-smells",
  "violations": [
    {
      "file_path": "src/Foo.cs",
      "line_number": 42,
      "label": "suggest",
      "finding": "<smell>. <why it matters>. <smallest safe fix>.",
      "evidence": "Feature Envy: <quoted hunk>"
    }
  ],
  "passed": [
    { "rule": "Duplicated Code", "conclusion": "not present", "scope": "src/Foo.cs" },
    { "rule": "Tooling filter", "conclusion": "dropped analyzer-covered finding", "scope": "src/Bar.cs:12" }
  ],
  "counts": { "candidates_total": 5, "after_filter": 2, "filtered_out": 3, "passed": 12 }
}
```

## Rules
- `label` is one of `bug | suggest | nit` (code smells are usually `suggest` or `nit`).
- `line_number` is the new-file line on the right side of the diff.
- One finding per `violations` entry — never combine unrelated smells.
- `evidence` for this axis names the Fowler smell and quotes the hunk (e.g. `Feature Envy: <hunk>`).
- `passed` includes each smell checked with no match, plus each candidate dropped by a review rule (with the filtering rule named in `rule`).
- `counts.after_filter` must equal `len(violations)`; `counts.filtered_out` must equal the number of dropped candidates.
