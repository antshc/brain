# Flow: /implement-spec

Orchestrate a routed ticket graph into one integration branch and draft PR.
Follow this flow in order; load each linked procedure before its phase.

Load [GitHub constraints](./references/github.md#constraints) before any
GitHub action, including preparation reads/writes in step 1.

Only this orchestrator launches agents and controls scheduling, integration,
publication, and closure. Follow the
[Subagent launch contract](./references/sequential.md#subagent-launch-contract)
for every launch and rework.

## Inputs

- GitHub spec issue URL, plan file path, or inline plan/description.
- `mode`: `sequential` (default) or `parallel`.
- Parallel settings: `max-parallel=<positive integer>` (default `3`);
  optional `schedule=graph`.
- Spec routing: `repo:target:<owner/repo>` and `repo:base:<branch>`.
  Plan preparation collects target repository, base branch, and initiative ID.

## Workflow

1. Detect input type:
   → A: Plan file or inline description → Run
     [Prepare Plan](./references/breakdown.md#prepare-plan).
   → B: GitHub spec issue → Run
     [Prepare Spec](./references/breakdown.md#prepare-spec).
   → Unsupported or ambiguous input: Ask for valid input; stop.
   Preparation resolves spec identity and routing. Run
   [Breakdown Initiative](./references/breakdown.md#breakdown-initiative)
   only when the spec has no tickets; otherwise reuse its graph.

2. Read the complete ticket graph: spec, tickets, comments, blockers,
   and parents. Follow
   [Read the task graph](./references/github.md#read-the-task-graph);
   retain explicit `OWNER/REPO#NUMBER` identities.

3. Validate scope, repository routing, and dependencies using
   [Graph validation](./references/github.md#graph-validation).
   → Reject cycles and missing scope.
   → Resolve routing ambiguity before writes.
   → Defer open `hitl` tickets and their transitive dependants.
   → Verify closed blockers in the base; resolve external blockers.
   Record each ticket's scope, status, blockers, and supporting evidence.

4. Explore implementation scope and test seams as needed.
   Follow [Scope and scheduling](./references/parallel.md#scope-and-scheduling).
   Reuse planner evidence when available; derive footprints, conflicts,
   and critical path otherwise. Bound scope before selecting tickets.

5. Validate execution mode and settings:
   → C: Sequential (default).
   → D: Parallel.
   Follow [Execution settings](./references/parallel.md#settings)
   before creating execution branches or worktrees.

6. Create the integration branch and worktree.
   Follow [Integration setup](./references/worktrees.md#integration-setup).
   Validate ownership, paths, and base commit; confirm the new worktree
   is clean before execution.

7. Execute selected mode:
   → C: Run [Sequential Implementation](./references/sequential.md#sequential-implementation).
   → D: Run [Parallel Implementation](./references/parallel.md#parallel-implementation).
   Use [Implementer prompt](./references/sequential.md#implementer-prompt)
   for one fresh implementer per ticket.
   Parallel ticket isolation follows
   [Ticket worktrees](./references/worktrees.md#ticket-worktrees).
   Verify results before integration/publication; recompute readiness
   after each verified integration and publication.

8. Check the remaining frontier using
   [Frontier check](./references/github.md#frontier-check).
   → Unresolved blockers remain: Report blockers, preserve work,
     keep spec open and PR draft; stop before downstream phases.

9. Run [App Verification](./references/sequential.md#app-verification).
   Detect the app verification harness; delegate verification and bounded
   fixes when available. Record verdict, evidence, fixes, or the permitted
   skip reason. Unresolved `fail`/`partial` findings keep the spec open;
   continue through the remaining phases.

10. Run [Chore Pass](./references/fetch-diff.md#chore-pass).
    Fetch the current PR diff, delegate behavior-preserving cleanup,
    verify and push any resulting commit, and report out-of-scope findings.

11. Verify pushed commits, PR coverage, metadata, checks, draft state,
    and clean worktree.
    Follow [Publication verification](./references/github.md#publication-verification).
    Preserve the source root, PR URL, final head, and evidence pointers
    outside the integration worktree.

12. Remove the integration worktree.
    Follow [Cleanup](./references/worktrees.md#cleanup).
    Confirm removal from disk and Git's worktree registry.
    → Unsafe or failed cleanup: Preserve/report work; stop before review.
    Keep the integration branch and PR.

13. Run [Code Review](./references/github.md#code-review)
    from `SOURCE_ROOT`, after confirmed integration-worktree removal.
    Pass the PR URL and source root. Review uses a fresh detached worktree;
    record findings, coverage, posting results, and reviewed head.

14. Finalize using
    [Closure gates](./references/github.md#closure-gates)
    and [Completion report](./references/github.md#completion-report).
    Recheck current PR head, checks, ticket coverage, verification,
    review findings, and publication results.
    → All closure gates pass: Close spec; verify remote state.
    → Otherwise: Keep spec open and report findings.
    → Keep PR draft; never merge or mark ready.
