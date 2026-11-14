# Living document

Wayfinder owns dispatch, fog, progress and local integration; HLD owns synthesis. Standalone Spec publication is unchanged.

## Draft authoring

- Preserve HLD core order; use specific Pending markers for unsupported core content/diagrams. Keep Confluence structural markers.
- Store every uncertainty, risk, conflict and next action in root Not yet specified; HLD Open Questions are user-owned presentation content, including empty answers. Do not populate or reconcile that section automatically.
- Consume supported integrated findings and explicit human decisions. Pending prototypes remain outside integration/HLD until explicit approval and verified integration; Contract Options additionally require Choice. While awaiting approval, update fog/progress only, not prototype-derived HLD conclusions. Return new gaps to Wayfinder, not more research launched by synthesis.
- Synthesize consequences in requirements, solution, decisions, assumptions/limitations, testing and rollout. Retain reports/sketches locally with root/child issue inventories; no artifact appendices or disguised report/package copies in Detailed Design. Keep source provenance only in ignored Source Material.

## Incremental reconciliation

1. Read latest HLD and incoming result/session; match canonical source and stable root fog ID in internal provenance. Done when stronger/conflicting evidence and affected design surfaces are identified.
2. Update supported consequences in place; preserve untouched content, user choices and diagram approval gates. Preserve the user Open Questions section verbatim. Done when changed requirements, decisions, diagrams, testing and rollout agree, or a blocker is explicit.
3. Return incomplete/conflicting evidence and risks to Wayfinder for root fog updates; standalone HLD returns them inline to caller. Keep prototype-derived conclusions Pending until approved integration, and candidate choices Pending until selected-only integration. Done when every gap has an owner/next action outside user presentation questions.
4. Maintain one cumulative Source Material row per canonical map/ticket/report/Grill stream; no invented legacy provenance or duplicate rows. Retain publication-exclusion markers. Done when reprocessing would leave row counts unchanged.
5. Remove legacy report/sketch appendices and repair their references while preserving local evidence/issue inventories. For legacy agent-owned Open Questions, migrate to root fog before removing only unambiguously agent-owned entries; preserve user entries and ask on ambiguous ownership. Done when no evidence is lost and presentation content remains intact.
6. Return result identity/gaps for local commit and tracker synchronization. Draft means pending core content, unresolved design obligations in root fog or unmet readiness checks; user presentation questions alone do not set readiness. Done when every consumed obligation is supported in design or has a precise root blocker.
