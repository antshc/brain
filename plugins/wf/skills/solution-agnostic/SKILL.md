---
name: solution-agnostic
description: Rewrite requirements, capabilities, and stories to remove implementation artifacts (widget, screen, table, endpoint, flag, worker, access role), raising each to the behavior and entity it enables. Use to scrub requirement or story text of leaked design before it is written down.
---

# Solution-Agnostic

Scrub requirement, capability, or story text of implementation artifacts so every statement names a **behavior and entity** — what the system *does* and the outcome the actor gets — never the thing that is built to deliver it (widget, screen, table, endpoint, flag, access role).

## The rule

Every statement is solution-agnostic: it names a behavior and an entity, never an implementation artifact. This governs **capability titles**, **stakeholder requirements**, **functional requirements**, **business rules**, and **acceptance criteria** alike.

## The domain glossary exception

A **domain glossary** is an allowed list of terms the business already uses to name entities and behaviors. When one is provided:
- **Prefer the domain glossary.** Use its terms verbatim for entities, states, and behaviors instead of inventing paraphrases, even when a term looks like an artifact.
- **Allow any term defined in the glossary.** A term on the allowed list is treated as domain language, not a leaked artifact — keep it as-is and do not de-reference it.
- Continue to scrub every term that is **not** in the glossary using the swap test and the de-referencing tables below.

## The swap test

If swapping the UI or the technology would force a reword, the statement is over-specified. Apply the test to every line:
- Reject: *Surface active alerts in the page header* · *Manage tasks on the Monitoring page* · *Store the soft-delete flag*.
- Prefer: *Surface the count of active alerts* · *Manage tasks* · *Keep a deleted item recoverable for its retention window*.

## The de-referencing move

When a statement names an artifact, raise it **one level** to the behavior it enables and push the artifact down into design:
1. Find the artifact term (a screen, column, endpoint, status flag, worker, access role).
2. Ask what the actor actually gets from it — what they perceive, can do, or are told.
3. Rewrite the statement as that behavior + entity; drop the artifact.

## Apply the de-referencing tables

**Always** apply the bundled tables in [references/solution-agnostic-terms.md](references/solution-agnostic-terms.md) — they map leaked artifacts (UI, data, API, domain-state, process, access) to the behavior to state instead.

## Output

Return the same text with every artifact term scrubbed and raised to behavior + entity, followed by a short note listing each correction made (the leaked term → the behavior it became). If no artifact terms remain, say so.
