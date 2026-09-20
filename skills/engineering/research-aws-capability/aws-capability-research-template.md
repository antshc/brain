# AWS Capability Research: {{capabilityName}}

**Rules** — apply while filling this scaffold, then delete this block and every `**Rules:**` line from the result.

- Every claim carries a full AWS doc URL plus section heading, or a probe command with the observed response field.
- Quote the deciding sentence whenever it is short enough to settle the claim on sight.
- Docs prove the documented envelope; only a live call proves this account's envelope — record any mismatch as a finding.
- Nothing reaches the diagram, tables, or conclusion without a Fact or Limit behind it.

- Design intent: {{what the product wants AWS to do, in one line}}
- Question: {{the decision being settled — service, API action, and the exact case}}
- Scope: {{services, API actions, regions/partitions, instance families, OS/architectures, account model; what's explicitly out}}
- Status: investigating | answered

## Summary

**Rules:** 2-3 sentences answering the framed question. Lead with the edge that most constrains the design, not the confirmation that the happy path works.

{{summary}}

## Envelope

**Rules:** `flowchart` branching the design's inputs into the supported path, the fallback path, and each blocker. `sequenceDiagram` instead when the finding is about call order, propagation, or polling. Every node carries the doc URL or probe that established it.

```mermaid
flowchart TD
    {{inputs branching into supported / fallback / blocker outcomes, each node noting its source}}
```

## API contract

**Rules:** one row per parameter the design will actually send. `Allowed values` is the documented enumeration or range, not a paraphrase.

| API action | Parameter | Required | Allowed values | Default | Evidence |
|---|---|---|---|---|---|
| {{action}} | {{parameter}} | {{yes/no}} | {{values}} | {{default}} | {{url#section — `quoted line`}} |

## Facts

**Rules:** one row per confirmed claim. Prefer facts that contradict what the design assumed over facts that confirm it.

| # | Fact | Evidence |
|---|---|---|
| 1 | {{fact}} | {{url#section — `quoted line`}} |

## Limits

**Rules:** one row per edge of the envelope. `Hard` means no support ticket raises it. `Class` is exactly one of supported / fallback / blocker, and `Design impact` says what the code must do about it.

| # | Limit | Hard or adjustable | Class | Design impact | Evidence |
|---|---|---|---|---|---|

## Assumptions

**Rules:** plausible but unconfirmed. `What would verify it` is a concrete action — a doc page to read, a CLI command to run — not "investigate further".

| # | Assumption | Why unverified | What would verify it |
|---|---|---|---|

## Unknowns

**Rules:** `Next probe` names the exact doc query or CLI command.

| # | Unknown | Next probe |
|---|---|---|

## Conclusion

**Rules:** state the verdict — supported, supported with a named fallback, or blocked — and name the limit that decides it.

{{conclusion}}
