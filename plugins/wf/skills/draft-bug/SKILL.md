---
name: draft-bug
description: Draft one reproducible bug report from observed behavior and available codebase context. Use when the user asks to write, draft, format, or file a bug, defect, regression, or unexpected-behavior report, or when another skill needs a bug body.
---

# Draft Bug

Draft and print one standalone bug report that defines the affected behavior, reproduction, actual result, expected result, and useful technical context.

**Input:** observed behavior and any available affected users, expected behavior, impact, boundaries, preconditions, reproduction steps, evidence, and technical context. Derive omitted details from the conversation and repository when evidence is available.

## Workflow

1. **Scope the bug** → state the affected behavior or users, expected versus actual behavior, impact, boundaries, and definition of fixed. *Done when* the scope identifies one observable defect without prescribing an implementation or unverified root cause.
2. **Sweep context** → inspect the nearest relevant documentation, tests, configuration, logs, errors, and implementation surfaces when repository access can clarify the report. Run `/explore-codebase` skill for a bounded read-only lookup when the evidence path is unclear. Stop once the report fields can be stated accurately; root-cause analysis is outside this skill. *Done when* every included technical claim is grounded in supplied or observed evidence and remaining unknowns stay explicit.
3. **Write reproduction** → list only required preconditions, then numbered user actions from the starting state to the observed result. *Done when* another person can attempt the reproduction without inferring setup or intermediate actions.
4. **Separate results** → state the observed outcome under Actual Results and the required behavior under Expected Results. *Done when* the two results are directly comparable and use concrete, testable language.
5. **Verify** → apply the Quality Check line by line. *Done when* every check passes and the report contains no invented facts.

## Quality Check

- The Bug scope covers affected behavior or users, expected versus actual behavior, impact, boundaries, and the observable definition of fixed.
- Preconditions contain only state or setup required before the first action.
- User Actions are ordered, reproducible actions and contain no expected outcomes.
- Actual Results report observations, including exact error text or identifiers when available.
- Expected Results define one externally verifiable outcome.
- Technical notes contain only useful known evidence, references, environment details, or explicit unknowns; they do not speculate about root cause.
- Unknown required details are marked `Unknown` rather than invented.

## Output Format

Use this exact structure without wrapper prose:

```markdown
{{BugScope| PO bug scope: affected behavior/users, impact, boundaries, definition of fixed. Exclude implementation/root cause unless scope-relevant}}

**Preconditions**
- {{Required state/setup}}

**User Actions**
1. ...
2. ...
3. ...

**Actual Results:**
{{What happens}}

**Expected Results:**
{{What should happen}}

---
<details>
<summary>Technical notes</summary>

**Technical notes**
{{Any useful technical context}}
<details>
```