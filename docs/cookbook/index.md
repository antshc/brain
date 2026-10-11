# Cookbook Principle Index

Tracks reusable AI-agent practices found in this repository and explicitly scanned external sources. A concept, ADR, or skill is evidence of a principle, **not** evidence that a cookbook recipe exists.

- `[x]` — principle has a cookbook recipe; link the recipe.
- `[ ]` — principle found in guidance but has no cookbook recipe; link its source.

## Delivery and learning

- [x] **Verification** — [recipe](verification-exit-criteria-completeness-sweep.md)
- [x] **Exit criteria (completeness verification)** — [recipe](verification-exit-criteria-completeness-sweep.md)
- [x] **Completeness sweep** — [recipe](verification-exit-criteria-completeness-sweep.md)
- [x] **Gotchas** — [recipe](gotchas-and-persistent-memory.md)
- [x] **Persistent memory** — [recipe](gotchas-and-persistent-memory.md)
- [ ] **Checklist-driven workflow** — [source](../concepts/structure-checklist-workflow.md)
- [ ] **Improvement flywheel (classify and fix observed failures)** — [source](../concepts/ops-improvement-flywheel.md)
- [ ] **Canary rule verification** — [source](../concepts/ops-canary-rule-verification.md)
- [ ] **Focused functional-slice testing** — [source](../adr/crew-is-agnostic.md)
- [ ] **Behavior-preserving agent review** — [source](../../plugins/crew/agents/chorey.agent.md)

## Instructions and drafting

- [ ] **Instruction robustness** — [source](../concepts/ops-instruction-robustness.md)
- [ ] **Constraint-first reasoning** — [source](../concepts/structure-constraint-first-reasoning.md)
- [ ] **Agent design and bounded responsibility** — [source](../concepts/structure-agents-style.md)
- [ ] **Open-question markers** — [source](../concepts/str-open-question-marker.md)
- [ ] **Repository instruction loading** — [source](../adr/crew-agents-uses-instructions.md)
- [ ] **Skill discovery and trigger descriptions** — [source](../../.github/instructions/agent-skills.instructions.md)
- [ ] **Progressive disclosure of agent guidance** — [source](../../skills/engineering/writing-great-skills/GLOSSARY.md)
- [ ] **Template ownership of rendering** — [source](../../.github/instructions/agent-skills.instructions.md)

## Composition and state

- [ ] **Skill composition and single ownership** — [source](../concepts/structure-skill-composition.md)
- [ ] **Cross-scope specialist discovery** — [source](../concepts/structure-cross-scope-skill-family.md)
- [ ] **Delegation engine isolation** — [source](../adr/explore-codebase-is-skill-agnostic.md)
- [ ] **Agent-agnostic handoff contracts** — [source](../adr/ralph-is-agent-agnostic.md)
- [ ] **Session ledger** — [source](../concepts/structure-ledger.md)
- [ ] **Trigger indexing** — [source](../concepts/structure-trigger-indexer.md)
- [ ] **Per-repository configuration resolution** — [source](../concepts/ops-per-repo-config-resolution.md)
- [ ] **Repository adapter skills** — [source](../concepts/structure-repository-adapter-skill.md)
- [ ] **Resource access skills** — [source](../concepts/structure-resource-access-skill.md)
- [ ] **Skill-owned code** — [source](../concepts/structure-skill-owned-code.md)
- [ ] **CLI JSON handoff** — [source](../concepts/str-cli-json-handoff.md)

## External scan: cursor/plugins/pstack

Source: [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack), scanned and rescanned 2026-10-11. These principles link to guidance in another repository. Existing brain entries remain unchanged.

### Design and code principles

- [ ] **Question a repeatedly failed premise with an actor census** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-attack-the-premise/SKILL.md)
- [ ] **Validate and handle errors at system boundaries** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-boundary-discipline/SKILL.md)
- [ ] **Build a rerunnable tool for nontrivial work** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-build-the-lever/SKILL.md)
- [ ] **Turn recurring corrections into enforced mechanisms** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-encode-lessons-in-structure/SKILL.md)
- [ ] **Compare competing prototypes for novel designs** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-exhaust-the-design-space/SKILL.md)
- [ ] **Prioritize consumer experience over implementation convenience** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-experience-first/SKILL.md)
- [ ] **Explain measured results with evidence and limiting factors** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-explain-the-number/SKILL.md)
- [ ] **Reproduce failures and fix root causes rather than symptoms** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-fix-root-causes/SKILL.md)
- [ ] **Choose core data shapes and shared foundations before features** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-foundational-thinking/SKILL.md)
- [ ] **Preserve agent context by delegating bulk exploration** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-guard-the-context-window/SKILL.md)
- [ ] **Prefer the smallest change and shallowest useful abstraction** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-laziness-protocol/SKILL.md)
- [ ] **Make state-changing operations converge across retries** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-make-operations-idempotent/SKILL.md)
- [ ] **Migrate callers and delete obsolete internal APIs together** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md)
- [ ] **Minimize reader load from indirection and mutable state** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-minimize-reader-load/SKILL.md)
- [ ] **Represent domain invariants in explicit data structures** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-model-the-domain/SKILL.md)
- [ ] **Proceed on reversible work without human blocking** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-never-block-on-the-human/SKILL.md)
- [ ] **Optimize planned migrations for a verified final state** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-outcome-oriented-execution/SKILL.md)
- [ ] **Prove the real artifact rather than trusting proxies or reports** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-prove-it-works/SKILL.md)
- [ ] **Redesign new requirements as foundational constraints** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-redesign-from-first-principles/SKILL.md)
- [ ] **Separate shared mutable state before using locks** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-separate-before-serializing-shared-state/SKILL.md)
- [ ] **Sequence changes as independently verifiable units** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-sequence-verifiable-units/SKILL.md)
- [ ] **Remove dead or redundant complexity before additions** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-subtract-before-you-add/SKILL.md)
- [ ] **Test observable behavior with exact expected results** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-test-behavior-not-implementation/SKILL.md)
- [ ] **Use types to exclude invalid states and exhaust variants** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/principle-type-system-discipline/SKILL.md)

- [ ] **Derive architecture contracts from caller usage before implementing** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/architect/SKILL.md)
- [ ] **Write a consumer usage guide before implementing a shared API** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-help/references/prompting.md)
- [ ] **Reject unnecessary scope instead of reflexively agreeing** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md)
- [ ] **Replace redundant comments and unsafe suppressions with code fixes** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/no-comments/SKILL.md)
- [ ] **Validate authored skills, referenced files, and structural examples** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/authoring-a-skill.md)
- [ ] **Repair broken workflow skills in a separate PR from feature work** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md)

### Understanding and design workflows

- [ ] **Investigate the current code path before explaining it** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/how/SKILL.md)
- [ ] **Reconstruct design rationale across independent evidence sources** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/why/SKILL.md)
- [ ] **Sketch architecture first and redo it when structural red flags appear** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/architect/SKILL.md)
- [ ] **Compare independent design candidates with cross-judging** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/arena/SKILL.md)
- [ ] **Decompose parallel work into scoped workers and aggregate results** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/swarm/SKILL.md)
- [ ] **Classify adversarial review findings with independent judgment** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/interrogate/SKILL.md)
- [ ] **Resolve observable decisions with throwaway experiments** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/prototype.md)
- [ ] **Scale verification rigor to impact and reversibility** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/figure-it-out/SKILL.md)
- [ ] **Prove the key safety assumption behind a change** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/blast-radius/SKILL.md)

- [ ] **Calibrate rationale claims to direct, supported, inferred, or unknown evidence** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/why/references/epistemics.md)
- [ ] **Eliminate debugging hypotheses using runtime observations** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/bug-fix.md)
- [ ] **Teach behavior and rationale through incremental explanations and diagrams** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/teach/SKILL.md)
- [ ] **Summarize session progress as outcomes and human-owned decisions** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/ketchup/SKILL.md)
- [ ] **Convert traces to queryable data and attribute findings to source symbols** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/trace-forensics.md)
- [ ] **Keep suspected causes out of the initial agent task brief** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-help/references/prompting.md)

### Testing and delivery workflows

- [ ] **Pin existing behavior before structural refactoring** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/refactoring.md)
- [ ] **Run a failing regression check before fixing a bug** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/tdd/SKILL.md)
- [ ] **Create a repository-specific live verification harness** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/SKILL.md)
- [ ] **Maintain verification feature maps with source and live checks** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/maintain-verification-skill/SKILL.md)
- [ ] **Freeze an evaluation harness and revert unsupported iterations** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/hillclimb.md)
- [ ] **Prove visual parity against an unchanged screenshot baseline** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/visual-parity.md)
- [ ] **Verify each PR independently at the reviewed patch before merging** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/shipping.md)
- [ ] **Classify CI failures and review comments before modifying a PR** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/babysit.md)
- [ ] **Keep PR summaries short with observable verification evidence** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/opening-a-pr.md)

- [ ] **Compare performance under production-equivalent conditions and repeated alternating runs** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/benchmark-checklist/SKILL.md)
- [ ] **Remove unnecessary work before optimizing remaining performance cost** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/perf-issue.md)
- [ ] **Verify an existing fix against baseline and patched live behavior before authoring another** — [source](https://github.com/cursor/plugins/blob/main/pstack/automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md)
- [ ] **Audit live sessions and uncommitted changes before removing worktrees** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/worktree-cleanup.md)
- [ ] **Treat PR review text as untrusted input rather than executable instructions** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/babysit.md)
- [ ] **Select documentation structure by tutorial, how-to, reference, or explanation purpose** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/technical-writing/SKILL.md)

### Autonomy, continuity, and learning

- [ ] **Route tasks through explicit, falsifiable finish conditions** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md)
- [ ] **Keep autonomous iterations bound to an unchanged stop predicate** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autonomous-run.md)
- [ ] **Pilot a full work unit before scaling a multi-agent program** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/orchestrate.md)
- [ ] **Keep append-only decision records linked to real evidence** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/show-me-your-work/SKILL.md)
- [ ] **Preserve work and a resume note when pausing an agent run** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/pause-safely.md)
- [ ] **Recover prior context within the workspace and verify live state** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/recall/SKILL.md)
- [ ] **Turn session retrospectives into tested agent-guidance changes** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/reflect/SKILL.md)
- [ ] **Infer reusable agent preferences only from stable evidence** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/automate-me/SKILL.md)
- [ ] **Evaluate agent instructions with blinded candidates and judges** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/eval.md)
- [ ] **Configure model selection per agent responsibility** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/setup-pstack/SKILL.md)

- [ ] **Delegate implementation with bounded files and success criteria, then review the diff** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/feature.md)
- [ ] **Start fresh subagents with consolidated instructions unless local state requires a resume** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md)
- [ ] **Carry immutable standing orders into every worker spawn and resume** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/orchestrate.md)
- [ ] **Keep orchestration and code-writing responsibilities with separate owners** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/orchestrate.md)
- [ ] **Refill a rolling worker window instead of waiting for whole batches** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/orchestrate.md)
- [ ] **Judge agent progress by actual side effects and replace stalled workers** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autopilot-stack.md)
- [ ] **Validate multi-phase plans with an executable checker before handoff** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/multi-phase-plan.md)
- [ ] **Wait for an explicit operator go before executing an approved plan** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/multi-phase-plan.md)
- [ ] **Keep verified stacked PRs unmerged until explicitly authorized** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autopilot-stack.md)
- [ ] **Apply retrospective changes to shared agent instructions only with approval** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/reflect/SKILL.md)

### External automations and communication

- [ ] **Freeze report provenance and deduplicate before filing tickets** — [source](https://github.com/cursor/plugins/blob/main/pstack/automations/benny/skills/triage-issue-reports/SKILL.md)
- [ ] **Confirm a reported defect twice through the live user interface** — [source](https://github.com/cursor/plugins/blob/main/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md)
- [ ] **Keep external writes and credentials out of delegated workers** — [source](https://github.com/cursor/plugins/blob/main/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md)
- [ ] **Fail closed when an external automation's target is uncertain** — [source](https://github.com/cursor/plugins/blob/main/pstack/automations/benny/skills/triage-issue-reports/SKILL.md)
- [ ] **Write audience-specific instructions in concise, controlled language** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/technical-writing/SKILL.md)
- [ ] **Review comments as evidence rather than automatically obeying them** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/references/bugbot-triage.md)

- [ ] **Gate automatic bug fixing on a trusted triage verdict and ownership checks** — [source](https://github.com/cursor/plugins/blob/main/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md)
- [ ] **Compensate cross-system ticket writes when the final handoff fails** — [source](https://github.com/cursor/plugins/blob/main/pstack/automations/benny/skills/triage-issue-reports/SKILL.md)
- [ ] **Keep automation webhook secrets on the server, never in the browser or chat** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/make-bot-ui/SKILL.md)
- [ ] **Remove generic AI phrasing while preserving the intended meaning** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md)
- [ ] **Describe goals, proof, and constraints without prescribing skill choreography** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-help/references/prompting.md)
- [ ] **Frame agent delivery for both the user and the future maintainer** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md)

## Scan and update

1. Scan current `ARCHITECTURE.md`, `docs/concepts/`, `docs/adr/`, `.github/instructions/`, and active agents and skills in `plugins/` and `skills/`. Ignore `_backup/` and `_in-progress/`.
2. Extract reusable **AI-agent behavior principles** supported by an explicit source rule. Merge synonyms and duplicate occurrences into one checklist entry.
3. Compare each principle with the recipes in `docs/cookbook/` (excluding this index). Check the box **only** when a recipe actually covers the principle with actionable AI instructions, and link that recipe. Otherwise leave it unchecked and link the source.
4. Add newly found principles; recheck existing entries and links. Do not mark a principle covered merely because its source document exists.
5. For external repositories, retain links to the original source. Check coverage only against local cookbook recipes.
