# Define Concept

## Inputs

A described concern or request to discover candidates, repository/docs root, and optional existing Concept/context. Own candidate selection, scope, and decisions. Return control to the router for **Resource map** to load Questioning and Concept categories before use; for **Index actions** to load index mechanics. Internal handoffs preserve this route's progress; never recursively invoke this skill.

## Evidence

Every fact in a suggestion, a question, or the recorded Concept is either a cited inspection result or a user answer from this session. A fact inspection cannot settle becomes a question to the user, carrying the evidence that left it open. A recommended answer cites its evidence or is labelled `proposal`. Return control to the router for **Select and load**, route `concept-body`, to load the Concept procedure; apply its **Evidence** and **Terminology** before continuing candidate work. Do not render yet.

## Inspection

1. Form tracks: one focused path → one track; distinct non-overlapping tracks (separate deployables, workflow boundaries, configuration versus tests, categories) → one bounded subquestion each; a track needing another's answer → sequential. No duplicate lookups for areas already in flight.
2. Spawn one built-in `explore` subagent per independent track, together in one batch; sequence dependent tracks. Brief: target, bounded question, read-only, return shape with `path:line` evidence. Blocked tracks → record the blocked evidence request and continue independent tracks.
3. Consolidate results: resolve conflicts with targeted evidence; state remaining uncertainty.

Done when every track returned its requested shape or an explicit blocker.

## Candidate ranking

A Concept pays off in `/design grill` when its index row's `default` lets a decision clear that skill's **Decision states** evidence checklist, turning a question into a Feature Assumption. Rank candidates by, in order:

1. **Default-ability** — rank by independently reusable decision keys with direct choices and checkable selection conditions across the scope. Several settled variants can qualify; unknown conditions or conflicting choices remain blurry. Inspection supports a proposal, not policy; defaults require user confirmation.
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

### Load recorded Concepts

Apply **Load index** to `ARCHITECTURE.md` and relevant building-block indexes; consume all Concept rows. An absent index or optional section means zero rows there; malformed or unread rows remain a blocker, not zero. Map each row to one or more categories from the router-loaded Concept categories, or mark it `unmapped`. Done when every row is consumed and categorized or a load blocker is reported.

### Match the described candidate, or sweep for candidates

- **Described** — the user described the concept to add. Apply **Scan and match** over the `Crosscutting Concepts` table with the description's terms and paths, and open each matched record's body. Run Inspection over the described concern and each matched record for drift. A rule that is not crosscutting → apply the loaded Concept procedure's **Where the rule belongs**; report its home and stop.
- **Not described** — sweep. Run Inspection at `thorough`, with one parallel track per category group of the arc42 list plus one drift track over the recorded Concepts. Give each track its group's categories and the item 1 mapping as `@inputs`, and this `@work` instruction verbatim:

  > For each category, report: present in the codebase, with file-and-line citations, or `no evidence found in inspected scope`; the building blocks where its decision recurs; whether the code makes one consistent choice (quote it) or several (list each with citations); the recorded Concept covering it, if any. For the drift track, report per recorded Concept every rule or `default` the code contradicts, with citations. Report only what you cite.

Done when the described candidate has its match verdict and drift result, or every arc42 category and every recorded Concept has a cited sweep verdict.

### Offer candidates and take the user's pick

- **Described** — offer extend (what the record already covers, what the description adds, cited drift) or create (its arc42 category, why no record covers it).
- **Not described** — present every applicable candidate, new and extend, ranked by **Candidate ranking**, as one table: rank, candidate, arc42 category, `new | extend`, candidate `default` or its variations, recurrence, drift, citations. After the table, list the remaining categories as `no evidence found in inspected scope`.

Done when the user has picked one candidate and `extend | create`. The user rejects every candidate → return to item 2 with their steer.

### Frame the decision tree

Map the chosen candidate's decisions: scope, applicable contexts, shared behavior and invariants, `default`, exceptions, verification. A single feature choice is not a crosscutting concept. Mark as **blurry** every branch where evidence shows variation, conflicting implementations, missing tests, undocumented intent, or an unverified claim. Done when every branch is settled by cited evidence or listed as a decision.

### Resolve through questioning and inspection

Follow the router-loaded Questioning contract over the tree. Ask every blurry branch as a question carrying its cited evidence; each default clause, its selection conditions, and exceptions are always user-confirmed decisions. Before each round, identify the facts its frontier needs and run Inspection, giving each track the concept, exact scope, and a distinct question. Done when the user confirms shared understanding, as the questioning reference requires.

### Consolidate findings

Resolve conflicting reports with targeted reads. Separate documented intent, observed behavior, and proposed policy. Surface drift or a material unsupported claim as a decision or an unknown and return to item 5. Done when no conflict or unsupported claim remains unasked.

### Evidence sweep

List every planned `Rules` bullet, scenario, and `Implementation Map` row, plus each default clause, condition, and exception. Map each to a citation or a user answer. Resolve each unmapped item to exactly one of: ask the user (return to item 5), drop it, or mark it `not verified`. Default clauses, conditions, and exceptions MUST be user-confirmed; `not verified` cannot substitute for settling them. Done when no item is unmapped.

### Document and record

Return control to the router for **Select and load**, route `concept-body`, from the resolved concept and cited evidence; select `dom`, `str`, or `ops`, load its template through **Resource map**, and render the body. Then return control to the router for **Select and load**, route `concept-record`, passing the compliant body and user-confirmed `default` to apply its gate and extend or create the record. Resume **Report** after the recording result. An explicit request to define the concept authorizes this write after the questioning confirmation; no second permission prompt. If the gate fails, report the appropriate home and do not create a Concept.

### Report

Report the recorded path, `extended | created`, remaining `not verified` items, and — after a sweep — the unchosen ranked candidates. Keep source and test files read-only throughout.

## Completion criteria

The selected Concept and its owning index row are recorded from confirmed decisions, or a gate/load blocker is explicit. Report the written path, create/extend result, unverified coverage, and unchosen candidates; source and test files remain unchanged.
