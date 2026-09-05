---
name: to-zdesign
description: Create or incrementally extend an authoritative feature design from spec files, confirmed grill-design conversation context, Wayfinder maps or decision issues, and existing designs. Use for first-pass design synthesis, adding later specs, capturing a completed design conversation, or merging resolved GitHub decisions without losing existing content.
---

This skill takes the current conversation context and codebase understanding and produces or update one `docs/designs/{{featureSlug}}.md`. Synthesize the solution. Do not interview during synthesis. Put unresolved source conflicts in `Open Questions`.

## 1. Resolve inputs
Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the design, and respect any Architecture, concepts, ADRs in the area you're touching.

## 2. Ground and rank evidence
Treat existing content outside `Open Questions` as resolved unless marked draft, tentative, or assumed.

Let stronger evidence update weaker content. Preserve equal-authority conflicts and add them to `Open Questions`. NEVER remove or weaken sourced or existing resolved content without stronger explicit evidence.

**Provenance stays out of the body.** ADRs, Concepts, Architecture, and tickets are grounding evidence, not citable content — never name or link them anywhere in the document body (`Requirements`, `Current State`, `Solution Overview`, `Decisions`, appendices, etc.). Absorb what they establish as plain, self-contained statements instead of attributing it to the source document. The only place any of these four may be named or linked is a row in `Source Material`.

## 3. Reconcile capabilities

A capability is stable, solution-agnostic behavior with one purpose. It is not a UI, implementation detail, or one-off task.

Assign every sourced requirement to one capability. Match by purpose and change boundary, not title. Merge only when purpose, actors, rules, permissions, lifecycle, failures, contracts, ownership, and rate of change remain shared. Otherwise split.

Open [design-template.md](design-template.md) with the file-reading tool and draft `Requirements` from its exact table shape: one row per capability. Put the title, stakeholder requirement, and functional requirements in `Requirement`; put business rules and edge cases in `Details`. Use `Source` only for PO or Dev team.

Name capabilities with behavior and domain entities. Keep functional requirements externally visible and testable. Add design-discovered behavior only when evidence supports it.

## 4. Synthesize the solution

Open [design-template.md](design-template.md) with the file-reading tool — even if already read this session, do not paraphrase it from memory. Populate every core section in the exact order and heading text the template defines. Use `Not applicable — {{reason}}` when a core section does not apply. Omit only optional flow, sequence, and implementation appendix sections.

Keep `Solution Overview` at architecture level: responsibilities, interfaces, ownership, cross-boundary flows, failures, and testing implications.

`design-template.md` holds diagram placement and routing comments only. It does not own reusable Mermaid skeletons. `Solution Overview` diagrams are optional — omit all by default; add one only when the user explicitly asks for it. These are the only diagrams `Solution Overview` may hold; each is solution-level, not per-capability, and each is always the complete current diagram — never a delta:

| Diagram | Include for | Template |
| --- | --- | --- |
| Solution Diagram (`C4Container`) | Deployable/runnable containers and the actors/external systems around them | Follow `/to-diagram` skill **Solution Diagram** in current mode |
| Flow Diagram (`swimlane-beta`) | Solution-level process flow where container or component ownership is itself a design decision | Follow `/to-diagram` skill **Swimlane Diagram** in current mode |
| Sequence Diagram (`sequenceDiagram`) | High-level interaction between components, citizen classes, or IDesign-style classes (Manager, Engine, Accessor) — never method-level detail | Follow `/to-diagram` skill **Sequence Diagram** in current mode |

If merging into an existing design that already contains a diagram, NEVER modify, regenerate, or remove it silently. Stop and ask the user for confirmation before changing or removing any existing diagram.

Select implementation appendices from evidence. The two diagram appendices (Class Diagram, Sequence Diagram) are optional — include one only when the user explicitly asks for it, even if the triggering evidence is present. Never add a Flowchart appendix — a flowchart is `Solution Overview`-only. Before drafting any appendix, open its template file from the table below — do not compose an appendix from recollection of its shape:

| Appendix | Include for | Template |
| --- | --- | --- |
| REST API Delta | HTTP contract or behavior changes | Follow `/to-contract-delta` skill **API delta rules** — include a `Scenarios` subsection per endpoint per the template's rules |
| GUI Design Delta | User-visible state or interaction changes | Follow `/to-contract-delta` skill **GUI delta rules** — include a `Scenarios` subsection per surface per the template's rules |
| Database Schema Delta | Persistence contract changes | Follow `/to-contract-delta` skill **Database delta rules** |
| Class Diagram | User explicitly requests it, and evidence shows decided class responsibilities or relationships | Follow `/to-diagram` skill **Class Diagram** in delta mode |
| Sequence Diagram | User explicitly requests it, and evidence shows decided interaction order, cross-boundary calls, or failure branching, at implementation-level detail | Follow `/to-diagram` skill **Sequence Diagram** in delta mode |
| Deployment View Delta | Deployment topology, hosting, or infrastructure node changes for the feature | Follow `/to-diagram` skill **Deployment View** in delta mode |

Open and read only the templates for appendices that evidence triggers. Insert complete appendices in table order. Include changed content only. Follow `/to-contract-delta` skill for REST API Delta, GUI Design Delta, and Database Schema Delta; follow `/to-diagram` in delta mode for the Class Diagram, Sequence Diagram, and Deployment View content — this skill still owns capability/requirement/solution-overview prose composition and all diagram inclusion/placement decisions.

## 5. Merge incrementally

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

## 6. Verify before writing

1. Confirm every template file used in steps 3–4 was opened this run, not recalled from memory.
2. Map every source obligation to a capability, solution element, testing decision, and relevant diagram or appendix.
3. Populate every core section, in the template's section order, or mark it not applicable.
4. Keep at most the diagrams the user explicitly requested; do not add, change, or remove any diagram without asking first.
5. Include every evidence-triggered appendix and no empty appendix heading.
6. Remove template instructions and unresolved placeholders; keep Confluence markers verbatim (see Gotchas).
7. Put every unresolved conflict in `Open Questions`.
8. Compare an update with the pre-merge design. Restore unsupported loss.
9. Remove duplicate requirements, capabilities, and source rows.
10. Every included REST API Delta Scenario is backed by a delta bullet or requirement, with no invented scenarios, and its schema field names and enum values verified against the swagger/contract file.
11. Every included GUI Design Delta Scenario is backed by a delta row or requirement, with no invented scenarios, and its component/field names verified against the GUI source. A new Deployment View Delta appendix, if included, is evidence-backed like every other appendix.
12. Scan the full body (everything outside `Source Material`) for any ADR, Concept, ARCHITECTURE, or Jira reference (link, ID like `ADR NNNN`/`PROJ-NNNN`, or title mention) and rewrite each as a plain statement of what it establishes, with no attribution or link. This applies to legacy content in an existing design being merged, not only newly drafted text.

## Gotchas

- **`<!-- confluence:toc -->`, `<!-- confluence:wide-table -->`, and `<!-- confluence:ignore:start -->`/`<!-- confluence:ignore:end -->` are structural Confluence-importer syntax, not model placeholders** — never strip them while clearing template instructions.

Write the result. Call it a draft while `Open Questions` is non-empty.
