---
name: draft-toi
description: Drafts a feature Transfer of Information (TOI) locally from the bundled template, grounded in workspace docs and codebase exploration, in plain English, with real tweak keys, GUI and REST API scenarios, and an optional swimlane. Use for a TOI, feature handover, or knowledge transfer.
---

# Draft TOI

TOI = engineering hands a developed feature to technical teams (Support, QA, Docs, Training, Field). Not formal training; those teams reuse it to build training, documentation, and labs. Reader did **not** build the feature.

## Inputs

- `feature` — feature or topic name. Required.
- [`jiraKey`] — epic key. Epic only; no user stories or bugs in Related content.
- [`sources`] — pasted Jira text, design doc, demo/recording links, owner name.
- [`outputPath`] — default `toi/{{featureSlug}}.md` under the current workspace root.

If `feature` is missing or matches more than one feature, ask the user with the ask_user tool before collecting evidence.

## Constraints

- **MUST** use `./toi-template.md` from this skill's base directory as the single structure source. Read it on every run.
- **MUST** keep template headings, heading levels, and section order.
- **MUST** ground every statement in collected evidence. **MUST NOT** invent behavior, numbers, defaults, permissions, or limits. Unverified → record as an open question (see Gaps).
- **MUST** write every section in plain language per Plain language. No section is exempt.
- **MUST NOT** change source code or commit. Author only the TOI file.
- Draft locally only: read the local workspace and user-supplied `sources`. **MUST NOT** call Jira, Confluence, GitHub, or other remote services; **MUST NOT** scan pull requests — scan the codebase instead.
- **MUST NOT** link or cite workspace Markdown files (glossary, architecture, ADRs, concepts, service docs) in the TOI; Support cannot open them. Restate the needed fact in plain language. Link only externally reachable URLs from `sources` (Jira, design doc, demo, public docs/KB).
- Discover doc and source locations in the user's workspace at run time; do not assume a fixed folder layout.

## Workflow

1. **Resolve inputs.** Done when `feature`, scope, and `outputPath` are fixed.
2. **Read the template.** Done when the heading list and header-table fields are known.
3. **Collect doc evidence** from every source below. Done when each template section has leads with a source, or is marked a gap.

   | Source | Gives |
   |---|---|
   | User-supplied `sources` (pasted Jira text, acceptance criteria, design doc) | overview, motivation, scope, limits, owner |
   | Workspace glossary | the approved term for each concept |
   | Workspace architecture docs, ADRs, concepts | rationale, flow, lifecycle |
   | Workspace service docs, API contracts (OpenAPI/swagger), configuration docs | components, API behavior, settings, defaults, restart need |

   - Locate these by searching the workspace; skip any that do not exist and record the gap.
   - Keep the evidence map (section → fact → source) outside the TOI.

4. **Explore the codebase (legwork).** Find hard facts in source; docs and Jira are leads, not proof. Spawn read-only subagents; in each, *run `explore-codebase` skill to find where code lives, what calls it, how a flow works, and which file holds a literal or config, in the current repo or a named external codebase*. Rationale: preserve parent context for drafting. Spawn one subagent per target below, in parallel. Pass each request verbatim:
   - `@work` := question: "For feature `{{feature}}` (keywords: {{keywords}}), answer the Exploration checklist rows marked for this target."
   - `@depth` := `thorough`.
   - `@target` := one of: current repository; GUI repository; pipeline definitions; other system components the feature touches (for example Payment gateway, Identity provider); third-party packages owning symbols absent from local source.
   - `@outputShape` := per checklist row: fact, file + symbol evidence, unknowns; row not applicable to the target → `n/a`.
   - `@inputs` := `feature`, keywords, user-supplied `sources`, the Exploration checklist.
   - No `@outputArtifact`; results return to the parent and feed the evidence map.

   Done when every Exploration checklist item has evidence, is marked not applicable, or is a gap.
5. **Resolve conflicts.** Source code is authoritative for behavior, keys, defaults, endpoints, and labels; user-supplied Jira text for motivation and scope; ADRs for rationale. On conflict, follow the authority and add the conflict as an open question. Done when no contradiction remains unreported.
6. **Draft.** Fill sections in template order. Done when no `<…>` hint and no author-only instruction line remains.
   - Keep the first two lines of the intro blockquote; delete the author-instruction line.
   - Keep the `<!-- adf:toc -->` marker on its own line after the header table; Confluence publishing converts it to a table of contents.
   - Always keep Overview, Motivation, How does it work?, Limitations, Troubleshooting, FAQ / Open questions.
   - Delete any other section or subsection only when it does not apply to the feature (for example, no setting → delete Configuration and tweaks; no artifact change → delete Artifact structure). Unknown ≠ not applicable.
   - How does it work?: follow How does it work rules.
   - Configuration and tweaks: list every tweak with its real key and real default from source. State whether a service restart is needed and mark settings that need DEV contact.
7. **Rewrite in plain language.** Done when every sentence passes Plain language.
8. **Verify.** Reread the final file section by section against Plain language and Completion criteria; fix and reread until clean. Recheck every tweak key, default, endpoint, and GUI label against the evidence map. If a diagram exists and `mmdc` is available, render it once to confirm valid syntax. Done when a full pass finds no violation.
9. **Report** to the user: output path, evidence map summary, open questions, sources not reached.

## Exploration checklist

| Item | Find | Target(s) and where |
|---|---|---|
| Deployables | user-visible deployables the feature touches (Storefront web app, Admin portal, CLI, Order service, Payment gateway, Identity provider) and their handoffs | current repository and other system components: architecture / system-context docs, service entry points |
| Scenarios | user-visible scenarios: trigger, visible result, failure result | current repository and GUI repository: controllers, GUI pages, tests; user-supplied acceptance criteria |
| GUI | per scenario: page name, element titles (buttons, menus, columns, fields, dialogs, messages) as shown to the user | GUI repository: page and component templates, localization strings |
| REST API | per scenario: operation name, `METHOD <host>/path`, path and query parameters, request body, response body, status codes; per field: type, required, default, possible values (enums, validation ranges), meaning; per service: Swagger UI route, operation tag and operationId | current repository: controllers, request/response models, API contracts; Swagger UI route prefix in service startup |
| Tweaks | real key, real default from the configuration read call, supported values, read once at startup vs per use (restart need) | current repository: configuration read call sites; configuration docs as leads |
| Artifacts | when the feature adds or changes an artifact (order export, invoice PDF, report, package): folder/file tree and meaning of each file | current repository: code that writes the artifact, tests with sample output |
| Behavior | permissions, fallback, cleanup jobs and intervals, upgrade handling, log messages, limits | current repository: source and tests; third-party packages: behavior outside local code |
| Delivery | how the feature ships and is installed or upgraded (packages, images, installers) | pipeline definitions |

Use the docs only as a starting point for keys and defaults; the source call site wins on conflict.

## How does it work rules

- Stay high level, at user-visible deployable level. No classes, methods, or internal modules.
- Start with a brief description of how the feature works: 3–6 sentences in one paragraph. State the trigger, the main steps across the user-visible deployables, and the visible result.
- The diagram is optional. Add it only when it helps, for example when the flow has handoffs between 2 or more deployables. Skip it for simple flows; the description and scenarios are enough. When skipped, delete the diagram instruction line and the scaffold from the template.
- When a diagram is added: *run `doc-behavior-diagram` skill for a Mermaid swimlane diagram of responsibility handoffs and who owns each step*, using Swimlane Diagram, solution responsibility, one lane per user-visible deployable (and the user). Use Flowchart instead only when one deployable owns the whole flow. Labels follow Plain language.
- Swimlane stays high level: user-visible steps and handoffs only, about 3–7 lanes and 4–10 steps; no internal components, calls, retries, or data stores; collapse internal work into one step or a subprocess.
- Wrap every diagram in `<details>` with a `<summary>` naming the flow and view, for example `<summary>Guest checkout — Solution Responsibility</summary>`.
- Group scenarios by client section, in order: GUI, REST API, Other clients (CLI, Postman collection, scripts). Example scenarios: "Place an order as a guest", "Refund an order". One subsection per user-visible scenario under each client that supports it; clients can differ in steps, options, and results. Delete a client section with no scenarios. A scenario missing from a client → state it is not available there.
- Start every scenario with its own paragraph: user goal, action, visible result.
- GUI: name the page and the exact element titles in **bold**, in click order.
- REST API: give the operation name, `METHOD <host>/path`, the request body, the response body, and the main status codes. Bodies carry the smallest field set: required fields plus fields the scenario needs; drop optional and unrelated fields; keep JSON valid; real field names and realistic sample values. Use JSON code blocks. Use `<host>` for the host, never a real IP or hostname.
- REST API: wrap the field tables and JSON examples of each operation in one `<details>` with `<summary><operation name> — parameters, request, and response</summary>`; keep the operation line and Swagger link outside it. Use bold labels, not headings, inside `<details>`.
- REST API field tables (Microsoft REST reference style): URI parameters (path and query), Request body, Responses (status codes), and response fields. One row per field in the shown bodies; nested field → `parent.child`. Columns: Name, In (parameters only), Required, Type, Default, Possible values, Description. Default and possible values come from source (model defaults, enums, validation attributes); none → `—`. Description states what the field controls or reports, in plain language.
- REST API Swagger link: when a scenario has a REST API entry point, add a Swagger UI link `<host>/<swagger UI route>` with the verified route of the owning service. Append the deep link `#/<tag>/<operationId>` only when tag and operationId are verified. Unverified route → open question.
- Artifact structure: include only when the feature adds or changes an artifact. Show the folder/file tree and one line per file on what it contains.

## Plain language

Write in ASD-STE100 Simplified Technical English (STE) in every section, including tables, diagram labels, troubleshooting, and FAQ.

- Active voice. Present tense for system behavior.
- Max 25 words per sentence; max 20 in procedural steps. One idea per sentence.
- One meaning per word. Use one term per concept; take it from the workspace glossary.
- Name no actors (`we`, `our`, `a team member`). Make the system the subject ("The Order service creates …") or start with the action ("Open …", "Checked …").
- Imperative for procedures and troubleshooting actions.
- `must` = requirement; `can` = possibility. Avoid `should`, `may`, `might`.
- Expand each abbreviation on first use (stock keeping unit (SKU)).
- Max 6 sentences per paragraph.
- Keep high-level technical terms: components, runtimes, libraries, protocols, cloud services (for example OpenSSL, Python 3, Redis, PostgreSQL, Stripe, OAuth 2.0).
- Exclude low-level identifiers: class, method, script, file, table, setting, and tweak names; paths; commands; literal log strings. Describe them by purpose instead.
- **Exceptions** — use exact values, in code format or **bold**: tweak keys and defaults in the Configuration and tweaks table; `METHOD <host>/path`, Swagger UI links, JSON bodies, and field tables in REST API blocks; GUI page names and element titles; file and folder names in Artifact structure. Prose around them still follows Plain language.
- Include version names or IDs only when the topic is an upgrade. The header-table release field is metadata, not prose.

| Weak | Plain |
|---|---|
| Carts are deleted by `AbandonedCartCleanupJob` every `cart_cleanup_interval`. | The Cart service deletes abandoned carts on a fixed interval. A setting controls the interval. The default is 1 hour. |
| We added a fallback in case the payment gateway might be unreachable. | If the payment gateway is unreachable, the Checkout service retries the request three times. |
| Look for `Payment capture failed` in `/var/log/shop/checkout.log`. | Search the Checkout service log for the message that reports a failed payment capture. |

## Gaps

When evidence for a needed fact is missing or conflicting, write it under FAQ / Open questions as `Open: <question> — owner: <name or team>`. Do not fill the related section with a guess. Report all gaps to the user.

## Completion criteria

- File exists at `outputPath` with template headings in template order.
- Every statement traces to the evidence map, or is an open question.
- Every section follows Plain language; no low-level identifier remains outside the Exceptions.
- How does it work? has a brief description of how the feature works, an optional swimlane (or flowchart) at deployable level, and scenarios grouped by client section (GUI, REST API, Other clients), each with its own paragraph; REST API details wrapped in `<details>`; `<!-- adf:toc -->` present.
- Every tweak row has the real key and the real default from source.
- Artifact structure exists when the feature adds or changes an artifact.
- No link or citation to a workspace Markdown file; no pull request used as a source.
- Report lists sources not reached and open questions.
