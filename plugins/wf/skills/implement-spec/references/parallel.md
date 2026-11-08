# Parallel

Experimental. Load only for `mode=parallel`, after graph validation and integration setup. The orchestrator owns launches, *Frontier check*, and every later phase.

## Scope and scheduling

1. **Graph source.** Use *Effective graph* with planner footprints, conflicts, and implementer recommendations; retain inferred blockers across native refreshes. For existing sub-issues the planner ran in read-only `analyze` mode; for zero sub-issues it ran in `breakdown` mode. Reject cycles; mark `hitl` tickets and unsatisfied transitive dependants `deferred`; verify the ready frontier and critical path against the fetched base. `file` conflicts serialize concurrent writes; contract consumers become blocker edges only when order matters, otherwise `soft`. Never invent blocker edges to represent the worker cap. Done when graph, readiness, conflict evidence, and implementer recommendations exist.
2. **Report the graph** per *Graph report*, with paths and conflicts, before the first launch.

## Parallel Implementation

Implementers never write in the integration worktree.

1. **Slot.** Launch ticket `n` whenever it is ready (blockers integrated), non-`hitl`, has no `file` conflict with an in-flight ticket, and fewer than `MAX_PARALLEL` are in flight. `soft` conflicts never block a launch. Verify and integrate each completed ticket as it settles, without waiting for unrelated in-flight tickets. Keep a completed worker's slot/conflict reservation until its integration settles. Return control to the orchestrator for *Effective graph* after each validated integration and publication; use only its recomputed frontier.
2. **Select.** When ready tickets outnumber free slots or file-conflict, choose the largest set with no `file` conflict among its members. Tie-break: critical path, then most direct dependants unblocked, then longest wait. A ready ticket skipped in two selection rounds goes first next round. Report every skipped ready ticket as `deferred: #N, file conflict with #M (path)`.
3. **Create the ticket worktree** per worktrees *Ticket worktrees*; record `@prevHead(n)`.
4. **Delegate.** Return control to the orchestrator for *Launch implementer* (Parallel column) with the eligible tickets: one fresh background implementer per ticket. Done when each returns its final JSON.
5. **Verify and commit.** The orchestrator validates the edits and evidence per *Launch implementer*, then commits once in `TICKET_WORKTREE(n)` against `@prevHead(n)`.
6. **Apply sequentially.** In the clean integration worktree, one verified ticket at a time (critical path first), the orchestrator applies `git cherry-pick --no-commit <ticket SHA>`. On conflict, undo only the paths changed by this tentative application and run *Integration rework*.
7. **Re-check assumptions.** Before committing the integration, compare the tentative paths/contracts with unfinished tickets' footprints and prerequisites. Material mismatch or unusable verification → undo the tentative application and return control to the orchestrator for *Targeted replanning*. Retain inferred blockers/conflict reservations until evidence-backed reanalysis supersedes them; pass integrated paths as a pointer.
8. **Verify and integrate.** Run the cheapest affected build/test on the tentative application. On success, the orchestrator uses `git commit -C <ticket SHA>` and verifies one new commit and a clean worktree. On failure, undo only the tentative application and run *Integration rework*.
9. **Publish** per *Ticket publication*.
10. **Clean the ticket worktree** per worktrees *Ticket worktrees*.

Done when each integrated ticket has exactly one serialized cherry-picked commit, writers stayed isolated, and ticket branches/worktrees are removed or reported. Once the frontier is exhausted, return control to the orchestrator for *Frontier check*.

### Integration rework

- The orchestrator records the clean integration HEAD before applying. To undo an unsuccessful tentative application, run `git restore --source=<recorded integration HEAD> --staged --worktree` for only the paths staged or conflicted by the tentative application. Verify the original HEAD and a clean worktree. If other edits appear or the affected paths cannot be attributed safely, preserve the worktree and report a blocker.
- The orchestrator rebases its unpublished ticket commit onto the current integration HEAD when needed. If the rebase conflicts, the worker edits the conflict files and reruns checks in the ticket workspace. The orchestrator stages the resolution and continues the rebase. The worker leaves Git state to the orchestrator.
- For a code fix after a failed integration check, the worker edits and reruns checks in the ticket workspace. After verifying the result, the orchestrator updates its own unpublished ticket commit with `git commit --amend`. Verify exactly one ticket commit over the current integration base before retrying. Keep the existing two-round cap and preserve blocked work. Never rewrite the integration branch or published commits.

## Readiness example

A and B have no blockers; C is blocked only by A. Start A and B when capacity permits. After A is verified, integrated, checked and published, C may start while B still runs, provided C has no file conflict with an in-flight ticket. A finished worker alone does not satisfy its dependants. No ticket ready but workers in flight → wait for a result; report a blocked frontier only when no worker can make progress.
