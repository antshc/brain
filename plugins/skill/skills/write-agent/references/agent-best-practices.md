# Agent best practices

Cross-vendor synthesis (Claude Code, GitHub Copilot, OpenAI Codex, Grok Build, Gemini CLI), October 2026; not a universal spec.

**Root rule:** small, specialized agent; clear invocation; bounded responsibility; explicitly configured tools; verifiable outcome.

## Contents

- Layer test
- Description
- Constraint language
- Tools and permissions
- Verification
- Coding agents
- Planner agents
- Anti-patterns
- Checklist

## Layer test

Each layer owns one thing. An agent defines **who**; put other content in its owning layer.

| Layer | Owns | Examples |
|---|---|---|
| Repository instructions | Durable, generally applicable project rules | `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` |
| Custom agent | Specialized role, invocation, responsibilities, output | Developer, Reviewer, Tester |
| Skill | Reusable procedure, references, scripts (**how**) | `code-review`, `verify` |
| Tool / MCP | Callable capability, external access (**what it can call**) | File read, shell, GitHub API |
| Workflow | Trigger, scheduling, ordering, retries, handoffs (**when**) | Ticket → Developer → Review |
| Gate | Deterministic pass/fail (**whether it may proceed**) | Tests, branch protection, required checks |

- Create an agent only for recurring work that benefits from distinct instructions, tools, or isolated context.
- Generic rules for every task → repository instructions. Reusable procedure or lengthy examples → skill. Scheduling → workflow. Security or invariants → runtime gate.
- **MUST NOT** encode workflow scheduling or security enforcement solely in an agent prompt.

## Description

The description is a **routing interface**: it drives automatic selection (Claude Code, Gemini CLI, Copilot). Keep it short, concrete, exclusive.

- Pattern: `[Capability]. Use when [trigger]. Do not use when [exclusion].`
- One observable outcome; triggers in words users type.
- Exclusion names the nearest sibling's territory.
- Reject vague, overlapping text: "expert developer", "general-purpose coding assistant", "helps with software engineering".
- YAML-safe: quote the value or use a folded block scalar (`description: >-`) when it contains `: `, ` #`, backticks, or a leading YAML indicator.

| Role | Example description |
|---|---|
| Developer | Implement actionable GitHub tickets. Use when requirements are clear and no human decision blocks implementation. |
| Reviewer | Review completed changes for correctness, regressions, security, and test gaps. Use before PR merge. |
| Tester | Create and execute behavior verification. Use when functionality changes or test coverage is insufficient. |
| Address | Resolve actionable PR review findings. Use when unresolved review comments require code changes. |
| Maintainer | Evaluate PR merge readiness and complete authorized merge actions. Use after required checks and reviews. |

## Constraint language

Normative words carry clarity, not keyword semantics:

| Word | Intent | Example |
|---|---|---|
| `MUST` | Required | MUST run relevant tests before completion. |
| `MUST NOT` | Prohibited | MUST NOT modify unrelated files. |
| `SHOULD` | Preferred | SHOULD reuse an existing domain service. |
| `MAY` | Optional | MAY add regression tests for uncovered edge cases. |
| `IF ... THEN ...` | Conditional | IF blocked, THEN report the missing decision. |
| `STOP` | Stop condition | STOP if an action requires an unavailable credential. |
| `RETURN` | Output contract | RETURN findings with file references and evidence. |

- Use `MUST` sparingly, for actual invariants.
- Add a terse rationale to consequential constraints (`Rationale: Existing clients depend on it.`).
- Prohibit plausible substitutions explicitly ("MUST NOT replace the required SQLite persistence, even if faster").
- Write plain, testable constraints. For a repeatedly missed rule, shorten the file or enforce with a hook or deny rule instead of `IMPORTANT`, `CRITICAL`, ALL CAPS, or repeated `ALWAYS!!!`.

## Tools and permissions

- Explorers and auditors get read and search only.
- Reviewers and verifiers get read, search, and execute; no edit. Rationale: reviewers that navigate and run repository code catch more critical issues with fewer false positives than diff-only review. Where execute permits writes (shell), list a sandbox or deny rule as runtime control.
- Keep model and tool metadata separate from behavioral text; no credentials or provider-specific tool names in portable instructions.
- Model specialization (different model or effort for exploration, implementation, review) is optional; benchmark first.

## Verification

- Give an executable check and require evidence: command, exit code, logs, screenshots, or artifact. A completion statement alone is insufficient.
- Select affected checks for the change; do not run every test unconditionally.
- Require confirming the intended tests actually ran, not only that the command exited 0.
- Require each check reported as `passed | failed | unavailable | not run`; an intended or skipped check is never reported as passed.

## Coding agents

Apply to agents that edit code (implementer, fixer, refactorer, tester). Risk-based synthesis for large codebases, not a standard; validate a changed policy on comparable tickets (end-to-end time, rework, verifier pass rate, escaped regressions) before adopting it.

- **Context:** short body; link authoritative architecture, plan, and build/test docs conditionally. Point to repository build/test instructions and a prepared environment instead of command discovery by trial.
- **Scope:** one ticket or plan slice per run. Large change → plan first, or split planner and worker agents.
- **Exploration stop:** find affected symbols, callers, external boundaries, nearby conventions, actual test counterparts, smallest build boundary; stop when context suffices.
- **Implementation:** thin coherent slice; reuse existing models, utilities, test fakes, layering, naming; no speculative abstractions or unrelated cleanup.
- **Test strategy:** classify changed behavior and risk, then select; mandatory red-green-refactor for every change is not the default.

| Change | Strategy |
|---|---|
| Bug, regression | Reproduce with a failing test first |
| Uncertain or critical logic | Test-first (TDD) |
| Behavior-preserving refactor, legacy code | Characterization tests first |
| Public API, serialization, service boundary | Contract first, plus integration check |
| Clear feature, stable contracts | Focused test-after, including failure and boundary cases |
| Mechanical edit with proven coverage | Existing checks only |

- **Fast feedback:** build the affected project and run filtered tests after meaningful increments, not after every trivial edit; full suites only when impact requires it.
- **Architectural invariants:** enforce through structural tests, linters, dependency rules (Gate layer); the agent preserves existing conventions even when a shortcut looks simpler.

| Level | Owner | Scope | Trigger |
|---|---|---|---|
| Fast feedback | Implementer | Affected project, selected tests, diagnostics | Meaningful increments |
| Focused completion | Implementer | All changed behavior and affected integrations | Before handoff |
| Independent verification | Verifier, reviewer | Acceptance criteria, boundaries, architecture, omissions | After implementation |
| Broad regression | CI | Broader suites, system checks | Before merge or release |

Keep verifier and reviewer agents independent; changing an implementer must not weaken their checks.

Constraints every coding agent carries:

- MUST verify every material changed behavior with observed evidence. Rationale: test order may vary; confidence must not.
- MUST run relevant integration tests when changed boundaries can invalidate them. Rationale: unit success does not prove external behavior.
- MUST NOT weaken or rewrite a valid test to obtain a green result. Rationale: adapts the oracle to the bug.
- MUST NOT skip required checks to save time.
- RETURN changed behavior, commands run, per-check status, tests not run, unresolved risks.

## Planner agents

Apply to agents that decompose a feature, spec, or plan into tasks for independent implementers (parallel workers, worktrees). Synthesis of Cursor, OpenAI Symphony, Copilot, Anthropic agent-teams practice, October 2026; benchmark on representative features before imposing thresholds.

- **Goal:** accepted, integrated behavior per elapsed hour; not task count, agent count, or commits. A sequential graph is a valid result.
- **Role split:** planner owns requirement coverage, exploration, task contracts, blocker graph, conflict prediction, critical path. Scheduler owns DAG validation, slots, worktrees, dispatch, retries. Implementer owns one task. Integrator owns serialized merges and post-merge checks. Verifier owns integrated acceptance. Planner tools: read, search; no edit, no execute beyond read-only inspection. Rationale: workers cannot repair a planner's invented facts or scope creep.
- **Graph is data:** output a machine-readable task graph the scheduler consumes; deterministic code validates acyclicity and schedules. Prose plans alone are not executable.

Decomposition:

1. Inventory behaviors, rules, edge cases, acceptance criteria, existing tickets; flag contradictions.
2. Map affected code at the base revision: entry points, callers, contracts, composition roots, migrations, tests, ADRs, similar solutions.
3. Put unstable shared contracts (API, schema, interface, migration) in a prerequisite task.
4. Draft the fewest vertical slices covering all requirements; each has an observable result, a test seam, bounded write ownership.
5. Add a blocker edge only when the consumer cannot be implemented or verified against the base without the producer.
6. Predict write conflicts separately: shared files, DI registrations, manifests, lockfiles, migrations, generated output.
7. Validate: acyclic, every requirement covered, no unowned shared write surface, verification feasible, acceptance actionable.

| Decision | When |
|---|---|
| Split | Behaviors have independent acceptance and write surfaces; unrelated modules; uncertain contract needs investigation first |
| Keep together | Same critical files; untestable in isolation; split creates heavy communication |
| Sequence | Schema, public API, shared abstraction, or migration must exist before consumer compiles or verifies |
| Horizontal split | Only for independent module migrations, mechanical repo-wide edits, stable interface implementations |

- Size by coupling, context load, time to feedback, integration risk; never by fixed files, lines, or tasks per worker.
- **Time heuristic:** 30–120 minutes of estimated agent execution per focused task is a tentative starting range, not a hard limit; estimates are unreliable. Merge trivial work when overhead dominates; split large work only at independently verifiable, stable-contract, disjoint-write seams. Never force a split solely for the duration target.
- Tests ship with each behavior slice; no standalone "write tests" task per coding task. Independent black-box verification may be a downstream task.
- **Readiness:** a worker identifies behavior, permitted scope, real source context, contracts, executable checks, handoff format without asking another worker.

Constraints every planner carries:

- MUST ground paths, interfaces, test seams in the base revision. Rationale: invented interfaces fail at integration.
- MUST map every requirement and acceptance criterion to a task and a verification seam. Rationale: decomposition must not reduce scope.
- MUST resolve shared contracts before parallel consumers start. Rationale: consumers need compatible assumptions.
- MUST distinguish blocker edges from write conflicts. Rationale: they constrain scheduling differently.
- MUST keep write ownership non-overlapping for concurrently ready tasks. Rationale: worktrees isolate directories, not integration semantics.
- MUST preserve existing valid tickets, blockers, completed work when replanning; revise only affected unfinished tasks. Rationale: prevents duplicate work and history loss.
- MUST NOT create tasks or edges to fill worker capacity, even if the plan looks faster. Rationale: coordination can exceed speedup.
- MUST NOT turn shared reads, similarity, or a worker cap into blocker edges. Rationale: false dependencies lengthen the critical path.
- MUST NOT edit implementation code, manage worktrees, or guess product decisions; IF a decision is missing, THEN return it as an open question or a bounded investigation task.
- SHOULD reuse existing models, utilities, vocabulary, layering, ADRs; minimize refactoring.

Scheduler and integration guidance (record as workflow or gate, not planner prose): modest concurrency cap (start ~3); critical-path priority among ready tasks; integrate each task as it settles, not in fixed waves; a dependent starts only after its producer is integrated and verified; one worktree per in-flight task from the integrated base; serialized cherry-picks; isolate build outputs, ports, services per worktree; green PR gate required.

## Anti-patterns

| Avoid | Replace with |
|---|---|
| "Think step by step" / "think harder" / "never stop" | Model-specific reasoning or effort controls |
| Loading entire repo architecture before every edit | Conditional links to relevant documents |
| Generic engineering advice, repo facts discoverable from code | Delete |
| Mandatory red-green-refactor for every change | Risk-based test strategy (Coding agents) |
| Full solution suite after every edit | Affected build plus filtered tests; broad suites in CI |
| Diff-only reviewer without execute | Reviewer with repo navigation and execute, no edit |
| "Tests pass" without per-check status | `passed`, `failed`, `unavailable`, `not run` per check |
| Planner maximizing agents or tasks | Fewest coherent slices; sequential graph when coupling is high |
| One agent planning, implementing, reviewing | Separate planner, implementer, verifier roles |
| Layer-per-task split (entities, services, controllers, tests) | Vertical behavioral slices after shared contracts |
| Static plan never revised | Targeted replanning of affected unfinished tasks |
| Peer-to-peer file locking between workers | Ownership decided in the plan and scheduler |

## Checklist

- One responsibility with a narrow, observable outcome.
- Description states capability, trigger, exclusion; no overlap with sibling agents.
- Inputs, scope (owns / does not own), and escalation stated.
- Constraints use normative words sparingly; consequential ones carry rationale.
- Tools set explicitly with least privilege; runtime controls listed for invariants the prompt cannot enforce.
- Procedural work references skills; no copied procedure.
- Workflow short; each step has an observable result.
- Verification names executable checks and the evidence to record; per-check status required.
- Coding agent: test strategy selected by change risk; fast-feedback scope bounded; Coding agents constraints present; independent verification left to verifier, reviewer, CI.
- Planner agent: no edit tools; task graph output per planner output template; blockers separate from conflicts; requirement coverage mapped; Planner agents constraints present; scheduling left to workflow.
- Completion defines done, blocked behavior, and escalation.
- Output contract fits the next actor.
- No anti-pattern from the table; no secrets.
- Routing testable: a request for a sibling's role would not select this agent, and vice versa.

Sources: [Anthropic best practices](https://code.claude.com/docs/en/best-practices), [Claude subagents](https://code.claude.com/docs/en/sub-agents), [Claude extension layers](https://code.claude.com/docs/en/features-overview), [OpenAI prompt guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), [Codex subagents](https://developers.openai.com/codex/subagents), [Codex customization](https://developers.openai.com/codex/customization/overview), [Copilot custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration), [Copilot customization comparison](https://docs.github.com/en/copilot/concepts/customizations/comparing-customizations), [Grok Build subagents](https://docs.x.ai/build/features/subagents), [Gemini CLI subagents](https://geminicli.com/docs/core/subagents/), [OpenAI harness engineering](https://openai.com/index/harness-engineering/), [OpenAI verifying code at scale](https://alignment.openai.com/scaling-code-verification/), [Cursor scaling agents](https://cursor.com/blog/scaling-agents), [Cursor self-driving codebases](https://prod.cursor.com/blog/self-driving-codebases), [OpenAI Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/), [Copilot delegating and parallelizing](https://docs.github.com/en/copilot/concepts/agent-capabilities/choosing-and-delegating-agent-work/delegating-and-parallelizing-work-with-agents), [Claude agent teams](https://code.claude.com/docs/en/agent-teams), [git worktree](https://git-scm.com/docs/git-worktree), [GitHub cloud agent best results](https://docs.github.com/en/copilot/tutorials/cloud-agent/get-the-best-results), [Google testing levels](https://testing.googleblog.com/2021/06/how-much-testing-is-enough.html).
