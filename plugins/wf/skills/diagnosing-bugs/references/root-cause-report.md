# Draft Root Cause

Render and print one root-cause summary. Drafting is transcription: add no new facts and run no probes.

## Input

Resolve `logPath` per the [Hypothesis log](hypothesis-log.md), or use the log path a caller provides.

Use:
- checked hypotheses from the log;
- current-run evidence for mechanism-chain facts not represented as hypotheses;
- analysis inputs (images, log archives, logs, HAR, dumps) with what each contributed.

## Gate

At least one hypothesis MUST be `confirmed`.

If none is confirmed, stop and report that the root cause is not established.

## Map

Fill the Template:

- **Summary of issue** — setup, reported symptom vs actual behavior, current system behaviour per surface, assessment against design, and verdict.
- **Impact** — who and what is affected, how much, business consequence, and what is not affected.
- **Root cause & mechanism** — confirmed hypothesis plus ordered mechanism chain.
- **Evidence** — deciding facts and their evidence.
- **Ruled out** — falsified hypotheses and their deciding evidence.
- **Artifacts** — every analysis input artifact, including ones found not relevant.
- **Known gap / tracking** — only when supported by current evidence.
- **Prevention** — other instances of the same fault and a cheap always-on signal that would have shown the deciding fact; only when supported by current evidence.

Every mechanism claim MUST cite re-checkable evidence via its Evidence row id (`E1`, `E2`, …). Unsupported claims are omitted or marked `Unknown`.

If an authoritative source was used, preserve its canonical URL.

## Business language

**Summary of issue**, **Impact**, **Root cause & mechanism**, and **Why this fails:** MUST use business language: describe what the user or system does and sees, not how the code is built.

- **Allowed:** business terms; affected cloud resources (queue, bucket, table, function); public contracts (REST endpoint names, event names); page names; user-visible page elements (button, field, tab, message) and how the user reaches them.
- **MUST NOT:** class, method, or variable names; file paths or `path:line`; internal component, module, or service-class names.
- Code-level references belong only in Evidence, Ruled out, and Known gap / tracking.

## Writing style

- Short plain sentences, one fact each; present tense for system behavior; no hedging or filler.
- Open with the concrete setup, then what the user sees vs what the system does.
- Name pages, tabs, wizards, states, and fields exactly as the product shows them; bold them in bullets.
- Bold the deciding qualifier in a contrast (**no**, **some**, **only**).
- Put REST endpoints and contract names in backticks.
- Lead sub-blocks with a bold sentence label ending in `.` (`**Current system behaviour.**`, `**Assessment.**`), not extra headings.
- List per-surface rules or per-layer changes as bullets: `- **Surface:** behavior.`
- State timing and cadence as numbers (`every 5 minutes`).
- End Summary of issue with a one-line bold verdict: **regression**, **bug**, **works as designed**, or **feature request**.

## Template

```markdown
<!-- @: terse; every claim traces to checked hypotheses or current-run evidence; no placeholder left unresolved -->
# {{title|symptom + affected feature or page, one line, business language}}

## Summary of issue

{{2-5 sentences|setup, what was reported vs what actually happened; business language}}

**Current system behaviour.** {{one line|context of the rules below}}
- **{{surface|page, tab, or state}}:** {{when it shows what; bold deciding qualifier}}

<!-- @: Assessment states whether reported expectation matches design and, if not, what each layer would need -->
**Assessment.** {{1-2 sentences|design vs reported expectation}}
- **{{layer|Backend, Frontend, …}}:** {{needed change}}

This reads as a **{{verdict|regression, bug, works as designed, feature request}}**{{, not a …|optional contrast}}.

## Impact

{{2-3 sentences|affected users/roles/tenants, pages, REST endpoints, cloud resources; triggering conditions; volume (users, requests, records) and frequency; business consequence (wrong data, blocked action, financial, SLA/SLO breach); what is not affected; since when; unsupported facts `Unknown`; business language; cite Evidence row ids}}

## Root cause & mechanism

{{1-2 sentences|confirmed hypothesis and setup facts the mechanism depends on; business language}}

**Why this fails:**

<!-- @: one item per mechanism-chain link, cause first; business language; cite Evidence row ids -->
1. **{{label|short mechanism name}}:** {{one line}} ({{E1, E2}})

## Evidence

<details>
<summary>Evidence table</summary>

| Id | Check | Finding | Source / Reference |
|---|---|---|---|
| E1 | {{what was checked}} | {{actual observed fact}} | {{[name:line](path#Lline), `command` → signal, `archive!entryPath:line`, `image` + quoted text, or [title](canonicalUrl)}} |

</details>

## Ruled out

<!-- @: one line per falsified hypothesis; omit section if none -->
- **{{hypothesis}}** — {{observed fact that falsified it}} ({{evidence}})

## Artifacts

<!-- @: one row per analysis input artifact; omit section if none supplied -->
| Artifact | Type | Used for |
|---|---|---|
| {{name or path; archive entries as archive!entryPath}} | {{screenshot \| log archive \| log \| HAR \| dump \| recording}} | {{what it showed or proved; cite Evidence row ids; `not relevant` if unused}} |

## Known gap / tracking

<!-- @: omit section if unsupported -->
{{ticket id, TODO path:line, or upstream issue URL}}

## Prevention

<!-- @: omit section if unsupported -->
- **Same fault elsewhere:** {{path:line list or `none found`; cite Evidence row ids}}
- **Signal:** {{cheap always-on log, metric, assertion, or error message that would have shown the deciding fact}}
```

## Redact

Replace secrets with `<REDACTED>`. Quote only signal lines.

## Output

Print the rendered summary without wrapper prose.

MUST NOT save the rendered summary to a file.
