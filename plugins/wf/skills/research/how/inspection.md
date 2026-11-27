# Inspection evidence

Apply proof checks relevant to the assigned angle at How’s selected depth. Behavior, Flow, and Data complement one answer; include deciding internal behavior, persistence, package, and provider semantics.

## Codebase lookups

Spawn the `hunty` agent for every codebase lookup; if the spawn fails, record the blocked evidence request and continue independent work. Sequence dependent lookups. Use the filled explorer prompt for system evidence and bounded requests for gaps. Fill the `hunty` Brief:

- `@work` — the filled explorer prompt, or a bounded question starting with the lookup's `@work` prefix below (`Exact literal X` / `Symbol Type.Member` when applicable). Name the deployable or repository targets as stated and the return shape: the explorer prompt's Evidence return, or cited `file:line` findings and gaps for a bounded follow-up. A Flow request names both ends in user or code words. Preserve literal and symbol spelling.
- Thoroughness — `thorough` for explorer prompts; `medium` for bounded follow-ups unless the gap needs variants.

| Lookup | `@work` prefix |
|---|---|
| Flow: handoffs, next handler, deployables a message crosses | `Flow from <A> to <B>:` |
| Behavior: trigger → executing symbol chain, names unknown | `Names unknown:` |
| Behavior: known symbol's callers, implementations, double vs real | `Symbol Type.Member:` |
| Data: writers and readers of an item or store | `Names unknown:` |
| Isolated symbol or package call site | `Symbol Type.Member:` |
| Citation line, config key, route path, table or queue name | `Exact literal X:` |

The `hunty` skill handles Graphify. For restored package evidence, name the package, version, and type or member in `@work`. Confirm the resolved package ID, version, type or member, and the deciding XML or decompiled source. Record missing package evidence as unknown.

## Evidence checks

- Trace the executing path and its selected provider or binding. A test exercising that path supports its own setup and outcome. Repo docs, comments, and PR descriptions establish intent. Record mismatches. Inspect IaC and migrations for deployed bindings and storage behavior. Use serializers and mappers to establish the written shape.
- Distinguish **facts** with decisive citations, **assumptions** with a way to verify them, and **unknowns** with exact next checks. Derive the answer from confirmed facts and state what unresolved evidence could change it.
- Trace the real implementation when a flag, profile, or environment substitutes a mock, stub, emulator, or recorded response. Identify the actual environment before making consistency, lag, or expiry claims.

## Runtime checks

Static source establishes possible behavior. When runtime selection, ordering, binding, or a live value could change the answer, use authorized access and a safe target to check the actual outcome. Prefer existing test results, read-only queries, or correlated traces. Stay within `hunty`'s read-only contract for delegated evidence. If a check needs an instrumented or state-changing probe, keep it outside `hunty` and run it only when the request authorizes that probe on a safe target. Otherwise record the claim, blocker, and exact next check.

Record the command or query, environment, and observation. For a distributed trace, record the correlation ID and observed handoffs. Keep runtime results separate from code-derived possibilities in the report.
