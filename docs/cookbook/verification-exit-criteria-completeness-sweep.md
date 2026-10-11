# Recipe: Verification, Exit Criteria, and Completeness Sweep

## Problem

AI agents can declare work complete when tests pass, even if requirements are missing. Multi-part tasks need separate checks for correctness, completion conditions, and scope coverage.

- **Verification:** Does the implemented behavior work?
- **Exit Criteria (Completeness Verification):** Does the result meet all defined completion conditions?
- **Completeness Sweep:** Were any required obligations omitted?

## Example

**Task:** Implement RBAC for the API and GUI. Support new and upgraded installations.

**AI Instructions:**

> 1. **Exit Criteria:** Define observable completion conditions before implementation. Require evidence for each condition.
> 2. **Verification:** Test changed behavior. Record results. Do not claim checks that did not run.
> 3. **Completeness Sweep:** Run last. Reconstruct all obligations from the request. Match each to implementation and evidence. Resolve or explicitly report missing obligations.
> 4. Declare completion only when all exit criteria pass and no obligations remain unaccounted for.

## Best Practices

- Define measurable exit criteria before implementation.
- Use verification evidence to evaluate exit criteria. Passing tests alone does not prove completion.
- Run the completeness sweep last for multi-part tasks. Do not duplicate checks already proving full coverage.

## Related Recipes

- None yet.
