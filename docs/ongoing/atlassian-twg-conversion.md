# Atlassian skill body conversion through twg

<details>
<summary>Reviewers</summary>

| **Role** | **Name** |
|---|---|
| Author (Feature Lead) | |
| Reviewers (Architect \ TL) | |
| PO | |

</details>

<!-- adf:toc -->

# Problem Statement and Goals

The `atlassian` skill moves Confluence page and Jira work-item bodies through its own REST client and the `atlassian-python-api` library, converting ADF to and from Markdown in-process. Every other Atlassian operation already runs through the `twg` CLI. Two access paths mean two client stacks and more code to maintain.

Goal: decide whether body fetch and publish can move to `twg`, and through which twg body format — HTML plus a Markdown package converter, or twg Markdown — without losing any conversion the skill supports today. The decision rests on a feature compatibility matrix and two live prototypes measured byte for byte against the current converter.

# Glossary and Abbreviations

<details>
<summary>Glossary and Abbreviations</summary>

| **Term** | **Description** |
|---|---|
| twg | Atlassian Teamwork Graph CLI; reads and writes Confluence and Jira content with `--format html` or `--format md` bodies. |
| ADF | Atlassian Document Format, the JSON body model Confluence and Jira store. |
| Current converter | The skill's in-process ADF↔Markdown converter on `main` at the baseline revision, used by Fetch page, Publish page, Fetch work and Publish work. |
| twg-html route | twg reads/writes HTML bodies; a Markdown package converts HTML↔Markdown, plus custom handlers for skill-specific constructs. |
| twg-md route | twg reads/writes Markdown bodies directly; twg owns the conversion. |
| Capability | One catalogued construct or behaviour the skill must round-trip, identified by its regression capability ID or converter test behaviour. |
| Verdict | Per-capability, per-direction outcome: twg automatic, implement on twg, keep REST fallback, or lost. |
| Parity | Byte-identical Markdown compared with the current converter's output. |

</details>

# Requirements

<details>
<summary>Requirements</summary>

<!-- adf:wide-table -->
| **#** | **Requirement** | **Priority** | **Details** | **Source** |
|---|---|---|---|---|
| 1 | The `atlassian` skill has one selected twg body route backed by evidence. | MVP |  | Dev team |
| 1.1 | *The design selects exactly one route — twg-html with a Markdown package converter, or twg-md — for Confluence page and Jira work-item bodies.* | MVP | • Selection follows the compatibility matrix and both prototype comparisons.<br>• A route may keep a justified minimal REST remainder for capabilities twg cannot carry. | Dev team |
| 1.2 | *Every capability the skill supports today has a verdict in both directions.* | MVP | • Rows cover every regression capability and every behaviour asserted by the Markdown/ADF converter tests.<br>• Verdict is one of twg automatic, implement on twg, keep REST fallback, lost.<br>• A capability with no evidence stays Pending, never assumed. | Dev team |
| 1.3 | *Parity is measured byte for byte against the current converter.* | MVP | • Publish direction: the same fixture is published by the current path and by each twg route into sibling pages; all are fetched by the current fetcher and compared.<br>• Fetch direction: a page published by the current publisher is read by each twg route and compared with the current fetch.<br>• Whitespace or list-marker differences count as differences. | Dev team |
| 1.4 | *The design lists, per capability, what the selected route covers automatically and what must be implemented on top.* | MVP | • Each "implement on twg" row names the mechanism, for example a converter handler or targeted HTML edit.<br>• Each REST fallback row states why twg cannot carry it. | Dev team |
| 1.5 | *Prototypes run against live Confluence and Jira test targets without colliding.* | MVP | • Confluence runs create their own subpages under the designated test parent page, so runs execute in parallel.<br>• Jira runs reuse one subtask of the designated test parent work item and run sequentially. | Dev team |

</details>

# Assumptions and Limitations

- Baseline is `main` at the revision that includes the Confluence conversion guards; later converter changes require re-running the comparison.
- twg 1.4.2 exposes `html` and `md` body formats only, with no raw ADF body; constructs that exist only in ADF must survive through HTML macros, the Markdown dialect, or a REST fallback.
- Prototype verdicts depend on the twg version under test; a twg upgrade can change verdicts.
- twg owns its HTML and Markdown conversions and publishes no per-node contract; documentation alone cannot establish byte-identical parity, so prototypes decide every row not explicitly documented.
- twg Markdown is documented as lossy for rich Confluence content: panels, status and emoji render as text, other macros as placeholders, layouts and ADF-only nodes may be lost.
- twg HTML is documented as the lossless editing format; macros are written as extension HTML, and targeted HTML edits preserve untouched nodes exactly.
- twg returns Jira descriptions as ADF on read, so Jira fetch can reuse the current ADF→Markdown converter; Jira writes accept HTML, Markdown or plain text.
- Attachments (upload/download) and inline comments (read with highlight marker id, create with text selection) have twg commands; Draw.io custom-content records have none found.
- Pending — selected Markdown package pair and its licence (Research).

# Out of Scope

- Migrating the production `atl.py` body tactics to the selected route.
- Rewriting the existing decision record on twg versus REST access; the selected route is the input for that later change.
- Search, people, spaces and other non-body operations, which already run through twg.
- Address page comments targeted edits, which already run through twg.

# Solution Overview

Pending — selected route and its fetch/publish design follow the compatibility matrix and prototype comparison.

## Use cases

- **Fetch a Confluence page as Markdown**: an agent reads a page through the selected twg route and receives Markdown identical to today's Fetch page output.
- **Publish Markdown to a Confluence page**: an agent creates or updates a page from Markdown through the selected twg route; the stored page fetches back identical to a page published today.
- **Fetch a Jira work item as Markdown**: an agent reads a work-item description through the selected twg route with output identical to today's Fetch work.
- **Publish Markdown to a Jira work item**: an agent creates or updates a work-item description through the selected twg route with the same stored result as today's Publish work.

## Fetch body through twg

Pending — sequence diagram and decisions after route selection.

### Decisions

- Pending — fetch decisions after route selection.

## Publish body through twg

Pending — sequence diagram and decisions after route selection.

### Decisions

- Pending — publish decisions after route selection.

# Testing Guidelines

<details>
<summary>Testing Guidelines</summary>

## Testing by Dev

- The existing round-trip regression catalogue and Markdown/ADF converter tests define the parity checks.
- Pending — prototype harness shape and how the selected route reuses these tests.

## QA Testing Focus Areas

Not applicable — developer tooling with no QA-owned product surface.

## Scale

Not applicable — single-page and single-work-item operations; no scale-sensitive behaviour.

</details>

# Rollout Considerations

<details>
<summary>Rollout Considerations</summary>

## Feature Flag

Not applicable — design decision only; production migration is out of scope.

## Backward Compatibility

Pending — Markdown dialect compatibility for pages already fetched or published with the current converter.

## Upgrade Considerations

Pending — dependency changes (Markdown package added, REST library retained or removed).

</details>

# Open Questions

<details>
<summary>Open Questions</summary>

| **Question** | **Answer** |
|---|---|

</details>

# Detailed Design

## Compatibility matrix

<details>
<summary>Compatibility matrix</summary>

**Evidence summary:** The baseline has 37 regression capabilities and 14 converter-test behaviours (51 rows). Documentation establishes support for structural HTML, extension-HTML macros, attachments, inline-comment markers and Jira ADF reads; it documents Markdown loss for panels, status, emoji, macros and layouts; per-node forms for most dialect constructs are undocumented. Prototype verdicts pending.

| Row group | twg-html (documented) | twg-md (documented) | Jira |
|---|---|---|---|
| Headings, marks, lists, blockquote, rule, plain tables | Structural HTML supported; exact form pending prototype | Exact form pending prototype | Fetch reuses current converter (ADF read); publish pending |
| Status lozenges, panels | Form pending prototype | Flattened to text | Fetch reuses current converter |
| TOC, expand | Extension HTML supported; read form pending | Placeholder or lost | Not applicable / reuses converter |
| Breakout, table layout and width | Pending prototype | Layout loss documented | Not applicable |
| Inline-comment anchors | Marker id present in HTML; preserved by targeted edits; full-body write pending | Lost | Not applicable |
| Attachments, media, diagram sidecars | twg attachment commands; media node form pending | Media may be missing | twg attachment commands |
| Draw.io custom content | No twg command found — REST fallback candidate | Same | Not applicable |
| Validation, detection, error guards | Client-side converter, unchanged | Client-side converter, unchanged | Unchanged |

</details>

# Checklists

<details>
<summary>Checklists</summary>

## Main Workflows

Not applicable — developer tooling; no VPG, VRA or undo workflows.

## Interfaces & Operations

| **Item** | **Applicable** | **Details** |
|---|---|---|
| Alerts / Events / Tasks | not applicable |  |
| API | applicable | Confluence and Jira body access moves from REST to the twg CLI. |

## Resiliency

| **Item** | **Applicable** | **Details** |
|---|---|---|
| ZVM Restart | not applicable |  |
| VRA Restart | not applicable |  |
| Network Disconnections | applicable | Pending — twg timeout and retry behaviour. |
| Locking, Synchronization | applicable | Pending — twg snapshot-token conflict handling on page update. |

## Supportability

Not applicable — no analytics, tweaks or product logs.

## Security

| **Item** | **Applicable** | **Details** |
|---|---|---|
| STRIDE analysis, Passwords, Data Validations | not applicable |  |
| Authentication, Authorization | applicable | twg uses the same configured API token through injected environment credentials. |
| New endpoints created and their security features | not applicable |  |
| Used unauthenticated endpoints | not applicable |  |
| Used unencrypted endpoints | not applicable |  |
| New server endpoints | not applicable |  |
| New secrets (incl. new places for existing secrets) | not applicable |  |
| FIPS compliance | not applicable |  |

## Containers \\ Appliance Changes

Not applicable — no containers or appliance.

## 3rd Party & Open Source Review & Deliverables

| **Component** | **Version** | **License** | **URL** | **Usage** |
|---|---|---|---|---|
| Pending — Markdown package selected by research |  |  |  |  |

## External Deliverables Change

| **Item** | **Applicable** | **Details** |
|---|---|---|
| Requires Change to Documentation? | applicable | Skill references for the body tactics change after migration. |
| Requires or affects Swagger? Was this executed? | not applicable |  |
| New Permissions or change in policies? | not applicable |  |
| Involves scripts or anything that isn't part of the binaries of the application? | applicable | Skill-owned Python scripts. |

</details>
<!-- adf:ignore:start -->

# Source Material

| **Source** | **Kind** | **Contribution** |
|---|---|---|
| Wayfinder charting session 2026-11-16 | Grill conversation | Destination, scope, parity bar (byte-identical), comparison oracle, verdict set, test targets, package-selection approach, baseline revision. |
| docs/adr/atl-is-twg-first-with-rest-adf-content.md | Spec | Current access split and the previously rejected twg-for-content option this effort re-evaluates. |
| tests/wf/atlassian/regression/scripts/capabilities.py | Spec | Capability catalogue for matrix rows. |
| https://github.com/antshc/brain/issues/396 | Wayfinder map | Destination, notes, test targets. |
| docs/research/atlassian-twg-conversion/twg-feature-support.md | Wayfinder evidence | Combined twg-html vs twg-md documented-support matrix (partial: authenticated body-formats and live samples blocked); baseline inventory of 51 rows; Jira ADF read path; non-body twg commands. |
<!-- adf:ignore:end -->
