<!-- @: Planner task-graph output contract; inline into the planner agent's Output section. -->
<!-- @: Ticket-backed systems: replace `id` with real issue refs and `dependsOn` with native blocker edges; do not invent a second task database. -->

Return exactly one JSON object.

| Field | Content |
|---|---|
| `status` | `completed \| blocked` |
| `tasks[]` | One per task; never empty when `completed` |
| `tasks[].id` | Stable ID (`T1`) or issue ref; preserved across replans |
| `tasks[].goal` | One observable behavior the task delivers |
| `tasks[].requirements` | Requirement or acceptance IDs covered; non-empty |
| `tasks[].scope` | Predicted files, modules, or symbols written; real paths |
| `tasks[].dependsOn` | Hard blocker task IDs; `[]` when none |
| `tasks[].acceptance` | Observable pass conditions, including failure and boundary cases |
| `tasks[].verification` | Grounded checks or test seams; `[]` never allowed |
| `tasks[].context` | Source paths, ADRs, artifacts the worker reads first |
| `tasks[].handoff` | What the worker returns (commit SHA, checks run, decisions) |
| `conflicts[]` | Write overlaps between tasks not linked by `dependsOn`; `[]` when none |
| `conflicts[].tasks` | Pair of task IDs |
| `conflicts[].kind` | `file \| soft` (`file` = same path written; `soft` = shared registry, manifest, generated output) |
| `conflicts[].evidence` | Concrete path or symbol both tasks write |
| `ready` | Task IDs with no unmet `dependsOn`, executable now |
| `criticalPath` | Longest `dependsOn` chain, ordered task IDs |
| `openQuestions[]` | Blocking decisions; `[]` when none |
| `openQuestions[].question` | Decision needed from a human |
| `openQuestions[].evidence` | Source showing why it is unresolved |

```json
{
  "status": "completed",
  "tasks": [
    {
      "id": "T1",
      "goal": "Define the cache contract and fallback behavior",
      "requirements": ["FR-1", "BR-2"],
      "scope": ["src/Workers/JournalCache/IJournalCache.cs"],
      "dependsOn": [],
      "acceptance": ["Contract preserves the remote-read fallback"],
      "verification": ["dotnet test --filter JournalCacheContract"],
      "context": ["src/Workers/JournalReader.cs", "docs/adr/0007-cache.md"],
      "handoff": ["commit SHA", "executed checks with status", "decisions made"]
    }
  ],
  "conflicts": [
    { "tasks": ["T2", "T3"], "kind": "soft", "evidence": "src/Program.cs DI registration" }
  ],
  "ready": ["T1"],
  "criticalPath": ["T1", "T2"],
  "openQuestions": []
}
```

Failure shape:

```json
{
  "status": "blocked",
  "tasks": [],
  "conflicts": [],
  "ready": [],
  "criticalPath": [],
  "openQuestions": [
    { "question": "Should cache misses fall back to remote reads or fail?", "evidence": "Spec FR-1 and BR-2 conflict" }
  ]
}
```
