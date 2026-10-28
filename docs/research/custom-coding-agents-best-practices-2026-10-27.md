# Custom Coding Agents: Industry Best Practices (2026)

Research date: 2026-10-27  
Scope: Claude Code, GitHub Copilot, OpenAI Codex, Grok Build (xAI), Gemini CLI.  
Purpose: reusable custom coding-agent instructions, configuration, tool permissions, and workflow contracts.

## Bottom line

**Use small, specialized agents with clear invocation rules, bounded responsibilities, explicitly configured tools, and verifiable outcomes.** Keep repository-wide rules, reusable skills, runtime gates, and agent identities separate. Recent vendor guidance favors concise, contextual instructions over elaborate prompts and repeated emphasis.

These are synthesized recommendations, not a universal agent-file specification. Platform settings and discovery mechanisms differ.

## 1. Industry recommendations

| Priority | Practice | Recommendation | Rationale |
| --- | --- | --- | --- |
| MUST | One responsibility | Define a narrow, observable outcome for each agent. | Reduces overlapping delegation and scope drift. |
| MUST | Invocation contract | State when to use the agent and when not to. | Descriptions control automatic selection in several CLIs. |
| MUST | Explicit boundaries | Describe inputs, allowed work, prohibited work, and escalation. | Prevents unintended adjacent tasks. |
| MUST | Verification | Give an executable check and require evidence. | A completion statement alone is insufficient. |
| MUST | Runtime enforcement | Apply permissions, hooks, sandboxes, or CI for invariant rules. | Instructions are probabilistic, not a security boundary. |
| SHOULD | Concise instructions | Remove generic engineering advice, redundant personas, and repo facts discoverable from code. | Less conflicting context and lower cost. |
| SHOULD | Progressive disclosure | Put detailed procedures in skills and load relevant references only when needed. | Keeps unrelated task context out. |
| SHOULD | Least-privilege tools | Give each agent only the tools needed for its role. | Limits accidental writes and external actions. |
| SHOULD | Output contract | Return changes/findings, checks, evidence, and blockers. | Enables downstream workflow consumption. |
| MAY | Model specialization | Use different models/effort for exploration, implementation, and review. | Can optimize cost and latency; benchmark first. |

Official basis: [Anthropic best practices](https://code.claude.com/docs/en/best-practices), [OpenAI's September 2026 guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), [GitHub customization comparison](https://docs.github.com/en/copilot/concepts/customizations/comparing-customizations).

## 2. Separate the customization layers

| Layer | Owns | Examples |
| --- | --- | --- |
| Repository instructions | Durable, generally applicable project rules | `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` |
| Custom agent | Specialized role, invocation, responsibilities, output | Developer, Reviewer, Tester, Address, Maintainer |
| Skill | Reusable procedure, instructions, references, scripts | `to-spec`, `to-tickets`, `code-review`, `verify` |
| Tool / MCP | Callable capability and external service access | File read, shell, GitHub API, browser |
| Workflow | Trigger, scheduling, ordering, retries, handoffs | Ticket → Developer → Review → Address |
| Gate | Deterministic pass/fail control | Unit tests, branch protection, required checks |

Do not encode workflow scheduling or security enforcement solely as an agent prompt. In Loop, an agent defines **who**, a skill defines **how**, a tool defines **what it can call**, a workflow defines **when**, and a gate decides **whether it may proceed**.

Sources: [Claude extension layers](https://code.claude.com/docs/en/features-overview), [Codex customization](https://developers.openai.com/codex/customization/overview), [Copilot customization](https://docs.github.com/en/copilot/concepts/customizations/comparing-customizations).

## 3. Platform comparison (October 2026)

| Platform | Project agent definition | Format | Selected metadata | Notes |
| --- | --- | --- | --- | --- |
| Claude Code | `.claude/agents/*.md` | YAML frontmatter + Markdown | `name`, `description`, `tools`, `model`, `skills`, `memory`, `isolation`, `permissionMode` | The Markdown body is the subagent system prompt. |
| GitHub Copilot | `.github/agents/*.agent.md` or `.github/agents/*.md` | YAML frontmatter + Markdown | `name`, `description`, `tools`, `model`, `target`, invocation controls | IDE and cloud support differ; IDE handoffs are not supported by GitHub cloud agent. |
| OpenAI Codex | `.codex/agents/*.toml` | TOML | `name`, `description`, `developer_instructions`, model settings, feature toggles | Custom agents inherit parent permissions; prompt text does not create a read-only sandbox. |
| Grok Build | `.grok/agents/` | Grok-specific agent definitions | Agent types and personas | Built-in `general-purpose`, `explore`, `plan`; persona overlays configure behavior. |
| Gemini CLI | `.gemini/agents/*.md` | YAML frontmatter + Markdown | `name`, `description`, `tools`, `model`, `max_turns`, `timeout_mins` | Agent descriptions guide automatic delegation. |

Platform docs: [Claude subagents](https://code.claude.com/docs/en/sub-agents), [Copilot agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration), [Codex subagents](https://developers.openai.com/codex/subagents), [Grok Build subagents](https://docs.x.ai/build/features/subagents), [Gemini CLI subagents](https://geminicli.com/docs/core/subagents/).

Repository instruction file support is not identical:

- Claude Code: `CLAUDE.md` and supported `AGENTS.md` discovery, plus scoped `.claude/rules/`.
- Copilot CLI: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, and path-specific instructions. Supported files vary across Copilot surfaces; combined instructions have no general precedence guarantee.
- Codex: `AGENTS.md`, hierarchical overrides, a size limit (32 KiB by default).
- Grok Build: `AGENTS.md`, related compatibility names, and nested scoped rules.
- Gemini CLI: `GEMINI.md` project context; custom agents are separate definition files.

Sources: [Claude memory](https://code.claude.com/docs/en/memory), [Copilot CLI instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions), [Codex AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md), [Grok project rules](https://docs.x.ai/build/features/project-rules), [Gemini subagents](https://geminicli.com/docs/core/subagents/).

## 4. Leading words and constraint language

Use simple normative vocabulary for clarity, **not** because models have a special keyword interpreter:

| Word | Intent | Example |
| --- | --- | --- |
| `MUST` | Required | MUST run relevant tests before completion. |
| `MUST NOT` | Prohibited | MUST NOT modify unrelated files. |
| `SHOULD` | Preferred | SHOULD reuse an existing domain service. |
| `MAY` | Optional | MAY add regression tests for uncovered edge cases. |
| `IF ... THEN ...` | Conditional | IF blocked, THEN report the missing decision. |
| `STOP` | Stop condition | STOP if an action requires an unavailable credential. |
| `RETURN` | Output contract | RETURN findings with file references and evidence. |

For consequential constraints, include a terse rationale:

```markdown
- MUST preserve the public API.
  Rationale: Existing clients depend on it.
- MUST NOT replace the required SQLite persistence mechanism,
  even if another approach is faster or simpler.
  Rationale: The architecture decision is already approved.
- SHOULD reuse existing domain services.
  Rationale: Avoid duplicate business rules.
```

Use `MUST` sparingly for actual invariants. Modern Anthropic guidance explicitly discourages adding `IMPORTANT` or ALL CAPS to repeatedly missed instructions; shorten the file or enforce the rule with a hook or deny rule. Generic “think harder”, “never stop”, and “you are a world-class expert” filler does not define an observable outcome. [Anthropic best practices](https://code.claude.com/docs/en/best-practices).

**No prompt wording guarantees a restriction.** Enforce unsafe operations through the runtime, not just `MUST NOT` text.

## 5. Recommended sections and order

| # | Section | Content | Required? |
| --- | --- | --- | --- |
| 1 | Identity | One-sentence role and outcome | Yes |
| 2 | Invocation | Use when / do not use when | Yes |
| 3 | Inputs | Task contract and necessary context | Yes |
| 4 | Scope | Owns / does not own | Yes |
| 5 | Constraints | Non-negotiable rules, limits, rationale | Yes |
| 6 | Tools & permissions | Tools needed and authorization boundaries | Yes; configure in the runtime |
| 7 | Workflow | Short ordered steps | Yes |
| 8 | Verification | Executable checks, evidence | Yes |
| 9 | Completion | Definition of done, blockers, escalation | Yes |
| 10 | Output | Return schema for the next actor | Yes |

The sections are a **cross-vendor synthesis**, not required names. Combine sections for a very small agent. Put lengthy procedures or examples in skills instead.

### Portable agent body

```markdown
# Role

You are [agent]. Your responsibility is [specific outcome].

## Invocation

Use when [trigger].
Do not use when [exclusion].

## Inputs

- [Required task input]
- [Relevant references]

## Scope

- Own [responsibility].
- Do not perform [adjacent work].

## Constraints

- MUST [non-negotiable requirement].
- MUST NOT [prohibited action].
- SHOULD [preferred approach].

## Workflow

1. Inspect relevant context.
2. Execute work within the assigned scope.
3. Run applicable verification.
4. Return results and evidence.

## Verification

- Run [specific check].
- Confirm [acceptance criterion].
- Record command, result, or artifact.

## Completion and failure

- Done when [observable conditions].
- If blocked, report the missing decision; do not invent requirements.
- Preserve recoverable unfinished work.

## Output

Return outcome, changes/findings, verification evidence, and blockers.
```

## 6. Agent descriptions and routing

The description is a **routing interface**. Keep it short, concrete, and exclusive. This is particularly important for automatic subagent selection in Claude Code and Gemini CLI, and for Copilot's specialized agents.

Recommended pattern: `[Capability]. Use when [trigger]. Do not use when [exclusion].`

| Loop agent | Example description |
| --- | --- |
| Developer | Implement actionable GitHub tickets. Use when requirements are clear and no human decision blocks implementation. |
| Reviewer | Review completed changes for correctness, regressions, security, and test gaps. Use before PR merge. |
| Tester | Create and execute behavior verification. Use when functionality changes or test coverage is insufficient. |
| Address | Resolve actionable PR review findings. Use when unresolved review comments require code changes. |
| Maintainer | Evaluate PR merge readiness and complete authorized merge actions. Use after required checks and reviews. |

Avoid vague, overlapping descriptions such as “expert developer”, “general-purpose coding assistant”, or “helps with software engineering”. OpenAI also recommends descriptions narrow enough to avoid triggering a skill for adjacent tasks. Sources: [Claude subagents](https://code.claude.com/docs/en/sub-agents), [Gemini subagents](https://geminicli.com/docs/core/subagents/), [OpenAI prompt guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).

## 7. Distinct custom agent examples

The official libraries provide several **different specialist roles**, not merely the same Reviewer ported to multiple CLIs:

| Role | Official example | Responsibility |
| --- | --- | --- |
| Reviewer | [Anthropic](https://code.claude.com/docs/en/sub-agents) | Find actionable problems without editing code. |
| Debugger | [Anthropic](https://code.claude.com/docs/en/sub-agents) | Reproduce a failure, fix its cause, verify it. |
| Test specialist | [GitHub](https://docs.github.com/en/copilot/reference/custom-agents-configuration) | Improve test coverage without editing production behavior. |
| Implementation planner | [GitHub](https://docs.github.com/en/copilot/reference/custom-agents-configuration) | Break requirements into an actionable implementation plan. |
| Codebase explorer | [OpenAI Codex](https://developers.openai.com/codex/subagents) | Trace execution paths and gather code evidence. |
| Documentation researcher | [OpenAI Codex](https://developers.openai.com/codex/subagents) | Verify version-specific APIs against official documentation. |
| Security auditor | [Gemini CLI](https://geminicli.com/docs/core/subagents/) | Find security weaknesses and report findings. |

The following are concise, source-inspired **adaptations**, not verbatim vendor examples. They demonstrate different roles across CLIs. Validate model names and available tools against the installed client.

### 7.1 Reviewer — Claude Code: `.claude/agents/reviewer.md`

```markdown
---
name: reviewer
description: Review changes for correctness, regressions, and security risks. Use after implementation or before PR merge.
tools: Read, Glob, Grep
model: sonnet
---

# Role

Review changes independently.

## Constraints

- MUST NOT edit implementation files.
- MUST report only actionable findings.
- MUST provide file references and evidence.
- SHOULD prioritize correctness over style.

## Workflow

1. Inspect changed code and relevant callers.
2. Trace affected behavior.
3. Identify reproducible defects.
4. Return evidence-based findings.

## Output

For each finding return location, impact, evidence, and correction.
```

Claude accepts YAML frontmatter and Markdown body; `name` and `description` are required. The above tool allowlist excludes editing tools. [Claude subagents](https://code.claude.com/docs/en/sub-agents).

### 7.2 Debugger — Claude Code: `.claude/agents/debugger.md`

```markdown
---
name: debugger
description: Diagnose and fix reproducible defects. Use when a failure, exception, or regression has evidence.
tools: Read, Edit, Grep, Glob, Bash
---

# Role

Find and fix the root cause of the reported failure.

## Constraints

- MUST reproduce the problem before changing code when feasible.
- MUST make the smallest defensible correction.
- MUST NOT change unrelated behavior.

## Workflow

1. Capture error details and reproduction steps.
2. Trace the failing execution path and test hypotheses.
3. Apply the minimal fix.
4. Run regression checks and record results.

## Output

Return root cause, changed files, reproduction and verification evidence.
```

Adapted from Anthropic's official Debugger example, which intentionally includes editing tools. [Claude subagents](https://code.claude.com/docs/en/sub-agents).

### 7.3 Developer — GitHub Copilot: `.github/agents/developer.agent.md`

```markdown
---
name: developer
description: Implement an actionable ticket with tests. Use when requirements are clear and implementation is authorized.
tools: ["read", "search", "edit", "execute"]
---

# Role

Implement the assigned ticket.

## Constraints

- MUST preserve public contracts unless the ticket explicitly changes them.
- MUST NOT expand scope or modify unrelated files.
- MUST report missing decisions instead of inventing requirements.

## Workflow

1. Read the ticket, acceptance criteria, and affected code.
2. Implement the smallest complete change.
3. Add or update relevant tests.
4. Run affected checks and inspect the diff.

## Output

Return changed files, completed requirements, test evidence, and blockers.
```

This is a Loop-oriented implementation agent, inspired by Codex's focused `ui_fixer` example and expressed with Copilot's documented tool aliases. [Codex examples](https://developers.openai.com/codex/subagents), [Copilot tool aliases](https://docs.github.com/en/copilot/reference/custom-agents-configuration).

### 7.4 Test specialist — GitHub Copilot: `.github/agents/test-specialist.agent.md`

```markdown
---
name: test-specialist
description: Improve test coverage and verify changed behavior. Use for missing tests, failing checks, or regression scenarios.
tools: ["read", "search", "edit", "execute"]
---

# Role

Write and run behavior-focused tests.

## Constraints

- MUST NOT modify production code.
- MUST make tests deterministic and isolated.
- MUST preserve the original failing result as evidence before fixing a test.

## Workflow

1. Identify behaviors and missing coverage.
2. Add focused unit or integration tests.
3. Run relevant tests and inspect failures.
4. Report the observed results, not just a pass/fail claim.

## Output

Return test files, covered behaviors, commands, results, and gaps.
```

Adapted from GitHub's official Testing Specialist. The explicit allowlist is narrower than the source example, which omits `tools` and therefore enables all available tools. [Copilot examples](https://docs.github.com/en/copilot/reference/custom-agents-configuration).

### 7.5 Implementation planner — GitHub Copilot: `.github/agents/implementation-planner.agent.md`

```markdown
---
name: implementation-planner
description: Create an implementation plan from approved requirements. Use before coding complex changes.
tools: ["read", "search", "edit"]
---

# Role

Turn requirements into a reviewable implementation plan.

## Constraints

- MUST NOT implement production code.
- MUST identify decisions and external dependencies.
- MUST state acceptance criteria and verification work.

## Workflow

1. Inspect requirements and affected architecture.
2. Break work into ordered, independently verifiable tasks.
3. Identify risks, dependencies, and missing decisions.
4. Write the plan as Markdown.

## Output

Return tasks, dependencies, acceptance criteria, risks, and blockers.
```

Adapted from GitHub's official Implementation Planner. This remains a planning agent even though its tool list permits editing the plan file. [Copilot examples](https://docs.github.com/en/copilot/reference/custom-agents-configuration).

### 7.6 Codebase explorer — Codex: `.codex/agents/code-explorer.toml`

```toml
name = "code_explorer"
description = "Trace relevant execution paths and gather code evidence. Use before planning or changing unfamiliar code."

developer_instructions = """
# Role

Map the code responsible for the assigned behavior.

## Constraints

- MUST NOT modify implementation files.
- MUST cite actual paths and symbols.
- MUST distinguish observed behavior from hypotheses.

## Workflow

1. Find entry points and affected callers.
2. Trace state transitions and dependencies.
3. Inspect focused code paths.
4. Report the relevant symbols and evidence.

## Output

Return entry points, call paths, dependencies, and uncertainties.
"""
```

Adapted from Codex's official `pr_explorer` and `code_mapper` examples. Codex requires `name`, `description`, and `developer_instructions`. The no-edit instruction is guidance, not an isolated read-only sandbox. [Codex subagents](https://developers.openai.com/codex/subagents).

### 7.7 Security auditor — Gemini CLI: `.gemini/agents/security-auditor.md`

```markdown
---
name: security-auditor
description: Identify security weaknesses in a code change. Use for authentication, authorization, input handling, and secret exposure reviews.
kind: local
tools:
  - read_file
  - grep_search
max_turns: 10
---

# Role

Audit assigned code for exploitable weaknesses.

## Constraints

- MUST NOT edit files.
- MUST explain exploitability and affected code paths.
- MUST NOT report speculative risks without evidence.

## Workflow

1. Identify trust boundaries and external inputs.
2. Trace authentication, authorization, and data handling.
3. Verify concrete weaknesses.
4. Report actionable findings.

## Output

Return location, risk, evidence, and remediation.
```

Adapted from Gemini CLI's official Security Auditor example, which also demonstrates an agent-specific tool allowlist and turn limit. [Gemini CLI subagents](https://geminicli.com/docs/core/subagents/).

These are samples, not a requirement to maintain seven agents. Create a specialist only for recurring work that benefits from distinct instructions, tools, or isolated context.

## 8. Anti-patterns replaced in 2026

| Avoid | Replace with |
| --- | --- |
| Large inspirational persona | One-sentence role and observable outcome |
| Repeated `CRITICAL!!!` / `ALWAYS!!!` | Plain, testable constraints; enforcement where needed |
| “Think step by step” / “think harder” | Model-specific reasoning/effort controls |
| Loading entire repo architecture before every edit | Conditional links to relevant documents |
| Rigid 30-step itinerary for every task | Short workflow plus meaningful checks |
| Running every test unconditionally | Affected checks selected for the change |
| Trusting “tests pass” in final prose | Command, exit code, logs, screenshots, or evidence artifact |
| All tools enabled on all agents | Least-privilege capabilities and permissions |
| Several agents with overlapping descriptions | Clear routing triggers and exclusions |
| Prompts pretending to enforce security | Runtime sandbox, deny rules, hooks, branch protection |

Sources: [Anthropic best practices](https://code.claude.com/docs/en/best-practices), [OpenAI guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), [GitHub Copilot guidance](https://docs.github.com/en/copilot/concepts/customizations/comparing-customizations).

## 9. Recommendations for `antshc/loop` and `antshc/brain`

1. **Define one canonical behavioral contract per agent** in a shared source directory; render adapters for Claude, Copilot, and Codex as needed. This is a Loop-specific proposal, not vendor discovery behavior.
2. **Keep model and tool metadata separate from behavioral text** where practical; do not embed credentials or provider-specific tool names in the canonical instructions.
3. **Reference skills for procedural work** (`to-spec`, `code-review`, proof) rather than copying large instructions into every agent.
4. **Use factory gates for observable completion**. Agents report evidence; workflow code evaluates the check and decides the transition.
5. **Test agent routing** with positive and negative prompts: a Developer request should not select Reviewer, and a read-only Reviewer request should not select Developer.
6. **Test instruction adherence against actual tool traces and artifacts**, not only an agent's self-report.
7. **Version and audit prompts**. Add a rule when a mistake recurs; remove stale rules when the model or workflow changes.

Suggested portable source layout:

```text
agents/                      # Proposed canonical source; not auto-discovered
  developer.md
  reviewer.md
  tester.md
  address.md
  maintainer.md
.claude/agents/              # Claude adapter
.github/agents/              # Copilot adapter
.codex/agents/               # Codex adapter
```

## Primary official sources

- Anthropic — [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices)
- Anthropic — [Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- Anthropic — [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- Anthropic — [Extend Claude Code](https://code.claude.com/docs/en/features-overview)
- OpenAI — [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), September 11, 2026
- OpenAI — [Codex subagents](https://developers.openai.com/codex/subagents)
- OpenAI — [Codex AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- OpenAI — [Codex customization](https://developers.openai.com/codex/customization/overview)
- GitHub — [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- GitHub — [Comparing Copilot customization features](https://docs.github.com/en/copilot/concepts/customizations/comparing-customizations)
- GitHub — [Copilot CLI custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)
- xAI — [Grok Build subagents](https://docs.x.ai/build/features/subagents)
- xAI — [Grok Build project rules](https://docs.x.ai/build/features/project-rules)
- Google — [Gemini CLI subagents](https://geminicli.com/docs/core/subagents/)

*Research compares documentation available on 2026-10-27. Exact fields, model aliases, and client coverage can change. Verify the target CLI before installation.*
