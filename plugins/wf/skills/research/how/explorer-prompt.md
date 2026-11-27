# Explorer prompt

Fill the placeholders; pass the brief verbatim as the `codebase` agent's task; it names the angle's targets and asks for the Evidence return. How passes findings to How report Explain. Cover only this angle; others may have independent explorers.

## Original question

> {QUESTION}

## Assigned angle

{EXPLORATION_ANGLE}

- Flow ends — `Flow from {FROM} to {TO}` in user or code words; Flow angle only, else omit
- Targets or refs — {TARGETS_OR_REFS}
- Research depth — {DEPTH}
- Applicable lens and proof checks — {LENS_AND_CHECKS}

## Collect evidence

Resolve targets/revisions and read contracts first per the `codebase` agent's rules. Discover relevant deployables, functional slices, triggers, candidate paths, and boundaries before deep tracing when ownership is unknown. A deployable is independently started/deployed; a library, script, chart, or bundle belongs to its executing unit unless independently started. Cite startup/deployment proof; mark unresolved classifications.

Trace the actual executing path from trigger to observable outcome. Confirm registration, selected implementation, provider/fallback, configuration/flags, data transformations, and relevant failures/retries/async paths. Apply supplied proof checks only to steps needed to settle this question; deepen where the outcome depends on it, not through unrelated methods.

For impact grounding, take the changed symbols or contracts, reviewed checkout/revision or dirty state, and any endpoint pairs from the assigned angle. Find consumers through usages, implementations, and `rg`, including configuration, event subscriptions, and wire or data contracts. Carry the dependency evidence below into the report draft.

For each internal handoff, establish sender, wire contract, receiver, and deployment/config binding. Matching names are insufficient. Continue into accessible source across repositories while its behavior affects the scoped outcome. Stop at a proven external terminal or explicit scope boundary with the integration contract and reason. Inaccessible source ends source coverage, not downstream behavior proof. A missing sender/receiver/binding remains an unconfirmed crossing. Record cycles as revisits, not new deployables.

Resolve decisive C# dependency behavior through the `codebase` agent's NuGet rules, including the restored package version, assembly/TFM, and exact member. XML documents intent; source or decompiled implementation establishes execution. Missing restore/source/tools → name the gap; do not guess version or behavior. Keep searches bounded to resolved targets and package cache.

Stay read-only per the `codebase` agent's rules. If static evidence leaves a deciding runtime claim open, use only authorized read-only checks on a safe target; prefer existing test results, read-only queries, or correlated traces. Record command/query, environment, and observation. Mutation, unavailable access, or unsafe target → report claim, consequence, blocker, and exact next check.

Cite decisive source lines in place. Separate executing source, documented intent, runtime observations, assumptions, and unknowns. Support non-obvious behavior with evidence; historical motivation without evidence is a Why question. Return evidence inline, not a user-facing report or diagram.

## Evidence return

Include only applicable fields; keep narrow answers compact.

- **Scope and revision** — assigned question/angle, targets/revisions, observed environment.
- **Deployables and slices** — independently running units, functional responsibilities, startup/deployment evidence; key types/services and ownership.
- **Flow** — ordered triggers, decisions, calls, data, and outcomes; citations for each material claim.
- **Dependency evidence** — for each material changed boundary, record reviewed revision or dirty state, consumers or hops verified with source file/line citations, and the consequence and next check for each unresolved gap.
- **Boundaries** — inputs/outputs, sender, contract, receiver, and binding evidence at handoffs/stores.
- **Terminals and coverage** — relevant branches traced/excluded; external terminals, scope stops, inaccessible-source stops, cycles, unconfirmed crossings; stopping reason and completeness consequence.
- **Packages** — resolved ID/version, assembly/TFM, type/member, XML/source/decompiled provenance and deciding evidence.
- **Gotchas** — consequential edge cases, failures/fallbacks, conflicts, surprising behavior.
- **Runtime** — checks, environment, observed results, limits.
- **Files read** — compact evidence index the router can verify.
- **Open questions** — assumptions, unknowns, evidence gaps; consequence and exact next check.
