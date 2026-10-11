---
name: document-template
description: Documents architecture, ADR decisions, procedures, and reference behavior with purpose-fit structure, source-backed claims, and concise maintainable prose.
---

# Documentation Skill Template

## Inputs
- `{{audience|Reader and task}}`
- `{{sources|Code, decision, runtime evidence, or existing documentation}}`

## Workflow
1. Choose tutorial, how-to, reference, or explanation based on the reader's goal. *Done when* the document answers one main need.
2. Extract verifiable facts, assumptions, decisions, and alternatives from authoritative sources. *Done when* unsupported details are marked.
3. Render using `{{format|Selected document template}}` with working references and concise language. *Done when* a reader can locate all needed information.
4. Check technical accuracy, links, and preserved rationale. *Done when* the document matches current behavior and states uncertainties.

## Guardrails
- MUST NOT invent rationale, commands, or measurements.
- MUST NOT erase prior ADR decisions; supersede them with traceable new records.

## Completion criteria
- The document serves its stated reader, has verifiable claims, and preserves important context.

## Handoff
- `{{document|Path, purpose, sources, unresolved assumptions}}`
