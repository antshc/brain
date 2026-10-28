Parallel mode procedure. Load only when `mode` is `parallel`.

## Settings

- `MAX_PARALLEL`: default 3; user may override.
- `schedule`: `waves` (default) | `graph`.
- `TICKET_BRANCH(n)` = `INTEGRATION_BRANCH-t<n>`; `TICKET_WORKTREE(n)` = `WORKTREES_ROOT/INITIATIVE_ID-t<n>`, where `n` is the ticket number. Confirm each path stays under `WORKTREES_ROOT`; never reuse an existing path or branch.

## Plan

1. **Plan source.** Planner runs only in SKILL.md *Breakdown Initiative* (spec had zero sub-issues); reuse its result. Spec already had sub-issues → **MUST NOT** spawn a planner; build the plan inline from the run-local map: `hitl` tickets and transitive dependants `deferred`; wave 0 = ready tickets, wave N = tickets whose blockers are all in earlier waves; split waves larger than `MAX_PARALLEL` into consecutive waves; critical path = longest blocker chain. Inspect source footprints and shared hot files/contracts to derive `conflicts`; serialize overlapping tickets conservatively before launch. Unexpected cherry-pick conflicts go through Run step 5 rework. Done when the plan exists.
2. **Return the plan.** Render the result to the user as a table, then the critical path and deferred tickets:

   | Wave | Ticket | Blockers | Paths | Note |
   |---|---|---|---|---|
   | 0 | acme/shop#12 | none | `src/Export/Schema/` | |
   | 0 | acme/shop#13 | none | `src/Api/Auth/` | |
   | 1 | acme/shop#14 | none | `src/Export/Schema/` | conflict:#12 |
   | 1 | acme/shop#15 | #12 | `src/Export/Writer/` | |

   Deferred: `#16` hitl; `#17` blocked-by `#16`.


## Run

Use the integration worktree only for merging, publishing, verification, and chore. Implementers never write there.

1. **Slot.** Launch ticket `n` only when it is ready (blockers integrated), non-`hitl`, has no `conflicts` pair with an in-flight ticket, and fewer than `MAX_PARALLEL` are in flight. `waves`: launch the whole wave, wait for every ticket of the wave to settle, then merge. `graph`: launch whenever a slot and a ready non-conflicting ticket exist; merge each as it settles, then recompute the frontier.
2. **Create the ticket worktree.** `git -C SOURCE_ROOT worktree add -b TICKET_BRANCH(n) TICKET_WORKTREE(n) <integration HEAD>`; verify clean and `HEAD` equals the integration head. Record `@prevHead(n)`.
3. **Delegate.** Prepare [implementer.md](../agents/implementer.md) using the main skill placeholder mapping with `{{worktreePath}}` = `TICKET_WORKTREE(n)`, `{{featureBranch}}` = `TICKET_BRANCH(n)`, `{{targetBranch}}` = `INTEGRATION_BRANCH`, `{{initiativeCommits}}` = integration log. Return the eligible tickets and prompts to `SKILL.md`; only the orchestrator launches them as background subagents through its Subagent launch contract with the absolute reference handoff so they run concurrently. Done when each returns its final JSON.
4. **Verify per ticket.** Using the main skill result-verification guards, against `TICKET_WORKTREE(n)`: `HEAD` equals `result.commit`, exactly one commit since `@prevHead(n)`, subject prefix, clean. Rework goes to that ticket's subagent, at most two rounds.
5. **Merge sequentially.** In the integration worktree, one ticket at a time, in wave order (critical path first): `git cherry-pick <result.commit>`; the integration head gains exactly one commit with the ticket's subject. On conflict: `git cherry-pick --abort`, then send the ticket's subagent a rework asking it to rebase `TICKET_BRANCH(n)` onto the integration head, resolve, rerun its checks, and keep one commit; re-verify and re-pick. After two failed rounds, preserve the worktree, mark the ticket and its dependants blocked, and continue other tickets. **MUST NOT** use merger subagents, merge commits, force, or reset.
6. **Post-merge check.** After the last merge of a wave (or each merge in `graph`), run the cheapest affected build/test in the integration worktree; a failure that the merged ticket caused goes back to that ticket's subagent as rework (new commit on the ticket branch, re-pick).
7. **Publish and close.** Using the main skill publication guards, once per merged batch: push, open or update the draft PR, close each integrated ticket.
8. **Clean ticket worktrees.** After a ticket is integrated, `git -C SOURCE_ROOT worktree remove TICKET_WORKTREE(n)` without force and delete its run-owned branch with `git -C SOURCE_ROOT branch -D TICKET_BRANCH(n)` (cherry-picked commits are not ancestors, so `-d` refuses). Preserve dirty or unmerged ones and report path/branch.

The app-verification through finalization phases of the main workflow run unchanged once the frontier is exhausted.
