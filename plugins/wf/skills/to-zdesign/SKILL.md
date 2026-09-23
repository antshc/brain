---
name: to-zdesign
description: Create or incrementally extend an authoritative feature design from spec files, confirmed grill-design conversation context, Wayfinder maps or decision issues, and existing designs. Use for first-pass design synthesis, adding later specs, capturing a completed design conversation, or merging resolved GitHub decisions without losing existing content.
disable-model-invocation: true
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

Open [design-template.md](design-template.md) with the file-reading tool and draft `Requirements` from its exact table shape: one row per capability. Put the title, stakeholder requirement, and italicized functional sub-requirements in `Requirement`. Leave stakeholder requirement `Details` empty. Only functional sub-requirements have `Details`; render their business rules and edge cases as separate unlabeled bullets. Use `Source` only for PO or Dev team.

Name capabilities with behavior and domain entities. Keep functional requirements externally visible and testable. Add design-discovered behavior only when evidence supports it.

## 4. Synthesize the solution

Open [design-template.md](design-template.md) with the file-reading tool — even if already read this session, do not paraphrase it from memory. Populate every core section in the exact order and heading text the template defines. Use `Not applicable — {{reason}}` when a core section does not apply. Omit the Building Block View only when its inclusion rule does not apply; omit implementation appendices that evidence does not trigger. `Current State` is the one exception to the `Not applicable` rule: remove it entirely unless the user explicitly asked for it.

Populate `Use cases` with one bold-titled bullet per place the user interacts with the feature (install, create, upgrade, undo, and similar).

Keep `Solution Overview` at architecture level: responsibilities, interfaces, ownership, cross-boundary flows, failures, and testing implications.

`design-template.md` holds diagram placement and routing comments only. It does not own reusable Mermaid skeletons.

The reader-facing architecture-representation section is arc42's Building Block View. Include it when the solution spans multiple components and teams across the organization; otherwise include it only when the user explicitly requests it. Every included representation is a complete current view, never a delta. Follow `/doc-architecture-diagram` skill in current mode. Select exactly one representation per section and use its concrete name — `System Context Diagram`, `Container Diagram`, or `Component Diagram` — as both the H2 and `<summary>` text. Repeat the complete section for another coordinated representation when needed. Never emit the template's slash-separated title options.

| Representation | Include for |
| --- | --- |
| System Context (`C4Context`) | Landscape, scope, actors, and external systems when the system boundary needs orientation |
| Container Diagram (`C4Container`) | Deployable/runnable building blocks and their responsibilities |
| Component Diagram (`C4Component`) | Optional decomposition of one selected deployable when its internal architectural responsibilities matter |

Beneath each architecture representation, describe every shown building block's responsibility in a bullet with the building block name in bold.

A **functional slice** is an end-to-end implementation of a distinct system behavior or outcome. Its boundaries follow functional responsibility rather than technical layers. It belongs to one deployable; a cross-deployable flow connects functional slices through their contracts. Its test seams are the observable inputs and outputs where the slice can be tested independently.

A design has one or many functional slices. Synthesize each slice as the template's complete repeatable H2 block: an unprefixed behavior title, a `<details>` wrapper containing exactly one current-mode behavior diagram, then `**Decisions**` with bold decision names and their context/rationale. Follow `/doc-behavior-diagram` skill **Flowchart** or **Swimlane Diagram** when process or responsibility ownership is primary; follow `/doc-behavior-diagram` skill **Sequence Diagram** when temporal interaction is primary. Keep method-level behavior in `Detailed Design: Implementation Appendix`.

When merging into an existing design, preserve every architecture or functional-slice diagram unless the user confirms its modification, regeneration, or removal.

Select implementation artifacts from evidence and wrap each independently reviewable artifact in one complete generic block from `design-template.md`. Give every block a unique title that identifies its artifact and purpose, a concise evidence summary, an optional artifact link, and artifact-specific content. Remove all child blocks when no artifacts apply.

Include supported artifacts in this deterministic type order: GUI mockups, screenshots, and other visuals; API, GUI, database, resource, and other contract deltas; low-level diagrams; prototype findings; research summaries. Preserve source order within a type unless the existing design has a stable order.

Consume supplied GUI assets and existing research and prototype outputs only. Do not generate a missing mockup or run research or a prototype during synthesis. Put genuinely required missing implementation evidence in `Open Questions`.

- **GUI/visual:** Embed a supplied repository image with useful alt text and a repository-relative path; link a supplied non-image or external visual artifact. Summarize the implementation decision or state the visual establishes. Keep visual evidence separate from the GUI contract delta.
- **Contract:** Follow `/doc-contracts` skill **Assemble and write a contract delta** for each triggered API, database, resource, or other contract kind. Follow `/doc-contracts` skill **Assemble and write a GUI delta** for each triggered GUI contract. Put the complete authoritative output inside its artifact block.
- **Low-level diagram:** Include a Class Diagram or implementation-level Sequence Diagram only when the user explicitly requests it and evidence supports it. Include a Deployment View Delta when evidence shows deployment topology, hosting, or infrastructure node changes. Follow `/doc-code-diagram` skill **Class Diagram** in delta mode for a Class Diagram. Follow `/doc-behavior-diagram` skill **Sequence Diagram** in delta mode for an implementation-level Sequence Diagram. Follow `/doc-architecture-diagram` skill **Deployment View** in delta mode for a Deployment View Delta. Put the complete Mermaid output inside its artifact block. Keep Flowcharts in `Solution Overview` only.
- **Prototype:** State the technical question, observed facts, and resulting decision; link the throwaway branch or durable prototype result; include only the smallest decision-bearing code or configuration snippet. Present the snippet as prototype evidence, never production code.
- **Research:** State terse findings and implementation consequences, then link exactly once to the durable research Markdown artifact. Keep primary-source links in that artifact, not the design body.

GUI assets, prototype result links, and the single research artifact link are implementation evidence or deliverables, not attribution links. The body ban on ADR, Concept, Architecture, and ticket names and links still applies.

Populate every `Checklists` subsection. Per the template's own row rule, keep only the applicable/not-applicable value and fill `Details` when relevant; remove a whole subsection only when its entire category is not applicable, and note that in `Details`.

## 5. Merge incrementally

For a new design, instantiate the template. For an existing design, merge section by section.

- Preserve untouched prose, diagrams, and appendices.
- Preserve existing functional-slice boundaries and diagrams unless confirmed changes require an update.
- Preserve existing artifact blocks; update a block matching the same artifact and purpose instead of duplicating it, and remove or supersede one only when stronger evidence supports the change.
- Add non-conflicting obligations once.
- Update only content supported by stronger evidence.
- Update matching capability rows instead of duplicating them.
- NEVER regenerate an existing design wholesale.

Maintain `Source Material`:

- Use the canonical identifier in `Source`.
- Set `Kind` to `Spec`, `GitHub issue`, `Wayfinder map`, `Wayfinder decision`, `Wayfinder evidence`, or `Grill conversation`.
- Record every consumed research or prototype source. Use `Wayfinder evidence` only when the source is Wayfinder evidence; otherwise select the existing source kind that matches its provenance.
- Keep `Contribution` as a cumulative summary of still-valid consumed evidence.
- Update an existing canonical source row on re-run. Do not duplicate it.
- Add one row for each consumed Wayfinder map and closed child issue.
- Merge later grill sessions into the same canonical row. Preserve prior confirmed outcomes unless current equal-or-stronger evidence explicitly supersedes them. Remove superseded text; deduplicate retained text.
- Do not invent sources for legacy content.
- Keep the section wrapped in `<!-- adf:ignore:start -->`/`<!-- adf:ignore:end -->` — it is repo-internal provenance, not Confluence-reader content.

## 6. Verify before writing

1. Confirm every template file used in steps 3–4 was opened this run, not recalled from memory.
2. Map every source obligation to a capability, solution element, testing decision, and relevant diagram or appendix.
3. Populate every core section, in the template's section order, or mark it not applicable. `Current State` is removed entirely, never marked not applicable, unless the user asked for it. `Use cases` has one bold-titled bullet per interaction point.
4. Include the arc42 Building Block View when the solution spans multiple components and teams across the organization; otherwise include it only on explicit request. Give each representation its own section whose H2 and `<summary>` use the same concrete representation name; emit no slash-separated title options. Preserve every existing architecture diagram unless the user confirmed a change.
5. Give every functional slice exactly one current-mode flow, swimlane, or sequence diagram inside its `<details>` wrapper, followed by `**Decisions**` and one or more bold decision names with context/rationale. Use titles without `Flow Diagram:` or `Sequence Diagram:` prefixes, and emit no shared top-level `Decisions` section.
6. Give every implementation artifact its own generic block with a unique title and purpose, concise evidence summary, optional valid artifact link, and applicable artifact-specific content; emit no empty block or child heading when no artifacts apply.
7. Remove template instructions and unresolved placeholders; keep Confluence markers verbatim (see Gotchas).
8. Put every unresolved conflict in `Open Questions`.
9. Compare an update with the pre-merge design. Restore unsupported loss.
10. Remove duplicate requirements, capabilities, and source rows.
11. Order artifact blocks by GUI/visual, contract delta, low-level diagram, prototype, then research; preserve source order within each type unless the existing design has a stable order. Remove duplicates and restore any unsupported artifact loss from the pre-merge design.
12. Resolve every embedded image path and artifact link. Use useful image alt text and repository-relative paths for repository images.
13. Keep prototype snippets minimal and decision-bearing. Give every research block exactly one durable research-artifact link and no copied primary-source link. Exclude Class Diagrams and implementation-level Sequence Diagrams unless explicitly requested, and require evidence for every Deployment View Delta.
14. Every included API contract Scenario is backed by a delta bullet or requirement, with no invented scenarios, and its schema field names and enum values verified against the swagger/contract file.
15. Every included GUI contract Scenario is backed by a delta row or requirement, with no invented scenarios, and its component/field names verified against the GUI source.
16. Scan the full body (everything outside `Source Material`) for any ADR, Concept, ARCHITECTURE, or Jira reference (link, ID like `ADR NNNN`/`PROJ-NNNN`, or title mention) and rewrite each as a plain statement of what it establishes, with no attribution or link. This applies to legacy content in an existing design being merged, not only newly drafted text.
17. In `Checklists`, confirm every subsection is present unless its whole category is not applicable (noted in `Details`), and every row keeps only one applicable/not-applicable value.

## Gotchas

- **`<!-- adf:toc -->`, `<!-- adf:wide-table -->`, and `<!-- adf:ignore:start -->`/`<!-- adf:ignore:end -->` are structural Confluence-importer syntax, not model placeholders** — never strip them while clearing template instructions.

Write the result. Call it a draft while `Open Questions` is non-empty.
