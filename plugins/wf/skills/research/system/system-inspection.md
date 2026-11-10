# System inspection

Use these depth and evidence rules to answer a question about the as-built system. [How](../how/how.md) owns the report structure and path.

## Select depth

| Question | Depth | Evidence |
|---|---|---|
| Narrow system question | Concise | One focused Explore pass. Confirm the deciding behavior and cite the primary source. |
| Complex system question | Detailed | Apply relevant lenses. Trace outcome-relevant boundaries, failure paths, and edge cases. Split only independent evidence work that benefits from parallel lookup. |
| Explicit inspection or verification | Full | Apply the relevant lens checks throughout the requested scope. Verify material runtime-dependent claims or identify the claim, blocker, and exact next check. |

Explicit inspection or verification sets the minimum depth. Escalate when extra boundaries, consequential failure paths, or conflicting evidence leave the question open. A supplied axis selects the primary lens. Infer it from the question when omitted.

## Select lenses

| Lens | Use for | Reference |
|---|---|---|
| Behavior | One deployable's triggers, execution, and outcomes | [Behavior](behavior-inspection.md) |
| Flow | Handoffs and contracts across deployables | [Flow](flow-inspection.md) |
| Data | A data boundary, including keys, ownership, consistency, migration, concurrency, retention, or deletion | [Data](data-inspection.md) |
| Focused | An isolated call, symbol, or package API in a saved answer | Use the relevant checks below. |

Load only the references that help answer the question. A lane's internal decision, persistence semantics, or cloud behavior that determines the outcome belongs in the same answer. Follow the relevant lens or verify provider evidence for that detail. Treat a separately scoped question as independent work for a later request.

## Codebase lookups

Send each Explore request directly to `hunter`. If Hunter is unavailable, record the blocked evidence request and continue independent work. Sequence dependent lookups. Use the filled explorer prompt for a system evidence pass, and use bounded requests to fill evidence gaps. Pass each Explore request:

- `@work` — the filled explorer prompt or a bounded question. For a bounded question use a prefix such as `Exact literal X`, `Symbol Type.Member`, or `Names unknown` when applicable. Preserve literal and symbol spelling.
- `@shape` and `@depth` — from the lookup table for the assigned angle.
- `@target` — deployable or repository names as stated.
- `@outputShape` — the explorer prompt's Evidence return, or cited `file:line` findings and gaps for a bounded follow-up.

| Lookup | `@shape` | `@depth` |
|---|---|---|
| Flow: handoffs, next handler, deployables a message crosses | `relationship` | `thorough` |
| Behavior: trigger → executing symbol chain, names unknown | `relationship` | `medium` |
| Behavior: known symbol's callers, implementations, double vs real | `symbol` | `medium` |
| Data: writers and readers of an item or store | `relationship` | `medium` |
| Isolated symbol or package call site | `symbol` | `quick` |
| Citation line, config key, route path, table or queue name | `literal` | `quick` |

Hunter handles Graphify. For restored package evidence, send a request with `@shape: nuget`. Confirm the resolved package ID, version, type or member, and the deciding XML or decompiled source. Record missing package evidence as unknown.

## Evidence checks

- Trace the executing path and its selected provider or binding. A test exercising that path supports its own setup and outcome. Repo docs, comments, and PR descriptions establish intent. Record mismatches. Inspect IaC and migrations for deployed bindings and storage behavior. Use serializers and mappers to establish the written shape.
- Distinguish **facts** with decisive citations, **assumptions** with a way to verify them, and **unknowns** with exact next checks. Derive the answer from confirmed facts and state what unresolved evidence could change it.
- Trace the real implementation when a flag, profile, or environment substitutes a mock, stub, emulator, or recorded response. Identify the actual environment before making consistency, lag, or expiry claims.

## Runtime checks

Static source establishes possible behavior. When runtime selection, ordering, binding, or a live value could change the answer, use authorized access and a safe target to check the actual outcome. Prefer existing test results, read-only queries, or correlated traces. Stay within Hunter's read-only contract for delegated evidence. If a check needs an instrumented or state-changing probe, keep it outside Hunter and run it only when the request authorizes that probe on a safe target. Otherwise record the claim, blocker, and exact next check.

Record the command or query, environment, and observation. For a distributed trace, record the correlation ID and observed handoffs. Keep runtime results separate from code-derived possibilities in the report.
