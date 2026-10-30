---
name: to-spec
description: Turn the current conversation into a spec and publish it as a GitHub issue or explicit offline Markdown — no interview, just synthesis of what you've already discussed.
argument-hint: "What is the target branch and Initiative ID? (e.g. `release/1.1.10`, `PROJ-1234`)"
---

This skill takes the current conversation context and codebase understanding and produces a spec (you may know this document as a PRD). Do NOT interview the user — just synthesize what you already know.

An **Initiative** is a coordinated product change tracked as one planning effort and may encompass multiple Capabilities and Features. A **Requirements** is a set of one Stakeholder requirement together with its Functional requirements, Business rules, Edge cases. A **Spec** packages one or more Requirements sets for planning and handoff.

Load [github.md](./github.md) for GitHub repository resolution, labels, duplicate prevention, and publication.

Explicit offline publishing or a reported GitHub/tool/authentication failure → save the spec to `docs/specs/{{initiativeIdSlug}}.md` as Markdown, following **Offline publishing** in the reference. Local output is not a published GitHub issue.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any Concepts and ADRs in the area you're touching.

2. Draft the Spec using the template below. If the Initiative changes an API, Database, or Resource contract, Run `/doc-contracts` skill once per touched contract kind and inline its substantive contract content under **Contracts Delta**, preserving contract facts while removing skill references and authoring directives.

Ask the user: _"What is the target branch and Initiative ID? (e.g. `release/1.1.10`, `PROJ-1234`)"_ if not provided as arguments to this skill.

Resolve `{{repository}}` (`owner/name`): a `workspace/` folder holding exactly one checkout → that checkout's own `origin` remote. More than one checkout → ask which. No `workspace/` folder → the current repository's `origin` remote. Never ask for it when exactly one candidate exists.

3. Architect design — apply only when an architect skill run happened in this conversation; otherwise skip and omit the **Design sketch** decision. Follow **Architect design** below.

4. Before publishing, check the entire rendered ticket body: **no skill references** — no skill names, skill paths, invocation instructions, or template directives, including in inlined contract output. Only the **Design sketch** `{{artifactUrl}}` placeholders may remain; attaching fills them. Skills guide authoring internally; publish only their substantive decisions and content. Derive `{{specTitle}}` as a short title naming the Spec's outcome. Follow **Publish spec** in [github.md](./github.md) with the checked body (no Initiative, branch, or repository metadata — publication adds them as title prefix and labels), `{{initiativeId}}`, `{{specTitle}}`, `{{targetBranch}}`, and `{{repository}}` — no additional triage.

5. Architect run → after the issue is verified, follow **Attach design artifacts** in [github.md](./github.md) with the issue number and the bundle manifest. Offline → follow its offline branch instead.

## Architect design

Classify the run's outputs by role, never by file name:

- **Synthesized design** — the final design package; its synthesis decision names the base candidate.
- **Base candidate** — the candidate the synthesis decision builds on; its `design` document and `sketch` tree. Synthesis decision names none or several → ask the user which candidate is the base.
- **Excluded** — losing candidates, task statement, rubric, grounding notes, run scratch. Never attach or quote them.

Map the synthesized design, then the base candidate's design, into the body; the synthesis wins on conflict:

- Problem and caller usage → **Problem Statement** and **Solution**, user-facing.
- Behavior the design commits to → **Requirements**, solution agnostic.
- Module shape, types, invariants, tradeoffs, rejected alternatives, synthesis decision → **Implementation Decisions** as prose, after the **Design sketch** decision.
- Open questions and risks → **Further Notes**.

The body MUST NOT name the architect skill, candidate labels, or the run's local paths.

Wrap the base candidate's sketch — never another candidate's — into artifacts:

```
python3 ./scripts/bundle_artifacts.py --sketch <base candidate sketch path> --out-dir <new empty temp dir outside the repository>
```

Exit 2 → report stderr and stop before publishing; never drop a sketch file to make it pass. The printed manifest lists each artifact's `name`, `type`, and `file`; the first is the **Sketch index** mapping each sketch path to its artifact names. Draft the **Design sketch** decision with every manifest name and `{{artifactUrl}}` placeholders that publication fills.

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

**Functional Requirements**

What the system must do — concrete, testable, externally visible behavior. Avoid implementation detail. Write each as an imperative behavior, without a `The system must` prefix.

A LONG, numbered list of functional requirements. Each functional requirement should be in the format of:

{{n}}. {{behavior}} when {{condition}}.

<functional-requirement-example>
1. *Retain deleted files for 30 days before permanent deletion.*
2. *Allow administrators to restore a deleted file to its original location.*
</functional-requirement-example>

This list of Functional requirements should cover all relevant behavior in this Requirement set.

**Business Rules**

<!-- Omit if no business rules exist for this Requirement set. -->

Invariants that must always hold, independent of any single user action. Each rule should be in the format of:

{{n}}. If {{condition}}, {{invariant}}.

**Edge Cases**

<!-- Omit if no edge cases exist for this Requirement set. -->

Boundary conditions and their expected handling. Each edge case should be in the format of:

{{n}}. {{boundaryCondition}} → {{expectedHandling}}.

</details>

## Implementation Decisions

<!-- Omit the Design sketch decision when no architect run happened. -->

- **Design sketch (binding):** the selected design sketch is attached to this issue as artifacts. Use it as the map for where logic goes and how code is structured: its types, signatures, module boundaries, and file locations. Start from the **Sketch index**. When the sketch conflicts with the Requirements or the codebase, the Requirements win; choose the option that best fits them.
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

<!-- Omit this section entirely if no API, Database, or Resource contract changed. -->

The changed API, Database, or Resource contracts, one block per kind. Include only the substantive contract content.

## Testing Decisions

A bullet list of agreed testing decisions: relevant test categories, observable seams, reusable coverage described by behavior, and known gaps. Omit test-file paths, fixed test-method names, and all skill references.

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the Initiative.

</spec-template>
