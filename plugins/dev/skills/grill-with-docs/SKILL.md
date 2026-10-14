---
name: grill-with-docs
description: "Stress-tests a plan, design, or idea through a relentless interview, resolves domain terminology against code, and captures canonical terms in GLOSSARY.md as decisions crystallise."
disable-model-invocation: true
---

# Grill with Docs

Interview until the user confirms a shared understanding. Capture resolved domain language during the interview; implementation waits for confirmation.

## Process

1. Read the topic and relevant code. Read root `GLOSSARY.md` if present; its absence is not a setup problem. Model the discussion as a **design tree**: each decision branches into its dependent decisions.
2. Compute the **frontier**: decisions whose prerequisites are settled. Investigate environmental facts yourself; ask the user for decisions, not facts available from code or tools. Delegate only substantial independent investigation. A pending investigation blocks only its dependent questions.
3. Interview the frontier, recommending an answer for each question. Word questions so "yes" accepts the recommendation. Use the host's question tool when available, one question at a time when required; otherwise present a numbered round of independent questions. Wait for answers before asking dependent questions.
4. Challenge language and assumptions throughout:
   - Surface conflicts with existing glossary definitions and ask which meaning is intended.
   - Replace vague or overloaded words with precise canonical terms.
   - Invent concrete edge-case scenarios to test relationships and boundaries.
   - Cross-check claims against code; surface contradictions rather than treating either source as automatically correct.
   - When a term is resolved, immediately update root `GLOSSARY.md` using [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md). Create the file only when the first term is resolved. Keep definitions domain-only, not implementation decisions or scratch notes.
5. Recompute the frontier after each answer or investigation. Continue until every branch is settled or explicitly deferred with the user; never silently assume an answer.
6. Summarise the agreed design, constraints, glossary changes, and explicit deferrals. Obtain confirmation of shared understanding before implementing the discussed design.

## Completion criteria

- No unresolved branch remains silently assumed; deferrals are explicit.
- Resolved domain terms are captured in root `GLOSSARY.md` using canonical vocabulary.
- The user has confirmed the shared understanding; the discussed design has not been implemented without approval.
