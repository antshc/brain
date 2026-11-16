# Task

## Purpose

Render one self-contained implementation work item. The caller selects scope, boundaries, dependencies and publication policy.

## Inputs

Task title, included outcome, exclusions, parent Spec when present, verbatim addressed requirements/rules/edge cases, implementation decisions, producer contracts/assumptions, relevant Concepts/ADRs, affected layers/modules, artifact excerpts and criteria-to-check mapping. Accept functional, structural, behavior-preserving and mixed work. Missing scope or unresolved decisions → return the precise gap.

## Required resources

Read the router's Task template and local requirements resources. For `normalize`, return after Requirements rules without rendering a full task.

## Workflow

1. **Check coverage.** Match the supplied scope to source requirements, constraints and artifact pieces. Do not split or expand the task. Done when all supplied obligations have a destination or an explicit gap.
2. **Render.** Fill the Task template; include every mandatory section and each triggered conditional section. Copy addressed source text verbatim, with its identifiers. Keep technical relocation paths, symbols, project references, selected sketch excerpts and evidence exact. Done when the body is independently implementable.
3. **Normalize.** Apply requirements rules to authored behavior and acceptance criteria, preserving technical sections and verbatim sources. Done when each criterion states a concrete pass/fail result.
4. **Contracts and checks.** Use the router's Contracts producer for every touched kind; populate Verify section with supplied or verified commands, prerequisites, expected results and retained evidence. Report unavailable prerequisites and unknown commands rather than inventing them. Done when each criterion has a check and no required contract output is missing.

## Update behavior

Read existing content first. Add missing relevant artifact pieces without duplicate excerpts or overwriting user-authored content. Preserve unaffected requirements, decisions and canonical links.

## Completion criteria

- Every mandatory template section is populated; conditional sections match actual scope.
- Every addressed requirement appears verbatim with its identifier; supplied behavior, source relationships and technical constraints survive.
- Relevant artifact pieces map both ways to requirements or criteria; no unrelated pieces appear.
- Each criterion has a concrete check; missing facts remain explicit gaps.
- The caller retains task decomposition, graph edges, labels, approvals and publication.

## Output

Return title and full task body, with gaps separately. A GitHub issue or Jira work item is a destination, not another artifact type.
