---
name: to-tickets
description: Breaks a spec into tracer-bullet GitHub tickets. Accepts an optional plan or plan.md to guide slicing.
argument-hint: "{{milestoneTitle}} [{{implementationDetails}}, `plan.md`]"
---

# Implementation details to Issues

## Process

### 1. Gather inputs

`{{milestoneTitle}}` is **required**. If not provided as argument, ask the user.

**If only `{{milestoneTitle}}` is provided:**

Resolve the target repo once.

**bash:**
```bash
REPO=$(git remote get-url origin | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##')
```

**PowerShell:**
```powershell
$REPO = $(git remote get-url origin) `
  -replace '^git@[^:]+:','' `
  -replace '^https?://[^/]+/','' `
  -replace '\.git$',''
```

Find the spec issue by milestone and label:
```bash
gh issue list --repo "$REPO" --milestone "{{milestoneTitle}}" --label "spec" --json number,title,body,comments --limit 1
```
If no issue is found, ask the user for the GitHub issue number and fetch it:
```bash
gh issue view {{issueNumber}} --repo "$REPO" --json number,title,body,comments
```
Use the issue title, body, and comments as the spec content.

**If `{{milestoneTitle}}` and (`{{implementationDetails}}` or `plan.md`) is provided:**

Use the implementation details as the spec content instead of a GitHub issue:
- **File path** (e.g. `./plans/feature.md`, `/memories/session/plan.md`) — read the file.
- **Inline text** — use directly.

### 2. Explore the codebase and scan ADRs/Concepts

If you have not already explored the codebase, do so to understand the current state of the code. 
Issue titles and descriptions should use the project's domain glossary vocabulary (CONTEXT.md).
Read the ADR and Concept indexes in `ARCHITECTURE.md`, then open every ADR under `docs/adr/` and every Concept under `docs/concepts/` that touches the area you're changing.
- **Concepts** capture the architectural backbone (layering, module/interface design, persistence slices, testing strategy) — slices and their acceptance/testing decisions MUST conform to them. See `manage-docs/CONCEPT-FORMAT.md`.
- **ADRs** capture localized decisions — respect and reference the relevant ones in the issue body.
- Confirm you have scanned both `docs/adr/` and `docs/concepts/` before moving on; if either directory is absent, note that and continue.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be 'HITL' or 'AFK'. HITL slices require human interaction, such as an architectural decision or a design review. AFK slices can be implemented and merged without human interaction. Prefer AFK over HITL where possible.

<vertical-slice-rules>

- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Any prefactoring should be done first
</vertical-slice-rules>

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL | AFK
- **Blocked by**: which other slices (if any) must complete first
- **Functional Requirements covered**: which functional requirements from the spec this addresses

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Create the GitHub issues

For each approved slice, create a GitHub issue using `gh issue create --repo "$REPO" --milestone "{{milestoneTitle}}" --label "hitl"`.

Use `--label "hitl"` for all issues `HITL` or `AFK` to indicate that user review is required.

The `--milestone "{{milestoneTitle}}"` from the spec is required for each command, if missing ask user. 
Use the issue body template below.

Create issues in dependency order (blockers first) so you can reference real issue numbers in the "Blocked by" field.

<issue-template>
## Parent Spec

#{{specIssueNumber}}

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

Avoid specific file paths or code snippets — they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it here and note briefly that it came from a prototype. Trim to the decision-rich parts — not a working demo, just the important bits.

## Acceptance criteria
<acceptance-criteria-rule>
- Written for a manual QA tester. Each criterion must be a single, self-contained check the tester can perform and judge as pass or fail without reading code or the spec.
- Phrase as an observable action and its expected result (e.g. "When {{action}}, then {{observableOutcome}}").
- Use the domain language of the spec or the CONTEXT.md. Never reference file paths, class names,variable names, or other implementation details.
- Avoid vague or unverifiable words such as "works", "correctly", "properly", "as expected". State the exact expected outcome instead.
- If a relevant error condition exists, add a criterion for the expected behavior during that failure (e.g. the message or state the tester should see).
</acceptance-criteria-rule>

- [ ] Acceptance criteria 1
- [ ] Acceptance criteria 2
- [ ] Acceptance criteria 3

## Blocked by

- Blocked by #{{issueNumber}} (if any)

Or "None - can start immediately" if no blockers.

## Functional Requirements addressed

Reference by number from the parent spec:

- {{functionalRequirementName}}
- ...

## Implementation Decisions

- Preserve integration constraints and assumptions required for implementation.
- Use short technical statements and implementation-oriented language.
- No specific file paths or code snippets (they become outdated quickly).

### Verify section

This section is used to verify the code changes. List the tests that will be added, updated, and run to verify the task's changes. 
- *Mandatory*: The Verify section must be present in every issue. It is used to verify the code changes. if the Code changes verification strategy or the Testing strategy from the `ARCHITECTURE.md` present use them to guide the verification. Include the commands what will be use to run the integration, REST API automation tests for the verification.
- Only test external behavior, not implementation details.
- List which modules will be tested and prior art for the tests.

</issue-template>

Do NOT close or modify the parent issue.

---

## Troubleshooting

**Label not found** (`hitl` or `spec` label missing): run `/manage-backlog` action **Setup labels** to create the required labels, then retry. If the `/manage-backlog` skill is not available, fall back to saving the tickets to `docs/tickets/` as markdown.
