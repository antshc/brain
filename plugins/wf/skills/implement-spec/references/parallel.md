Parallel mode procedure. Load only when `mode` is `parallel`.

## Settings

- `MAX_PARALLEL`: default 3; user may override.
- Graph scheduling only. Optional `schedule=graph` is a compatibility alias; reject every other schedule before side effects.
- `TICKET_BRANCH(n)` = `INTEGRATION_BRANCH-t<n>`; `TICKET_WORKTREE(n)` = `WORKTREES_ROOT/INITIATIVE_ID-t<n>`, where `n` is the ticket number. Confirm each path stays under `WORKTREES_ROOT`; never reuse an existing path or branch.

## Plan

1. **Graph source.** Planner runs only in SKILL.md *Breakdown Initiative* (spec had zero sub-issues); reuse its ticket blocker graph and conflicts. Spec already had sub-issues → **MUST NOT** spawn a planner; derive the graph inline from the run-local map. Reject cycles; mark `hitl` tickets and unsatisfied transitive dependants `deferred`; initial ready frontier = non-deferred tickets whose blockers are verified in the base. Critical path = longest blocker chain. Inspect source footprints and shared hot files/contracts to derive `conflicts`; serialize overlapping tickets conservatively before launch. Conflicts restrict concurrency; do not invent blocker edges to represent a runtime worker cap. Unexpected cherry-pick conflicts go through Run step 5 rework. Done when the graph, readiness and conflict evidence exist.
2. **Return the graph.** Render ticket-to-blocker adjacency as a table, then ready frontier, conflicts, critical path and deferred tickets. Blocker → dependent is the edge direction; `none` is an explicit root, not an omitted row.

   | Ticket | Blocked by | Paths | Conflicts with |
   |---|---|---|---|
   | acme/shop#12 | none | `src/Export/Schema/` | acme/shop#14 |
   | acme/shop#13 | none | `src/Api/Auth/` | none |
   | acme/shop#14 | none | `src/Export/Schema/` | acme/shop#12 |
   | acme/shop#15 | acme/shop#12 | `src/Export/Writer/` | none |
   | acme/shop#16 | none | - | deferred: hitl |
   | acme/shop#17 | acme/shop#16 | - | deferred: blocked by #16 |

   Ready: #12, #13, #14 (select a non-conflicting subset). Critical path: #12 → #15. Deferred: #16 `hitl`; #17 blocked by #16. List deferred tickets' blocker edges too; never omit nodes from the reported graph.


## Run

Use the integration worktree only for merging, publishing, verification, and chore. Implementers never write there.

1. **Slot.** Launch ticket `n` only when it is ready (blockers integrated), non-`hitl`, has no `conflicts` pair with an in-flight ticket, and fewer than `MAX_PARALLEL` are in flight. Launch whenever a slot and a ready non-conflicting ticket exist. Verify and integrate each completed ticket as it settles; do not wait for unrelated in-flight tickets. Recompute the frontier after each validated integration and publication. Keep a completed worker's slot/conflict reservation until integration settles.
2. **Create the ticket worktree.** `git -C SOURCE_ROOT worktree add -b TICKET_BRANCH(n) TICKET_WORKTREE(n) <integration HEAD>`; verify clean and `HEAD` equals the integration head. Record `@prevHead(n)`.
3. **Delegate.** Prepare [implementer.md](../agents/implementer.md) using the main skill placeholder mapping with `{{worktreePath}}` = `TICKET_WORKTREE(n)`, `{{featureBranch}}` = `TICKET_BRANCH(n)`, `{{targetBranch}}` = `INTEGRATION_BRANCH`, `{{initiativeCommits}}` = integration log. Return the eligible tickets and prompts to `SKILL.md`; only the orchestrator launches them as background subagents through its Subagent launch contract with the absolute reference handoff so they run concurrently. Done when each returns its final JSON.
4. **Verify per ticket.** Using the main skill result-verification guards, against `TICKET_WORKTREE(n)`: `HEAD` equals `result.commit`, exactly one commit since `@prevHead(n)`, subject prefix, clean. Rework goes to that ticket's subagent, at most two rounds.
5. **Merge sequentially.** In the integration worktree, one verified completed ticket at a time (critical path first when multiple are available): `git cherry-pick <result.commit>`; the integration head gains exactly one commit with the ticket's subject. On conflict: `git cherry-pick --abort`, then send the ticket's subagent a rework asking it to rebase `TICKET_BRANCH(n)` onto the integration head, resolve, rerun its checks, and keep one commit; re-verify and re-pick. After two failed rounds, preserve the worktree, mark the ticket and its dependants blocked, and continue other tickets. **MUST NOT** use merger subagents, merge commits, force, or reset.
6. **Post-merge check.** After each merge, run the cheapest affected build/test in the integration worktree; a failure that the merged ticket caused goes back to that ticket's subagent as rework (new commit on the ticket branch, re-pick).
7. **Publish and close.** Using the main skill publication guards, after each validated integration: push, open or update the draft PR, close each integrated ticket.
8. **Clean ticket worktrees.** After a ticket is integrated, `git -C SOURCE_ROOT worktree remove TICKET_WORKTREE(n)` without force and delete its run-owned branch with `git -C SOURCE_ROOT branch -D TICKET_BRANCH(n)` (cherry-picked commits are not ancestors, so `-d` refuses). Preserve dirty or unmerged ones and report path/branch.

The app-verification through finalization phases of the main workflow run unchanged once the frontier is exhausted.

## Readiness example

A and B have no blockers; C is blocked only by A. Start A and B when capacity permits. After A is verified, integrated, checked and published, C may start while B still runs, provided C conflicts with no in-flight ticket. A finished worker alone does not satisfy its dependants. When no ticket is ready but workers remain in flight, wait for a result; report a blocked frontier only when no worker can make progress.
