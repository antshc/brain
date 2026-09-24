---
name: probe-concept
description: Inspect how a shared domain, structural, or operational concept is implemented across a codebase. Use to find representative implementations, variations, tests, and drift with file-and-line evidence before defining or documenting an arc42 Crosscutting Concept; also called by define-concept inspection agents.
---

# Inspect Concept

Inspect the **as-built** shared approach, read-only. Do not author a rule, change files, or infer that a recurring implementation is a deliberate policy. `/define-concept` resolves policy; `/doc-concept` writes its body.

1. Frame one candidate concept, affected repositories and building blocks, and the question to settle. Read any matching `ARCHITECTURE.md` index row and existing Concept to learn the documented intent. Do not assume every category is present or inspect unrelated categories. Classify by the shared concern, not the component it was found in — the kind is what step 2 traces and what tells the caller which `/doc-concept` template a write would use.

| Concern | Kind |
|---|---|
| Business processes — their triggers, stages, outcomes, and failure behavior | `domain` |
| Architecture/design patterns (including codebase-specific patterns), domain rules, user-facing validation, transactions, persistence, caching, concurrency, integration | `structure` |
| Security, error handling, testing, configuration, migration, installation, logging, disaster recovery, domain safety, runtime safety or batch operations | `ops` |

2. Trace representative execution paths, boundaries, configuration, storage or messages, and tests as applicable. Look for independent occurrences, exceptions, legacy variants, and counterexamples. For a domain concept, follow its trigger to observable outcome; for structural, follow the shared implementation pattern; for operational, check configuration, runtime behavior, and verification.
3. Prefer executing source and production configuration over tests, docs, and comments for behavior claims. Tests demonstrate exercised behavior; docs express intent. Report disagreement as drift. If static reading cannot close a material claim, state a specific probe rather than guessing; do not modify the repository to run it.
4. Return a bounded evidence packet to the caller:

```md
**Concept / scope:** <name; `domain`|`structure`|`ops`; repositories and building blocks inspected>
**Shared mechanism:** <how it works, or none found>
**Facts:** <claim → filename-only link with visible line numbers>
**Variations / counterexamples:** <different behavior and evidence>
**Tests / observable seams:** <what is verified, with evidence>
**Intent vs implementation:** <aligned, drift, or undocumented>
**Unknowns / next probes:** <unverified claim and exact check>
```

For every repo file claim use `[filename](relative/path#Lstart):Lstart-Lend` (single line: `:Lstart`), adjacent to the claim. Distinguish FACT (verified with citation), ASSUMPTION (plausible, unverified), and UNKNOWN (specific missing evidence). Do not turn a code example into a universal requirement. Give the caller exact scoped evidence; do not write a concept file or index row.
