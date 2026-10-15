---
name: implement-spec
description: "Implements a GitHub spec's blocking ticket graph sequentially on one integration branch and worktree, one fresh implementer subagent per ticket, then runs a chore refinement subagent and bug review against the PR. Honors repo routing labels and hitl skips; closes verified tickets."
disable-model-invocation: true
---

Orchestrate: select, delegate, verify, record. The goal is the whole spec implemented on one **integration branch** in one run-owned worktree at `<repo-root>/workspace/<repo>.worktrees/<initiative-id>`, with a reviewed, ready PR referencing every implemented issue.

## Inputs

- Spec issue URL `https://github.com/OWNER/REPO/issues/NUMBER`; its sub-issues are the **tickets**, linked by blocking relationships (the **task graph**).
- Spec labels `repo:target:<owner/repo>` (source repository) and `repo:base:<branch>` (PR base).
- Source-root `GLOSSARY.md` when present; use its vocabulary.

## Constraints

- **GitHub reference:** **MUST** load [GitHub reference](./references/github.md) before any GitHub action, including reads, and run GitHub I/O through `gh` per its prerequisites, procedures, and failure handling. If it cannot be loaded, stop and report.
- **Repository guard:** spec and tickets may live outside the source repository. **MUST** keep each issue's `OWNER/REPO#NUMBER` identity, route issue reads/comments/closures to its owning repository, and route Git, implementation, and PR operations only to the resolved source repository. **MUST NOT** infer an issue's repository from the checkout, PR repository, or a matching number; resolve ambiguous ownership before writing.
- **HITL guard:** a ticket labeled `hitl` is **skipped**. **MUST NOT** implement, delegate, comment on, close, or add a closing reference for it. Re-read labels at each selection. A skipped ticket is not a satisfied blocker; its dependants stay unready unless it is closed and its result is in the integration base. While one stays open, keep the spec open and reference it in the PR without a closing keyword.
- **One ticket = one subagent:** **MUST** launch a fresh implementer subagent per ticket, one at a time, and wait for its result before the next. **MUST NOT** implement tickets in the orchestrator context, batch tickets, or reuse a previous ticket's subagent. Rationale: isolates ticket context and keeps the orchestrator's context for scheduling and verification. If subagents are unavailable, stop and report; never substitute direct implementation.
- **Prompt templates:** **MUST** build each subagent prompt from its bundled template with every `{{placeholder}}` filled — [implement.md](./references/implement.md) per ticket, [chore.md](./references/chore.md) for the chore pass. Pass context pointers (issue refs, paths, commits), not duplicated content.
- **Implementation focus guard:** stay on ticket work. **MUST NOT** troubleshoot environment, network, Docker, port, registry, or external-service problems; make at most one quick confirmation attempt, verify through test seams (unit tests, fakes, mocks, in-memory/stub implementations), and record the skipped check and its error in the ticket evidence. Infrastructure-only failures do not block advancement; failures caused by the ticket's code do. `implement.md` carries this guard to implementers.
- **Single worktree:** use the same integration branch and worktree for every ticket, chore, and review fix. **MUST NOT** create per-ticket branches/worktrees or merger subagents, reset or discard existing work, or merge the PR.

## Workflow

1. **Read the graph.** Read the spec and all tickets with comments, parent links, and blockers. Resolve tracker repository, source repository, and base per the GitHub reference; resolve missing or conflicting routing before writing. Mark `hitl` tickets skipped. Reject cycles or tickets without scope. Treat a closed blocker as satisfied only when its result is in the integration base; cancelled or duplicate issues require explicit resolution. Done when every ticket has status, blockers, and owning repository in a run-local map.
2. **Explore** only as needed to establish ticket scope and test seams. Delegate bounded exploration when separate context is warranted; save shared notes outside the repo and pass their paths as pointers. Done when each ticket's scope is clear enough to delegate.
3. **Create the worktree** per GitHub reference *Single worktree lifecycle*; set `@initiativeId` from the spec title prefix before the first `:` and record `BASE_COMMIT`. Done when the worktree is clean and `HEAD` is the new integration branch at `BASE_COMMIT`.
4. **Delegate one ticket.** Select one ready, non-`hitl` ticket from the **frontier**. Record `@prevHead` = worktree `HEAD`. Fill `implement.md`:

   | Placeholder | Value |
   |---|---|
   | `{{worktreePath}}` | `WORKTREE_PATH` |
   | `{{featureBranch}}` | integration branch |
   | `{{targetBranch}}` | `BASE_BRANCH` |
   | `{{ticketJson}}` | ticket's `gh issue view` JSON plus a `comments` array from the comments read; include `OWNER/REPO#NUMBER` |
   | `{{initiativeCommits}}` | `git -C WORKTREE_PATH log --reverse --format='%H %s%n%n%b' BASE_COMMIT..HEAD`, or `None yet.` |
   | `{{commitSubjectPrefix}}` | `ccode(<initiativeId> <OWNER/REPO#NUMBER>): ` |

   Launch a fresh subagent with the filled prompt. Done when it returns the final JSON object.
5. **Verify the result.** For `completed`: `HEAD` equals `result.commit`, exactly one commit since `@prevHead`, subject starts with the prefix, worktree clean, and `result.verification` names executed checks and results. Run cheap confirmations yourself when evidence is thin. On a mismatch or `failed`, send rework to the same ticket's subagent, at most two rounds; then stop advancing, preserve the work, and report. Done when the ticket is **integrated** (verified commit on the integration branch) or the run is stopped.
6. **Publish the ticket.** After the first integrated commit, push and open a draft PR against `BASE_BRANCH`; later, push and extend coverage. Per the GitHub reference, add a `Closes OWNER/REPO#NUMBER` line, post the evidence comment, and close the ticket as completed. Done when push, PR body, comment, and closure are read back.
7. **Repeat.** Recompute the frontier and repeat steps 4–6 for the next ready ticket. A blocker is satisfied when its implementation is integrated in this run or verified in the base; external blockers need verified resolution. When unfinished tickets remain but none are ready, report the blockers, preserve the work, and skip to step 10.
8. **Chore pass** once all in-scope tickets are integrated and pushed. *Load [fetch-diff.md](./references/fetch-diff.md)* and split the PR diff into `@diffDir`. Record `@prevHead`. Fill `chore.md`: `{{featureBranch}}`, `{{pullRequestUrl}}`, `{{worktreePath}}`, `{{targetBranch}}` as above; `{{diffDir}}` = `@diffDir`; `{{branchCommits}}` = the `{{initiativeCommits}}` log; `{{commitSubjectPrefix}}` = `chore(<initiativeId>): `. Launch a fresh chore subagent. Verify: zero or one commit since `@prevHead`, matching subject when present, worktree clean, checks reported. Push, then remove `@diffDir`. Report its out-of-scope findings; do not act on them. Done when the chore result is verified and pushed or recorded as none/failed.
9. **Bug review** after the chore result is pushed. The PR diff has changed, so *load [fetch-diff.md](./references/fetch-diff.md)* again and split the current PR diff into a new `@diffDir`. Record `@prevHead`. Launch a fresh review subagent with pointers: `WORKTREE_PATH`, integration branch, `BASE_BRANCH`, PR URL, and `@diffDir` with its `_manifest.tsv` as the only diff source (no refetching from the PR; take real paths from the manifest). It reviews the diff for bugs and logic errors, fixes findings sequentially in the same worktree, reruns affected checks, commits, and returns findings with fix commit, evidence, or deferral reason per finding. **MUST NOT** review or fix in the orchestrator context or reuse a ticket or chore subagent. Verify: new commits since `@prevHead` match the reported fixes, worktree clean, checks reported; then push and remove `@diffDir`. If a required review skill is unavailable, report the blocker and agree an alternative; never silently skip. Done when every finding is fixed or explicitly deferred.
10. **Finalize.** Confirm required checks and PR coverage, push remaining commits, and mark the PR ready. Close the spec as completed only when every in-scope ticket is integrated and closed, review fixes are committed, and no `hitl` ticket is open. Remove the run-owned worktree per the GitHub reference; preserve and report dirty, unpushed, or incomplete work. Keep the branch and PR.

## Output

Report: PR URL and state; per ticket — integrated commit and evidence, closure, or blocker; skipped `hitl` tickets with the dependants they block; chore and review commits; skipped infrastructure checks; worktree status.

## Completion criteria

- No `hitl` ticket was implemented, closed, or given a closing reference.
- Each integrated ticket has one verified commit by its own subagent, evidence comment, and completed closure on its owning repository; no unimplemented issue is closed or reported as closed.
- Chore pass, then bug review, each ran in its own fresh subagent after the last ticket; their commits are on the pushed branch.
- Source repository and PR base match the routing labels or an agreed resolution; the PR is ready, links the spec and every implemented ticket, and reports pending/failed checks accurately.
- The spec is closed only if every in-scope ticket is closed and no `hitl` ticket is open.
- The worktree is removed or explicitly accounted for, with no user work discarded.

## Completeness sweep

Last: map every spec requirement and ticket to implementation, tests, and relevant docs. Resolve gaps or report explicit deferrals before declaring completion.
