# Agent best practices

Cross-vendor synthesis (Claude Code, GitHub Copilot, OpenAI Codex, Grok Build, Gemini CLI), October 2026; not a universal spec.

**Root rule:** small, specialized agent; clear invocation; bounded responsibility; explicitly configured tools; verifiable outcome.

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

- Read-only roles (reviewer, explorer, auditor) get read and search only.
- Keep model and tool metadata separate from behavioral text; no credentials or provider-specific tool names in portable instructions.
- Model specialization (different model or effort for exploration, implementation, review) is optional; benchmark first.

## Verification

- Give an executable check and require evidence: command, exit code, logs, screenshots, or artifact. A completion statement alone is insufficient.
- Select affected checks for the change; do not run every test unconditionally.

## Anti-patterns

| Avoid | Replace with |
|---|---|
| "Think step by step" / "think harder" / "never stop" | Model-specific reasoning or effort controls |
| Loading entire repo architecture before every edit | Conditional links to relevant documents |
| Generic engineering advice, repo facts discoverable from code | Delete |

## Checklist

- One responsibility with a narrow, observable outcome.
- Description states capability, trigger, exclusion; no overlap with sibling agents.
- Inputs, scope (owns / does not own), and escalation stated.
- Constraints use normative words sparingly; consequential ones carry rationale.
- Tools set explicitly with least privilege; runtime controls listed for invariants the prompt cannot enforce.
- Procedural work references skills; no copied procedure.
- Workflow short; each step has an observable result.
- Verification names executable checks and the evidence to record.
- Completion defines done, blocked behavior, and escalation.
- Output contract fits the next actor.
- No anti-pattern from the table; no secrets.
- Routing testable: a request for a sibling's role would not select this agent, and vice versa.

Sources: [Anthropic best practices](https://code.claude.com/docs/en/best-practices), [Claude subagents](https://code.claude.com/docs/en/sub-agents), [Claude extension layers](https://code.claude.com/docs/en/features-overview), [OpenAI prompt guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), [Codex subagents](https://developers.openai.com/codex/subagents), [Codex customization](https://developers.openai.com/codex/customization/overview), [Copilot custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration), [Copilot customization comparison](https://docs.github.com/en/copilot/concepts/customizations/comparing-customizations), [Grok Build subagents](https://docs.x.ai/build/features/subagents), [Gemini CLI subagents](https://geminicli.com/docs/core/subagents/).
