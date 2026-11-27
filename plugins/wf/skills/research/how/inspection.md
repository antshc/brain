# Inspection evidence

Apply proof checks relevant to the assigned angle at How’s selected depth. Behavior, Flow, and Data complement one answer; include deciding internal behavior, persistence, package, and provider semantics.

## Codebase lookups

Spawn the `codebase` agent for every codebase lookup; if the spawn fails, record the blocked evidence request and continue independent work. Sequence dependent lookups. Use the filled explorer prompt for system evidence and bounded requests for gaps. Fill the `codebase` task:

- Task — the filled explorer prompt, or a bounded question starting with the lookup's prefix below (`Exact literal X` / `Symbol Type.Member` when applicable). Name the deployable or repository targets as stated and the return shape: the explorer prompt's Evidence return, or cited `file:line` findings and gaps for a bounded follow-up. A Flow request names both ends in user or code words. Preserve literal and symbol spelling.
- Thoroughness — `thorough` for explorer prompts; `medium` for bounded follow-ups unless the gap needs variants.

The `codebase` agent's Task prefixes define how each prefix is searched; pick it here.

| Lookup | Task prefix |
|---|---|
| Flow: handoffs, next handler, deployables a message crosses | `Flow from <A> to <B>:` |
| Behavior: trigger → executing symbol chain, names unknown | `Names unknown:` |
| Behavior: known symbol's callers, implementations, double vs real | `Symbol Type.Member:` |
| Data: writers and readers of an item or store | `Names unknown:` |
| Isolated symbol or package call site | `Symbol Type.Member:` |
| Citation line, config key, route path, table or queue name | `Exact literal X:` |

For restored package evidence, name the package, version, and type or member in the task. Confirm the resolved package ID, version, type or member, and the deciding XML or decompiled source. Record missing package evidence as unknown.

## Evidence checks

- The `codebase` agent applies its Evidence rules (executing source vs intent, test scope, doubles, fact/assumption/unknown labels). Trace the executing path and its selected provider or binding.
- Derive the answer from confirmed facts and state what unresolved evidence could change it.
- Identify the actual environment before making consistency, lag, or expiry claims.

## Runtime checks

Static source establishes possible behavior; runtime selection, ordering, binding, or a live value can change the answer. Delegated `codebase` evidence follows the agent's read-only runtime rule; the brief states whether runtime checks are authorized and on which target. An instrumented or state-changing probe stays outside `codebase` and runs only when the request authorizes it on a safe target; otherwise record claim, blocker, and exact next check. For a distributed trace, record the correlation ID and observed handoffs. Keep runtime results separate from code-derived possibilities in the report.
