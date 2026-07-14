# I/O Schema — requirements-coverage axis

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
      { "symbol": "...", "contract": "before -> after", "nullability": "...", "callers": "...", "fan_out": "3 files / 7 callers", "overrides": "no", "risk_flag": "low" }
    ],
    "risk_flags": []
  },
  "spec": { "source": "issue #123", "content": "As a user I can ... The system must ..." }
}
```

`spec` is required by this axis. When no spec is found it is `null`, and the agent returns the
"no spec available" result described below.

## Output

```json
{
  "axis": "requirements-coverage",
  "violations": [
    {
      "file_path": "src/Foo.cs",
      "line_number": 42,
      "label": "bug",
      "finding": "<missing/partial/scope-creep/wrong>. <why it matters>. <smallest safe fix>.",
      "evidence": "Spec: \"The system must reject expired tokens\""
    }
  ],
  "passed": [
    { "rule": "Requirement: reject expired tokens", "conclusion": "implemented correctly", "scope": "AuthService.Validate" },
    { "rule": "Spec-anchor filter", "conclusion": "dropped unanchored gap", "scope": "src/Bar.cs:88" }
  ],
  "counts": { "candidates_total": 4, "after_filter": 2, "filtered_out": 2, "passed": 7 }
}
```

## No spec available

```json
{
  "axis": "requirements-coverage",
  "violations": [],
  "passed": [],
  "note": "no spec available",
  "counts": { "candidates_total": 0, "after_filter": 0, "filtered_out": 0, "passed": 0 }
}
```

## Rules
- `label` is one of `bug | suggest | nit`.
- `line_number` is the new-file line on the right side of the diff (for scope creep, the line the unrequested behavior lives on).
- One finding per `violations` entry — never combine unrelated requirements.
- `evidence` for this axis quotes the exact spec line the finding maps to.
- `passed` includes each requirement confirmed implemented correctly, plus each candidate dropped by a review rule (with the filtering rule named in `rule`).
- `counts.after_filter` must equal `len(violations)`; `counts.filtered_out` must equal the number of dropped candidates.
