---
name: to-zdesign
description: Synthesize Wayfinder decisions and one or more specs into an authoritative feature design, or merge stronger evidence into an existing design without losing resolved content.
argument-hint: "{{sourceReference}} [{{sourceReference}} ...]"
disable-model-invocation: true
---

# To ZDesign

Create or update `docs/designs/{{featureSlug}}.md` from one or more source references. Do not interview the user during generation; produce a coherent draft and put unresolved decisions in `Open Questions`.

Copy this checklist and check off items as you complete them:

```markdown
To ZDesign Progress:
- [ ] 1. Resolve sources and identity
- [ ] 2. Ground the design
- [ ] 3. Reconcile capabilities
- [ ] 4. Synthesize the solution
- [ ] 5. Merge and write
- [ ] 6. Run the completeness sweep
```

## 1. Resolve sources and identity

Require at least one source reference. A source may be a Wayfinder map or decision ticket, a spec ticket, or a repository file. For ticket references, Run `/manage-backlog`'s skill **Read ticket**, then read every linked resolution needed to understand the feature; read repository files directly.

Infer `featureName` from the sources' shared destination or title and derive one stable kebab-case `featureSlug`. Conflicting identities go to `Open Questions`; choose the narrowest title supported by every source rather than asking the user.

## 2. Ground the design

Read `CONTEXT.md`, `ARCHITECTURE.md`, and the code areas named by the sources. Use glossary terms, obey matching Concepts and ADRs, and derive current boundaries, contracts, data ownership, failure behavior, and testing seams from code rather than guessing.

If `docs/designs/{{featureSlug}}.md` exists, read it in full and treat it as an input. Authority, strongest first: explicit decisions in the current request; resolved Wayfinder decisions; resolved content in the existing design; specs. A stronger source may update weaker content. Otherwise preserve existing human-authored and resolved content.

## 3. Reconcile capabilities

Draft `Requirements` as the numbered table in [design-template.md](templates/design-template.md): each top-level row is one capability and its `N.x` rows are functional requirements. The row numbers express document hierarchy, not capability IDs; use `Source` for the PO / Dev team category, not source provenance.

Match a capability by semantic purpose and independent change boundary, never by title alone. Merge requirements when one purpose statement covers both and their actors, rules, permissions, lifecycle, failures, contracts, ownership, and rate of change do not diverge. Otherwise add or split the capability.

Design discoveries may add behavior or clarify an existing requirement. Never silently remove or weaken sourced behavior without an explicit current-request or resolved Wayfinder decision. Preserve incompatible statements and add the conflict to `Open Questions`.

Keep capability titles and requirements solution-agnostic: name behavior and domain entities, not screens, controls, endpoints, classes, services, or storage. Every functional requirement is externally visible and testable; keep invariants under `Business Rules` and boundary handling under `Edge Cases`.

## 4. Synthesize the solution

Read [design-template.md](templates/design-template.md) and populate every core section. Write `Not applicable — {{reason}}` when a core section does not apply; omit only optional flow, sequence, and implementation appendix sections.

Keep `Solution Overview` at architecture level: components or modules, responsibilities, interfaces, data ownership, cross-boundary flows, failure handling, and testing implications. Always include one solution-level Mermaid `flowchart`; add flow or sequence diagrams only for materially distinct actors or decision paths.

Keep code-level detail in `Detailed Design: Implementation Appendix`. Select appendices from source evidence:

| Appendix | Include when | Template |
| --- | --- | --- |
| REST API Delta | HTTP methods, paths, headers, query parameters, request or response fields, statuses, validation, or behavior change. | [rest-api-delta-template.md](templates/rest-api-delta-template.md) |
| GUI Design Delta | User experiences, controls, visible states, permissions, validation, loading, empty, error, or interaction behavior change. | [gui-delta-template.md](templates/gui-delta-template.md) |
| Database Schema Delta | Persisted fields, types, nullability, defaults, keys, indexes, constraints, or relationships change. | [database-schema-delta-template.md](templates/database-schema-delta-template.md) |
| Class Diagram | Class responsibilities or relationships are design decisions. | [class-diagram-template.md](templates/class-diagram-template.md) |

Read only each applicable template, instantiate it from grounded evidence, and place the complete sections in `implementationAppendices` in table order. Omit an inapplicable appendix entirely. Reuse the delta semantics established by `/to-delta`, but do not run it; this skill owns appendix composition.

## 5. Merge and write

For a new design, instantiate the template at `docs/designs/{{featureSlug}}.md`. For an existing design, merge section by section: preserve untouched prose and diagrams, update only content supported by stronger evidence, union non-conflicting additions, and remove content only when the strongest source explicitly supersedes it.

Merge each existing implementation appendix under the same authority ordering. Preserve unsupported existing appendix content, update only lines supported by stronger evidence, and add new applicable appendices in the fixed order without regenerating existing appendices wholesale.

Never regenerate an existing design wholesale. Keep unresolved contradictions visible in `Open Questions` and write the useful remainder of the draft without pausing for answers.

## 6. Run the completeness sweep

Before completion:

1. Map every source obligation to one capability, solution element, testing decision, and relevant diagram or appendix.
2. Verify every core template section is populated or says `Not applicable — {{reason}}`.
3. Verify exactly one solution-level Mermaid `flowchart` exists and every additional diagram represents a materially distinct flow or decision; an appendix `classDiagram` does not replace the solution-level diagram.
4. Verify every selected appendix has triggering evidence, every persistence change maps to a Database Schema Delta, and no omitted appendix leaves an empty heading.
5. Verify every instantiated appendix contains only changed content and has no hidden instruction or unresolved placeholder.
6. Verify every unresolved conflict appears in `Open Questions` and no sourced behavior was silently weakened or removed.
7. Compare an updated design with its pre-merge content and restore any unsupported loss.
8. Fix every uncovered obligation before reporting completion; while `Open Questions` is non-empty, describe the artifact as a draft, never final.
