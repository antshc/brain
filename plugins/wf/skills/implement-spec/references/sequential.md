# Sequential

Load only for `mode=sequential` (the default), after graph validation and integration setup. The orchestrator owns launches, *Frontier check*, and every later phase.

## Sequential Implementation

### Preconditions

- *Ticket publication*, *Pull request lifecycle*, and *Closure and cleanup* loaded; `SOURCE_ROOT`, `WORKTREE_PATH`, `INTEGRATION_BRANCH`, `BASE_BRANCH`, `BASE_COMMIT`, `INITIATIVE_ID`, and `RUN_DIR` resolved.
- **One** clean integration worktree and branch for the run, per worktrees *Integration writes*; no per-ticket branches/worktrees.

### Run

1. **Select one ticket.** Recompute the ready frontier from the run-local map; choose one in-scope, non-`hitl` ticket whose blockers are satisfied. None ready while unfinished tickets remain → return control to the orchestrator for *Frontier check*. Done when one eligible ticket is selected or the run stops.
2. **Record the integration tip.** Confirm `WORKTREE_PATH` is clean and on `INTEGRATION_BRANCH`; record `@prevHead` = `HEAD`. Done when the starting commit and branch are verified.
3. **Delegate.** Return control to the orchestrator for *Launch implementer* (Sequential column): a **fresh implementer subagent** in the foreground. Done when its final JSON is available.
4. **Verify and rework** per *Launch implementer*. Done when the commit is verified or the ticket is stopped.
5. **Publish** per *Ticket publication*, only after step 4 succeeds.
6. **Repeat** from step 1 with a **new** implementer subagent.
7. **Return.** When all in-scope, non-deferred tickets are integrated, pushed, and closed, return control to the orchestrator for *Frontier check*.
