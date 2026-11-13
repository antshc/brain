# Living document

Apply when Wayfinder selects one repository spec/HLD. Wayfinder owns dispatch, branch policy and publication; the selected Spec/HLD playbook owns synthesis. Ordinary standalone publication remains unchanged.

## Draft authoring

- Use the selected template in its defined order. Preserve core sections; write `Pending — <specific missing evidence or decision>` instead of fabricating content or calling unknown content not applicable. Remove template directives/placeholders; preserve structural Confluence markers.
- Evolving-draft mode permits pending diagrams and contract artifacts only while the corresponding evidence/choice is unresolved. Record the gap in Open Questions; render supported diagrams/deltas through their producer skills as evidence arrives. Full readiness requires the normal author's checks, including contracts and required diagrams.
- Consume findings, not presumed results. Label source-based facts, runtime observations, assumptions and human choices distinctly. Research/Prove do not choose human preferences. No research or experiment is launched by synthesis; return new gaps to Wayfinder's Automatic runs.
- Keep issue/map/ticket provenance in Source Material; HLD reader-facing prose absorbs decisions without ticket attribution. Link research/experiment artifacts by commit-pinned URL while their separate PRs are unmerged; do not copy evidence branches into the document branch or create broken relative links to absent files.

## Incremental reconciliation

1. Read the latest document and incoming result/session. Match canonical source and stable question identity (ticket ref plus question when one ticket covers several); keep the identity in Source Material, not HLD reader prose. Done when existing content and stronger/conflicting evidence are identified.
2. Map each supported consequence to affected requirements, solution/decisions, assumptions, scope, testing, rollout, diagrams and evidence summaries. Update in place, preserving untouched content and author-specific diagram approval rules. Done when all affected surfaces agree; a blocked update remains explicit.
3. Reconcile Open Questions using Question/Answer columns. Retain answered rows; put the supported answer and implication in Answer and applicable body sections. Prefix incomplete answers `Partial —`, unresolved conflicts `Conflict —`, and missing decisions/evidence `Pending —`. Extend/refine an existing question or append newly surfaced ones once. Superseded answers identify the replacement and reason; preserve prior user choices unless explicitly superseded. Done when unresolved rows and settled facts are distinguishable.
4. Maintain one Source Material row per canonical map, ticket, report or Grill session stream; update cumulative contributions on reprocessing. Spec repository documents append the Source Material shape below; HLD uses its template. No invented legacy provenance. Done when repeated input would leave content/row counts unchanged.
5. Verify every consumed obligation appears in the document or has a named gap. Draft status means unresolved/partial/conflicting questions, pending core content or unmet author readiness checks; answered rows alone do not keep it draft. Return result identity and gaps to Wayfinder for publication. Done when synchronization is reviewable and readiness is stated accurately.

## Spec Source Material

Append only in repository-document mode; keep internal provenance outside the reader body.

```markdown
<!-- adf:ignore:start -->
## Source Material

| Source | Kind | Contribution |
| --- | --- | --- |
| <canonical source ref; stable question identity when needed> | <map, decision, evidence or Grill conversation> | <cumulative supported contribution> |
<!-- adf:ignore:end -->
```
