---
description: Jira semantics, safe read and write rules, transitions, and handoffs for workitems, projects, boards, sprints, and fields.
---

# Jira Rules

Use when Jira is the source of truth or a Jira mutation is required. Skip when Jira is only one supporting artifact inside a cross-product answer.

Read a known issue with `twg jira workitem get <KEY> --site <SITE>`; pass multiple keys positionally to read a set. `get` rejects `--id` (used by transition); use the positional key or `--issue-id`.

Verify mutation contracts first; describe them with the planned commands.

## Jira Semantics

- "Issue" and "workitem" are the same Jira object in user language.
- Jira projects/spaces are not Atlas projects. Use Jira for issue containers, schemes, boards, versions, components, filters, and dashboards.
- JSM requests have an underlying Jira workitem, but approvals, portals, queues, request types, and SLAs belong to JSM.
- Search results are candidate anchors; use the native workitem read for final fields and status. Plain `get` avoids supplemental hydration; add `--comments` and/or `--remote-links`, or `--full` for all fields plus both.
- For "what should I pick next," query actual open Jira work or the requested board backlog. Do not rank from broad activity alone.
- Read a set of workitems in one call: `jira workitem get`, `jira workitem bulk-get`, and `context jira workitem` all accept every key at once. Never loop `get` over a key list. When the fields are queryable, use `jira workitem query --jql <jql> --fields <fields>` and skip hydration.

## Safe Reads And Writes

- Read current state before update, transition, link, comment, or delete.
- Discover create/update field metadata before supplying required or custom fields.
- Use returned `customfield_*` IDs rather than display names in writes.
- Discover available transitions instead of guessing a transition name or ID.
  - Run `twg jira workitem transition --id <KEY> --site <SITE> -o json` without `--transition-id` to discover available transitions and their required screen fields. This call is read-only.
  - Select one and use its `requirements` to gather field values before calling with `--transition-id`.
  - Treat required fields as user-decision inputs. If the user did not supply a required value, ask before transitioning; do not infer or choose an allowed value. This includes Resolution: a request to cancel does not imply `Won't Do`, `Declined`, `Duplicate`, or another Resolution.
- Keep global Jira field administration separate from workitem field values.
- Use typed workitem artifact links to add Jira remote links to PRs, repos, deployments, builds, branches, commits, Loom videos, or meetings. These are not Jira Software devinfo/provider writes.
- Verify mutations with a native read and report the resulting key and URL.

## Handoffs

- Dependencies, related documents, implementation links: `twg-context-discovery`.
- Owners, experts, authority, escalation: `twg-responsibility-routing`.
- Project, sprint, team, or leadership synthesis: `twg-status-rollups`.
- Jira anchor traced to PRs or repositories: `twg-engineering-work`.
- Incident, PIR, or reliability workflows: `twg-operational-health`.
