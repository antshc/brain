---
name: research
description: >-
  Investigate technical questions across source code, docs, packages, and external evidence, or search a Graphify knowledge graph. Return cited findings. Use for 'research X', 'trace this flow', 'find callers of X', 'why was X built', or 'query the graph'. Not for testing one claim → `prove`.
---

# Research

Router. Read the request, select one route per independent question, load its playbook, spawn its agents, and deliver cited findings. The router never reads source itself. Only this skill spawns research agents; agents never spawn subagents or load this skill. Callers load this skill in their own session, never inside a wrapper subagent.

## Request

The only input is the request text. Ask only when it holds no question. Discover from it:

- **Questions** — split independent questions; keep dependent ones in order.
- **Route** — a route the request names (`Route: Explore | How | Why | Cloud | Web`) wins; `/research why <question>` selects Why; otherwise infer per Routing.
- **Why depth** — full by default; anchor when the request asks only for code, commit, and PR context.
- **Targets** — repositories, deployables, symbols, checkouts/refs, providers, versions, live-value needs.
- **Framing** — requested content, diagrams, sections, lens (Behavior, Flow, Data). Preserve it verbatim for the agents.
- **Destination** — a file path or folder the request names for the result.

Ambiguous scope → state a bounded interpretation and proceed.

## Delivery

- Explore → return `hunty` verdicts inline to the requester; no file. The requester uses the cited findings directly.
- How, Why, Cloud, Web → always save one Markdown report per independent question. Return only the report pointers, never the findings inline:

  ```
  Research reports — read each in full before using its findings:
  - <question> → <absolute path> (<route>; complete | partial: <gap> | blocked: <blocker>)
  ```

  Present the paths as clickable links to the user.
- Default location: the agent harness session workspace, `<session>/files/research/<question-slug>.md`; distinct slugs per question. No session workspace → `<repository root>/tmp/research/<question-slug>.md`.
- Request names a location → save there instead; resolve a relative path against the requester's repository root; a folder gets `<question-slug>.md`. A combined report only when the request asks for one. Conflicting locations for one report → ask before writing.
- Agents return evidence and drafts inline. Only the router writes reports.

## Routing

Route independent questions separately; sequence dependent evidence. Provider/data facts that determine a system answer stay in How. After a route returns, deliver it before selecting the next question.

Read the selected playbook in full before acting. Each playbook names which listed resources its triggers load; read those in full from this skill's base directory, not caller CWD.

| Route | Select when | Playbook | Agents | Resources | Result |
|---|---|---|---|---|---|
| Explore | Codebase exploration a calling agent uses as working evidence: find files or code, where is X, who calls Y, what does Z return, how parts connect, a restored package API, a graph query, path, or explain | [Explore](explore/explore.md) | `hunty` | None; `hunty` loads NuGet and Graphify | Inline `hunty` findings |
| How | Current behavior in source, configuration, restored packages; explicit inspection | [How](how/how.md) | [hunty](agents/hunty.md), then [explainy](agents/explainy.md) for Detailed/Full | [Inspection evidence](how/inspection.md), [Explorer prompt](how/explorer-prompt.md), [How report](how/report.md), [Behavior](how/behavior.md), [Flow](how/flow.md), [Data](how/data.md), [NuGet](how/nuget.md), [Graphify](how/graphify.md), [How request guide](how/README.md) | Inline lookup verdict or one cited explanation |
| Why | Rationale: why code, a constraint, or a workaround exists; what led to a change; `/research why <question>` | [Why](why/why.md) | [whyy](agents/whyy.md) anchor, then one per evidence category; [composy](agents/composy.md) | [Epistemics](why/epistemics.md), [Code archaeology](why/sources/code-archaeology.md), [Atlassian](why/sources/atlassian.md), [Linear](why/sources/linear.md), [Notion](why/sources/notion.md), [Slack](why/sources/slack.md), [Datadog](why/sources/datadog.md), [Sentry](why/sources/sentry.md), [Databricks](why/sources/databricks.md), [Incident postmortems](why/sources/incident-postmortem.md) | Rationale, source coverage, confidence; or cited anchor at anchor depth |
| Cloud | Independent AWS/Azure provider question | [Cloud](cloud/cloud.md) | [cloudy](agents/cloudy.md); `hunty` for restored SDK gaps | [Cloud template](cloud/cloud-inspection-template.md), [AWS](cloud/aws.md), [Azure](cloud/azure.md) | Cited constraints and applicability |
| Web | Other external question | [Web](web/web.md) | [weby](agents/weby.md) | None | Primary-source findings |

Graphify is a `hunty` tactic, not a route. Graph build, update, or export requests → report the build entry point named in `<root>/GRAPHIFY.md`; never build.

## Spawning agents

Every route agent is a prompt file under `agents/`, discovered through this skill, never a registered agent. Playbook text *spawn `<name>`* means this recipe; `<name>` is never an agent type, agent name, or `agentName`. For each spawn:

1. Read `agents/<name>.md` in full and fill its Brief or placeholders: question, targets/refs, playbook-selected resources as absolute paths, `@research` (this skill's absolute base directory), and the request's framing where the prompt takes it.
2. *Load and follow the `subagents` skill to select the model and effort for a named subagent role* with role `<name>`.
3. Spawn a skill-capable general-purpose worker (`general-purpose`, or the harness's default subagent when it has no agent types) with the filled prompt as its whole task and that model; read-only unless the prompt grants a write. Batch independent spawns in one parallel response; sequence dependent ones.
4. Spawn failed or unavailable → report the blocked request with its consequence and continue independent work.

Give follow-ups to a fresh worker with the original brief, the prior report, and the bounded gap. Large reading fan-out or material measurement claims → *Load and follow the `principles` skill to load indexed engineering principles by name*; select `Guard the context window` for bounded briefs and `Explain the number` before relying on measurements.

## Completion criteria

- Each How, Why, Cloud, or Web question has a saved report and a pointer with its status; each Explore lookup has an inline verdict or a named blocker; framing matches the request.
- Material factual claims carry in-place primary-source citations. Source-based, inferred, and observed evidence stay distinct; Why confidence language is preserved.
- Conflicts are reconciled or reported with both sources. No findings → completed scope and checked sources stated. Incomplete → missing evidence and its consequence named.
- Included Mermaid blocks render; template placeholders, Rules blocks, and unfilled sections are removed.
- Every evidence claim came from a spawned route agent; no agent spawned another.
