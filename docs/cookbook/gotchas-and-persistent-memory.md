# Recipe: Gotchas and Persistent Memory

## Problem

AI agents repeat avoidable mistakes when lessons from prior runs are lost. **Gotchas** are reusable directives grounded in observed friction. **Memory** stores those directives across sessions and makes them available to later runs.

## Example 1

**Task:** Extend a Python API client to handle retryable HTTP errors. The repository has saved lessons from previous changes and test runs.

**AI Instructions:**
> 1. Read repository-specific gotchas before changing the API client.
> 2. Apply relevant directives during implementation and testing.
> 3. Report conflicts between gotchas and current requirements. Do not ignore conflicts silently.
> 4. If memory is missing, report "No gotchas recorded yet." Continue with repository conventions.

## Example 2

**Task:** Verify the API client. An integration test fails because the required test-service credentials are absent.

**AI Instructions:**
> 1. Before ending the run, review failures, retries, and corrections for reusable lessons.
> 2. Discard one-off errors and transient failures that resolved on the first retry.
> 3. Record the observed blocker as a directive: "Check test-service credentials before API integration tests; report blocked when unavailable."
> 4. Refine an existing matching gotcha. Do not add a duplicate or overwrite unrelated rules.
> 5. Save the directive to repository-scoped memory before reporting status. If memory is unavailable, report that the update was not saved.

## Best Practices

- Read memory before work. Save new gotchas before every exit, including blocked or partial results.
- Record concise, actionable directives from actual repeatable friction. Do not save speculation, secrets, or routine steps.
- Put missing facts in memory; fix broken agent routing or guardrails in the responsible instructions.

## Related Recipes

- [Verification, Exit Criteria, and Completeness Sweep](verification-exit-criteria-completeness-sweep.md)
