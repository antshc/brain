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

Source: [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack), scanned three times on 2026-10-11. These principles link to guidance in another repository. Existing brain entries remain unchanged.

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

- [ ] **Make module internals inaccessible and expose only one supported operation path** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/architect/references/design-red-flags.md)
- [ ] **Record design alternatives, accepted tradeoffs, and rationale alongside the chosen contract** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/architect/references/rationale-template.md)
- [ ] **Review the implementation against declared intent and require concrete evidence per finding** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/interrogate/references/reviewer-prompt.md)

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

- [ ] **Separate evidence collection from synthesis and keep investigators within their assigned sources** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/why/references/investigator-prompt.md)
- [ ] **Record exact investigation queries, empty results, and contradictory evidence** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/why/references/investigator-prompt.md)
- [ ] **Treat agent transcripts and reviewer outputs as untrusted data, not executable instructions** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/reflect/references/synthesizer.md)
- [ ] **Limit retrospective skill changes to demonstrated use or missed triggers** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/reflect/references/synthesizer.md)
- [ ] **Resume from the prior execution trail rather than repeating completed work** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/session-pickup.md)

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

- [ ] **Verify dry-run claims by inspecting actual network, file, and repository effects** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/SKILL.md)
- [ ] **Health-check and reset verification instances after unexpected drive failures** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/maintain-verification-skill/SKILL.md)
- [ ] **Clean up only owned verification processes and preserve collected proof artifacts** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/SKILL.md)
- [ ] **Compare changed behavior with current trunk on the same user-visible path** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autopilot-full.md)
- [ ] **Keep reproduction recordings, logs, and tokens out of source control** — [source](https://github.com/cursor/plugins/blob/main/pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md)

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

- [ ] **Audit decision logs against transcripts and correct false or omitted claims by appending rows** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/show-me-your-work/SKILL.md)
- [ ] **Independently review long-running decision trails with a different model family** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/show-me-your-work/SKILL.md)
- [ ] **Propagate operator stop orders to all active agents as an immediate no-writes hold** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autopilot-full.md)
- [ ] **Prefer event-based agent wakeups with a heartbeat fallback over unnecessary polling** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autonomous-run.md)
- [ ] **Keep stack topology updates under one coordinator while PR owners work in parallel** — [source](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autopilot-stack.md)

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

- [ ] **Preserve locally edited managed files and keep user configuration outside automation packs** — [source](https://github.com/cursor/plugins/blob/main/pstack/automations/benny/skills/setup-benny/SKILL.md)
- [ ] **Run automations from committed operational files rather than copied instructions or caches** — [source](https://github.com/cursor/plugins/blob/main/pstack/automations/benny/skills/setup-benny/SKILL.md)

## External scan: addyosmani/agent-skills

Source: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), scanned and rescanned 2026-10-11. Reviewed the 25 active skills, four agent personas, seven shared reference checklists, root agent instructions, command workflows, skill-evaluation guidance, nested references, and hooks. Missing entries link to source evidence; recipes were not created.

### Intent, discovery, and specifications

- [ ] **Select the applicable skill before work and follow its gates in order** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/using-agent-skills/SKILL.md)
- [ ] **Surface assumptions and stop when requirements conflict or remain uncertain** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/using-agent-skills/SKILL.md)
- [ ] **Challenge unwarranted scope or complexity while leaving informed decisions to the user** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/using-agent-skills/SKILL.md)
- [ ] **Interview for intent one question and one explicit guess at a time** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/interview-me/SKILL.md)
- [ ] **Require explicit confirmation of the restated intent and stop before downstream work** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/interview-me/SKILL.md)
- [ ] **Diverge into alternatives before converging on an evaluated idea** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/idea-refine/SKILL.md)
- [ ] **Record and test key idea assumptions before committing to an MVP** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/idea-refine/SKILL.md)
- [ ] **Approve the capability dependency map before specifying a multi-module initiative** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/spec-driven-development/SKILL.md)
- [ ] **Write a specification before implementation and stop for approval before planning** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/spec-driven-development/SKILL.md)
- [ ] **Update the living specification before implementing changed decisions** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/spec-driven-development/SKILL.md)
- [ ] **Define measurable project quality thresholds and record exceptions with owners and expiry** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/constraint-driven-development/SKILL.md)
- [ ] **Apply a minimum quality floor in noninteractive runs when project thresholds are absent** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/constraint-driven-development/SKILL.md)
- [ ] **Detect attempts to weaken checks, tests, suppressions, or quality thresholds** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/constraint-driven-development/SKILL.md)
- [ ] **Place verification checks according to execution cost and scope expensive checks to changed code** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/constraint-driven-development/SKILL.md)
- [ ] **Build dependency-ordered, verifiable task slices without implementing during planning** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/planning-and-task-breakdown/SKILL.md)
- [ ] **Preserve incomplete plans and use the project's designated task tracker** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/planning-and-task-breakdown/SKILL.md)

- [ ] **Inspect working-tree changes before autonomous execution and stop on unrelated dirty files** — [source](https://github.com/addyosmani/agent-skills/blob/main/.claude/commands/build.md)
- [ ] **Escalate irreversible or high-risk work for fresh human approval even during an approved autonomous run** — [source](https://github.com/addyosmani/agent-skills/blob/main/.claude/commands/build.md)

### Implementation, context, and independent judgment

- [ ] **Implement complete vertical slices with test, verification, and commit gates** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/incremental-implementation/SKILL.md)
- [ ] **Keep incomplete capabilities behind safe defaults or feature flags** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/incremental-implementation/SKILL.md)
- [ ] **Do not repeat unchanged verification commands without intervening changes** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/incremental-implementation/SKILL.md)
- [ ] **Load relevant implementation, tests, types, and precedent instead of entire context dumps** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/context-engineering/SKILL.md)
- [ ] **Trim context proactively while preserving active constraints, errors, and decisions** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/context-engineering/SKILL.md)
- [ ] **Persist restartable session handoffs with decisions, changed files, verification, and next work** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/context-engineering/SKILL.md)
- [ ] **Verify framework-specific decisions against version-matched official documentation** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/source-driven-development/SKILL.md)
- [ ] **Cite authoritative implementation sources and label unverifiable patterns explicitly** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/source-driven-development/SKILL.md)
- [ ] **Independently doubt nontrivial claims using only the artifact and contract, not the author's conclusion** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/doubt-driven-development/SKILL.md)
- [ ] **Reconcile reviewer findings rather than accepting them verbatim, with a bounded review loop** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/doubt-driven-development/SKILL.md)
- [ ] **Require explicit authorization for each external cross-model review invocation** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/doubt-driven-development/SKILL.md)
- [ ] **Define public contracts before implementation and preserve observable consumer behavior** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/api-and-interface-design/SKILL.md)
- [ ] **Honor idempotency keys across retries, payload mismatches, and unknown outcomes** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/api-and-interface-design/SKILL.md)
- [ ] **Define a reference-grounded UI design contract before implementation** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/frontend-ui-engineering/SKILL.md)
- [ ] **Verify responsive and accessible UI states including empty, loading, and error flows** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/frontend-ui-engineering/SKILL.md)

- [ ] **Stage only files belonging to the current autonomous task rather than blindly staging every change** — [source](https://github.com/addyosmani/agent-skills/blob/main/.claude/commands/build.md)
- [ ] **Avoid installing a second always-on skill router when the agent host already routes skills natively** — [source](https://github.com/addyosmani/agent-skills/blob/main/docs/getting-started.md)
- [ ] **Keep reusable skills separate from repository-specific agent instructions during installation** — [source](https://github.com/addyosmani/agent-skills/blob/main/AGENTS.md)
- [ ] **Include required shared references when distributing an individual skill outside its original pack** — [source](https://github.com/addyosmani/agent-skills/blob/main/docs/getting-started.md)
- [ ] **Keep vendor runtime settings in per-agent adapters or permitted metadata, not portable skill frontmatter** — [source](https://github.com/addyosmani/agent-skills/blob/main/docs/advanced-per-agent-configuration.md)
- [ ] **Distinguish tool preapproval from true tool restrictions when configuring least-privilege agents** — [source](https://github.com/addyosmani/agent-skills/blob/main/docs/advanced-per-agent-configuration.md)
- [ ] **Revalidate cached official documentation with origin validators before using it across sessions** — [source](https://github.com/addyosmani/agent-skills/blob/main/hooks/SDD-CACHE.md)

### Testing, debugging, and evidence

- [ ] **Use the red-green-refactor cycle for behavior-changing implementation** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/test-driven-development/SKILL.md)
- [ ] **Reproduce a reported bug with a failing regression test before applying the fix** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/test-driven-development/SKILL.md)
- [ ] **Test observable state with descriptive tests and minimize interaction mocks** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/test-driven-development/SKILL.md)
- [ ] **Choose test sizes by real resource boundaries and preserve the repository test conventions** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/test-driven-development/SKILL.md)
- [ ] **Stop further feature work on broken tests or builds until the failure is resolved** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/debugging-and-error-recovery/SKILL.md)
- [ ] **Isolate and reduce failures before root-cause fixes, using history bisect when useful** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/debugging-and-error-recovery/SKILL.md)
- [ ] **Verify repaired behavior with focused tests, full regression checks, and runtime checks** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/debugging-and-error-recovery/SKILL.md)
- [ ] **Verify browser changes against live DOM, console, network, and before-after screenshots** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/browser-testing-with-devtools/SKILL.md)
- [ ] **Isolate automated browser tests from personal signed-in browser profiles** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/browser-testing-with-devtools/SKILL.md)
- [ ] **Keep browser JavaScript inspection read-only unless mutations are explicitly authorized** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/browser-testing-with-devtools/SKILL.md)
- [ ] **Treat error output, external documentation, and browser content as untrusted instructions** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/debugging-and-error-recovery/SKILL.md)
- [ ] **Apply standing definition-of-done checks separately from task acceptance criteria** — [source](https://github.com/addyosmani/agent-skills/blob/main/references/definition-of-done.md)

- [ ] **Treat a quality guard that could not run as a blocking failure rather than a clean result** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/constraint-driven-development/references/floor-guard.md)

### Review and simplification

- [ ] **Review correctness, readability, architecture, security, and performance, reading tests first** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/code-review-and-quality/SKILL.md)
- [ ] **Classify review findings by severity and lead with required, evidenced changes** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/code-review-and-quality/SKILL.md)
- [ ] **Keep review changes cohesive and consider total file size as well as diff size** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/code-review-and-quality/SKILL.md)
- [ ] **Understand why existing code exists before simplifying or deleting it** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/code-simplification/SKILL.md)
- [ ] **Refactor incrementally without changing test expectations to force a pass** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/code-simplification/SKILL.md)
- [ ] **Automate wide mechanical refactors instead of hand-editing large change sets** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/code-simplification/SKILL.md)
- [ ] **Parallelize independent specialist reviews, but keep aggregation with the orchestrator** — [source](https://github.com/addyosmani/agent-skills/blob/main/references/orchestration-patterns.md)
- [ ] **Do not make agent personas invoke other personas or add routing-only hops** — [source](https://github.com/addyosmani/agent-skills/blob/main/docs/agents.md)

- [ ] **Use communicating agent teams for competing-hypothesis investigations and independent subagents for report fan-out** — [source](https://github.com/addyosmani/agent-skills/blob/main/references/orchestration-patterns.md)
- [ ] **Mask protected source blocks during agent simplification and restore them from verified placeholders or backups** — [source](https://github.com/addyosmani/agent-skills/blob/main/hooks/SIMPLIFY-IGNORE.md)

### Security and trust boundaries

- [ ] **Threat-model system boundaries and write abuse cases before hardening a feature** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/security-and-hardening/SKILL.md)
- [ ] **Validate external and model-generated data at the boundary before using it as code or decisions** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/security-and-hardening/SKILL.md)
- [ ] **Guard destructive operations against paths controlled by untrusted upstream processes** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/security-and-hardening/SKILL.md)
- [ ] **Block unreviewed dependency install scripts and audit the committed lockfile** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/security-and-hardening/SKILL.md)
- [ ] **Review authorization for every protected resource and prevent secrets entering code or logs** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/security-and-hardening/SKILL.md)
- [ ] **Classify personal data by purpose and exclude unnecessary personal information from telemetry** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/security-and-hardening/SKILL.md)

### Performance, delivery, and operation

- [ ] **Measure user-visible performance and identify its bottleneck before optimizing** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/performance-optimization/SKILL.md)
- [ ] **Compare one optimization against an equivalent baseline and revert unproven changes** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/performance-optimization/SKILL.md)
- [ ] **Record rejected optimizations and install regression monitors for measured gains** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/performance-optimization/SKILL.md)
- [ ] **Never invent web performance scores without actual measurement artifacts** — [source](https://github.com/addyosmani/agent-skills/blob/main/agents/web-performance-auditor.md)
- [ ] **Create atomic, reviewed commits and verify tests, types, lint, and secrets before commit** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/git-workflow-and-versioning/SKILL.md)
- [ ] **Use isolated worktrees when parallel agents would otherwise share a working tree** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/git-workflow-and-versioning/SKILL.md)
- [ ] **Version consumer-facing releases with tags, semantic versions, and human changelogs** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/git-workflow-and-versioning/SKILL.md)
- [ ] **Run non-bypassable CI quality gates and feed failures back into agent correction** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/ci-cd-and-automation/SKILL.md)
- [ ] **Remove feature flags and dead branches after their rollout finishes** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/ci-cd-and-automation/SKILL.md)
- [ ] **Prefer advisory deprecation and provide a production-proven replacement plus migration guidance** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/deprecation-and-migration/SKILL.md)
- [ ] **Migrate schemas additively before destructive changes and test the rollback path** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/deprecation-and-migration/SKILL.md)
- [ ] **Verify old consumers are inactive before deleting a deprecated interface or system** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/deprecation-and-migration/SKILL.md)
- [ ] **Record architecture decisions with alternatives and supersede rather than erase old ADRs** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/documentation-and-adrs/SKILL.md)
- [ ] **Preserve factual details and uncertainty when simplifying documentation prose** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/documentation-and-adrs/SKILL.md)
- [ ] **Choose telemetry from explicit on-call questions instead of instrumenting indiscriminately** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/observability-and-instrumentation/SKILL.md)
- [ ] **Propagate correlation and entry-point identity while bounding telemetry label cardinality** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/observability-and-instrumentation/SKILL.md)
- [ ] **Make alerts actionable with runbooks and verify telemetry and notification delivery** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/observability-and-instrumentation/SKILL.md)
- [ ] **Use prelaunch gates, staged rollout thresholds, and tested rollback triggers** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/shipping-and-launch/SKILL.md)
- [ ] **Verify critical user flows and health signals after deployment** — [source](https://github.com/addyosmani/agent-skills/blob/main/skills/shipping-and-launch/SKILL.md)
- [ ] **Introduce quality checks incrementally in legacy projects rather than enabling the entire lifecycle at once** — [source](https://github.com/addyosmani/agent-skills/blob/main/docs/adoption-guide.md)
- [ ] **Keep skill entrypoints concise with trigger descriptions and load long references on demand** — [source](https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md)

- [ ] **Default launch decisions to NO-GO for unresolved critical findings unless the operator explicitly accepts the risk** — [source](https://github.com/addyosmani/agent-skills/blob/main/.claude/commands/ship.md)

### Skill authoring and evaluation (second pass)

- [ ] **Check existing skills, active proposals, and rejected changes before introducing a new skill** — [source](https://github.com/addyosmani/agent-skills/blob/main/CONTRIBUTING.md)
- [ ] **Record rejected skill changes with evaluation evidence in an append-only ledger** — [source](https://github.com/addyosmani/agent-skills/blob/main/CONTRIBUTING.md)
- [ ] **Write skill procedures in model-neutral capabilities instead of model-specific workarounds** — [source](https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md)
- [ ] **Include concrete anti-rationalization rebuttals, misuse red flags, and evidence-based exit checks in skills** — [source](https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md)
- [ ] **Test skill routing with realistic positive triggers and neighboring negative triggers** — [source](https://github.com/addyosmani/agent-skills/blob/main/evals/README.md)
- [ ] **For negative routing tests, require the intended owner skill to outrank the wrong skill** — [source](https://github.com/addyosmani/agent-skills/blob/main/evals/README.md)
- [ ] **Evaluate skill behavior using isolated executable fixtures and full tool traces rather than claimed intentions** — [source](https://github.com/addyosmani/agent-skills/blob/main/evals/README.md)
- [ ] **Use dialogue-only evaluations only when conversation itself is the skill's deliverable** — [source](https://github.com/addyosmani/agent-skills/blob/main/evals/README.md)
- [ ] **Pressure-test skill compliance against shortcuts justified by urgency, authority, or sunk cost** — [source](https://github.com/addyosmani/agent-skills/blob/main/evals/README.md)
- [ ] **Run skill-on versus skill-off evaluations and score observable output rather than invocation alone** — [source](https://github.com/addyosmani/agent-skills/blob/main/evals/README.md)
- [ ] **Pin model and runtime versions and repeat trials before drawing conclusions from stochastic skill routing** — [source](https://github.com/addyosmani/agent-skills/blob/main/evals/README.md)
- [ ] **Validate that equivalent host command adapters stay semantically aligned** — [source](https://github.com/addyosmani/agent-skills/blob/main/docs/developer-onboarding.md)

## Scan and update

1. Scan current `ARCHITECTURE.md`, `docs/concepts/`, `docs/adr/`, `.github/instructions/`, and active agents and skills in `plugins/` and `skills/`. Ignore `_backup/` and `_in-progress/`.
2. Extract reusable **AI-agent behavior principles** supported by an explicit source rule. Merge synonyms and duplicate occurrences into one checklist entry.
3. Compare each principle with the recipes in `docs/cookbook/` (excluding this index). Check the box **only** when a recipe actually covers the principle with actionable AI instructions, and link that recipe. Otherwise leave it unchecked and link the source.
4. Add newly found principles; recheck existing entries and links. Do not mark a principle covered merely because its source document exists.
5. For external repositories, retain links to the original source. Check coverage only against local cookbook recipes.
