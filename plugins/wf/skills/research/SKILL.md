---
name: research
description: >-
  Investigate technical questions across source code, docs, packages, and external evidence, or search a Graphify knowledge graph. Return cited findings. Use for 'research X', 'trace this flow', 'find callers of X', 'why was X built', or 'query the graph'. Not for testing one claim → `prove`.
---

# Research

Router. Read the request, frame it against the repository's contracts, select one route per independent question, load its playbook, spawn its agents, and deliver cited findings. The router reads only contract documents and the graph manifest; it never reads source code. Define charts or resumes a research map in the caller's session; its evidence topics use the same route pipeline. The router may read map state and write map/report files; source investigation remains in evidence workers. Only this skill spawns research agents; agents never spawn subagents or load this skill. Callers load this skill in their own session, never inside a wrapper subagent.

## Request

The only input is the request text. Select Define before requiring a factual question: `/research define <prompt-or-map-path>`, `Route: Define`, or an unambiguous request to chart/resume a research map selects Define. A destination prompt or existing map path suffices; ordinary factual questions keep evidence routing. Ask only when there is neither a question nor a map prompt/path. Discover from it:

- **Questions** — split independent questions; keep dependent ones in order.
- **Route** — a route the request names (`Route: Define | Explore | How | Why | Cloud | Web`) wins; `/research why <question>` selects Why; otherwise infer per Routing.
- **Why depth** — full by default; anchor when the request asks only for code, commit, and PR context.
- **Targets** — repositories, deployables, symbols, checkouts/refs, providers, versions, live-value needs.
- **Framing** — requested content, diagrams, sections, lens (Behavior, Flow, Data). Preserve it verbatim for the agents.
- **Destination** — a file path or folder the request names for the result.

Ambiguous scope → state a bounded interpretation and proceed.

## Frame

Evidence routes: run once per request, before Routing. Define defers framing until each interview lookup or research topic has a sharp question; reuse established repository facts, frame each topic, and pass its requested destination. Produce one **Frame** per question and pass it to every agent the question spawns.

1. **Repository root.** Set `@repoRoot` to `git rev-parse --show-toplevel`, run once from the agent session's launch folder, not the current CWD. Not inside a Git repository → no Frame; pass targets as named.
2. **Contracts.** Read the `@repoRoot` contract material, nearest owner first: `GLOSSARY.md` (terms), `ARCHITECTURE.md`, `DEPLOYMENT.md`, `README.md` (ownership, runtime boundaries); then the `@repoRoot` copies whose folder or filename names the target, including `*.swagger.json` (REST) and `*.configuration-tweaks.md` (configuration). Match on the name; do not read every service's set.
3. **Resolve the target.** Use the repositories, services, and refs the request names; none named → current repository.
   - **Building-block index** — **MUST** read `@repoRoot/ARCHITECTURE.md`'s `Deployables` table before declaring a target unresolved. A row's `Location` maps a Deployable name or its Trigger condition to a local path (`workspace/<repo>[/subpath]` or absolute); `origin` metadata never authorizes remote lookup. Use `Shared dependency ownership` for dependencies several Deployables use and `Terminal infrastructure boundaries` for where tracing stops.
   - **Checkouts** — list `<name> → <absolute path>` for `@repoRoot`, the main codebase under `@repoRoot/workspace/`, and every local path those tables name that exists on disk. Missing checkout or ref → mark that target `unresolved`; continue the others.
   - **Worktree targets** — set `@worktreeRoot` to its `git rev-parse --show-toplevel` and `@mainCheckout` to the parent of `git -C @worktreeRoot rev-parse --path-format=absolute --git-common-dir`. Source evidence stays in `@worktreeRoot`; graph lookup uses `@mainCheckout`.
   - **Graph** — the only graph is `@repoRoot/graphify-out/` (harness root); never look for `graphify-out/` in `workspace/<repo>` checkouts or worktrees. Read `@repoRoot/graphify-out/manifest.json` once and record, per target, whether it is covered (paths relative to `@repoRoot`; worktree paths via `@mainCheckout`). Absent → `graph: none`.
4. **Rephrase.** Restate the question in `GLOSSARY.md` terms: replace informal words with the defined term, keep the original wording beside it, and note each term's meaning in one line. Keep literals, symbols, and quoted text verbatim. Use the rephrased question to select the route; do not ask the requester to confirm it.

Frame shape, passed verbatim in each brief:

```text
Question: <original>
Rephrased: <glossary-term question>
Terms: <term> — <meaning> (<GLOSSARY.md path>)
Route: <route> — <reason>
Targets: <name> → <absolute path> [@ <ref>] | unresolved: <reason>
Deployables/boundaries: <relevant Deployables, shared dependencies, terminal boundaries from ARCHITECTURE.md>
Contracts read: <absolute paths>
Graph: <@repoRoot>/graphify-out/ — covers <targets> | none
```

Include only facts that help the agents; omit empty lines.

## Delivery

- Define → save the research map, present its topic table, fog and exclusions at checkpoints, and return the final or paused map with clickable map/report links. Its topic reports use the explicit map-owned destinations; only this route saves Explore verdicts to topic files. Report-only delivery below applies to standalone evidence routes, not Define checkpoints.
- Explore → return `hunty` verdicts inline to the requester; no file. The requester uses the cited findings directly.
- How, Why, Cloud, Web → always save one Markdown report per independent question. Return only the report pointers, never the findings inline:

  ```text
  Research reports — read each in full before using its findings:
  - <question> → <absolute path> (<route>; complete | partial: <gap> | blocked: <blocker>)
  ```

  Present the paths as clickable links to the user.
- Default location: the agent harness session workspace, `<session>/files/research/<question-slug>.md`; distinct slugs per question. No session workspace → `<repository root>/tmp/research/<question-slug>.md`.
- Request names a location → save there instead; resolve a relative path against the requester's repository root; a folder gets `<question-slug>.md`. A combined report only when the request asks for one. Conflicting locations for one report → ask before writing.
- Agents return evidence and drafts inline. Only the router writes reports.

## Routing

Route independent questions separately; sequence dependent evidence. Provider/data facts that determine a system answer stay in How. After a standalone evidence route returns, deliver it before selecting the next question. Define may batch independent frontier topics; record their results in the map before the next frontier.

Read the selected playbook in full before acting. Each playbook names which listed resources its triggers load; read those in full from this skill's base directory, not caller CWD.

| Route | Select when | Playbook | Agents | Resources | Result |
|---|---|---|---|---|---|
| Define | Chart or resume a research map; `/research define <prompt-or-map-path>` | [Define](playbooks/define.md) | No dedicated agent; existing evidence routes per topic | [Questioning](references/define-questioning.md), [Research map](templates/research-map.md); both required in full before charting/resuming | Saved map, checkpoint tables, topic reports and final or paused state |
| Explore | Codebase exploration a calling agent uses as working evidence: find files or code, where is X, who calls Y, what does Z return, how parts connect, a restored package API, a graph query, path, or explain | [Explore](explore/explore.md) | `hunty` | None; `hunty` loads NuGet and Graphify | Inline `hunty` findings |
| How | Current behavior in source, configuration, restored packages; explicit inspection | [How](how/how.md) | [hunty](agents/hunty.md), then [explainy](agents/explainy.md) for Detailed/Full | [Inspection evidence](how/inspection.md), [Explorer prompt](how/explorer-prompt.md), [How report](how/report.md), [Behavior](how/behavior.md), [Flow](how/flow.md), [Data](how/data.md), [NuGet](how/nuget.md), [Graphify](how/graphify.md), [How request guide](how/README.md) | Inline lookup verdict or one cited explanation |
| Why | Rationale: why code, a constraint, or a workaround exists; what led to a change; `/research why <question>` | [Why](why/why.md) | [whyy](agents/whyy.md) anchor, then one per evidence category; [composy](agents/composy.md) | [Epistemics](why/epistemics.md), [Code archaeology](why/sources/code-archaeology.md), [Atlassian](why/sources/atlassian.md), [Linear](why/sources/linear.md), [Notion](why/sources/notion.md), [Slack](why/sources/slack.md), [Datadog](why/sources/datadog.md), [Sentry](why/sources/sentry.md), [Databricks](why/sources/databricks.md), [Incident postmortems](why/sources/incident-postmortem.md) | Rationale, source coverage, confidence; or cited anchor at anchor depth |
| Cloud | Independent AWS/Azure provider question | [Cloud](cloud/cloud.md) | [cloudy](agents/cloudy.md); `hunty` for restored SDK gaps | [Cloud template](cloud/cloud-inspection-template.md), [AWS](cloud/aws.md), [Azure](cloud/azure.md) | Cited constraints and applicability |
| Web | Other external question | [Web](web/web.md) | [weby](agents/weby.md) | None | Primary-source findings |

Define selects evidence routes internally through Frame, Routing and Spawning agents, never by recursively loading this skill. Interview facts follow the same pipeline; Concepts belong to `architecture-records` route `define-concept`.

Graphify is a `hunty` tactic, not a route. Graph build, update, or export requests → report the build entry point named in `<root>/GRAPHIFY.md`; never build.

## Spawning agents

Every route agent is a prompt file under `agents/`, discovered through this skill, never a registered agent. Playbook text *spawn `<name>`* means this recipe; `<name>` is never an agent type or `agentName`; use it only as the spawn's display name. For each spawn:

1. Read `agents/<name>.md` in full and fill its Brief or placeholders: question with its Frame (`@frame` for `hunty`; prepended to the question elsewhere), targets/refs, playbook-selected resources as absolute paths, `@research` (this skill's absolute base directory), and the request's framing where the prompt takes it.
2. *Load and follow the `subagents` skill to select the model and effort for a named subagent role* with role `<name>`. Its result is the user's configured model, not a guess: never skip this step or drop the model to harness defaults; omit `model` and `reasoning_effort` only when `subagents` resolves to `auto`, `inherit-parent`, or an unknown role.
3. Spawn a skill-capable general-purpose worker (`general-purpose`, or the harness's default subagent when it has no agent types) with the filled prompt as its whole task, passing the resolved model as `model` and effort as `reasoning_effort`, `<name>` as `name`, and a description starting with `<name>:` (e.g. `hunty: Discover upgrade topology`) so the UI shows the role; read-only unless the prompt grants a write. Batch independent spawns in one parallel response; sequence dependent ones.
4. Spawn failed or unavailable → report the blocked request with its consequence and continue independent work.

Give follow-ups to a fresh worker with the original brief, the prior report, and the bounded gap. Large reading fan-out or material measurement claims → *Load and follow the `principles` skill to load indexed engineering principles by name*; select `Guard the context window` for bounded briefs and `Explain the number` before relying on measurements.

## Completion criteria

- Define: map and findings match the presented state; remaining work has explicit status and links; finish only when Topics and Not yet specified are empty or the user confirms remaining work cannot change the destination. Paused maps remain resumable, not complete. The caller retains the decision and implementation.
- Each How, Why, Cloud, or Web question has a saved report and a pointer with its status; each Explore lookup has an inline verdict or a named blocker; framing matches the request.
- Material factual claims carry in-place primary-source citations. Source-based, inferred, and observed evidence stay distinct; Why confidence language is preserved.
- Conflicts are reconciled or reported with both sources. No findings → completed scope and checked sources stated. Incomplete → missing evidence and its consequence named.
- Included Mermaid blocks render; template placeholders, Rules blocks, and unfilled sections are removed.
- Every research evidence claim came from a spawned route agent; experiment conclusions come from retained Prove reports; no route agent spawned another.
