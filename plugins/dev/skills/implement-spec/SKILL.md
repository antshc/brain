---
name: implement-spec
description: "Implements a GitHub spec and its blocking ticket graph sequentially on one integration branch in one worktree, honors repository routing labels, and prepares a reviewed pull request with verified ticket coverage."
disable-model-invocation: true
---

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

**MUST** load the bundled [GitHub reference](./github.md) before any GitHub action, including reads. Execute GitHub actions through `gh` according to its prerequisites, procedures, and failure handling. If the reference cannot be loaded, stop and report the blocker. No setup-generated tracker configuration is required.

**Repository guard:** The spec and sub-issues may live outside the development/PR repository. **MUST** preserve each issue's `OWNER/REPO#NUMBER` identity, route issue reads/comments to its owning repository, and route implementation, Git, and PR operations only to the resolved source repository. **MUST NOT** infer an issue's repository from the current checkout, PR repository, or matching issue number; resolve ambiguous ownership before proceeding.

The goal is the entire spec implemented on a single **integration branch** in one run-owned worktree under the source repository's `.fake/worktrees/`, with a reviewed pull request referencing every implemented issue for closure on merge.

The tickets form a **task graph** with blocking relationships. Select one ticket at a time from the ready **frontier**; finish and validate it before starting another.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers.

Use the same integration branch and worktree for all tickets and review fixes. Implement directly or delegate one ticket at a time; wait for its result before proceeding. Do not create per-ticket branches/worktrees or use merger subagents.

## Steps

1. Read the spec and all tickets, including comments, parent links, and blockers, using the GitHub reference. Resolve the spec's `repo:target:<owner/repo>` and `repo:base:<branch>` labels to the source checkout and integration base; keep issue operations in the tracker repository and Git/PR operations in the source repository. Resolve missing or conflicting routing explicitly before writing. Read source-root `GLOSSARY.md` when present; use its vocabulary without requiring the file. Reject cycles or missing ticket scope before scheduling. Treat a closed blocker as satisfied only when its implemented result is present in the integration base; cancelled or duplicate issues require explicit resolution, not automatic satisfaction.

2. Explore only as needed to establish ticket scope and testing seams. If separate context is warranted, delegate bounded exploration; save any shared notes outside the repo and pass context pointers to subsequent implementers.

3. Record the source repository and target base branch. Follow the GitHub reference to create one integration branch and one worktree at `<source-repo-root>/.fake/worktrees/<spec-id>` without overwriting existing work. Confirm the new worktree is clean and on that branch; perform all implementation and checks there.

4. Select one ready ticket and implement it directly on the shared integration branch in that worktree:
   - start from the clean, validated integration tip; never reset or discard existing work;
   - Use test-driven development, red-green-refactor, and behavior tests to build the ticket;
   - run relevant checks against the cumulative result, commit the ticket, and record its commit and validation evidence. Failed checks or incomplete work block advancement.

5. Mark the ticket **integrated** only when its committed implementation is verified on the integration branch. After the first such commit, push and open a draft GitHub PR against the recorded source base. Add closing references for the spec and implemented tickets, extending coverage as tickets complete; comment on each implemented issue with the PR pointer and evidence. A branch with no commits ahead of its base cannot open a PR.

6. Recompute the **frontier** after each verified ticket commit, then repeat steps 4-5 for one next ready ticket. A blocker is satisfied for this run when its implementation is verified on the integration branch, even while its issue remains open pending PR merge. External blockers still require verified resolution. If unfinished tickets remain but none are ready, report the blockers and preserve the work; do not bypass dependencies or start tickets concurrently.

7. Once all tickets are integrated, review the integration branch for bugs and logic errors. Fix all reported issues sequentially in the same worktree, commit fixes, and rerun affected checks. If a required skill is unavailable, report the blocker and obtain agreement on an alternative; never silently skip development or review.

8. Confirm the final branch passes required checks and the PR covers the spec and every implemented ticket; push remaining commits and mark the draft PR ready. Do not merge the PR or close issues early. Closing keywords take effect only when merged into the repository's default branch; for another target, report the remaining closure step explicitly.

9. Remove only this run's clean worktree after all its commits are verified and pushed to the PR branch; preserve and report dirty, unpushed, or incomplete work. Keep the integration branch and PR.

## Completion criteria

- Every in-scope ticket has verified implementation and test evidence on the integration branch, developed sequentially in the same run-owned worktree.
- The source repository and PR base match the spec's routing labels or an explicitly agreed resolution for missing/conflicting routing; issue operations and PR closing references retain each issue's owning repository.
- The reviewed PR is ready, links the spec and tickets, and reports any pending checks or closure steps accurately; open issues are not misreported as closed.
- The run-owned worktree under the source repository's `.fake/worktrees/` is cleaned up or explicitly accounted for, with no user work discarded.
- Finally map every spec requirement and ticket to implementation, tests, and relevant documentation; resolve gaps or report explicit deferrals before declaring completion.
