
# Agent Skills: Latest Writing Best Practices (October 2026)

Based on guidance from the Agent Skills specification, Anthropic, OpenAI, and GitHub Copilot.

**Core principle:** Write Agent Skills as small, executable workflows with precise triggering conditions, explicit constraints, progressive disclosure, and verifiable completion criteria.

## 1. Four Core Principles

1. **Discoverability:** The skill description determines when an agent selects the skill. Describe what it does, when to use it, and recognizable triggers.
2. **Instruction precision:** Define required behavior, permitted decisions, prohibited substitutions, and failure handling.
3. **Context efficiency:** Keep essential instructions in `SKILL.md`. Load detailed references only when needed.
4. **Empirical verification:** Test whether the skill activates correctly and produces the expected result on realistic tasks.

## 2. Recommended Best Practices

| Practice | Recommendation | Priority |
|---|---|---|
| Trigger description | Describe what the skill does and when to use it | Critical |
| Single responsibility | One coherent workflow per skill | High |
| Imperative instructions | Use direct commands: Read, Run, Verify | High |
| Constraints | Express non-negotiable behavior explicitly | High |
| Progressive disclosure | Move specialized details into references | Critical |
| Degrees of freedom | Specify exact procedures only when necessary | High |
| Output contract | Define what the agent must produce | High |
| Verification | Define observable success conditions | High |
| Examples | Include examples for ambiguous behavior | Medium |
| Error handling | Define recovery, retries, and escalation | High |
| Deterministic scripts | Use scripts for repetitive or fragile operations | High |
| Skill evaluation | Test activation, correctness, and regressions | Critical |

Priorities are authoring recommendations, not official specification requirements.

## 3. Instruction Precision

Instruction precision makes agent behavior predictable without unnecessarily restricting implementation choices.

### Recommended instruction patterns

| Pattern | Weak | Better |
|---|---|---|
| Imperative | Consider running tests | Run the relevant tests |
| Constraint | Try to use existing tools | MUST use the existing tool |
| Conditional | Handle missing dependencies | If the dependency is unavailable, report the blocker |
| Scope | Keep changes small | Modify only files required by the task |
| Rationale | Use a subagent | Delegate exploration to preserve parent context |
| Verification | Make sure everything works | Run affected tests and report results |
| Completion | Finish the task | Complete only when required outputs exist and verification passes |
| Reference loading | Read documentation | Read `references/aws.md` when targeting AWS |

### Constraint → Mechanism → Rationale → Failure Behavior

Use this pattern for critical requirements.

**Constraint:** What MUST or MUST NOT happen?

**Mechanism:** How must the agent execute the requirement?

**Rationale:** Why does this mechanism matter?

**Failure behavior:** What happens when execution is blocked?

Example:

> MUST delegate codebase exploration to a subagent.
>
> The subagent must return relevant file paths and supporting evidence.
>
> MUST NOT substitute direct exploration, even if faster or simpler.
>
> Rationale: Preserve parent context and isolate exploratory responsibility.
>
> If delegation is unavailable, report the blocker rather than silently substituting another mechanism.

Use `MUST` and `MUST NOT` for mandatory rules only. Use ordinary imperative language for workflow steps and `prefer` for defaults that allow alternatives.

A rationale helps an agent interpret a requirement, but it does not guarantee compliance. Verify critical constraints through observable actions or external checks.

## 4. Recommended SKILL.md Template

```markdown
---
name: review-design
description: Reviews software designs for correctness,
  feasibility, risks, and missing decisions.
  Use when evaluating architecture proposals,
  design documents, or implementation approaches.
---

# Review Design

## Inputs

- Design document or implementation proposal.
- Repository context, when available.

## Constraints

- MUST distinguish verified facts from assumptions.
- MUST NOT modify implementation files.
- MUST report unresolved critical issues.

## Workflow

1. Read the design and relevant context.
2. Identify system boundaries and contracts.
3. Review each category in
   [Review Checklist](references/checklist.md).
4. Record findings with supporting evidence.
5. Identify risks, trade-offs, and open decisions.
6. Verify every applicable category was reviewed.

## Output

Return:
- Findings ordered by severity.
- Evidence for each finding.
- Recommended corrections.
- Open decisions and unresolved questions.

## Completion criteria

- Every applicable category has a review result.
- Every finding has supporting evidence.
- Unverified claims are marked as assumptions.
- Incomplete review scope is explicitly reported.
```

### Recommended directory structure

```text
review-design/
├── SKILL.md
├── references/
│   ├── checklist.md
│   └── examples.md
└── scripts/
    └── validate.py
```

Keep `SKILL.md` concise. The specification recommends fewer than 500 lines; 100–250 lines is a useful stricter editorial target.

Include only sections that materially help execution. Avoid duplicating instructions in workflow, output, and completion sections.

## 5. Progressive Disclosure

Use three levels of instruction loading:

1. **Metadata:** Skill name and description for discovery.
2. **SKILL.md:** Essential workflow and requirements.
3. **References:** Conditional or detailed supporting information.

Example:

```markdown
## Workflow

1. Determine the target platform.
2. For AWS, read `references/aws.md`.
3. For Azure, read `references/azure.md`.
4. Apply the relevant provider-specific procedure.
5. Verify the resulting configuration.
```

Do not load every reference unconditionally.

Keep shared procedures in one location. Avoid repeating equivalent rules across skills.

## 6. Match Instruction Precision to the Task

| Task | Agent freedom | Instruction style |
|---|---|---|
| Exploration | High | Define objective and evidence |
| Design | High–Medium | Define constraints and decision criteria |
| Implementation | Medium | Preserve contracts and conventions |
| Testing | Medium–Low | Define required checks and results |
| Migration | Low | Specify ordering, mechanism, recovery |
| Destructive operations | Very low | Require authorization and explicit safeguards |

**Rule:** Constrain what must remain true. Prescribe how only when necessary.

Avoid over-specification that prevents valid solutions.

Example:

```markdown
MUST preserve public API behavior.
Choose internal implementation details independently.
```

Prefer this over requirements that unnecessarily preserve every private class or method.

## 7. Define Failure Behavior

Choose an appropriate failure policy.

### Fail closed

Use when the mechanism is mandatory.

```markdown
MUST use the approved migration tool.

If unavailable:
- Stop the migration.
- Report the blocker.
- MUST NOT replace it with direct SQL.
```

### Controlled fallback

Use when alternatives are explicitly permitted.

```markdown
Search with `rg`.
If unavailable, use `grep -R`.
```

### Graceful degradation

Use when partial work remains valuable.

```markdown
Run relevant integration tests.

If the test environment is unavailable:
- Complete independent verification.
- Report the tests as not run.
- MUST NOT claim full verification succeeded.
```

## 8. Define Observable Completion Criteria

Completion must describe the required result, not merely that steps were executed.

Weak:

> Finish the implementation and make sure it works.

Better:

```markdown
## Completion criteria

- Requested behavior is implemented.
- Required tests pass against the final revision.
- Public contracts remain compatible.
- No required obligation remains unaccounted for.
- Any blocker is explicitly reported.
```

For multi-part tasks, run a final completeness sweep to identify missed requirements.

Avoid repeating the same checks in multiple sections.

## 9. Evaluation-Driven Skill Development

Treat skill authoring as an iterative engineering process.

1. Run representative tasks without the skill.
2. Identify the specific behavior that fails.
3. Write the smallest instruction that addresses it.
4. Run the same tasks with the skill.
5. Compare observed behavior and results.
6. Refine instructions and rerun regression cases.

### Evaluation dimensions

| Evaluation | Question |
|---|---|
| Trigger accuracy | Does the correct skill activate? |
| Execution correctness | Does the agent perform the required behavior? |
| Constraint compliance | Does it preserve mandatory mechanisms? |
| Recovery | Does it respond correctly to blocked or failed steps? |
| Regression | Did changes break previously working scenarios? |
| Efficiency | Does the skill add unnecessary context or actions? |

Test positive, negative, and near-miss prompts.

Include cases designed to tempt the agent into bypassing mandatory constraints.

Do not rely only on textual review of instructions; inspect actual execution traces and artifacts.

## 10. Skill Instructions vs Repository Instructions

| Location | Responsibility |
|---|---|
| `.github/copilot-instructions.md` | Repository-wide conventions |
| `.github/instructions/*.instructions.md` | File-scoped or conditional guidance |
| `.github/skills/<skill>/SKILL.md` | Specialized task workflow |
| `.github/skills/<skill>/references/` | Detailed supporting procedures |
| `.github/skills/<skill>/scripts/` | Deterministic automation |

Use repository instructions for broadly applicable behavior.

Use skills for specialized, reusable procedures.

## 11. Recommended Authoring Standard

```markdown
## Instruction Rules

- Write instructions in imperative form.
- Define observable behavior rather than subjective goals.
- Use MUST and MUST NOT for non-negotiable constraints.
- State mandatory mechanisms explicitly.
- Prohibit plausible substitutions when necessary.
- Give a concise rationale for non-obvious constraints.
- Define failure behavior for critical steps.
- Preserve implementation freedom outside constraints.
- Use progressive disclosure for detailed references.
- Define checkable completion criteria.
- Do not repeat instructions across files or sections.
- Remove instructions that do not change agent behavior.
- Evaluate critical rules against realistic tasks.
```

## 12. Final Recommendations

1. Optimize skill descriptions for accurate discovery.
2. Use short, imperative workflow instructions.
3. Make mandatory constraints explicit.
4. Explain non-obvious restrictions with concise rationales.
5. Define recovery behavior where silent substitution is dangerous.
6. Separate essential instructions from supporting references.
7. Define completion through observable evidence.
8. Preserve agent autonomy outside mandatory constraints.
9. Evaluate actual behavior rather than instruction wording alone.
10. Keep the skill as small as possible without losing necessary constraints.

**Guiding principle:**

Constrain what must remain true, prescribe how only when necessary, explain why when non-obvious, and define what happens when execution cannot proceed.

## References

- [Agent Skills Specification](https://agentskills.io/specification)
- [Anthropic — Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [OpenAI — Skill Creator](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)
- [Anthropic — Skill Creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
- [GitHub Copilot — Agent Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
