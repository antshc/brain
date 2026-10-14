---
name: to-tickets
description: "Breaks a plan, spec, or conversation into tracer-bullet GitHub tickets with acceptance criteria, parent links, and blocking dependencies, then publishes the approved task graph through gh."
disable-model-invocation: true
---

# To Tickets

Break a plan, spec, or conversation into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

**MUST** load the bundled [GitHub reference](./github.md) before any GitHub action, including reads. Execute GitHub actions through `gh` according to its prerequisites, procedures, and failure handling. If the reference cannot be loaded, stop and report the blocker. No setup-generated tracker configuration is required.

**Required input:** The user **MUST** supply the GitHub repository for publishing tickets as `OWNER/REPO`. If absent or malformed, ask for it and wait; never infer it from the checkout, remotes, or the parent spec's URL. Record it as `TRACKER_REPOSITORY`, separate from the development/PR repository and any parent issue's repository.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL), read the file or fetch the GitHub issue's full body and all comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Read root `GLOSSARY.md` when present and use its vocabulary in ticket titles and descriptions; proceed normally when absent.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first

</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change (rename a column, retype a shared symbol) whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket; green is promised only there.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Iterate until the user approves the breakdown.

### 5. Publish the tickets to GitHub

Publish one GitHub issue per approved ticket in dependency order, blockers first, using the issue template below. Record created issue URLs immediately; on partial failure report what exists and resume from it rather than duplicating tickets.

Set native blocking dependencies using database IDs, not issue numbers. If the source was an existing issue, attach each ticket as its sub-issue. Use the reference's explicit text fallback only when the capability is confirmed unavailable.

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

Do NOT close the parent or edit its body, labels, or status. Adding the approved sub-issue relationship is the only parent mutation allowed.

<issue-template>

## Parent

A reference to the parent GitHub issue (if the source was an existing issue, otherwise omit this section).

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective, not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- A reference to each blocking ticket, or "None (can start immediately)". Omit this section when blockers were set as native edges.

</issue-template>

Avoid specific file paths or code snippets: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Completion criteria

- Every approved slice exists as one GitHub issue in the user-supplied `TRACKER_REPOSITORY` with acceptance criteria.
- Read-back confirms each parent link and blocking edge, natively or through an explicitly reported fallback; the graph has no cycles.
- Report ticket URLs, dependencies, and the ready frontier. Leave parent content and status unchanged.
- Finally compare the published graph against the approved breakdown and source spec; resolve or explicitly report any omitted scope.
