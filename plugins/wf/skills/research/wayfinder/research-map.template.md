# Research map issue template

Render the root body below into the GitHub `wayfinder:map` issue after exact-proposal approval. This defines tracker state, never a second active Markdown map. Keep every section; use none for empty sections.

## Root body

```markdown
## Destination

<research question and outcome the evidence must support>

## Notes

<context, constraints, exact versions and required sources>

## Document and branches

- Document: docs/ongoing/<slug>-research.md
- Integration branch: wayfinder/<slug>; HEAD: <sha>
- Session base branch/SHA: <branch>/<sha>
- Worktree: <absolute path>; ownership record: <durable path outside disposable worktrees>
- Last reconciled: <evidence identity, result/integrated/document SHAs or none>
- Pending synchronization: <first unconfirmed step or none>
- Pending proposals: <retained draft paths/revisions, status and next action, or none>
- Pending human choice: <interview phase/question pointer and owner, or none>

## Findings so far

- [<topic title>](<report or sub-issue link>) — <supported conclusion, status and resolved unknown IDs>

## Not yet specified

- <stable unknown/risk ID>: <in-scope concern too vague to frame as a topic and consequence>
  - Status: <unframed | awaiting prerequisite framing>
  - Resolve when: <evidence criterion or missing framing; risk trigger, mitigation and verification>
  - Linked work: <related context or predecessor link; concrete work lives on its owner>
  - Next action / owner: <what settles it and who acts>
  - Outcome / limits: <supported evidence and residual risk>

## Out of scope

- <excluded work and reason; user scope decision and existing issue link when applicable>
```

Keep only coarse concerns in root Not yet specified. Graduate precise portions to approved children or durable pending drafts before removing their fog rows; retain coarse remainder. Pending approvals and open precise questions are not fog.

## Sub-issue body

Use `wayfinder:research` for a sharp factual question; `wayfinder:experiment` for one falsifiable hypothesis. Refer to topics by title. Resolve symbolic parents/blockers only to verified issue links after approval. Native parent/sub-issue edges are required; blockers use shared Wayfinder body references, not invented dependency state.

```markdown
## Question

<one factual question, or falsifiable claim with confirmed-when and refuted-when criteria>

## Unknowns

<stable unknown/risk IDs and provenance; criteria, consequence and risk/mitigation details owned here; no live root fog row required>

## Work

- Helper: research | prove
- Scope/target: <bounded inputs, revision/environment and limits>
- Output: <exact report path under owned result worktree>
- Expected result: <deciding evidence and proof limits>

## Research scope

<research only: Explore | How | Why | Cloud | Web; target, version, lens where applicable>

## Blocked by

<verified prerequisite issue links, or none; prerequisites must be integrated before dispatch>

## Part of

<verified parent map/issue link>

## Result

<added on dispatch: source revision, owned worktree/branch, pinned base, ownership record,
findings/evidence links and limits, exact payload identity, approval/integration state,
result/integrated/document SHAs, last sync and next action>
```

Remove Research scope for experiments and Result until dispatch. A partial, blocked, conflicting, rejected or inconclusive result remains open with its limitation and next action. Retain its stable unknown IDs and block dependent work.
