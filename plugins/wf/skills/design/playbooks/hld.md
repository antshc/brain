# High-level design (HLD)

Coordinate one authoritative HLD at `docs/ongoing/{{initiativeSlug}}.md`, or the caller's exact document worktree/path. Design owns evidence, risk decisions and readiness; Draft document owns authoring.

## Inputs

Use current conversation, specs, resolved decisions, glossary, Architecture, applicable ADRs/Concepts, existing HLD and available research/proof results. Explore current state when needed; do not interview during synthesis. On a requested legacy update, move only the canonical HLD to `docs/ongoing/`, preserve history and repair active links.

## Workflow

1. **Prepare evidence.** Rank sources and identify unresolved choices, conflicts and material risks. Wayfinder supplies supported integrated results; pending approval-gated prototypes remain excluded. Read Living document for Wayfinder/evolving drafts. Done when the authoring input includes source identities, resolved decisions, gaps and existing document state.
2. **Verify risks.** Standalone HLD uses Risk verification registered in the router before final synthesis. Wayfinder owns its evidence dispatch and risk queue. Record mitigation, actual method/result, reproduction, residual scope/blocker and next action on the owning issue/root or standalone return; planned checks are not proof. Done when material risks are verified or explicit draft blockers are retained.
3. **Author.** *Load and follow the `draft-document` skill to create and update high-level designs* using `hld`. Pass exact destination/worktree, current HLD, source-ranked inputs, verified outcomes, user choices, diagram approvals and `@evolvingDraft` when supplied. Receive the rendered document, changes, source conflicts and gaps. Done when supported conclusions are reflected without unsupported content loss.
4. **Reconcile.** Return unresolved decisions/evidence to Wayfinder for precise topic/proposal ownership or coarse Not yet specified classification; standalone returns exact blockers/next actions inline without creating a map. Preserve user-owned Open Questions. Wayfinder owns local commits/tracker synchronization; standalone authoring does not publish or commit. Done when each gap has an owner or standalone next action.

## Completion criteria

- One authored HLD covers supplied obligations; no duplicate authoritative copy or unsupported readiness claim.
- Existing presentation questions and diagram approvals survive; missing core evidence remains Pending.
- Reports/sketches stay local and source provenance remains publication-excluded.
- Publication requires the separate explicit `publish-hld` route.
