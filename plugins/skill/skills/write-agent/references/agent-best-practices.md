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
- Completion defines done, blocked behavior, and escalation.
- Output contract fits the next actor.
- No anti-pattern from the table; no secrets.
- Routing testable: a request for a sibling's role would not select this agent, and vice versa.

Sources: [Anthropic best practices](https://code.claude.com/docs/en/best-practices), [Claude subagents](https://code.claude.com/docs/en/sub-agents), [Claude extension layers](https://code.claude.com/docs/en/features-overview), [OpenAI prompt guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), [Codex subagents](https://developers.openai.com/codex/subagents), [Codex customization](https://developers.openai.com/codex/customization/overview), [Copilot custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration), [Copilot customization comparison](https://docs.github.com/en/copilot/concepts/customizations/comparing-customizations), [Grok Build subagents](https://docs.x.ai/build/features/subagents), [Gemini CLI subagents](https://geminicli.com/docs/core/subagents/), [OpenAI harness engineering](https://openai.com/index/harness-engineering/), [OpenAI verifying code at scale](https://alignment.openai.com/scaling-code-verification/), [Cursor scaling agents](https://cursor.com/blog/scaling-agents), [GitHub cloud agent best results](https://docs.github.com/en/copilot/tutorials/cloud-agent/get-the-best-results), [Google testing levels](https://testing.googleblog.com/2021/06/how-much-testing-is-enough.html).
