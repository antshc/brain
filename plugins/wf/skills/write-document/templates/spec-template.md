<!-- Prompt XML and literal placeholders are intentional. -->
<!-- markdownlint-disable MD033 -->

# Specification template

<spec-template>

## Problem Statement

<!-- Writing style: terse, concise, non-technical -->

The problem that the user is facing, from the user's perspective.

## Solution

<!-- Writing style: terse, concise, non-technical -->

The solution to the problem, from the user's perspective.

## Requirements

<!-- Writing style: non-technical, solution agnostic -->

One subsection per Requirement set. Each groups a Stakeholder requirement with its own Functional Requirements, Business Rules, and Edge Cases. Repeat the `### {{n}}. {{stakeholderRequirement}}` heading and its `<details>` block for every Requirement set covering the Initiative.

### {{n}}. {{stakeholderRequirement}}

<details>
<summary>{{n}}. {{stakeholderRequirement}}</summary>

**Functional Requirements:**

What the system must do — concrete, testable, externally visible behavior. Avoid implementation detail. Write each as an imperative behavior, without a `The system must` prefix.

A complete, numbered list of functional requirements. Each functional requirement should be in the format of:

{{n}}. {{behavior}} when {{condition}}.

<functional-requirement-example>
1. *Retain deleted files for 30 days before permanent deletion.*
2. *Allow administrators to restore a deleted file to its original location.*
</functional-requirement-example>

This list of Functional requirements should cover all relevant behavior in this Requirement set.

**Business Rules:**

<!-- Omit if no business rules exist for this Requirement set. -->

Invariants that must always hold, independent of any single user action. Each rule should be in the format of:

{{n}}. If {{condition}}, {{invariant}}.

**Edge Cases:**

<!-- Omit if no edge cases exist for this Requirement set. -->

Boundary conditions and their expected handling. Each edge case should be in the format of:

{{n}}. {{boundaryCondition}} → {{expectedHandling}}.

</details>

## Implementation Decisions

<!-- Omit the Design sketch decision when no accepted design package exists. -->

- **Design sketch (binding):** the selected design sketch is attached to this issue as artifacts. Use it as the map for where logic goes and how code is structured: its types, signatures, module boundaries, and file locations. Start from the **Sketch index**; the module map, when attached, maps sketch files to target locations. When the sketch conflicts with the Requirements or the codebase, the Requirements win; choose the option that best fits them.
  - [{{artifactName}}]({{artifactUrl}}) — one entry per artifact, Sketch index first.

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Architectural decisions and Concepts
- Technical clarifications from the developer
- Specific interactions

MUST NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Contracts Delta

<!-- Omit only when the Contracts gate listed no kinds. -->

*Load and follow the `doc-contracts` skill to write an API, database, resource, or GUI contract delta as a terse diff* once per touched kind (API, Database, Resource, other, GUI); inline its output verbatim, one block per kind, ordered API → Database → Resource → other → GUI.

## Testing Decisions

A bullet list of agreed testing decisions: relevant test categories, observable seams, reusable coverage described by behavior, and known gaps. Omit test-file paths, fixed test-method names, and all skill references.

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the Initiative.

</spec-template>
