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
5. **Verify and rework** per *Launch implementer*, against `TICKET_WORKTREE(n)` and `@prevHead(n)`.
6. **Merge sequentially.** In the integration worktree, one verified ticket at a time (critical path first): `git cherry-pick <result.commit>`; the integration head gains exactly one commit with the ticket's subject. On conflict: `git cherry-pick --abort`, then rework that ticket's subagent to rebase `TICKET_BRANCH(n)` onto the integration head, resolve, rerun its checks, and keep one commit; re-verify and re-pick. After two failed rounds, preserve the worktree, mark the ticket and its dependants blocked, and continue other tickets. **MUST NOT** use merge commits, force, or reset.
7. **Re-check assumptions.** After each integration, compare actual changed paths/contracts with unfinished tickets' footprints and prerequisites. Material mismatch or unusable verification → return control to the orchestrator for *Targeted replanning*. Retain inferred blockers/conflict reservations until evidence-backed reanalysis supersedes them; pass integrated paths as a pointer.
8. **Post-merge check.** Run the cheapest affected build/test in the integration worktree; a failure the merged ticket caused goes back to its subagent as rework (new commit on the ticket branch, re-pick).
9. **Publish** per *Ticket publication*.
10. **Clean the ticket worktree** per worktrees *Ticket worktrees*.

Done when each integrated ticket has exactly one serialized cherry-picked commit, writers stayed isolated, and ticket branches/worktrees are removed or reported. Once the frontier is exhausted, return control to the orchestrator for *Frontier check*.

## Readiness example

A and B have no blockers; C is blocked only by A. Start A and B when capacity permits. After A is verified, integrated, checked and published, C may start while B still runs, provided C has no file conflict with an in-flight ticket. A finished worker alone does not satisfy its dependants. No ticket ready but workers in flight → wait for a result; report a blocked frontier only when no worker can make progress.
