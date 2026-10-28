# Implement-Spec Flows

**Status:** Implemented

**Implementation plan:** [Implement-Spec Entry Flow Refactor Plan](./implement-spec-plan.md)

**Skill:** `plugins/wf/skills/implement-spec`

## Main flow

```text
Flow: /implement-spec

1. Detect input type:
   → A: Plan → Run Prepare Plan
   → B: Spec → Run Prepare Spec
   → Unsupported or ambiguous: Ask for valid input; stop.
2. Read complete ticket graph: tickets, comments, blockers, parents.
3. Validate scope, repository routing, and dependencies.
   → Reject cycles and missing scope.
   → Defer open hitl tickets and their dependants.
4. Explore implementation scope and test seams as needed.
5. Validate execution mode:
   → C: Sequential (default).
   → D: Parallel.
   → plan or other mode: Reject as unsupported; stop.
6. Create the integration branch and worktree.
7. Execute selected mode:
   → C: Run Sequential Implementation
   → D: Run Parallel Implementation
8. If unresolved blockers remain:
   → Report blockers, preserve work; stop.
9. Run App Verification.
10. Run Chore Pass.
11. Verify pushed commits, PR coverage, and clean worktree.
12. Remove integration worktree (preserve/report if unsafe).
13. Run Code Review.
14. Finalize:
    → All closure gates pass: Close spec.
    → Otherwise: Keep spec open and report findings.
    → Keep PR draft; never merge or mark ready.
15. End
```

## Subflow A: Prepare Plan

```text
1. Ask for target repository, target/base branch, initiative ID.
2. Validate inputs, remote branch, and source checkout.
3. Create GitHub spec with target/base routing labels.
4. Read back spec and routing.
5. Run Breakdown Initiative.
6. Return
```

## Subflow B: Prepare Spec

```text
1. Read GitHub spec and its native sub-issues.
2. Resolve source repository, base branch, initiative ID.
3. Check sub-issues:
   → Present: Use existing ticket graph; skip planner.
   → None: Run Breakdown Initiative.
4. Return
```

## Subflow: Breakdown Initiative

```text
1. Fetch validated base commit.
2. Launch fresh planner subagent with the bundled planner template.
3. Planner loads references/breakdown.md and its bundled references.
4. Apply the embedded online-only, non-interactive ticket workflow:
   → Explore applicable Concepts/ADRs and code/test seams.
   → Draft vertical slices with complete issue bodies.
   → Reconcile existing children, create missing tickets without hitl labels.
   → Link native parents/blockers and verify readback.
   → Never call /to-tickets or request breakdown approval.
5. Re-read and validate created tickets and dependencies.
6. Calculate the blocker graph, ready frontier, conflicts, and critical path.
7. Show the ticket-to-blocker graph, ready frontier, and deferred items.
8. Return
```

## Subflow C: Sequential Implementation

Procedure: [`references/sequential.md`](../../plugins/wf/skills/implement-spec/references/sequential.md).

```text
1. For each ready non-hitl ticket:
   → Launch a fresh implementer subagent for that ticket only.
   → Implement with TDD, run checks, commit exactly once.
   → Verify commit, clean tree, and evidence.
   → If invalid: Rework with same ticket agent (max 2 rounds).
   → If still invalid: Preserve work, report blocker; stop.
   → Push and create/update draft PR.
   → Publish evidence and close integrated ticket.
   → Recompute ready frontier.
2. Return
```

## Subflow D: Parallel Implementation

```text
1. Derive the blocker graph, conflicts, critical path, and deferred tickets.
2. Schedule from the graph only; max-parallel=3 by default.
3. Whenever a ready, non-conflicting ticket and worker slot exist:
   → In parallel:
      → Create one isolated branch/worktree per ready ticket.
      → Launch one fresh implementer per ticket.
      → Implement with TDD, run checks, commit exactly once.
      → Verify each result; rework max 2 rounds.
   → Process each completed implementation without waiting for unrelated workers.
   → Cherry-pick verified ticket commits into integration serially.
   → On conflict: Rework/rebase through that ticket's agent.
   → Run affected integration checks.
   → After each validated integration, push and update draft PR; publish evidence and close the integrated ticket.
   → Recompute readiness; start newly unblocked work while unrelated workers continue.
   → Remove clean ticket worktrees/branches; preserve blocked work.
4. Return
```

## Subflow: App Verification

```text
1. Detect project-local app-verification skills.
2. If none: Record skip; Return.
3. Launch a fresh verifier-fixer subagent.
4. Verify running app and capture evidence.
5. For each code-caused finding:
   → Fix application code, not the verification framework.
   → Commit fix and re-verify (max 2 fix attempts per finding).
6. Validate fix commits, checks, and evidence.
7. Push fixes and update draft PR.
8. Publish one verification verdict on the spec.
9. Preserve unresolved findings; Return.
```

## Subflow: Chore Pass

```text
1. Fetch and split the PR diff.
2. Launch a fresh chore subagent.
3. Apply behavior-preserving cleanup.
4. Verify zero or one chore commit, clean tree, and checks.
5. Push; report out-of-scope findings.
6. Return
```

## Subflow: Code Review

```text
1. Confirm integration worktree removal.
2. Invoke /code-review with PR URL and source root.
3. Independently review bugs, quality, smells, initiative coverage.
4. Publish findings and record failures to post.
5. Do not auto-fix review findings.
6. Return
```

## Completion invariants

1. One integration branch, one fresh implementer per ticket, one verified commit per integrated ticket.
2. Dependencies, routing, HITL skips, and test evidence are enforced.
3. Parallel workers never share a writable worktree; integration merges are serialized.
4. App verification precedes chore; independent review follows integration-worktree removal.
5. The spec closes only when all gates pass; the PR always remains a draft.
