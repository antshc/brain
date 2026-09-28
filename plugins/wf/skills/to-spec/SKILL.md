---
name: to-spec
description: Turn the current conversation into a spec and publish it to the project ticket tracker — no interview, just synthesis of what you've already discussed.
argument-hint: "What is the target branch and Initiative ID? (e.g. `release/1.1.10`, `PROJ-1234`)"
disable-model-invocation: true
---

This skill takes the current conversation context and codebase understanding and produces a spec (you may know this document as a PRD). Do NOT interview the user — just synthesize what you already know.

An **Initiative** is a coordinated product change tracked as one planning effort and may encompass multiple Capabilities and Features. A **Requirement set** is one Stakeholder requirement together with its Functional requirements, Business rules, Edge cases, and Acceptance criteria. A **Spec** packages one or more Requirement sets for planning and handoff. These definitions are local because this skill may run without the repository glossary.

The ticket tracker and triage label vocabulary should have been provided to you — Run `/manage-backlog` skill **Setup labels** if not. 

If the `/manage-backlog` skill is not available, fall back to saving the spec to `docs/specs/{{initiativeIdSlug}}.md` as markdown.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any Concepts and ADRs in the area you're touching.

2. Synthesize the agreed functional-testing decision: approved, declined, or deferred, including its scope and rationale. Preserve settled decisions without another interview; an unresolved decision stays explicitly unresolved. Prefer existing functional-slice tests at the highest useful observable seams. Discover applicable `testing-*` skills across repository, user, and installed scopes and follow the applicable `/testing-*` skills internally to establish feasibility and coverage gaps.

3. Draft the Spec using the template below. If the Initiative changes an API, Database, or Resource contract, Run `/doc-contracts` skill once per touched contract kind and inline its substantive contract content under **Contracts Delta**, preserving contract facts while removing skill references and authoring directives.

Ask the user: _"What is the target branch and Initiative ID? (e.g. `release/1.1.10`, `PROJ-1234`)"_ if not provided as arguments to this skill.

4. Before publishing, check the entire rendered ticket body: **no skill references** — no skill names, skill paths, invocation instructions, or template directives, including in inlined contract output. Skills guide authoring internally; publish only their substantive decisions and content. Keep testing scenarios independent of test-file paths and fixed method names. Run `/manage-backlog` skill **Publish spec** with the checked body and label `spec` — no additional triage.

<spec-template>

**Target Branch:** `{{targetBranch}}`
**Initiative ID:** `{{initiativeId}}`

## Problem Statement

<!-- Writing style: terse, concise, non-technical -->

The problem that the user is facing, from the user's perspective.

## Solution

<!-- Writing style: terse, concise, non-technical -->

The solution to the problem, from the user's perspective.

## Functional Requirements

<!-- Writing style: non-technical, solution agnostic -->

What the system must do — concrete, testable, externally visible behavior. Avoid implementation detail. Write each as an imperative behavior, without a `The system must` prefix.

A LONG, numbered list of functional requirements. Each functional requirement should be in the format of:

{{n}}. {{behavior}} when {{condition}}.

<functional-requirement-example>
1. *Retain deleted files for 30 days before permanent deletion.*
2. *Allow administrators to restore a deleted file to its original location.*
</functional-requirement-example>

This list of Functional requirements should cover all relevant behavior in the Initiative.

## Business Rules

<!-- Writing style: non-technical, solution agnostic. Omit this section if no business rules exist. -->

Invariants that must always hold, independent of any single user action. Each rule should be in the format of:

{{n}}. If {{condition}}, {{invariant}}.

## Edge Cases

<!-- Writing style: non-technical, solution agnostic. Omit this section if no edge cases exist. -->

Boundary conditions and their expected handling. Each edge case should be in the format of:

{{n}}. {{boundaryCondition}} → {{expectedHandling}}.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Architectural decisions and Concepts
- Technical clarifications from the developer
- Specific interactions

MUST NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Contracts Delta

<!-- Omit this section entirely if no API, Database, or Resource contract changed. -->

The changed API, Database, or Resource contracts, one block per kind. Include only the substantive contract content.

## Testing Decisions

A bullet list of the functional-testing decision (approved, declined, deferred, or unresolved), its scope and rationale, observable seams, reusable coverage described by behavior, and known gaps. Keep repository/accessor/proxy integration verification with implementation work.

List functional scenarios as bullets: `Given {{preconditions}}, when {{action}}, then {{observableOutcome}} — covers {{requirementReferences}}`. Cover the spec's functional requirements, business rules, edge cases, and acceptance criteria. Describe external behavior precisely enough to map to current test methods during execution; omit test-file paths, fixed test-method names, and all skill references.

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the Initiative.

</spec-template>
