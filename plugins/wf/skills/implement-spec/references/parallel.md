# Parallel

Load only for `mode=parallel`, after graph validation and integration setup. The orchestrator owns launches, *Frontier check*, and every later phase.

## Scope and scheduling

1. **Graph source.** Planner runs only in Breakdown Initiative (spec had zero sub-issues); reuse its blocker graph and conflicts. Spec already had sub-issues → **MUST NOT** spawn a planner; derive the graph inline from the run-local map: reject cycles; mark `hitl` tickets and unsatisfied transitive dependants `deferred`; initial ready frontier = non-deferred tickets whose blockers are verified in the base; critical path = longest blocker chain; derive `conflicts` from source footprints and shared hot files/contracts, serializing overlaps conservatively before launch. Conflicts restrict concurrency; never invent blocker edges to represent the worker cap. Done when graph, readiness and conflict evidence exist.
2. **Report the graph** per *Graph report*, with paths and conflicts, before the first launch.

## Parallel Implementation

Implementers never write in the integration worktree.

1. **Slot.** Launch ticket `n` whenever it is ready (blockers integrated), non-`hitl`, has no `conflicts` pair with an in-flight ticket, and fewer than `MAX_PARALLEL` are in flight. Verify and integrate each completed ticket as it settles, without waiting for unrelated in-flight tickets. Keep a completed worker's slot/conflict reservation until its integration settles. Recompute the frontier after each validated integration and publication.
2. **Create the ticket worktree** per worktrees *Ticket worktrees*; record `@prevHead(n)`.
3. **Delegate.** Return control to the orchestrator for *Launch implementer* (Parallel column) with the eligible tickets: one fresh background implementer per ticket. Done when each returns its final JSON.
4. **Verify and rework** per *Launch implementer*, against `TICKET_WORKTREE(n)` and `@prevHead(n)`.
5. **Merge sequentially.** In the integration worktree, one verified ticket at a time (critical path first): `git cherry-pick <result.commit>`; the integration head gains exactly one commit with the ticket's subject. On conflict: `git cherry-pick --abort`, then rework that ticket's subagent to rebase `TICKET_BRANCH(n)` onto the integration head, resolve, rerun its checks, and keep one commit; re-verify and re-pick. After two failed rounds, preserve the worktree, mark the ticket and its dependants blocked, and continue other tickets. **MUST NOT** use merge commits, force, or reset.
6. **Post-merge check.** Run the cheapest affected build/test in the integration worktree; a failure the merged ticket caused goes back to its subagent as rework (new commit on the ticket branch, re-pick).
7. **Publish** per *Ticket publication*.
8. **Clean the ticket worktree** per worktrees *Ticket worktrees*.

Done when each integrated ticket has exactly one serialized cherry-picked commit, writers stayed isolated, and ticket branches/worktrees are removed or reported. Once the frontier is exhausted, return control to the orchestrator for *Frontier check*.

## Readiness example

A and B have no blockers; C is blocked only by A. Start A and B when capacity permits. After A is verified, integrated, checked and published, C may start while B still runs, provided C conflicts with no in-flight ticket. A finished worker alone does not satisfy its dependants. No ticket ready but workers in flight → wait for a result; report a blocked frontier only when no worker can make progress.
