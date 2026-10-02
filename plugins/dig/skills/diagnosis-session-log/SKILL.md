---
name: diagnosis-session-log
description: Own the shared hypothesis log for diagnosis runs — defaulting to repository root/tmp/{{bugSlug}}-diagnosis.md — and record only checked hypotheses with their verification, observed fact, evidence, and result.
---
# Track Diagnosis Hypotheses

The log is a compact evidence record shared by `diagnosing-root-cause` and `diagnosing-bugs`. It records **only checked hypotheses**. Do not use it as a phase journal, command transcript, artifact list, test log, or fix log.

## Location

`bugSlug :=` short kebab-case name of the symptom.

Default:
`logPath := repository root/tmp/{{bugSlug}}-diagnosis.md`.

A caller may supply another `logPath` when it owns a specialized workflow.

Runs for the same bug slug MUST reuse the same log. Independent bugs use independent log files.

## Open

If `$logPath` exists, read it before testing new hypotheses and continue numbering after the last `H` entry.

If it does not exist, create its parent folder and initialize it from `Session log template`.

## Write

Append an entry **only after a hypothesis was actually checked**, including a check that ended blocked.

Every entry MUST contain:

- **Hypothesis** — the falsifiable cause being checked.
- **Prediction** — what should be observed if it is true.
- **Verification** — exactly how it was checked.
- **Fact** — the actual observed fact, not an inference or intended result.
- **Evidence** — re-checkable evidence supporting the fact.
- **Result** — `confirmed`, `falsified`, or `blocked`.

Evidence MUST be one or more of:

- code evidence: `path:line`;
- probe evidence: command/request plus the actual redacted signal output;
- authoritative-source evidence: the checked statement plus its canonical URL.

When an authoritative source is used to verify the hypothesis, the URL MUST be present in the same hypothesis entry.

Do not write an `open` hypothesis. Do not write phase starts, loop attempts, setup, cleanup, fixes, tests, artifacts, plans, or next steps.

## Redact

Secrets MUST be represented by environment-variable names or `<REDACTED>`. Keep only output lines carrying the verification signal.

## Session log template

```markdown
# Diagnosis Hypotheses

<!-- @: checked hypotheses only; append after verification, never before -->

## H{{n}} — {{short hypothesis}}

- Hypothesis: {{falsifiable cause}}
- Prediction: {{observable result if true}}
- Verification: {{how it was checked}}
- Fact: {{actual observed fact}}
- Evidence: {{path:line | command/request → redacted signal | authoritative statement + canonical URL}}
- Result: {{confirmed | falsified | blocked}}
```