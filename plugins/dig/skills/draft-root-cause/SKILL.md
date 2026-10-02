---
name: draft-root-cause
description: Render one cited root-cause summary from a confirmed diagnosis using the shared hypothesis log and current run evidence. Print it; do not save it.
argument-hint: "[bugSlug]"
---
# Draft Root Cause

Render and print one root-cause summary. Drafting is transcription: add no new facts and run no probes.

## Input

Resolve `logPath` per `diagnosis-session-log`'s Location section, or use the log path a caller provides.

Use:
- checked hypotheses from the log;
- current-run evidence for mechanism-chain facts not represented as hypotheses.

## Gate

At least one hypothesis MUST be `confirmed`.

If none is confirmed, stop and report that the root cause is not established.

## Map

Fill the Template:

- **Summary of issue** — reported symptom vs actual behavior.
- **Impact** — who and what is affected, how much, business consequence, and what is not affected.
- **Root cause & mechanism** — confirmed hypothesis plus ordered mechanism chain.
- **Evidence** — deciding facts and their evidence.
- **Ruled out** — falsified hypotheses and their deciding evidence.
- **Known gap / tracking** — only when supported by current evidence.

Every mechanism claim MUST cite re-checkable evidence via its Evidence row id (`E1`, `E2`, …). Unsupported claims are omitted or marked `Unknown`.

If an authoritative source was used, preserve its canonical URL.

## Business language

**Summary of issue**, **Impact**, **Root cause & mechanism**, and **Why this fails:** MUST use business language: describe what the user or system does and sees, not how the code is built.

- **Allowed:** business terms; affected cloud resources (queue, bucket, table, function); public contracts (REST endpoint names, event names); page names; user-visible page elements (button, field, tab, message) and how the user reaches them.
- **MUST NOT:** class, method, or variable names; file paths or `path:line`; internal component, module, or service-class names.
- Code-level references belong only in Evidence, Ruled out, and Known gap / tracking.

## Template

```markdown
<!-- @: terse; every claim traces to checked hypotheses or current-run evidence; no placeholder left unresolved -->
# {{title|symptom + affected feature or page, one line, business language}}

## Summary of issue

{{2-3 sentences|what was reported vs what actually happened; business language}}

## Impact

{{2-3 sentences|affected users/roles/tenants, pages, REST endpoints, cloud resources; triggering conditions; volume (users, requests, records) and frequency; business consequence (wrong data, blocked action, financial, SLA/SLO breach); what is not affected; since when; unsupported facts `Unknown`; business language; cite Evidence row ids}}

## Root cause & mechanism

{{1-2 sentences|confirmed hypothesis and setup facts the mechanism depends on; business language}}

**Why this fails:**

<!-- @: one item per mechanism-chain link, cause first; business language; cite Evidence row ids -->
1. **{{label|short mechanism name}}:** {{one line}} ({{E1, E2}})

## Evidence

| Id | Check | Finding | Source / Reference |
|---|---|---|---|
| E1 | {{what was checked}} | {{actual observed fact}} | {{[name:line](path#Lline) | `command` → signal | [title](canonicalUrl)}} |

## Ruled out

<!-- @: one line per falsified hypothesis; omit section if none -->
- **{{hypothesis}}** — {{observed fact that falsified it}} ({{evidence}})

## Known gap / tracking

<!-- @: omit section if unsupported -->
{{ticket id, TODO path:line, or upstream issue URL}}
```

## Redact

Replace secrets with `<REDACTED>`. Quote only signal lines.

## Output

Print the rendered summary without wrapper prose.

MUST NOT save the rendered summary to a file.
