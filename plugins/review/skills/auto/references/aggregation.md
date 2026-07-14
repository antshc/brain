# Aggregation & Display

The orchestrator collects three axis output payloads (each matching
`<skill-directory>/references/io-schema.md`) and produces one combined report. Keep the axes
**separate** — never merge or re-rank findings across axes.

## Step 1 — Deduplicate violations
For each axis, drop any `violations` entry already covered by an existing review comment.
Match on `file_path` + `line_number` + `label`. Carry forward only net-new, actionable violations.

## Step 2 — Combine counts
Roll up per-axis counts and a grand total:

| Axis | candidates_total | filtered_out | after_filter (violations) | passed |
|------|------------------|--------------|---------------------------|--------|
| quality-attributes | … | … | … | … |
| code-smells | … | … | … | … |
| requirements-coverage | … | … | … | … |
| **Total** | … | … | … | … |

`after_filter` for each axis must equal the number of carried-forward violations before
dedup; note separately how many were dropped by Step 1 dedup.

## Step 3 — Display to the user
Show both lists, grouped by axis, in this order:

```
## Quality-attributes
### Violations
- [label] file:line — finding (evidence)
### Passed
- rule — conclusion (scope)

## Code-smells
### Violations
...
### Passed
...

## Requirements-coverage
### Violations
...
### Passed
...

## Counts
<the roll-up table from Step 2>
```

If `requirements-coverage` returned "no spec available", show that note under its section
instead of lists.

## Step 4 — Hand violations to posting
Only the carried-forward **violations** proceed to formatting (`/to-review-comment`) and
posting (`/post-review-comment`). The **passed** lists are display-only and are never posted.
