---
name: implement-spec
description: "Implements a GitHub spec and its blocking ticket graph sequentially on one integration branch in one worktree, honors repository routing labels, and prepares a reviewed pull request with verified ticket coverage."
disable-model-invocation: true
---

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

**MUST** load the bundled [GitHub reference](./github.md) before any GitHub action, including reads. Execute GitHub actions through `gh` according to its prerequisites, procedures, and failure handling. If the reference cannot be loaded, stop and report the blocker. No setup-generated tracker configuration is required.

**Repository guard:** The spec and sub-issues may live outside the development/PR repository. **MUST** preserve each issue's `OWNER/REPO#NUMBER` identity, route issue reads/comments to its owning repository, and route implementation, Git, and PR operations only to the resolved source repository. **MUST NOT** infer an issue's repository from the current checkout, PR repository, or matching issue number; resolve ambiguous ownership before proceeding.

**Implementation focus guard:** Stay on ticket implementation. **MUST NOT** investigate or troubleshoot environment, network, Docker, container-port, service-reachability, or similar infrastructure problems (e.g., unreachable hosts, blocked or closed ports, Docker daemon/container failures, flaky registries or package feeds, missing external services). When such a problem blocks a check, make at most one quick attempt to confirm it (no diagnosis, reconfiguration, retries loops, or workarounds in the environment), then continue implementing and validating through the available **test seams**: unit tests, fakes, mocks, in-memory or stub implementations, and tests that need no external infrastructure. Record the skipped infrastructure-dependent check and its error as a one-line note in the ticket's evidence/PR comment so a human can run it later; an infrastructure-only failure is not by itself a reason to block ticket advancement. Failures caused by the ticket's code still block as described in step 4. Pass this guard to every implementer subagent.

The goal is the entire spec implemented on a single **integration branch** in one run-owned worktree at `<repo-root>/workspace/<repo>.worktrees/<initiative-id>`, with a reviewed pull request referencing every implemented issue for closure on merge.

The tickets form a **task graph** with blocking relationships. Select one ticket at a time from the ready **frontier**; finish and validate it before starting another.

**HITL guard:** A ticket labeled `hitl` is **skipped**: **MUST NOT** implement, delegate, comment on, or close it, nor add a closing reference for it. Re-read labels when selecting each ticket. A skipped ticket is not a satisfied blocker; its dependants stay unready unless it is closed or its result is already in the integration base. While any skipped ticket remains open, keep the spec open and reference it in the PR without a closing keyword. Report skipped tickets and the dependants they block.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers.

**One sub-issue = one subagent.** **MUST** launch a fresh implementer subagent for every ticket (sub-issue), exactly one ticket per subagent. **MUST NOT** implement tickets in the orchestrator context, batch several tickets into one subagent, or reuse/resume a previous ticket's subagent for the next ticket. The orchestrator only selects, delegates, verifies, and records. Run one ticket subagent at a time; wait for its result before launching the next.

Use the same integration branch and worktree for all tickets and review fixes. Do not create per-ticket branches/worktrees or use merger subagents.

## Steps

1. Read the spec and all tickets, including comments, parent links, and blockers, using the GitHub reference. Parse the spec's `OWNER/REPO#NUMBER` from its issue URL (`https://github.com/OWNER/REPO/issues/NUMBER`); that repository is the tracker. Resolve the integration (source) repository from the spec's `repo:target:<owner/repo>` label, and the base from `repo:base:<branch>`; map them to the source checkout and integration base. Keep issue operations in the tracker repository and Git/PR operations in the source repository. Resolve missing or conflicting routing explicitly before writing. Read source-root `GLOSSARY.md` when present; use its vocabulary without requiring the file. Mark `hitl` tickets skipped per the HITL guard. Reject cycles or missing ticket scope before scheduling. Treat a closed blocker as satisfied only when its implemented result is present in the integration base; cancelled or duplicate issues require explicit resolution, not automatic satisfaction.

2. Explore only as needed to establish ticket scope and testing seams. If separate context is warranted, delegate bounded exploration; save any shared notes outside the repo and pass context pointers to subsequent implementers.

3. Record the source repository and target base branch. Follow the GitHub reference to resolve `<repo>` from the `repo:target:<owner>/<repo>` label, the source checkout `<repo-root>/workspace/<repo>` (`<repo-root>` = caller's repository root; stop when `workspace/` is missing), and `<initiative-id>` from the spec title prefix before the first `:`. Create one integration branch and one worktree at `<repo-root>/workspace/<repo>.worktrees/<initiative-id>` without overwriting existing work. Confirm the new worktree is clean and on that branch; perform all implementation and checks there.

4. Select one ready ticket without the `hitl` label and launch a new dedicated subagent for that ticket only. Pass context pointers: the ticket's `OWNER/REPO#NUMBER`, the spec, the worktree path, the integration branch, and prior relevant commits/notes. The subagent implements on the shared integration branch in that worktree:
   - start from the clean, validated integration tip; never reset or discard existing work;
   - Use test-driven development, red-green-refactor, and behavior tests to build the ticket;
   - run relevant checks against the cumulative result, commit the ticket, and return its commit and validation evidence. Failed checks or incomplete work block advancement, except checks that cannot run due to environment/network/Docker/port problems, which follow the implementation focus guard (use test seams, note the skipped check).
   - The orchestrator verifies the returned commit and evidence itself; if rework is needed, send it to the same ticket's subagent, never to another ticket's subagent.

5. Mark the ticket **integrated** only when its committed implementation is verified on the integration branch. After the first such commit, push and open a draft GitHub PR against the recorded source base. Add closing references for the spec and implemented tickets, extending coverage as tickets complete; comment on each implemented issue with the PR pointer and evidence. Then **close that ticket** as completed (see the GitHub reference, *Closure and cleanup*) now that its commit is verified on the integration branch; never close a ticket whose commit or validation is missing. A branch with no commits ahead of its base cannot open a PR.

6. Recompute the **frontier** after each verified ticket commit, then repeat steps 4-5 for one next ready ticket with a new subagent. A blocker is satisfied for this run when its implementation is verified on the integration branch, whether its issue is still open or was closed by this run. External blockers still require verified resolution. If unfinished tickets remain but none are ready, report the blockers and preserve the work; do not bypass dependencies or start tickets concurrently.

7. Once all tickets are integrated, review the integration branch for bugs and logic errors. Fix all reported issues sequentially in the same worktree, commit fixes, and rerun affected checks. If a required skill is unavailable, report the blocker and obtain agreement on an alternative; never silently skip development or review.

8. Confirm the final branch passes required checks and the PR covers the spec and every implemented ticket; push remaining commits and mark the draft PR ready. Close the spec issue as completed only after every in-scope ticket is integrated, closed, and the review fixes are committed, and no `hitl` ticket remains open; do not close it otherwise. Do not merge the PR. Issues are closed by this run directly after their commits are verified on the integration branch, not by merge; keep the PR's closing keywords so merge remains consistent.

9. Remove only this run's clean worktree after all its commits are verified and pushed to the PR branch; preserve and report dirty, unpushed, or incomplete work. Keep the integration branch and PR.

## Completion criteria

- No `hitl` ticket was implemented, closed, or given a closing reference; each is reported with the dependants it blocks.
- Every in-scope ticket has verified implementation and test evidence on the integration branch, developed sequentially in the same run-owned worktree, each by its own dedicated subagent.
- The source repository and PR base match the spec's routing labels or an explicitly agreed resolution for missing/conflicting routing; issue operations and PR closing references retain each issue's owning repository.
- The reviewed PR is ready, links the spec and tickets, and reports any pending checks accurately; every integrated ticket (and the spec, once all tickets are integrated) is closed as completed, and no unimplemented issue is closed or misreported as closed.
- The run-owned worktree at `<repo-root>/workspace/<repo>.worktrees/<initiative-id>` is cleaned up or explicitly accounted for, with no user work discarded.
- Finally map every spec requirement and ticket to implementation, tests, and relevant documentation; resolve gaps or report explicit deferrals before declaring completion.
