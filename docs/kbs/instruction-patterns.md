# Reference: 20 Instruction Patterns for Agent Skills

A practical catalog for writing instructions that trigger reliably, preserve invariants, and produce verifiable outcomes. Choose a pattern for a particular agent failure mode; use only the parts needed. These names are **cookbook conventions**, not formal requirements in the Agent Skills specification.

**Strength:** MUST/MUST NOT = hard constraint; an imperative = a required workflow step; prefer = default with legitimate alternatives; consider = heuristic. Do not turn preferences into hard constraints.

## Triggering and decisions

### 1. TRIGGER → ACTION

**When:** A predictable condition must activate an action.

**Form:** When [observable condition], [action].

> When a change affects an external integration boundary, run the relevant integration tests.

**Check:** The execution trace shows the action when the trigger is satisfied.

### 2. CONDITION → BRANCH → ACTION

**When:** The workflow varies by task, target, or platform.

**Form:** Determine [discriminator]; for [A], do [A action]; for [B], do [B action]; otherwise [unknown-case handling].

> Determine the target cloud. For AWS, read the AWS reference; for Azure, read the Azure reference; for both, read both. If unresolved, report the missing input.

**Check:** All supported cases and the unknown case are accounted for.

### 3. PRECONDITION → CHECK → BLOCK

**When:** A dependent action is invalid or unsafe without a prerequisite.

**Form:** Before [operation], verify [prerequisite]; otherwise block [dependent action].

> Before deployment, verify credentials and target environment. If either is missing, do not deploy; report the blocker.

**Check:** No dependent operation runs when its prerequisite failed.

### 4. PRIORITY → DECISION

**When:** Several approaches work but a preferred default exists.

**Form:** Prefer [option] when [criteria]. Use [alternative] only when [exception].

> Prefer existing repository utilities when they satisfy the requirement. Create a helper only when existing utilities are insufficient.

**Check:** The alternative is justified against the decision criteria, not arbitrarily forbidden.

### 5. SOURCE → PRECEDENCE → CONFLICT

**When:** Documentation, implementation, and instructions may disagree.

**Form:** [Source] is authoritative for [scope]. On conflict, [reconcile or report].

> Use the approved API contract for externally observable behavior. If code differs, report the discrepancy before changing either side.

**Check:** Conflicts are visible; weaker sources do not silently override the authority.

## Constraints and execution

### 6. INVARIANT → PRESERVE

**When:** A property must survive a change.

**Form:** MUST preserve [observable invariant], except [explicit permitted change].

> MUST preserve public signatures unless the task explicitly requests an API change.

**Check:** The final diff and behavior preserve the invariant.

### 7. CONSTRAINT → MECHANISM → RATIONALE → FAILURE

**When:** The prescribed procedure matters, not just the result.

**Form:** MUST [invariant]. Use [mandatory mechanism]. MUST NOT [plausible substitute]. Rationale: [why]. If [blocked], [response].

> MUST use the repository migration tool; MUST NOT replace it with direct SQL, even if faster. Rationale: the tool records versions and rollback data. If unavailable, stop migration and report the blocker.

**Check:** The actual required mechanism was used. A similar-looking outcome is not sufficient.

### 8. SCOPE → CHANGE → EXCLUDE

**When:** The agent tends to expand a task beyond the request.

**Form:** Change [in-scope surface] for [goal]. MUST NOT alter [excluded surface].

> Change only files needed for the requested behavior. MUST NOT refactor unrelated components.

**Check:** The diff contains no unrelated changes.

### 9. INSPECT → CHANGE → VERIFY

**When:** Changes depend on existing contracts or callers.

**Form:** Inspect [contracts/usages], modify [target], verify [affected behavior].

> Read the interface and callers before editing it. Make the change, then verify affected callers.

**Check:** Existing behavior was understood before modification and validated afterward.

### 10. DELEGATE → CONTRACT → INTEGRATE

**When:** A subagent has a bounded responsibility; the parent must consume its output.

**Form:** Delegate [scope] with [inputs and constraints]. Require [evidence contract]. Integrate [findings].

> Delegate broad repository exploration to a subagent. Require file paths, evidenced findings, and unknowns. The parent incorporates findings into the plan. If delegation is mandatory and unavailable, report the blocker instead of silently exploring directly.

**Check:** Delegation occurred, the output meets its contract, and the parent uses it.

### 11. SEQUENCE → CHECKPOINT → CONTINUE

**When:** Step B must not start until step A is confirmed.

**Form:** Execute [A]. Verify [checkpoint]. Only then execute [B].

> Generate the migration, validate it, then update consumers. Continue only after validation succeeds.

**Check:** The checkpoint precedes the dependent step.

## Reliability and verification

### 12. EXECUTE → VERIFY → REPAIR → REVERIFY

**When:** The workflow requires a correction loop.

**Form:** Execute [change], verify [result], repair [caused failure], reverify [final result].

> Run affected tests. Fix failures caused by the change. Rerun tests against the final revision.

**Check:** Evidence corresponds to the final implementation, not an earlier revision.

### 13. FAILURE → RETRY → ESCALATE

**When:** Transient errors are recoverable but repeated attempts need a bound.

**Form:** On [classified transient error], retry at most [N] times; otherwise [escalate].

> Retry transient network failures at most twice. If still failing, report the operation and error; block its dependent step.

**Check:** No unbounded retry loop and no suppressed failure.

### 14. CHECK → APPLY → RECHECK

**When:** State changes should be safe to repeat.

**Form:** Check [current state]. Apply [missing change] only as needed. Confirm [target state].

> Check whether configuration exists. Create it only if missing. Verify final settings.

**Check:** Repeated runs converge without duplicates or accidental extra changes.

### 15. CLAIM → EVIDENCE → UNCERTAINTY

**When:** Findings could conflate assumptions with observations.

**Form:** Every [claim] includes [evidence]; otherwise mark [assumption or unknown].

> Support review findings with a source path, line, or test result. Mark unverified assumptions explicitly.

**Check:** Every assertion is grounded or visibly uncertain.

### 16. REQUIREMENT → EVIDENCE → COMPLETION

**When:** An agent can finish its steps but miss required outcomes.

**Form:** Map [each requirement] to [observable proof]. Complete only if [all obligations met].

> Map every acceptance condition to an artifact or check result. Declare completion only after required checks pass and no obligation is unaccounted for.

**Check:** Completion is tied to the result, not effort spent.

## Context, autonomy, and handoffs

### 17. CONTEXT → LOAD → APPLY

**When:** Instructions include specialized references not needed on every run.

**Form:** If [condition], read [specific reference] and apply [relevant rules].

> Read the security reference only when conducting a security review; apply the checks relevant to the task.

**Check:** Relevant reference loads on demand without unnecessary bulk context.

### 18. GOAL → CONSTRAINTS → FREEDOM

**When:** The agent needs implementation discretion within boundaries.

**Form:** Achieve [goal], preserve [invariants], exclude [scope], choose [internal details] independently.

> Implement the requested behavior while preserving public contracts and repository conventions. Choose private implementation details independently.

**Check:** Mandatory properties hold without imposing unnecessary structural rules.

### 19. IMPACT → AUTHORIZATION → EXECUTE

**When:** Operations are destructive, externally consequential, or expensive.

**Form:** Identify [impact and exact target]. Require [authorization] before [action]. Otherwise [stop affected action].

> Before deleting production resources, identify exact targets and obtain explicit authorization. Without it, stop deletion and continue only independent read-only work.

**Check:** No protected action occurred without authorization.

### 20. STATE → PERSIST → HANDOFF

**When:** Tasks span sessions, agents, or fresh execution contexts.

**Form:** Record [completed work, decisions, evidence, blockers, next step] in [durable state].

> Before ending an iteration, persist changed files, tests, decisions, open questions, and next action. Resume from persisted state rather than repeating completed work.

**Check:** A new agent can continue from the recorded handoff.

## Pattern selection

| Observed problem | Recommended patterns |
|---|---|
| Wrong action, routing, or precedence | 1–5: triggering and decisions |
| Shortcutting required processes or expanding scope | 6–11: constraints and execution |
| Unsupported success, retry loops, or missing verification | 12–16: reliability and evidence |
| Too much context or over-constrained implementation | 17–18: conditional loading and autonomy |
| Unsafe external actions or lost progress | 19–20: authorization and handoffs |

## Compose minimally

For critical mechanisms, combine **trigger → invariant → mechanism → prohibited substitute → rationale → failure handling → verification**. For a low-risk instruction, a single conditional imperative can suffice. Explain non-obvious constraints; do not repeat obvious reasons. A rationale helps interpretation but does **not** technically enforce compliance.

**Composite example:**

> When an external integration changes, MUST run existing integration tests for that boundary. MUST NOT replace them with mocks. Rationale: mocks do not exercise the real integration. If credentials are unavailable, report verification as incomplete. Complete only after the final revision passes required checks.

## Evaluate the instructions

Test positive, negative, and near-miss triggers. Include cases where a shortcut appears faster, where a required tool is unavailable, and where verification fails. Inspect actual traces, artifacts, and reports. Revise rules in response to observed failures rather than adding generic reminders.

## Related cookbook materials

- [Constraint-First Instructions and Anti-Rationalization Rules](constraint-first-instructions-and-anti-rationalization-rules.md)
- [Concise Instructions, Explicit Goals, and Model-Neutral Procedures](concise-instructions-explicit-goals-and-model-neutral-procedures.md)
- [Delegate Bulk Exploration to Preserve Context](delegate-bulk-exploration-to-preserve-context.md)
- [Verification, Exit Criteria, Completeness Sweep, and Definition of Done](verification-exit-criteria-completeness-sweep.md)
- [Writing Agent-Facing Documents](agent-skills.instructions.md)

## Further reading

- [Agent Skills specification](https://agentskills.io/specification)
- [Anthropic skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [OpenAI Skill Creator](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)

These references support general authoring practices. The 20 pattern labels and examples are this cookbook's synthesis, not quotations from those sources.