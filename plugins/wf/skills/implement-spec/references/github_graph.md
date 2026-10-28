# Ticket graph

Graph validation and frontier readiness.

## Graph validation

1. Reject cycles, naming the cycle, and tickets without scope.
2. Resolve tracker repository, source repository, and base per *Prerequisites*; resolve missing/conflicting routing before writes.
3. Mark `hitl` tickets and their unsatisfied transitive dependants `deferred`.
4. Verify closed blockers in `BASE_COMMIT`; explicitly resolve cancelled/duplicate issues and external blockers.
5. Record each ticket's identity, owner, status, scope, blockers, and evidence in the run-local map.

**Graph report.** Render ticket-to-blocker adjacency as a table, then ready frontier, conflicts, critical path and deferred tickets. Edge direction is blocker → dependent; `none` is an explicit root, not an omitted row. Show it after Breakdown Initiative and in parallel mode.

| Ticket | Blocked by | Paths | Conflicts with |
|---|---|---|---|
| acme/shop#12 | none | `src/Export/Schema/` | acme/shop#14 |
| acme/shop#13 | none | `src/Api/Auth/` | none |
| acme/shop#14 | none | `src/Export/Schema/` | acme/shop#12 |
| acme/shop#15 | acme/shop#12 | `src/Export/Writer/` | none |
| acme/shop#16 | none | - | deferred: hitl |
| acme/shop#17 | acme/shop#16 | - | deferred: blocked by #16 |

Ready: #12, #13, #14 (select a non-conflicting subset). Critical path: #12 → #15. Deferred: #16 `hitl`; #17 blocked by #16. List every node, including deferred tickets' blocker edges.

## Frontier check

1. Re-read labels and recompute readiness after each publication.
2. A blocker is satisfied only when integrated in this run or verified in the base.
3. Unfinished tickets remain but none are ready → report each unready ticket and why (open `hitl`, unresolved external dependency), preserve all work and the draft PR, keep the spec open, and stop before chore, verification, review, actualize/cleanup, or finalization. Never force progress or declare completion.
