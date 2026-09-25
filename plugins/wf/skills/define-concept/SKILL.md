---
name: define-concept
description: Define an arc42 Crosscutting Concept — suggest which Concept to add or extend when none is described, or check a described one against the recorded Concepts — then resolve it through questioning and read-only codebase inspection and record it. Use when asked to define, add, or improve a Concept, to find which Concept is missing or most valuable to write next, or to turn an observed recurring practice into a Concept.
---

# Define Concept

Own candidate selection, the concept's scope, and its decisions. `/questioning` owns the interview; `/explore-codebase` owns inspection; `/index-docs` owns scan and match; `/doc-concept` renders the body; `/record-concept` owns persistence and indexing. Do not reimplement their rules.

## Evidence

Every fact in a suggestion, a question, or the recorded Concept is either a cited inspection result or a user answer from this session. A fact inspection cannot settle becomes a question to the user, carrying the evidence that left it open. A recommended answer cites its evidence or is labelled `proposal`. Follow `/doc-concept`' skill **Evidence** and **Terminology** for what the body may claim.

## Grill-design value

A Concept pays off in `/grill-design` when its index row's `default` lets a decision clear that skill's **Decision states** evidence checklist, turning a question into a Feature Assumption. Rank candidates by, in order:

1. **Default-ability** — inspection shows one consistent choice across the scope, so a one-sentence `default` answers the decision directly with no genuine alternative.
2. **Recurrence** — the number of building blocks where the concept's decision recurs.
3. **Drift** — for an extend candidate, how far the code has moved from the recorded rules or `default`.

A category is **applicable** only when inspection cites its presence in the codebase.

## Workflow

Copy this checklist and check off items as you complete them:
```
Define Concept Progress:
- [ ] 1. Load recorded Concepts
- [ ] 2. Match the described candidate, or sweep for candidates
- [ ] 3. Offer candidates and take the user's pick
- [ ] 4. Frame the decision tree
- [ ] 5. Resolve through questioning and inspection
- [ ] 6. Consolidate findings
- [ ] 7. Evidence sweep
- [ ] 8. Document and record
- [ ] 9. Report
```

**1. Load recorded Concepts**

Read `ARCHITECTURE.md`'s `Crosscutting Concepts` table in full; an absent file or section means zero recorded Concepts. Map each row to one or more categories from [arc42-cross-cutting-concepts.md](arc42-cross-cutting-concepts.md), or mark it `unmapped`. Done when every row carries a category or `unmapped`.

**2. Match the described candidate, or sweep for candidates**

- **Described** — the user described the concept to add. Run `/index-docs`' skill **Scan and match** over the `Crosscutting Concepts` table with the description's terms and paths, and open each matched record's body. Run `/explore-codebase` skill to inspect the described concern and each matched record for drift. A rule that is not crosscutting routes per `/record-concept`' skill **Where the rule belongs**; report its home and stop.
- **Not described** — sweep. Run `/explore-codebase`' skill **Run caller-supplied work inside the subagent** at `thorough`, with one parallel subagent per category group of the arc42 list plus one drift track over the recorded Concepts. Give each subagent its group's categories, the item 1 mapping, and this instruction verbatim:

  > For each category, report: present in the codebase, with file-and-line citations, or `no evidence found in inspected scope`; the building blocks where its decision recurs; whether the code makes one consistent choice (quote it) or several (list each with citations); the recorded Concept covering it, if any. For the drift track, report per recorded Concept every rule or `default` the code contradicts, with citations. Report only what you cite.

Done when the described candidate has its match verdict and drift result, or every arc42 category and every recorded Concept has a cited sweep verdict.

**3. Offer candidates and take the user's pick**

- **Described** — offer extend (what the record already covers, what the description adds, cited drift) or create (its arc42 category, why no record covers it).
- **Not described** — present every applicable candidate, new and extend, ranked by **Grill-design value**, as one table: rank, candidate, arc42 category, `new | extend`, candidate `default` or its variations, recurrence, drift, citations. After the table, list the remaining categories as `no evidence found in inspected scope`.

Done when the user has picked one candidate and `extend | create`. The user rejects every candidate → return to item 2 with their steer.

**4. Frame the decision tree**

Map the chosen candidate's decisions: scope, applicable contexts, shared behavior and invariants, `default`, exceptions, verification. A single feature choice is not a crosscutting concept. Mark as **blurry** every branch where evidence shows variation, conflicting implementations, missing tests, undocumented intent, or an unverified claim. Done when every branch is settled by cited evidence or listed as a decision.

**5. Resolve through questioning and inspection**

Run `/questioning` skill over the tree. Ask every blurry branch as a question carrying its cited evidence; the `default` is always a user-confirmed decision. Before each round, identify the facts its frontier needs and inspect independent areas (separate deployables, workflow boundaries, configuration versus tests) through `/explore-codebase`' skill **Run caller-supplied work inside the subagent**, giving each agent the concept, exact scope, and a distinct question. One focused path → one agent; dependent paths → sequential. Do not launch duplicate fact lookups through `/questioning` for areas already in flight. Done when the user confirms shared understanding, as `/questioning` requires.

**6. Consolidate findings**

Resolve conflicting reports with targeted reads. Separate documented intent, observed behavior, and proposed policy. Surface drift or a material unsupported claim as a decision or an unknown and return to item 5. Done when no conflict or unsupported claim remains unasked.

**7. Evidence sweep**

List every planned `Rules` bullet, scenario, and `Implementation Map` row, plus the `default`. Map each to a citation or a user answer. Resolve each unmapped item to exactly one of: ask the user (return to item 5), drop it, or mark it `not verified`. Done when no item is unmapped.

**8. Document and record**

Select the `dom`, `str`, or `ops` kind and Run `/doc-concept` skill on the resolved concept and cited evidence. Run `/record-concept` skill with the body and the user-confirmed `default` to apply its gate and extend or create the record. An explicit request to define the concept authorizes this write after the questioning confirmation; no second permission prompt. If the gate fails, report the appropriate home and do not create a Concept.

**9. Report**

Report the recorded path, `extended | created`, remaining `not verified` items, and — after a sweep — the unchosen ranked candidates. Keep source and test files read-only throughout.
