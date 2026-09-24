---
name: define-concept
description: Define an arc42 Crosscutting Concept through questioning and parallel read-only inspection of the codebase, then document and record the agreed shared business process, implementation pattern, or operational policy. Use when asked to define a concept from a system, reconcile a proposed convention with existing code, or turn an observed recurring practice into a Concept.
---

# Define Concept

Own the concept's scope and decisions. `/questioning` owns the interview; `/inspect-concept` establishes codebase facts; `/doc-concept` renders the body; `/record-concept` owns persistence, frontmatter, and indexing. Do not reimplement their rules.

1. Frame one candidate shared concept and the affected system. Read `ARCHITECTURE.md`'s `Crosscutting Concepts` index and matching records; check for an existing owner before expanding a new concept. Map the decision tree for scope, applicable contexts, shared behavior/invariants, exceptions, and verification. A single feature choice is not a crosscutting concept.
2. Run `/questioning` for unresolved **decisions**. Before each round, identify environmental **facts** needed by that frontier. Spawn bounded read-only subagents for independent codebase areas (for example separate deployables, workflow boundaries, or configuration versus tests). Give each one the concept, exact scope, and a distinct question; instruct it to Run `/inspect-concept` and return its cited evidence packet. For one focused path use one agent; for dependent paths inspect sequentially. Ask independent frontier decisions while inspections run; wait for evidence only where a decision depends on it. Do not launch duplicate fact lookups through `/questioning` for areas already in flight.
3. Consolidate findings across agents. Resolve conflicting reports with targeted reads; separate documented intent, observed behavior, and proposed policy. Surface drift or a material unsupported claim to the user as a decision or an unknown, not a fabricated rule. Recompute the questioning frontier until the user confirms shared understanding, as `/questioning` requires.
4. Select the `domain`, `structure`, or `ops` kind and Run `/doc-concept` on the resolved concept and cited evidence. Pass the body to `/record-concept` to apply its gate and extend an existing record or create one. An explicit request to define and document the concept authorizes this write after the questioning confirmation; no second permission prompt. If the gate fails, report the appropriate home and do not create a Concept.
5. Report the recorded path, whether it was extended or created, and remaining evidence gaps. Keep source and test files read-only throughout.
