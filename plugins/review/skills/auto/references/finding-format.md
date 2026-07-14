# Finding Format

Every review sub-agent (Quality-attributes, Code-smells, Requirements-coverage) returns findings in this shared schema. Uniform findings make Step 7 deduplication and Step 8 formatting mechanical — do not invent per-axis shapes.

Each finding is one block:

```
AXIS: quality-attributes | code-smells | requirements-coverage
FILE_PATH: <repo-relative path exactly as in the diff header>
LINE_NUMBER: <new-file line number on the right side of the diff>
LABEL: bug | suggest | nit
FINDING: <the issue>. <why it matters>. <smallest safe fix>.
EVIDENCE: <axis-specific anchor — see below>
```

`EVIDENCE` carries the axis-specific anchor that justifies the finding:
- **quality-attributes** — the quality area and its conclusion (e.g. `Error handling — confirmed issue`).
- **code-smells** — the Fowler smell name and the quoted hunk (e.g. `Feature Envy: <hunk>`).
- **requirements-coverage** — the quoted spec line the finding maps to.

Rules:
- One finding per block — never combine unrelated issues.
- Emit findings only; do not post.
- Report only net-new, actionable findings grounded in code evidence (see `<skill-directory>/references/review-rules.md`).
- If an axis has nothing to report, return an empty list for that axis (Requirements-coverage may instead return "no spec available").
- Keep `FINDING` terse; the label and line rules match `<skill-directory>/references/comment-template.md`.
