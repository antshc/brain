---
name: to-tickets
description: Break a Spec into agent-executable Tracer-bullet functional slices. Accepts optional implementation details or `plan.md` to guide the breakdown.
argument-hint: "{{specIssueNumber}} [{{implementationDetails}}, `plan.md`] | offline {{localSpecPath}}"
disable-model-invocation: true
---

# Implementation details to Issues

## Process

Load [github.md](./references/github.md) for GitHub issue reads, native sub-issues, blockers, reruns, and explicit offline publishing.

### 1. Gather inputs

Online publishing requires `{{specIssueNumber}}`; ask if missing. Explicit offline mode instead requires supplied spec content and Initiative/source-repository metadata. Follow **Offline publishing** in [github.md](./references/github.md) for input resolution; skip online repository/spec lookups below.

**If only `{{specIssueNumber}}` is provided:**

Resolve the tracker repository once from the docs/harness root (current repository for single-repo work):

```
gh repo view --json nameWithOwner --jq .nameWithOwner
```

Set `{{trackerRepository}}` to the printed value for later GitHub operations; it is not the source repository encoded by `{{repoLabel}}`.

Find the spec issue using **Read spec** in [github.md](./references/github.md) with `{{specIssueNumber}}`. In explicit offline mode, use the supplied local spec; missing content or routing metadata requires user input before drafting.

Set `{{repoLabel}}` to the spec's single `repo:target:<owner>/<name>` label. None or several → ask the user.

Use the issue title, body, and comments as the spec content.

**If `{{specIssueNumber}}` and (`{{implementationDetails}}` or `plan.md`) is provided:**

Resolve `{{trackerRepository}}` and `{{repoLabel}}` as above. Use the implementation details as the spec content instead of the issue body:
- **File path** (e.g. `./plans/feature.md`, `/memories/session/plan.md`) — read the file.
- **Inline text** — use directly.

### 2. Explore the codebase and scan Concepts

If you have not already explored the codebase, do so to understand the current state of the code. 
Issue titles and descriptions should use the project's domain glossary vocabulary `CONTEXT.md`.
If `ARCHITECTURE.md` has an `Architecture Decision Records` or `Crosscutting Concepts` index, read it and open any record relevant to the area you're changing.
- **Concepts** capture shared domain behavior, implementation patterns, and operational policies (such as layering, validation, persistence, testing) — slices and their acceptance/testing decisions MUST conform to matched records. Their recording contract belongs to `record-architecture`'s `concept-record` mode.
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
- **Wave**: parallel execution wave
- **Functional Requirements covered**: which functional requirements from the spec this addresses

Derive the **parallel map** from Blocked by: wave 1 = slices with no blockers; wave n = slices whose blockers all sit in earlier waves. Slices in one wave run in parallel. Present it as `Wave n: {{slices}}`.

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships and waves correct? Would any wave have two slices editing the same code (merge them or add a blocker)?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Create the GitHub issues

Explicit offline mode → save the approved ticket bodies and symbolic dependency map through **Offline publishing** in [github.md](./references/github.md); skip GitHub creation/linking below. On a GitHub failure, use that procedure to preserve known remote state and remaining local drafts.

For each approved slice, follow **Create sub-ticket** in [github.md](./references/github.md), with `parentIssueNumber` = `{{specIssueNumber}}` and label `hitl,{{repoLabel}}`. Reconcile existing children before creating issues on reruns.

Use `hitl` as the label for all issues `HITL` or `AFK` to indicate that user review is required.

`{{specIssueNumber}}` is required for each call, if missing ask user.
Use the issue body template below.

Load `references/issue-template.md` and use it verbatim as the issue body structure — include every section, following each section's `<...-rule>` instructions to draft its content. If a slice touches an API, Database, or Resource contract, Run `/doc-contracts` skill once per touched contract kind and inline its output verbatim under the issue body's **Contracts Delta** section before creating the issue.

### 5a. Link blocking

After every issue exists, build the parallel map with native links: for each approved slice with blockers, follow **Link blocking** in [github.md](./references/github.md) with `issueNumber` = the slice, `blockedBy` = its blockers' issue numbers. On reruns, link only edges not already present.

*Done when* every approved **Blocked by** edge has a native link. Report the final map as `Wave n: #{{issue}}, …` with issue numbers.

Do NOT close or modify the parent issue.

---

## Troubleshooting

**Label not found:** follow **Labels** in [github.md](./references/github.md), then retry. Explicit offline publishing or a reported GitHub/tool/authentication failure → follow **Offline publishing** there; save approved tickets to `docs/tickets/` as Markdown, not as a local tracker.
