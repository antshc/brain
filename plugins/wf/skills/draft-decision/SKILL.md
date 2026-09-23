---
name: draft-decision
description: Draft a standalone architecture decision record (ADR) when explicitly requested. Decide whether to extend an existing ADR or create one, prepare its metadata and location, and call doc-decision to render the decision. Does not update ARCHITECTURE.md or run during grill-design.
---

# Draft Decision

Draft one point-in-time, localized architectural decision. Run only on an explicit request for an ADR or a standalone decision file. For a compact decision inside a design or decision list, call `/doc-decision` directly.

## ADR gate

Check whether the decision is hard to reverse, surprising without its context, and a real trade-off between viable alternatives. These are reasons to preserve an ADR rather than a local design decision. Architectural shape, integration patterns, technology lock-in, ownership boundaries, intentional deviations, and invisible constraints can qualify. If a criterion is missing, explain the narrower fit; honor an explicit request to draft the ADR anyway.

Shared domain, structural, or operational rules that future work must follow belong in `/record-concept`; contested terminology belongs in `/record-term`.

## Extend or create

Before writing, inspect existing ADRs in `docs/adr/` and any decision files the caller identifies. If one already owns the same decision area, extend that file and preserve its identity. Otherwise, create one standalone ADR. Do not invoke `/index-docs` or add an `ARCHITECTURE.md` row.

If writing into `docs/adr/`, create the directory lazily. Assign the next id from the highest four-digit filename prefix plus one (`0001` if empty). Name the file `docs/adr/{{nnnn}}-{{slug}}.md`.

## Draft and write

For an existing frontmatter-bearing ADR, retain its metadata and update only keys needed to describe the revised decision. For a new ADR, write:

```md
---
id: "{{nnnn}}"
title: {{decisionTitle}}
trigger: >-
  {{change types that make this decision relevant}}
summary: >-
  {{one-paragraph decision summary}}
default: >-
  {{choice to take when the design does not state one}}
owns: ["{{decision area}}"]
applies_to:
  - {{repo-relative path glob}}
related: ["{{related record id}}"]
---
```

`id` and `title` are required and match the filename and heading. Include `trigger`, `summary`, and `default` when known; omit optional keys rather than inventing values. Keep `owns` distinct from other known records. Use folded scalars for long text. Preserve existing cross-references when extending an ADR.

Call `/doc-decision` with **full** format and the established decision context. Explicitly request rationale and any meaningful rejected alternatives that the evidence supports; do not invent them. Write its output after the frontmatter. When the user requests text only, return the rendered draft without creating a file. Never update `ARCHITECTURE.md` as a side effect.
