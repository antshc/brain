---
argument-hint: Which feature design document, and which GUI surface(s) changed?
description: Add or update a ZIC GUI section in a feature design document, documenting only the delta each page or GUI component introduces.
disable-model-invocation: true
name: to-reqs-gui
---

Identify GUI changes from the context and document inside a feature design document. You write the **delta** — only what a surface _adds, modifies, or removes_, never the untouched rest of the UI.

A **surface** is either a **page** (its entry documents the changes to the GUI components on that page) or a **GUI component** itself (a utility component, or a Layout component used across pages such as header, menu, or badge).

Ask the questions one at a time to identify surfaces and their changes, if surfaces listed are unclear, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a *fact* can be found by exploring the codebase, look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.


Fill the template at [`reference/gui-delta.template.md`](reference/gui-delta.template.md), which holds the exact structure, markers, and tables to produce. Read it before writing.

## Step 1 — Assemble the change set

Identify the target design document and every **surface** the feature adds or changes. For each, gather from the design document and the codebase its behaviour, data-loading, sub-component, and grid changes. Ask the user for anything you cannot source — never invent behaviour or field mappings.

**Done when:** every surface in the change set has its behaviour, data-loading, sub-component, and grid changes captured.

## Step 2 — Fill the template

Write one `<details>` entry per surface under `GUI delta`, then the `Conventions` entries. Include **only changed** behaviour, sub-components, grid columns, and conventions; drop everything the feature leaves untouched.

**Done when:** every changed surface, grid, and convention is present, and every entry is a pure delta.

## Step 3 — Verify

Re-read the section against the change set from Step 1: 
- every surface present, 
- every page and gui component a pure delta

**Done when:** the section is written into the design document and the checks above hold.
