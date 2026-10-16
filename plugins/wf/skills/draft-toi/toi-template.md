# TOI: `<Feature / Topic Name>`

> **Transfer of Information (TOI)** — engineering hands a new product, feature, or topic to technical teams (Support, QA, Docs, Training, Field).
> Not formal training. Consumed by teams to build formal training, documentation, lab activities, etc.
> Write for readers who did **not** build the feature. Remove all `<…>` hints and unused sections before publishing.

| Field | Value |
| --- | --- |
| Feature / topic | `<name>` |
| Product / component | `<e.g. Storefront, Checkout service, Admin portal>` |
| Version / release | `<first version containing the feature>` |
| Owner / presenter | `<name>` |
| Related epic / Jira | `<KEY-123>` |
| Design doc | `<external link reachable by Support; never a workspace Markdown file>` |
| Demo / recording | `<link>` |
| Date | `<YYYY-MM-DD>` |

<!-- adf:toc -->

## Overview

<What the feature is, in 2–4 sentences. What changes for the user/system. Before vs. after behavior.>

## Motivation

<Why it was built: customer problem, cost, performance (latency, throughput), platform/vendor change, unsupported scenarios.>

- Problem: `<…>`
- Benefit / measured result: `<e.g. proof of concept showed checkout Nx faster, cost reduced by …>`
- External driver (if any): `<vendor deprecation, date, pricing>`

## Prerequisites

<What must exist before the feature works.>

### Permissions / roles

| Account / scope | Permission | Purpose |
| --- | --- | --- |
| `<account / tenant / role>` | `<permission>` | `<why needed>` |

### Other requirements

- `<version, license, infrastructure, configuration, upgrade step; e.g. payment gateway account, Redis cache>`

## How does it work?

<Brief description of how the feature works: 3–6 sentences covering the trigger, the main steps across user-visible deployables, and the visible result. No classes, methods, or internal modules.>

<!-- @: OPTIONAL diagram. Add only when it helps (for example handoffs between 2 or more deployables); otherwise delete this comment and the whole `<details>` block below. When added: *Run `doc-behavior-diagram` skill for a Mermaid swimlane diagram of responsibility handoffs and who owns each step*: Swimlane Diagram, current mode, solution responsibility, TB, one lane per user-visible deployable plus the user, high level, 4–10 user-visible steps, no internals; Flowchart only when one deployable owns the flow; replace the scaffold below. -->

<details>
<summary>Feature flow — Solution Responsibility</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
%% diagram-id: toi-feature-flow
swimlane-beta TB
  accTitle: Feature flow
  accDescr: Shows the feature steps and handoffs between the user and the deployables.

  subgraph user [User]
    start([Start])
    request[/1 - User action/]
    result[/4 - Visible result/]
    endNode([End])
  end

  subgraph deployableA [Deployable A]
    stepA[2 - Process step]
  end

  subgraph deployableB [Deployable B]
    stepB[3 - Process step]
  end

  start --> request -->|request| stepA -->|handoff| stepB -->|outcome| result --> endNode

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

</details>

<!-- @: group scenarios by client section: GUI, REST API, Other clients; repeat the scenario block per scenario; delete a client section with no scenarios -->

### GUI

#### `<user-visible scenario name>`

<What the user wants, what the user does, and the visible result; one paragraph, 2–4 sentences.>

1. Open the **`<page name>`** page.
2. Click **`<element title>`**.
3. `<visible result: status, message, column value>`

### REST API

#### `<user-visible scenario name>`

<What the API client wants, which operation it calls, and the result; one paragraph, 2–4 sentences.>

**`<operation name>`** — `<METHOD> <host>/<path>`

Try it in Swagger UI: `<host>/<swagger UI route>#/<tag>/<operationId>`

<details>
<summary><operation name> — parameters, request, and response</summary>

<!-- @: Microsoft REST reference style; one row per field in the bodies below; delete a table with no rows; nested object → `parent.child` row -->

**URI parameters**

| Name | In | Required | Type | Default | Possible values | Description |
| --- | --- | --- | --- | --- | --- | --- |
| `<name>` | `<path / query>` | `<yes / no>` | `<string / integer / boolean / enum / date-time>` | `<real default or —>` | `<enum values / range / —>` | `<what the parameter controls>` |

**Request body**

```json
<required fields + scenario fields only>
```

| Name | Required | Type | Default | Possible values | Description |
| --- | --- | --- | --- | --- | --- |
| `<field>` | `<yes / no>` | `<type>` | `<real default or —>` | `<enum values / range / —>` | `<what the field controls>` |

**Responses**

| Status code | Type | Description |
| --- | --- | --- |
| `<200 OK>` | `<response type>` | `<when it is returned>` |
| `<4xx / 5xx>` | `<error type>` | `<cause>` |

**Response `<status code>`**

```json
<fields the scenario reads only>
```

| Name | Type | Possible values | Description |
| --- | --- | --- | --- |
| `<field>` | `<type>` | `<enum values / range / —>` | `<what the field reports>` |

</details>

### Other clients

<!-- @: CLI, Postman collection, scripts, or other user-facing clients; name the client in each scenario -->

#### `<user-visible scenario name>` (`<client name>`)

<What the user wants, which client and command or request it uses, and the result; one paragraph, 2–4 sentences.>

1. `<step>`
2. `<visible result>`

### Artifact structure

<!-- @: include only when the feature adds or changes an artifact (order export, invoice PDF, report, package) -->

```text
<artifact-name>/
├── <folder>/
│   └── <file>
└── <file>
```

| File / folder | Contains |
| --- | --- |
| `<file>` | `<what the file holds and when it appears>` |

### Components and data

<Key components, resources, tables, files, mount paths, naming conventions, directory structure.>

| Property / item | Description |
| --- | --- |
| `<name>` | `<value / meaning>` |

### Normal path vs. fallback

- Normal: `<…>`
- Fallback / failure handling: `<what happens when a dependency is unavailable>`

### Lifecycle and cleanup

<When resources are created, reused, deleted; background cleanup jobs and intervals.>

### Interaction with existing features

<Related features, existing tweaks that are now ignored, e.g. discount rules, tax settings, inventory reservation, shipping options.>

### Upgrade behavior

<What happens to existing data/settings on upgrade; what to verify afterwards.>

## ⚠️ Limitations

- `<Unsupported scenario / ignored setting>`
- `<Platform or quota limit (include number and link)>`
- `<Known gaps, rare edge cases, what is monitored>`

## Configuration and tweaks

> State whether a service restart is required for tweaks to take effect. Mark tweaks that require contacting DEV.

<!-- @: real key and real default from the source configuration read call; never a placeholder or paraphrase -->

| Tweak key | Default | Supported values | Restart needed | Description / impact |
| --- | --- | --- | --- | --- |
| `<TWEAK_KEY>` | `<real default>` | `<values>` | `<yes / no>` | `<meaning, side effects>` |

## Tips & tricks

- `<Verification shortcuts, useful tools, recommended settings, sizing guidance>`

## Troubleshooting

### Enable detailed logs

<Tweak / log level / component to set.>

### Verify the feature is enabled and working

- Where to look: `<service log / DB table / admin portal>`
- Expected log line / value:

  ```text
  <expected log message>
  ```

### `<Symptom 1>`

- Likely cause: `<e.g. missing permission>`
- Where to look: `<log search string / table / field>`
- Fix / action: `<…>`

### `<Symptom 2>`

- Likely cause: `<…>`
- Where to look: `<…>`
- Fix / action: `<escalate to DEV when …>`

## FAQ / Open questions

- `<Anticipated question>` — `<answer>`

## Related content

<!-- @: external URLs only (Jira, design doc, demo, public docs/KB); never workspace Markdown files -->

- Epic: `{{KEY-123| The epic title with the link. Format : <ID>: <title> }}` — epic only; no user stories or bugs
- Design: `<link>`
- Demo: `<link>`
- Docs / KB: `<public link>`
