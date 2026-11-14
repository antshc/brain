# Inspection evidence

Apply proof checks relevant to the assigned angle at How’s selected depth. Behavior, Flow, and Data complement one answer; include deciding internal behavior, persistence, package, and provider semantics.

## Codebase lookups

Execute bounded lookups directly using Research's Local search and Evidence checklist. Sequence dependent lookups. Preserve exact literal/symbol spelling; name both ends of a Flow. Set the angle's local hints below, target/ref and expected cited evidence; no agent dispatch.

| Lookup | `@shape` | `@depth` | `@work` prefix |
|---|---|---|---|
| Flow: handoffs, next handler, deployables a message crosses | `relationship` | `thorough` | `Flow from <A> to <B>:` |
| Behavior: trigger → executing symbol chain, names unknown | `relationship` | `medium` | `Names unknown:` |
| Behavior: known symbol's callers, implementations, double vs real | `symbol` | `medium` | `Symbol Type.Member:` |
| Data: writers and readers of an item or store | `relationship` | `medium` | `Names unknown:` |
| Isolated symbol or package call site | `symbol` | `quick` | `Symbol Type.Member:` |
| Citation line, config key, route path, table or queue name | `literal` | `quick` | `Exact literal X:` |

Local search handles Graphify. For restored package evidence, apply the registered NuGet tactic directly with `@shape: nuget`. Confirm the resolved package ID, version, type or member, and the deciding XML or decompiled source. Record missing package evidence as unknown.

## Evidence checks

- Trace the executing path and its selected provider or binding. A test exercising that path supports its own setup and outcome. Repo docs, comments, and PR descriptions establish intent. Record mismatches. Inspect IaC and migrations for deployed bindings and storage behavior. Use serializers and mappers to establish the written shape.
- Distinguish **facts** with decisive citations, **assumptions** with a way to verify them, and **unknowns** with exact next checks. Derive the answer from confirmed facts and state what unresolved evidence could change it.
- Trace the real implementation when a flag, profile, or environment substitutes a mock, stub, emulator, or recorded response. Identify the actual environment before making consistency, lag, or expiry claims.

## Runtime checks

Static source establishes possible behavior. When runtime selection, ordering, binding, or a live value could change the answer, use authorized access and a safe target to check the actual outcome. Prefer existing test results, read-only queries, or correlated traces. Stay within Research's Read-only contract. An instrumented or state-changing probe belongs outside Research and requires its own authorized safe execution context. Otherwise record the claim, blocker, and exact next check.

Record the command or query, environment, and observation. For a distributed trace, record the correlation ID and observed handoffs. Keep runtime results separate from code-derived possibilities in the report.
