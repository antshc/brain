# Review Finding Template

Use this template for every review finding. Keep it actionable and grounded in code evidence. It carries all fields required to emit a finding and post it as a review comment.

## Field Rules

- `AXIS` the review axis that produced the finding: `code-smells`, `quality-attributes`, `requirements-coverage`, or `hitl`.
- `FILE_PATH` must be the repo-relative file path exactly as it appears in the diff header.
- `LINE_NUMBER` must be the new-file line number of the most relevant changed line on the right side of the diff.
- For multi-line ranges, use the last line of the relevant changed range.
- `LABEL` one of `bug | suggest | nit`.
- `FINDING_BODY` `<label>: <body>`, where `<body>` (`<the issue>. <why it matters>. <smallest safe fix>.`) is formatted via the `/to-review-tone` skill and the `<label>` is prefixed after formatting.
- Omit the snippet for `nit` findings.

## Template

```
AXIS: <review axis>
FILE_PATH: <repo-relative file path>
LINE_NUMBER: <new-file line number>
LABEL: <bug | suggest | nit>
FINDING_BODY: <label>: <the issue>. <why it matters>. <smallest safe fix>.
```

Optional minimal snippet:

````language
<tiny inline snippet or diff showing the smallest safe fix>
````
