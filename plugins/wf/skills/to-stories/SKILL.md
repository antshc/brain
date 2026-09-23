---
description: Turn raw requirements, `/to-spec` output, or `/to-zdesign` output into an approved ordered list of atomic User stories with numbered headings, Jira-sync metadata, dependencies, and one `/draft-story` body per story. Use when the user wants stories, backlog-ready items, Acceptance Criteria, or FE/BE-split work from requirements, a spec, or a design.
name: to-stories
disable-model-invocation: true
---

Turn conversation, raw requirements, spec or design into an ordered list of atomic, testable **User stories**, broken down by **Functional slice**.

This skill owns source normalization, the proposed breakdown and approval gate, story order and numbers, dependencies, numbered headings, Jira-sync metadata, and final list assembly. Run `/draft-story` skill exactly once per approved row for that story's formatted Title and body.

## Vocabulary

- An **Initiative tag** is an optional SCREAMING_SNAKE_CASE story-heading label that groups stories under an Initiative.
- A **Deployable kind** is the `[FE]` or `[BE]` prefix that identifies the Deployable owning a Functional slice.
- A **Functional slice** deployable-local, end-to-end implementation of a distinct system behavior or outcome.
Its boundaries follow functional responsibility rather than technical layers. It belongs to one deployable; a cross-deployable flow connects Functional slices through their contracts. Its test seams are the observable inputs and outputs where the slice can be tested independently.

Produce one or more User stories per Functional slice. Split non-atomic work by independently testable behavior, not by technical layer; one User story may touch every layer its Functional slice requires.

## Input Normalization

Normalize every accepted input form into the same proposed breakdown table while preserving every supplied field verbatim:

- **Raw requirements** → preserve supplied Features, Functional slices, Stakeholder requirements, Functional requirements, Business rules, Edge cases, error conditions, and Acceptance criteria; derive only absent structure.
- **`/to-spec` output** → preserve its supplied Functional requirements, Business rules, Edge cases, Implementation Decisions, Contracts Delta, and other relevant source fields; derive absent Features, deployable-local Functional slices, and Stakeholder requirements without rewriting supplied text.
- **`/to-zdesign` output** → preserve its supplied Initiative tag, Features, Functional slices, Stakeholder requirements, Functional requirements, Business rules, Edge cases, error conditions, Acceptance criteria, Implementation Decisions, Contracts Delta, IDs, and dependencies; derive only absent fields.

Keep source Business rules, Edge cases, error conditions, and Acceptance criteria attached to every proposed row they constrain so `/draft-story` can apply them. *Done when* all three input forms yield Proposed Breakdown Format and every supplied field remains verbatim.

## Breakdown

- **Identify Features by user-meaningful behavior.** A Feature may require several Functional slices.
- **Identify Functional slices by deployable-local responsibility.** FE and BE are separate Deployables, so each owns a distinct Functional slice prefixed with its Deployable kind. A cross-deployable flow becomes related Functional slices connected by contracts, not one cross-deployable slice.
- **Identify User stories by testable progress.** Split a Functional slice only where each User story has a distinct observable outcome; within one Deployable, never split merely at database, API, or other technical-layer boundaries.
- **Done when** every requirement is traced to the Functional slice or slices that implement it and every proposed User story advances exactly one Functional slice.

## Workflow
1. **Normalize input** → apply Input Normalization to the supplied raw requirements, `/to-spec` output, or `/to-zdesign` output. *Done when* every source field is either preserved verbatim in a proposed row or explicitly carried as source context for that row.
2. **Propose breakdown** → present Proposed Breakdown Format and wait for explicit approval; give FE and BE their own rows because they are separate Deployables. Revise and re-confirm requested merges, splits, reassignments, metadata, or dependencies. *Done when* the user explicitly approves the table; draft no story before approval.
3. **Number and link** → assign each approved row a story number in table order, retain supplied Jira ID and Epic ID values or use `TBD`, and resolve dependencies from approved in-batch rows only. Render each dependency as `(Story {{n}}, {{jiraId|TBD}})`; use `None` when a row has no in-batch dependency. *Done when* every row has a number, both IDs, and a valid Blocked by value.
4. **Draft each body** → Run `/draft-story` skill exactly once per approved row, passing its optional Initiative tag, Deployable kind, Feature, Functional slice, verbatim Stakeholder requirement, Functional requirements addressed, and source Business rules, Edge cases, and error conditions. Also pass source Acceptance criteria, Implementation Decisions, and Contracts Delta when relevant. *Done when* every approved row has exactly one body beginning with the required `**Title:**` line and passing `/draft-story`'s Quality Check.
5. **Assemble list** → emit one Output Format block per approved row in table order, placing that row's `/draft-story` body after its heading and Jira-sync metadata. *Done when* the list has one numbered heading, one metadata block, and one complete body per approved row, with no wrapper prose or cross-story index.

## Proposed Breakdown Format

| Story | Deployable kind | Initiative tag | Feature | Functional slice | Stakeholder requirement | Functional requirements addressed | Business rules | Edge cases and error conditions | Source Acceptance criteria | Jira ID | Epic ID | Depends on |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| {{n}} | {{deployableKind|[FE] or [BE]}} | {{[TAG]|optional}} | {{feature}} | {{functionalSlice}} | {{stakeholderRequirement|verbatim}} | {{functionalRequirements|verbatim references or statements}} | {{businessRules|verbatim or None}} | {{edgeCasesAndErrors|verbatim or None}} | {{sourceAcceptanceCriteria|verbatim or None}} | {{jiraId|supplied or TBD}} | {{epicId|supplied or TBD}} | {{approved in-batch rows|None}} |

## Quality Check

- Raw requirements, `/to-spec` output, and `/to-zdesign` output all normalize into Proposed Breakdown Format.
- Supplied fields remain verbatim; only absent fields are derived.
- The proposed table was explicitly approved before any story body was drafted.
- Every input requirement is traced to every Functional slice that implements it, without unexplained duplication.
- Story count matches the approved table row for row, and numbering follows table order.
- Run `/draft-story` skill exactly once per approved row; each run produces exactly one body.
- Every heading matches `## Story {{n}} — {{deployableKind}} {{[TAG]}} {{stakeholderRequirement}}`, omitting the Initiative tag and its following space when absent.
- Each body Title repeats the row's optional Initiative tag, Deployable kind, and verbatim Stakeholder requirement in `/draft-story`'s required order and format.
- Jira ID and Epic ID use supplied values or `TBD`.
- Blocked by references only in-batch `(Story n, Jira ID)` pairs or is `None`.
- Every source Functional requirement, Business rule, Edge case, error condition, and Acceptance criterion remains traceable through the resulting list.
- Each output block contains one numbered heading, one Jira-sync metadata block, and one `/draft-story` body; Jira-sync metadata appears only in this wrapper.

## Output Format

This is the sole composed story-list template. Emit one block per approved row in table order, separated by one blank line. Add no wrapper prose, summary section, or cross-story index.

```
## Story {{n}} — {{deployableKind|[FE] or [BE]}} {{[TAG]|optional Initiative tag followed by one space}}{{stakeholderRequirement|verbatim Stakeholder requirement}}

**Jira ID:** {{jiraId|supplied or TBD}}
**Epic ID:** {{epicId|supplied or TBD}}
**Blocked by:** {{blockedBy|(Story {{n}}, {{jiraId|TBD}}), (Story {{m}}, {{jiraId|TBD}}) | None}}

{{draftStoryBody|complete output from the row's single `/draft-story` run, beginning with `**Title:**`}}
```
