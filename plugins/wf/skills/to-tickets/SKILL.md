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

Resolve the target repo once (runs unmodified on Linux, macOS, and Windows — no bash- or PowerShell-only syntax):

```
python -c 'import re,subprocess; url=subprocess.run(["git","remote","get-url","origin"],capture_output=True,text=True,check=True).stdout.strip(); print(re.sub(r"\.git$","",re.sub(r"^(git@[^:]+:|https?://[^/]+/)","",url)))'
```

Set `$REPO` to the printed value for use in later steps (e.g. `/manage-backlog` actions that read `$REPO`).

Find the spec issue by milestone: via `/manage-backlog` **Find spec ticket**.

If no issue is found, ask the user for the GitHub issue number and fetch it:
via `/manage-backlog` **Read ticket**.

Use the issue title, body, and comments as the spec content.

**If `{{milestoneTitle}}` and (`{{implementationDetails}}` or `plan.md`) is provided:**

Use the implementation details as the spec content instead of a GitHub issue:
- **File path** (e.g. `./plans/feature.md`, `/memories/session/plan.md`) — read the file.
- **Inline text** — use directly.

### 2. Explore the codebase and scan ADRs/Concepts

If you have not already explored the codebase, do so to understand the current state of the code. 
Issue titles and descriptions should use the project's domain glossary vocabulary `CONTEXT.md`.
If `ARCHITECTURE.md` has a `Crosscutting Concepts` or `Architecture Decision Records` index, read it and open any record relevant to the area you're changing.
- **Concepts** capture the architectural backbone (layering, module/interface design, persistence slices, testing strategy) — slices and their acceptance/testing decisions MUST conform to matched records. See the `record-concept` skill.
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

For each approved slice, create a GitHub issue: via `/manage-backlog` **Create ticket**, passing the milestone `{{milestoneTitle}}` and label `hitl`.

Use `hitl` as the label for all issues `HITL` or `AFK` to indicate that user review is required.

The `{{milestoneTitle}}` from the spec is required for each call, if missing ask user.
Use the issue body template below.

Create issues in dependency order (blockers first) so you can reference real issue numbers in the "Blocked by" field.

Load `references/issue-template.md` and use it verbatim as the issue body structure — include every section, following each section's `<...-rule>` instructions to draft its content. If a slice touches an API, Database, or Resource contract, run `/to-delta` once per touched contract kind and inline its output verbatim under the issue body's **Contracts Delta** section before creating the issue.

Do NOT close or modify the parent issue.

---

## Troubleshooting

**Label not found** (`hitl` or `spec` label missing): run `/manage-backlog` **Setup labels** to create the required labels, then retry. If the `/manage-backlog` skill is not available, fall back to saving the tickets to `docs/tickets/` as markdown.
