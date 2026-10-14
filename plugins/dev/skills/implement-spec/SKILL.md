---
name: implement-spec
description: "Implements a GitHub spec and its blocking ticket graph on an integration branch, coordinates parallel worktrees, and prepares a reviewed pull request with verified ticket coverage."
disable-model-invocation: true
---

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

Use GitHub Issues through `gh`; follow the bundled [GitHub reference](./github.md). No setup-generated tracker configuration is required.

The goal is the entire spec implemented on a single **integration branch**, with a reviewed pull request referencing every implemented issue for closure on merge.

The tickets are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tickets which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers.

**Implementer subagents** should be run in the background where possible for maximum concurrency.

## Steps

1. Read the spec and all tickets, including comments, parent links, and blockers, using the GitHub reference. Read root `GLOSSARY.md` when present; use its vocabulary without requiring the file. Reject cycles or missing ticket scope before scheduling. Treat a closed blocker as satisfied only when its implemented result is present in the integration base; cancelled or duplicate issues require explicit resolution, not automatic satisfaction.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Record the target base branch and create the integration branch without overwriting existing work. After the first verified merge in step 5, push it and open a draft GitHub PR against that base. Add closing references for the spec and implemented tickets, extending them as tickets land. A branch with no commits ahead of its base cannot open a PR.

4. Use **implementer subagents** to implement each ticket, each in its own worktree on its own branch. Each implementer subagent:
   - starts in a clean, dedicated worktree based on the current integration tip; never resets or discards existing user work;
   - *Use test-driven development, red-green-refactor, and behavior tests to build the ticket*;
   - merges the integration branch tip into its own branch before reporting done

5. Once an **implementer subagent** completes, merge its work to the integration branch with a **merger subagent**. Serialize integration merges, resolve conflicts, and run relevant checks against the merged result. Only then record the ticket as **integrated**, with its commit and validation evidence; comment on its issue with a PR pointer.

6. Recompute the **frontier** after each verified integration. A blocker is satisfied for this run when its implementation is verified in the integration branch, even while its issue remains open pending PR merge. External blockers still require verified resolution. Start independent ready tickets concurrently; do not schedule a ticket already running.

7. Once all tickets are integrated, *Review code for bugs, and logic errors on the integration branch*. Fix all reported issues in a single **implementer subagent**, integrate the fixes, and rerun affected checks. If a required skill is unavailable, report the blocker and obtain agreement on an alternative; never silently skip development or review.

8. Confirm the final branch passes required checks and the PR covers the spec and every implemented ticket; push remaining commits and mark the draft PR ready. Do not merge the PR or close issues early. Closing keywords take effect only when merged into the repository's default branch; for another target, report the remaining closure step explicitly.

9. Remove only clean worktrees created for this run whose work is integrated; preserve dirty or unmerged work and report it.

## Completion criteria

- Every in-scope ticket has verified implementation and test evidence on the integration branch.
- The reviewed PR is ready, links the spec and tickets, and reports any pending checks or closure steps accurately; open issues are not misreported as closed.
- Run-owned worktrees are cleaned up or explicitly accounted for, with no user work discarded.
- Finally map every spec requirement and ticket to implementation, tests, and relevant documentation; resolve gaps or report explicit deferrals before declaring completion.
