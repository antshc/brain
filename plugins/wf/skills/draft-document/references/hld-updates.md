# HLD updates

## Incremental merge

For a new design, instantiate the template. For an existing design, merge section by section.

**Design delta.** Compare incoming evidence with the pre-merge design and derive every new or changed design obligation. An obligation may add or change a capability, Feature, Use case, requirement, behavior, decision, constraint, diagram, implementation artifact, or source contribution.

**Coverage map.** Before editing, map each design-delta obligation to the affected Requirements, Problem Statement and Goals, glossary, assumptions or scope, Solution Overview, Use cases, functional slices, testing, rollout, checklists, implementation artifacts, and source rows. Mark a surface unaffected only when the obligation does not change it. Keep the map transient; do not write it into the design.

- Preserve untouched prose/diagrams and user presentation questions. Remove legacy research/proof/sketch appendices only after preserving their local evidence inventory on the owning root/child issues; repair appendix references.
- Preserve existing functional-slice boundaries and diagrams unless confirmed changes require an update.
- Extend every affected existing section in place.
- Append a complete functional-slice H2 block when an obligation introduces a distinct behavior. Extend an existing slice only when the behavior, owning Deployable, contracts, and test seams remain coherent; otherwise add a new slice.
- Append a complete `Detailed Design` artifact H2 block when an obligation introduces an independently reviewable artifact.
- Preserve existing artifact blocks; update a block matching the same artifact and purpose instead of duplicating it, and remove or supersede one only when stronger evidence supports the change.
- Add non-conflicting obligations once.
- Update only content supported by stronger evidence.
- Update matching requirement rows instead of duplicating them.
- **Idempotency.** Reprocessing the same evidence leaves section count, requirement rows, functional slices, artifact blocks, and source rows unchanged.
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

## Protected presentation and evidence

Leave Open Questions empty on creation; preserve user entries verbatim, including blank answers. Return precise questions/risks to their owning topic/proposal; only unframeable concerns belong in the caller's root Not yet specified. Do not populate presentation questions with agent discovery gaps.

Consume only supported integrated results and explicit human decisions. Approval-gated prototype conclusions remain Pending until approved integration; Contract Options additionally require the caller's Choice and selected-only integration. Challenge this evidence follows the caller's automatic integration policy. Authoring never grants integration authority.

Remove legacy research/proof/sketch appendices only after the caller confirms evidence inventories are retained locally/on their owning issues. Return required metadata repairs for caller execution. Move unambiguously agent-owned legacy presentation questions to their precise owner or coarse fog only through the caller; preserve user entries and report ambiguous ownership.

Return document identity, supported changes and gaps for caller-owned commit/tracker synchronization. Readiness requires supported core content and resolved design obligations; presentation questions alone do not determine readiness.
