---
name: to-zdesign
description: Create or incrementally extend an authoritative feature design from spec files, confirmed grill-design conversation context, Wayfinder maps or decision issues, and existing designs. Use for first-pass design synthesis, adding later specs, capturing a completed design conversation, or merging resolved GitHub decisions without losing existing content.
---

# To ZDesign

Create or update one `docs/designs/{{featureSlug}}.md`. Do not interview during synthesis. Put unresolved source conflicts in `Open Questions`.

## 1. Resolve inputs

Accept these forms:

- `/to-zdesign {{sources}}`
- `/to-zdesign {{sources}} into {{designPath}}`
- `/to-zdesign` after a completed `/grill-design` session
- `/to-zdesign {{wayfinderIssue}}`

Normalize every source:

| Source | Canonical identifier | Read |
| --- | --- | --- |
| Repository file | Repo-relative path | File in full |
| GitHub issue | Canonical issue URL | `/manage-backlog` **Read ticket** |
| Grill conversation | `{{originatingCanonicalSource}}#grill-design`; else `grill-design:{{featureId}}`; else `grill-design:name:{{inputSlug}}` | Confirmed decisions and cleared assumptions only |
| Wayfinder map | Canonical map URL | Map, closed linked decision tickets, and their resolution comments |

For a repository file, resolve the real path inside the repository. Store its repo-relative path with `/` separators and filesystem casing. Collapse `.` and `..`. Reject paths outside the repository.

For a Wayfinder decision ticket, read its linked map. Use the final comment returned by **Read ticket** as the resolution; Wayfinder writes the answer last when closing. If no comment exists, use the map gist as context and add the missing resolution to `Open Questions`. If the final comment conflicts with the map gist, add the conflict to `Open Questions`.

For a map, run `/manage-backlog` **List sub-tickets**, then **Read ticket** for every closed child regardless of `wayfinder:*` label. Treat `wayfinder:grilling` and `wayfinder:prototype` resolutions as decisions. Treat `wayfinder:research` findings and `wayfinder:task` completion facts as factual constraints, not product decisions.

Do not read open child bodies. Add each open child to `Open Questions` as `{{canonicalIssueUrl}} — {{title}}`. On a later run, remove that entry when the issue closes and consume its resolution. Deduplicate by canonical URL. Do not add open children to `Source Material`.

Exclude unanswered questions, vetoed assumptions, rejected options, and superseded statements from conversation input. If no explicit source and no confirmed conversation outcome exist, stop without writing and request a source.

For a source-less grill conversation, derive `inputSlug` from its explicit feature ID or agreed feature name, in that order. If neither exists, stop without writing and request a target path or feature ID. A name-only grill identifier may create a new design but MUST NOT match an existing design; require an explicit target or feature ID to extend one.

## 2. Select the design

Select the target in order:

1. Use explicit `into {{designPath}}`.
2. Use exactly one design path linked by a source. If several are linked, stop.
3. Use exactly one design with a stable feature match. If several match, stop.
4. Infer a new `docs/designs/{{featureSlug}}.md` from the shared feature identity.

A stable match requires a shared feature ID, Wayfinder map, canonical source, or explicit backlink. NEVER match by title similarity alone.

For a new target, derive identity in order: explicit feature ID, Wayfinder destination, shared exact source identity, single-source identity. For a file, use its explicit feature ID, then first H1, then basename. For an issue, use its explicit feature ID, then map Destination, then issue title. For a source-less grill, use `inputSlug`. Convert the result to kebab-case. Do not strip or rewrite suffixes heuristically.

Before creating an inferred path, verify it does not exist. If it exists without a stable match, stop without writing and request an explicit path. Never merge because an inferred filename happens to exist.

Read the selected existing design in full. Do not redirect an explicit target.

## 3. Ground and rank evidence

Read `CONTEXT.md`, `ARCHITECTURE.md`, matching Concepts and ADRs, and source-named code. Derive current boundaries, contracts, ownership, failures, and test seams from code.

Treat repository documentation and code as constraints and current-state evidence, not product requirements.

Treat resolved research and task facts the same way. A spec cannot override a factual constraint; add a contradiction to `Open Questions`.

Apply authority in order:

1. Confirmed decisions in the current request or grill conversation.
2. Resolved Wayfinder decisions.
3. Resolved content in the existing design.
4. Specs.

Treat existing content outside `Open Questions` as resolved unless marked draft, tentative, or assumed.

Let stronger evidence update weaker content. Preserve equal-authority conflicts and add them to `Open Questions`. NEVER remove or weaken sourced or existing resolved content without stronger explicit evidence.

## 4. Reconcile capabilities

A capability is stable, solution-agnostic behavior with one purpose. It is not a UI, implementation detail, or one-off task.

Assign every sourced requirement to one capability. Match by purpose and change boundary, not title. Merge only when purpose, actors, rules, permissions, lifecycle, failures, contracts, ownership, and rate of change remain shared. Otherwise split.

Draft `Requirements` from [design-template.md](assets/design-template.md): one row per capability. Put the title, stakeholder requirement, and functional requirements in `Requirement`; put business rules and edge cases in `Details`. Use `Source` only for PO or Dev team.

Name capabilities with behavior and domain entities. Keep functional requirements externally visible and testable. Add design-discovered behavior only when evidence supports it.

## 5. Synthesize the solution

Read [design-template.md](assets/design-template.md). Populate every core section. Use `Not applicable — {{reason}}` when a core section does not apply. Omit only optional flow, sequence, and implementation appendix sections.

Keep `Solution Overview` at architecture level: responsibilities, interfaces, ownership, cross-boundary flows, failures, and testing implications.

`Solution Overview` diagrams are optional — omit all by default; add one only when the user explicitly asks for it. These are the only diagrams `Solution Overview` may hold; each is solution-level, not per-capability:

| Diagram | Include for | Template |
| --- | --- | --- |
| Solution Diagram (`C4Container`) | Deployable/runnable containers and the actors/external systems around them | [c4-container-diagram-template.md](assets/c4-container-diagram-template.md) |
| Flow Diagram (`flowchart`) | Solution-level process flow, decision path, or component wiring | [flowchart-delta-template.md](assets/flowchart-delta-template.md) |
| Sequence Diagram (`sequenceDiagram`) | High-level interaction between components, citizen classes, or IDesign-style classes (Manager, Engine, Accessor) — never method-level detail | Sequence Diagram section of [design-template.md](assets/design-template.md) |

If merging into an existing design that already contains a diagram, NEVER modify, regenerate, or remove it silently. Stop and ask the user for confirmation before changing or removing any existing diagram.

Select implementation appendices from evidence. The two diagram appendices (Class Diagram, Sequence Diagram) are optional — include one only when the user explicitly asks for it, even if the triggering evidence is present. Never add a Flowchart appendix — a flowchart is `Solution Overview`-only:

| Appendix | Include for | Template |
| --- | --- | --- |
| REST API Delta | HTTP contract or behavior changes | [rest-api-delta-template.md](assets/rest-api-delta-template.md) — include a `Scenarios` subsection per endpoint per the template's rules |
| GUI Design Delta | User-visible state or interaction changes | [gui-delta-template.md](assets/gui-delta-template.md) |
| Database Schema Delta | Persistence contract changes | [database-schema-delta-template.md](assets/database-schema-delta-template.md) |
| Class Diagram | User explicitly requests it, and evidence shows decided class responsibilities or relationships | [class-diagram-delta-template.md](assets/class-diagram-delta-template.md) |
| Sequence Diagram | User explicitly requests it, and evidence shows decided interaction order, cross-boundary calls, or failure branching, at implementation-level detail | [sequence-diagram-delta-template.md](assets/sequence-diagram-delta-template.md) |

Read only applicable templates. Insert complete appendices in table order. Include changed content only. Do not run `/to-delta`; this skill owns appendix composition.

## 6. Merge incrementally

For a new design, instantiate the template. For an existing design, merge section by section.

- Preserve untouched prose, diagrams, and appendices.
- Add non-conflicting obligations once.
- Update only content supported by stronger evidence.
- Update matching capability rows instead of duplicating them.
- NEVER regenerate an existing design wholesale.

Maintain `Source Material`:

- Use the canonical identifier in `Source`.
- Set `Kind` to `Spec`, `GitHub issue`, `Wayfinder map`, `Wayfinder decision`, `Wayfinder evidence`, or `Grill conversation`.
- Use `Wayfinder evidence` for research findings and task completion facts.
- Keep `Contribution` as a cumulative summary of still-valid consumed evidence.
- Update an existing canonical source row on re-run. Do not duplicate it.
- Add one row for each consumed Wayfinder map and closed child issue.
- Merge later grill sessions into the same canonical row. Preserve prior confirmed outcomes unless current equal-or-stronger evidence explicitly supersedes them. Remove superseded text; deduplicate retained text.
- Do not invent sources for legacy content.
- Keep the section wrapped in `<!-- confluence:ignore:start -->`/`<!-- confluence:ignore:end -->` — it is repo-internal provenance, not Confluence-reader content.

## 7. Verify before writing

1. Map every source obligation to a capability, solution element, testing decision, and relevant diagram or appendix.
2. Populate every core section or mark it not applicable.
3. Keep at most the diagrams the user explicitly requested; do not add, change, or remove any diagram without asking first. Never place a flowchart in an appendix — it belongs only in `Solution Overview`.
4. Include every evidence-triggered appendix and no empty appendix heading.
5. Remove template instructions and unresolved placeholders. Preserve `<!-- confluence:toc -->`, `<!-- confluence:wide-table -->`, and `<!-- confluence:ignore:start -->`/`<!-- confluence:ignore:end -->` verbatim — they are structural Confluence markers, not model placeholders.
6. Put every unresolved conflict in `Open Questions`.
7. Compare an update with the pre-merge design. Restore unsupported loss.
8. Remove duplicate requirements, capabilities, and source rows.
9. Every included REST API Delta Scenario is backed by a delta bullet or requirement, with no invented scenarios, and its schema field names and enum values verified against the swagger/contract file.

Write the result. Call it a draft while `Open Questions` is non-empty.
