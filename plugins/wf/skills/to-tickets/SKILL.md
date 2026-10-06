---
name: to-tickets
description: Break a Spec into agent-executable Tracer-bullet functional slices. Accepts optional implementation details or `plan.md` to guide the breakdown.
argument-hint: "{{specIssueNumber}} [{{implementationDetails}}, `plan.md`]"
disable-model-invocation: true
---

# Implementation details to Issues

## Process

### 1. Gather inputs

`{{specIssueNumber}}` is **required**. If not provided as argument, ask the user.

**If only `{{specIssueNumber}}` is provided:**

Resolve the target repo once (runs unmodified on Linux, macOS, and Windows — no bash- or PowerShell-only syntax):

```
python -c 'import re,subprocess; url=subprocess.run(["git","remote","get-url","origin"],capture_output=True,text=True,check=True).stdout.strip(); print(re.sub(r"\.git$","",re.sub(r"^(git@[^:]+:|https?://[^/]+/)","",url)))'
```

Set `$REPO` to the printed value for use in later steps (e.g. `/manage-backlog` actions that read `$REPO`).

Find the spec issue: via `/manage-backlog` **Find spec ticket** with `{{specIssueNumber}}`.

Set `{{repoLabel}}` to the spec's single `repo:target:<owner>/<name>` label. None or several → ask the user.

Use the issue title, body, and comments as the spec content.

**If `{{specIssueNumber}}` and (`{{implementationDetails}}` or `plan.md`) is provided:**

Resolve `$REPO` and `{{repoLabel}}` as above. Use the implementation details as the spec content instead of the issue body:
- **File path** (e.g. `./plans/feature.md`, `/memories/session/plan.md`) — read the file.
- **Inline text** — use directly.

### 2. Explore the codebase and scan Concepts

If you have not already explored the codebase, do so to understand the current state of the code. 
Issue titles and descriptions should use the project's domain glossary vocabulary `CONTEXT.md`.
If `ARCHITECTURE.md` has an `Architecture Decision Records` or `Crosscutting Concepts` index, read it and open any record relevant to the area you're changing.
- **Concepts** capture shared domain behavior, implementation patterns, and operational policies (such as layering, validation, persistence, testing) — slices and their acceptance/testing decisions MUST conform to matched records. See the `record-concept` skill.
- **ADRs** capture localized decisions — respect and reference matched records in the issue body.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be 'HITL' or 'AFK'. HITL slices require human interaction, such as an architectural decision or a design review. AFK slices can be implemented and merged without human interaction. Prefer AFK over HITL where possible.

<vertical-slice-rules>

- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Any prefactoring should be done first
- Identify the seam through which each slice is verified (e.g. an integration test observing the database layer) and prefer the highest seam that still exercises the slice end-to-end
</vertical-slice-rules>

### 3a. Draft spec-wide functional verification

When the spec approves automated functional verification, append one functional-testing ticket for the entire spec. Preserve declined/deferred decisions; unresolved automation scope remains a question in **Quiz the user**, not implicit approval. Carry the spec's scenario bullets and requirement references into the ticket, covering all functional requirements, business rules, edge cases, and acceptance criteria. Use label `tests` only for functional-test execution; adding or repairing test code remains an implementation slice.

Make the functional-testing ticket depend on every implementation slice for its parent spec, including test additions needed for identified coverage gaps. Describe reuse of existing functional-slice tests and observable seams without test-file paths or fixed method names. Execution maps scenarios to current methods. Missing coverage discovered at execution is unverified and becomes a `hitl` investigation ticket; Testy does not write tests.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL | AFK
- **Blocked by**: which other slices (if any) must complete first
- **Wave**: parallel execution wave
- **Functional Requirements covered**: which functional requirements from the spec this addresses
- **Work**: implementation or spec-wide functional testing; show the latter's complete scenario coverage and dependencies

Derive the **parallel map** from Blocked by: wave 1 = slices with no blockers; wave n = slices whose blockers all sit in earlier waves. Slices in one wave run in parallel; the functional-testing ticket takes the last wave. Present it as `Wave n: {{slices}}`.

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships and waves correct? Would any wave have two slices editing the same code (merge them or add a blocker)?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Create the GitHub issues

For each approved slice, create a GitHub issue: via `/manage-backlog` **Create sub-ticket**, with `parentIssueNumber` = `{{specIssueNumber}}` and label `hitl,{{repoLabel}}`.

Use `hitl` as the label for all issues `HITL` or `AFK` to indicate that user review is required.

Create the approved functional-testing ticket last, with `tests`, `hitl`, and `{{repoLabel}}`, as a sub-ticket of the same spec. Approval of the breakdown does not remove `hitl`: removing that label releases execution. Reuse an existing functional-testing ticket for the same spec instead of duplicating it on reruns.

`{{specIssueNumber}}` is required for each call, if missing ask user.
Use the issue body template below.

Load `references/issue-template.md` and use it verbatim as the issue body structure — include every section, following each section's `<...-rule>` instructions to draft its content. If a slice touches an API, Database, or Resource contract, Run `/doc-contracts` skill once per touched contract kind and inline its output verbatim under the issue body's **Contracts Delta** section before creating the issue.

### 5a. Link blocking

After every issue exists (including the functional-testing ticket), build the parallel map with native links: for each approved slice with blockers, via `/manage-backlog` **Link blocking** with `issueNumber` = the slice, `blockedBy` = its blockers' issue numbers. The functional-testing ticket's `blockedBy` = every implementation ticket of the spec. On reruns, link only edges not already present.

*Done when* every approved **Blocked by** edge has a native link. Report the final map as `Wave n: #{{issue}}, …` with issue numbers.

Do NOT close or modify the parent issue.

---

## Troubleshooting

**Label not found** (`hitl` or `spec` label missing): Run `/manage-backlog` skill **Setup labels** to create the required labels, then retry. If the `/manage-backlog` skill is not available, fall back to saving the tickets to `docs/tickets/` as markdown.
