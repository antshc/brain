---
name: probe-concept
description: Classify a candidate rule by its structural or operational concern, check whether that concern is already recorded, and inspect how it is implemented across a codebase. Use to return representative implementations, variations, tests, and drift with file-and-line evidence before an arc42 Crosscutting Concept is written; spawned as a subagent by grill-design and define-concept, and answers to that caller alone.
---

# Probe Concept

Inspect the **as-built** shared approach, read-only. This skill runs inside a spawned subagent: it asks the user nothing, writes no file, and authors no rule or index row — it returns one evidence packet and the caller decides what to record. `/record-concept` persists what the packet earns; `/define-concept` resolves policy; `/doc-concept` writes the body.

## 1. Classify the concern

Frame one candidate concept, the affected repositories and building blocks, and the question to settle. Classify by the shared **concern**, not the component it was found in — the concern is the dedup key **Scan recorded concerns** matches on, the target **Trace the implementation** follows, and what tells the caller which `/doc-concept` template a write would use.

| Concern | Characteristic | Kind |
|---|---|---|
| Architecture/design patterns | A recurring structural shape — layering, composition, extension point, codebase-specific idiom — that several building blocks instantiate the same way | `str` |

A candidate matching no row carries `Concern: unclassified` — report it, skip the dedup below, and trace the caller's question anyway.

## 2. Scan recorded concerns

Runs before any tracing. Re-probing a concern the repo already documents spends the caller's budget rediscovering a settled decision.

1. Read the `Crosscutting Concepts` index in `ARCHITECTURE.md` and list `docs/concepts/`. Neither existing is not a gap.
2. Match the classified concern and the candidate rule's surface against each row's Trigger condition and each record's title; open a body only to confirm a likely hit.
3. **Hit** — return the packet at once with `Existing record:` naming the path and what it already covers, tracing only the delta the caller's question asks about that the record leaves unanswered.
4. **No hit** — record `Existing record: none` and trace in full.

## 3. Trace the implementation

Trace representative execution paths, boundaries, configuration, storage or messages, and tests as applicable. Look for independent occurrences, exceptions, legacy variants, and counterexamples. For a `str` concern, follow the shared implementation pattern through every building block carrying it; for an `ops` concern, check declaration, runtime behavior, and verification.

Prefer executing source and production configuration over tests, docs, and comments for behavior claims. Tests demonstrate exercised behavior; docs express intent. Report disagreement as drift. If static reading cannot close a material claim, state a specific probe rather than guessing; do not modify the repository to run it.

## 4. Return the packet

```md
**Concept / scope:** <name; repositories and building blocks inspected>
**Concern:** <concern row; `str`|`ops`|unclassified>
**Existing record:** <path and what it already covers, or none>
**Shared mechanism:** <how it works, or none found>
**Facts:** <claim → filename-only link with visible line numbers>
**Variations / counterexamples:** <different behavior and evidence>
**Tests / observable seams:** <what is verified, with evidence>
**Intent vs implementation:** <aligned, drift, or undocumented>
**Unknowns / next probes:** <unverified claim and exact check>
```

For every repo file claim use `[filename](relative/path#Lstart):Lstart-Lend` (single line: `:Lstart`), adjacent to the claim. Distinguish FACT (verified with citation), ASSUMPTION (plausible, unverified), and UNKNOWN (specific missing evidence). Do not turn a code example into a universal requirement. Give the caller exact scoped evidence and let it own the write.
