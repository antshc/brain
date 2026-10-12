# Naming the result-check section of a skill

Evidence behind the `## Completion criteria` rule in [agent-skills.instructions.md](../../.github/instructions/agent-skills.instructions.md).

## Question

What do public agent-skill authors call the section that states how to tell a skill's result is done, and which name fits skills here? It must describe the observed result, never the commands that run a test suite.

## Sources read

Read on 2026-10-09.

| Source | URL |
| --- | --- |
| Addy Osmani, `agent-skills` | https://github.com/addyosmani/agent-skills |
| Matt Pocock, `skills` and `writing-for-agents` | https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md |
| GitHub `spec-kit` | https://github.com/github/spec-kit |
| Brady Gaster, `squad` | https://github.com/bradygaster/squad |
| Garry Tan, `gstack` | https://github.com/garrytan/gstack |
| Affaan Mustafa, `ECC` | https://github.com/affaan-m/ECC |
| Cursor `pstack` | https://github.com/cursor/plugins/tree/main/pstack |
| Anthropic, skill authoring best practices | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| `awesome-copilot` agent-skills instructions | https://github.com/github/awesome-copilot/blob/main/instructions/agent-skills.instructions.md |
| Agent Skills best practices | https://agentskills.io/skill-creation/best-practices |

Not read: the YouTube video, `agents.instructions.md`, "Building effective agents", the custom-agents configuration reference, and the two C# instruction files. `pstack` was read at README level only.

## Findings

No source names a section "Exit criteria" or "Completion criteria". The closest terms:

| Source | Term | Meaning |
| --- | --- | --- |
| Osmani | `## Verification`, with Rationalizations and Red Flags | Evidence requirements for the result: tests passing, build output, runtime data. Prose also says "exit criteria with evidence requirements". Separate `definition-of-done.md` holds the standing bar, contrasted with per-task acceptance criteria. |
| Pocock | "Steps and completion criteria" | Every step ends on a completion criterion. Clarity prevents premature completion; demand drives legwork. Strongest criteria are checkable and exhaustive. |
| spec-kit | Verdicts `verified`, `partial`, `failed`; `converge` ends at "Converged" | Graded outcome. "Missing verification is not a successful fix." |
| Squad | `### Success Criteria`, `### When to Escalate`, inline `✓ Validate:` | Criteria listed in the work prompt; per-step checks after each setup step. |
| gstack | Verification-evidence ledger (FRESH / STALE / MISSING), verify gate | Result evidence bound to working-tree state. |
| ECC | "Verification Loops", "evidence trail" | Checks loop until they pass. |
| Anthropic | Validation loops, checklists, verifiable intermediate outputs | No dedicated section; the validator is a workflow step. |
| awesome-copilot | When to Use, Prerequisites, Gotchas, Troubleshooting, References | No result-check section for the skill. |

Other sections worth noting: Rationalizations (excuses with rebuttals), Red Flags, Troubleshooting (symptom to fix, reactive; Gotchas are proactive), When to Escalate.

## Candidate names

| Name | Origin | Fit |
| --- | --- | --- |
| Exit criteria | ISTQB, ISO/IEC/IEEE 29119: conditions for officially completing a task | Considered first; formal, but a testing-process term. |
| Verification | Osmani, spec-kit, ECC, gstack; IEEE 1012 V&V | Most common, but reads as an activity and drifted into test-running sections here. Usable if defined as evidence of the result. |
| Completion criteria | Pocock ("completion criterion") | Chosen. Same meaning as Exit criteria, names the condition that tells the agent a step or skill is done, and does not suggest running tests. |
| Success criteria | Squad, OKR usage | Looser, outcome-oriented. |
| Definition of Done | Scrum; Osmani's checklist | A standing team-wide bar, not one skill's output. |
| Acceptance criteria | Agile user stories | Already used for stories here (`draft-story`, `to-story`). |
| Postconditions | Design by contract, UML | Precise but code-contract flavored. |

## Completion criteria versus completeness sweep

[Completion criteria](../../.github/instructions/agent-skills.instructions.md) define checkable conditions on the *expected result*. A [Completeness Sweep](../concepts/ops-completeness-sweep.md) is a *last coverage pass* that reconstructs all obligations and checks whether anything was omitted. Criteria answer "does the result meet its contract?"; the sweep answers "did we cover the whole requested scope?". Neither substitutes for correctness review or testing.

| Situation | Completion criteria | Completeness sweep | Rationale |
| --- | --- | --- | --- |
| Rename a method with one known caller | Only if step checks do not already prove the result | No | Small, bounded and directly observable. |
| Generate a diagram from a defined set of components | Yes, if coverage/relationships are not self-evident | No, if criteria enumerate the full input scope | Finite deliverable; avoid redundant checks. |
| Add a service with several operations | Yes | When callers, branches or error paths can be missed | Multiple independent obligations. |
| Refactor a component or implement a feature | Yes | Yes | Changes span contracts, callers, tests and behavior. |
| Implement RBAC across API, GUI and upgrades | Yes | Yes | A passing new-installation flow can hide a missing upgrade migration. |
| Research architecture across several systems | Yes, if a deliverable is specified | Yes, when source/concern coverage is not bounded | Conclusions can omit a system or constraint. |

### Example: implement RBAC

Completion criteria (specified in the skill): the API enforces roles; the GUI hides disallowed actions; unauthorized calls return 403; required test evidence exists.

Completeness sweep (performed last): re-read the request; reconstruct obligations for new and upgraded installations, role assignments, API and GUI paths, tests, documentation, configuration and error handling; map each to evidence; implement uncovered work, ask, or explicitly defer it. A missing Keycloak upgrade migration fails the sweep even if the tested new-installation behavior meets its criteria.

**Selection rule:** add `## Completion criteria` only when the result is not already proved by procedural checks. Add a closing completeness sweep when the scope contains independent obligations that can be silently omitted. Omit the sweep for small, bounded outputs if the step checks or completion criteria demonstrably cover every obligation. If used, the sweep runs after all other passes.

## Outcome

Use **Completion criteria**. Open options not yet adopted: a graded outcome (`verified | partial | failed`) inside the section, Rationalizations and Red Flags tables for the `ralph` skills, a Troubleshooting section, and When to Escalate.
