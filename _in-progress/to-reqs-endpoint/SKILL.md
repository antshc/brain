---
argument-hint: Which feature design document, and which endpoint(s) changed?
description: Add or update an Endpoints section in a feature design document, documenting only the delta each endpoint introduces.
disable-model-invocation: true
name: to-reqs-endpoint
---

Identify REST API changes from the context and document REST API resources changes inside a feature design document. You write the **delta** — only what an endpoint _adds, modifies, or removes_, never the untouched rest of the contract. A reader diffs the feature against today's API by reading your section alone.

Ask the questions one at a time to identify resources and their changes, if resources listed are unclear, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a *fact* can be found by exploring the swagger.json or codebase, look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.

Fill the template at [`reference/rest-api-delta.template.md`](reference/rest-api-delta.template.md): it holds the exact tables, collapsibles (`<details>`), section layout, and `Change` columns to produce. Copy it, replace every `<placeholder>`, and delete the parts the change set does not touch. Read it before writing.

## Step 1 — Assemble the change set

Identify the target design document and every endpoint the feature adds or changes. For each endpoint capture:

- Method + path, and whether it is **Added** (new endpoint), **Modified** (existing endpoint changing), or **Removed** (existing endpoint deleted).
- **Contract** changes — path, query/path params, request fields, response fields, headers, status codes.
- **Behaviour** changes — validation, side effects, ordering, defaults, error conditions.
- Which object schemas it adds, modifies, or removes, and which cross-cutting conventions (auth, pagination, error format, idempotency) it adds, modifies, or removes.

Ask the user for anything you cannot source from the design document or the codebase — never invent contract or behaviour.

**Done when:** every endpoint in the change set has its method+path, Added/Modified/Removed marker, and its contract and behaviour changes captured.

## Step 2 — Pick the layout by endpoint count

- **More than one endpoint** → the section has three top-level parts: `# Endpoints`, `# Objects`, `# Conventions`. Object schemas shared across endpoints live under `# Objects` and are referenced from endpoints as `#/Objects/Name`. Cross-cutting rules live under `# Conventions`.
- **Exactly one endpoint** → write only that endpoint entry, with its object schema **inlined** into the entry. Omit the `# Objects` and `# Conventions` sections entirely.

**Done when:** you know which of the two layouts applies and which sections you will write.

## Step 3 — Write each endpoint entry

Follow the template structure — resource under `##`, operation under `### <verb> <title>` — with these delta rules:

- Open the entry with a one-line summary, then a **Notes** subsection when there is anything to record — bullets capturing how the system behaves today, constraints, open questions, or notes the user provided. Omit it when empty.
- Add a **Behaviour changes** subsection: bullets for validation, side effects, ordering, defaults, and error-condition changes. Every bullet starts with **Added**, **Modified**, or **Removed**. Contract changes are carried by the schema/field tables, not repeated here.
- In every field, parameter, header, and status-code table, and in every JSON schema block, include **only the changed fields** — those added, modified, or removed — and drop untouched fields. Give each table a `Change` column valued `Added`, `Modified`, or `Removed`.
- Add an **Example** `<details>` block only when the user explicitly asked for examples.

**Done when:** every endpoint has a Behaviour changes subsection, and every table/schema in it lists only delta fields, each marked Added, Modified, or Removed.

## Step 4 — Objects (multi-endpoint layout only)

Under `# Objects`, add an entry for each shared object the feature adds, modifies, or removes, showing **only** its changed fields with the `Change` column. Skip objects the feature does not touch.

**Done when:** every shared object referenced by an endpoint delta is present with its delta fields, and no untouched object is listed.

## Step 5 — Conventions (multi-endpoint layout only)

Under `# Conventions`, document **only** the conventions the feature adds or changes (e.g. a new error code, a new idempotency rule). Omit the section if the feature changes no convention.

**Done when:** every changed convention is documented and no unchanged convention is restated.

## Step 6 — Verify

Re-read the written section against the change set from Step 1: every endpoint present, every table a pure delta, Examples present only if requested, and the layout matching the endpoint count.

**Done when:** the section is written into the design document and the checks above hold.
