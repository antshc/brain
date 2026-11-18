# High-level design (HLD)

## Contents

- Purpose
- Evolving draft
- Vocabulary
- Inputs
- Required resources
- Workflow
- Ground and rank evidence
- Reconcile capabilities
- Synthesize the solution
- Update behavior
- Completion criteria
- Gotchas
- Output

## Purpose

Use supplied decisions, evidence and codebase context to create or update one `docs/ongoing/{{initiativeSlug}}.md`. Do not interview during synthesis. Return unresolved source conflicts to Wayfinder for precise topic/proposal ownership or coarse Not yet specified classification, with the exact blocker/next action; standalone returns discovery gaps inline without creating a map. HLD Open Questions are user-owned presentation content: leave empty on creation and preserve existing user entries verbatim. On a requested legacy update, move the canonical HLD into `docs/ongoing/` and repair active links; preserve history and avoid duplicate authoritative copies. Do not bulk-migrate unrelated designs.

## Evolving draft

Wayfinder may supply `@evolvingDraft=true` with its exact document worktree/path. Read HLD updates registered in the router. Keep core headings/order and explicitly mark missing evidence/decisions Pending, including required diagrams/deltas not yet supportable; never fabricate them or mark unknown content not applicable. Return a draft with named gaps for the caller's commit; this does not establish readiness. All normal checks apply as evidence arrives and before declaring ready. Synthesis consumes results; Wayfinder owns evidence dispatch for its HLD. The caller supplies material-risk verification outcomes before final synthesis; direct authoring returns missing verification as a gap.

Apply HLD updates reconciliation to supported design consequences and internal provenance, preserving source ranks and diagram approvals. Exclude user presentation questions; return blocked updates as named gaps. Outside this mode, use ordinary HLD authoring.

## Vocabulary

- An **Initiative slug** is the Initiative's stable, filesystem-safe kebab-case identifier.
- A **Requirement set** groups one Stakeholder requirement with its Functional requirements, Business rules, Edge cases, and Acceptance criteria.
- A **Spec** packages one or more Requirement sets for planning and handoff.
- A **High-level design (HLD)** is the authoritative solution design for one Initiative and may cover multiple Capabilities, Features, and Functional slices.
- A **Functional slice** is an end-to-end implementation of one distinct behavior or outcome, bounded by functional responsibility, owned by one Deployable, and independently testable through observable inputs and outputs. Cross-deployable flows connect Functional slices through their contracts.

## Inputs

Use supplied current-state context, specs, resolved decisions, verified risks, integrated evidence, existing HLD, glossary and architecture records. Honor an exact output path/worktree; otherwise use `docs/ongoing/{{initiativeSlug}}.md`. Missing evidence or unresolved choices return to the caller.

## Required resources

Read the router's HLD template, Decision bullets, HLD updates and local requirements resources. For `normalize`, preserve the supplied structure and return after Requirements rules.

## Workflow

Follow Ground and rank evidence, Reconcile capabilities, Synthesize the solution, Update behavior, then Completion criteria. Done when the document is complete or precise draft gaps are returned.

## Ground and rank evidence

Treat existing content outside `Open Questions` as resolved unless marked draft, tentative, or assumed.

Let stronger evidence update weaker content. Preserve equal-authority conflicts and return them to the owning topic/proposal, coarse root fog or standalone caller without inventing a design decision. NEVER remove or weaken sourced or existing resolved content without stronger explicit evidence.

**Provenance stays out of the body.** Name/link ADRs, Concepts, Architecture and issues only in `Source Material` rows. Throughout the body, including appendices, restate their facts as plain, self-contained statements without attribution.

## Reconcile capabilities

Assign every sourced Requirement set to one Capability. Match by purpose and change boundary, not title. Merge only when purpose, actors, rules, permissions, lifecycle, failures, contracts, ownership, and rate of change remain shared. Otherwise split.

Open the design template listed in the router with the file-reading tool and draft `Requirements` from its exact table shape: one top-level row per Stakeholder requirement and one numbered sub-row per Functional requirement. Put the requirement text in `Requirement`; italicize Functional requirements. Leave Stakeholder requirement `Details` empty. Only Functional requirements have `Details`; render their Business rules and Edge cases as separate unlabeled bullets. Use `Source` only for PO or Dev team. Capability is the classification used during reconciliation, not a table row or label.

Apply requirements rules to authored capabilities and behavioral requirements; preserve protected source text. Add design-discovered behavior only when supplied evidence supports it.

## Synthesize the solution

Open the design template listed in the router with the file-reading tool — even if already read this session, do not paraphrase it from memory. Populate every core section in the exact order and heading text the template defines. Use `Not applicable — {{reason}}` when a core section does not apply. Omit the Building Block View only when its inclusion rule does not apply; omit Detailed Design artifact blocks that evidence does not trigger; exclude Research and Prototypes/Code Sketches appendices. `Current State` is the one exception to the `Not applicable` rule: remove it entirely unless the user explicitly asked for it.

Populate `Use cases` with one bold-titled bullet per actor goal within a Feature. A Feature may have multiple Use cases; an interaction point alone does not define one.

Keep `Solution Overview` at architecture level: responsibilities, interfaces, ownership, cross-boundary flows, failures, and testing implications.

`hld-template.md` owns diagram placement/routing comments, not reusable Mermaid skeletons.

The reader-facing architecture-representation section is arc42's Building Block View, within `Solution Overview`, inside a titled expand without a separate H2. Include it when the solution spans multiple components and teams across the organization; otherwise include it only when the user explicitly requests it. *Load and follow the `doc-diagram` skill to create Mermaid architecture diagrams to show system structure in a current Mermaid C4 Container Diagram* of deployable building blocks.

Beneath the representation, describe every shown building block's responsibility in a bullet with the building block name in bold.

Include the optional bold `Cross Deployable Flow` section only when a flow crosses multiple deployables. *Load and follow the `doc-diagram` skill to create a Mermaid swimlane diagram to show responsibility handoffs in a Mermaid swimlane diagram* across deployables, one lane per deployable, 1-5 major steps per lane.

A design has one or many functional slices. Synthesize each slice as the template's complete repeatable H2 block: an unprefixed behavior title, exactly one current-mode behavior diagram, then `**Decisions**`. *Load and follow the `doc-diagram` skill to show call order in a current Mermaid Sequence Diagram* of the slice. MUST load the router’s decision-bullet reference with the file-reading tool before rendering the slice's architectural decisions; append one compact bullet per decision under `**Decisions**`. Keep method-level behavior in `Detailed Design`.

When merging into an existing design, preserve every architecture or functional-slice diagram unless the user confirms its modification, regeneration, or removal.

Select implementation artifacts from evidence and wrap each independently reviewable artifact in one complete generic block from `hld-template.md`. Give every block a unique title that identifies its artifact and purpose, a concise evidence summary, an optional artifact link, and artifact-specific content. Remove all child blocks when no artifacts apply.

**Contracts gate.** Before selecting artifacts, list every contract kind the Initiative touches: API, Database, Resource, other, GUI, each with its resources or surfaces. Seed the list from a supplied design rationale's **Contracts touched** when present, then check requirements, functional slices, and the codebase for more. Every listed kind gets a contract artifact block from the **Contract** rule below; **MUST NOT** hand-write a delta. *Done when* each listed kind has a block opening with a `Legend:` line and one `#### header` + `<details>` per resource or surface; empty list → no contract artifact blocks.

Include supported artifacts in this deterministic type order: GUI mockups, screenshots, and other visuals; API, GUI, database, resource, and other contract deltas; low-level diagrams; prototype findings; research summaries. Preserve source order within a type unless the existing design has a stable order.

Consume supplied GUI assets and existing research and prototype outputs only. Do not generate a missing mockup or run research or a prototype during synthesis. Return genuinely required missing evidence to Wayfinder for precise owner/coarse fog classification or to the standalone caller. Consume caller-supplied material-risk verification outcomes; keep actual method/result and residual uncertainty on the owning issue/root, never user Open Questions. Missing verification blocks readiness and returns to the caller.

- **GUI/visual:** Embed a supplied repository image with useful alt text and a repository-relative path; link a supplied non-image or external visual artifact. Summarize the implementation decision or state the visual establishes. Keep visual evidence separate from the GUI contract delta.
- **Contract:** *Load and follow the `doc-contracts` skill to write an API, database, or resource contract delta* using **Assemble and write a contract delta** for each API, database, resource, or other contract kind the Contracts gate listed. *Load and follow the `doc-contracts` skill to write a GUI contract delta* using **Assemble and write a GUI delta** for each GUI surface the Contracts gate listed. Put the complete authoritative output inside its artifact block.
- **Low-level diagram:** Include a Class Diagram or implementation-level Sequence Diagram only when the user explicitly requests it and evidence supports it. Include a Deployment View Delta when evidence shows deployment topology, hosting, or infrastructure node changes. *Load and follow the `doc-diagram` skill to create the requested Mermaid Class Diagram, Sequence Diagram, or C4 Deployment View* in delta mode. Put the complete Mermaid output inside its artifact block. Keep Flowcharts in `Solution Overview` only.
- **Prototype:** State only supported observations and design consequences. Keep proof reports, logs, patches and sketch packages local, indexed on root/child issues; do not reproduce them in an appendix or disguised artifact inventory.
- **Research:** State terse supported findings and implementation consequences; no report appendix, local report link or copied full report. Root/child issues and ignored Source Material retain provenance.

Treat GUI assets and selected contract/diagram descriptions as design content. Keep research/proof/sketch inventories and local links only in issue metadata or ignored Source Material; apply Ground and rank evidence provenance rules.

Populate every `Checklists` subsection. Per the template's own row rule, keep only the applicable/not-applicable value and fill `Details` when relevant; remove a whole subsection only when its entire category is not applicable, and note that in `Details`.

## Update behavior

Apply HLD updates registered in the router. Compare the existing design and incoming evidence, map every changed obligation to affected sections, then merge in place. Done when every obligation is supported in the document or returned as an owned gap; unchanged input creates no duplicate rows, slices, artifact blocks or sources.

## Completion criteria

1. Confirm every required template was opened this run, not recalled from memory.
2. Map every source obligation to a capability, solution element, testing decision, and relevant diagram or internal evidence source.
3. Verify core sections, `Current State` inclusion and `Use cases` against Synthesize the solution.
4. Verify Building Block View inclusion/placement and existing-diagram approvals against Synthesize the solution.
5. Verify each slice's complete diagram/`**Decisions**` block against Synthesize the solution. Render one or more bullets from the loaded decision-bullet reference; omit `Flow Diagram:`/`Sequence Diagram:` title prefixes and shared top-level `Decisions`.
6. Verify each implementation artifact's complete generic block against Synthesize the solution; no empty block or child heading.
7. Remove template instructions and unresolved placeholders; keep Confluence markers verbatim (see Gotchas).
8. Account for every material risk through caller-supplied verification on the owning issue/root or standalone return: mitigation, actual method/result, reproduction, residual scope/blocker, next action. Planned checks are not proof. Preserve user Open Questions verbatim, including blank answers; no agent risk/unknown rows.
9. Compare an update with the pre-merge design. Restore unsupported loss.
10. Remove duplicate Requirement sets, requirements, and source rows.
11. Verify artifact ordering against Synthesize the solution; remove duplicates and restore unsupported pre-merge artifact loss.
12. Resolve every image path/artifact link; verify repository image paths and alt text against GUI/visual.
13. Verify reader-facing evidence exclusions, provenance placement and low-level diagram gates against Synthesize the solution.
14. Verify contract artifact blocks against Contracts gate, plus delta prefixes `+`, `-`, `%`, `~`. Missing or hand-written → re-run Contracts gate before writing.
15. Every included API contract Scenario is backed by a delta bullet or requirement, with no invented scenarios, and its schema field names and enum values verified against the swagger/contract file.
16. Every included GUI contract Scenario is backed by a delta row or requirement, with no invented scenarios, and its component/field names verified against the GUI source.
17. Scan the full body (everything outside `Source Material`) for any ADR, Concept, ARCHITECTURE, or Jira reference (link, ID like `PROJ-NNNN`, or title mention) and rewrite each as a plain statement of what it establishes, with no attribution or link. This applies to legacy content in an existing design being merged, not only newly drafted text.
18. Verify every `Checklists` subsection, row value and `Details` against Synthesize the solution.
19. Verify every design-delta obligation against the coverage map and written design. Every affected existing section is extended, every distinct new behavior has a complete functional-slice H2 block, and every triggered independently reviewable artifact has its own `Detailed Design` H2 block.
20. Mentally reapply inputs; remove rerun duplicates of requirement rows, slices, artifacts and sources. Result must remain unchanged.

## Gotchas

- **`<!-- adf:toc -->`, `<!-- adf:wide-table -->`, and `<!-- adf:ignore:start -->`/`<!-- adf:ignore:end -->` are structural Confluence-importer syntax, not model placeholders** — never strip them while clearing template instructions.
- Every touched kind requires a `doc-contracts` result even when the delta is small, additive, or already settled in a spec or design rationale; a spec's Contracts Delta is evidence, not a substitute.
- GUI changes (dialogs, pages, visible fields) are a contract kind; a new field shown in the UI usually means both an API and a GUI delta.

Wrap Requirements and every Mermaid fence in a meaningful expand; reuse an existing enclosing artifact expand instead of nesting redundantly. Preserve existing diagram content and approval gates. Reports and retained sketches remain local, indexed on root/child issues, never HLD appendices or Confluence subpages/attachments. Source Material remains publication-excluded.

## Output

Write the result at the authorized path, or return the body when saving is not authorized. Return changed sections, source conflicts and missing evidence separately. Call it a draft while root design obligations are unresolved/partial/conflicting, core content is pending or readiness checks are unmet. User presentation questions alone do not determine readiness.
