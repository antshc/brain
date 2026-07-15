---
name: 'to-review-finding'
description: 'Emit the shared PR-review finding schema as a single, actionable, ready-to-post finding. Invoked by review sub-agents and review skills.'
argument-hint: '<axis>'
---

# Review Finding

This skill owns the review finding: it emits the shared finding schema every review axis returns as a single, actionable finding whose `FINDING_BODY` is ready to post as a review comment. Uniform findings keep downstream deduplication and posting mechanical — do not invent per-axis shapes.

## Emit the finding

**Step 1 — Get the input**
`{{input}}` is the `<axis>` that produced the finding: one of `code-smells`, `quality-attributes`, `requirements-coverage`, or `hitl`. It fills the `AXIS:` field. Every other field (`FILE_PATH`, `LINE_NUMBER`, `LABEL`, `FINDING_BODY`) comes from the calling agent's or skill's analysis, with `FINDING_BODY` already formatted via the `/to-review-tone` skill.

**Step 2 — Emit**
Emit each finding as one block following the template structure in `<skill-directory>/references/finding-template.md`, writing using the **Field Rules**.

Rules:
- One finding per block — never combine unrelated issues.
- `FINDING_BODY` carries one finding: its label, the exact problem, the concrete impact, and the minimal change requested.
- `FILE_PATH` and `LINE_NUMBER` come from the diff so the finding links to the pull-request change.
- Emit findings only; do not post.
- If there is nothing to report, return an empty list (instead return "no findings").
