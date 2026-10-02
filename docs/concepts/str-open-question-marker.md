# Open-Question Marker

## Purpose

A skill drafting an artifact (scenario, design, plan) sometimes must fill in a choice the gathered facts don't settle — a setting, a rung, a scope boundary. Silently guessing hands the user an invented value disguised as a confirmed one; blocking on every such choice stalls the draft one question at a time. An Open-Question Marker lets the agent keep drafting while making every unsettled choice visible and resolvable in one pass.

## Concept

While drafting, the agent still picks a value for every choice — its own safest/cheapest default — but marks that choice `❓` inline, at the exact point it occurs, instead of stating it as settled. Drafting continues through every section this way. Before the draft counts as final, every `❓` in the document is collected and put to the user as one `questioning`-style round: each flagged choice becomes a numbered question with its options and the agent's recommended answer, all asked together rather than one at a time. The draft is done only once no `❓` remains. Because an answer can change facts a later choice depended on, the agent re-verifies affected sections after each round instead of only substituting the literal answer.

## Rules

- MUST mark a choice `❓` inline, at the point it occurs, when drafting a value or branch the gathered facts don't settle — and MUST still pick its own safest/cheapest default rather than leaving the choice blank or unstated.
- MUST NOT treat a draft as final while any `❓` marker remains in it.
- MUST surface every `❓` to the user as one round in `questioning`'s format — numbered, with options and a recommended answer — rather than asking them as they're written or leaving them for the user to find.
- MUST re-verify sections and choices downstream of an answered `❓` rather than only substituting the literal answer, since one answer can invalidate another choice made elsewhere in the draft.

## Example

`/prototype-cloud-scenario`'s Draft step 2 marks every fact-unsettled Fidelity, Target environment, or Prerequisites choice `❓` inline, then its Review step 3 asks each as a numbered question with options and a recommended answer, re-running fact-gathering after each answer round before editing. `/grill-design` marks open design-tree questions the same way (`❓ **Q1**`, `❓ **Q2**`) when handing a round to the user. Both consume the round format itself from `/questioning`, which owns asking the frontier of settled-enough questions together and recomputing it after each answer.
