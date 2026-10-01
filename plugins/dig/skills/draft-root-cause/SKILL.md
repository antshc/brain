---
name: draft-root-cause
description: Render one cited root-cause summary from a confirmed diagnosis using the shared hypothesis log and current run evidence. Print it; do not save it.
argument-hint: "[bugSlug]"
---
# Draft Root Cause

Render and print one root-cause summary. Drafting is transcription: add no new facts and run no probes.

## Input

Default hypothesis log:
`repository root/docs/tmp/{{bugSlug}}/diagnosis.md`.

A caller may provide another log path.

Use:
- checked hypotheses from the log;
- current-run evidence for mechanism-chain facts not represented as hypotheses.

## Gate

At least one hypothesis MUST be `confirmed`.

If none is confirmed, stop and report that the root cause is not established.

## Map

Fill `templates/root-cause-summary.template.md`:

- **Summary of issue** — reported symptom and observed impact.
- **Root cause & mechanism** — confirmed hypothesis plus ordered mechanism chain.
- **Evidence** — deciding facts and their evidence.
- **Ruled out** — falsified hypotheses and their deciding evidence.
- **Known gap / tracking** — only when supported by current evidence.

Every mechanism claim MUST cite re-checkable evidence. Unsupported claims are omitted or marked `Unknown`.

If an authoritative source was used, preserve its canonical URL.

## Redact

Replace secrets with `<REDACTED>`. Quote only signal lines.

## Output

Print the rendered summary without wrapper prose.

MUST NOT save the rendered summary to a file.
