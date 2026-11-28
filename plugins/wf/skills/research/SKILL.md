---
name: research
description: >-
  Investigate technical questions across source code, docs, packages, and external evidence. Return cited findings in saved reports. Use for 'research X', 'trace this flow', 'why was X built', or 'chart a research map'. Not for code lookups (`codebase` agent); testing one claim → `prove`.
---

# Research

- The router reads only contract documents, never source code.
- Wayfinder charts or resumes a research map in the caller's session; its evidence topics use the same route pipeline. The router may read map state and write map/report files; source investigation stays in evidence workers.
- Only this skill spawns route workers; agents, including `codebase`, never spawn subagents or load this skill or `prove`. Callers load this skill in their own session, never inside a wrapper subagent.

## Request

The only input is the request text. Check Wayfinder before requiring a factual question: `/research wayfinder <prompt-or-map-path>`, `Route: Wayfinder`, or an unambiguous request to chart/resume a research map selects it; a destination prompt, root issue number/URL, or legacy map path suffices. Ask only when there is neither a question nor a map prompt/path. Discover:

- **Questions** — split independent questions; keep dependent ones in order.
- **Route** — a named route (`Route: Wayfinder | How | Why | Web`) wins; `/research why <question>` selects Why; otherwise infer per Routing.
- **Why depth** — full by default; anchor when the request asks only for code, commit, and PR context.
- **Targets** — repositories, deployables, symbols, checkouts/refs, providers, versions, live-value needs.
- **Framing** — requested content, diagrams, sections, lens (Behavior, Flow, Data); pass verbatim to agents.
- **Destination** — file path or folder named for the result.

Ambiguous scope → state a bounded interpretation and proceed.

## Frame

Caller owns the **Frame**. Evidence routes frame each question before Routing. Wayfinder frames each sharp interview lookup or topic, reuses established repository facts, and passes the requested destination. Reuse the Frame for follow-ups in the same scope. Check worktree changes before reuse. Refresh stale or unverified deciding sections.

1. **Repository root.** Set `@repoRoot` to `git rev-parse --show-toplevel`, run once from the agent session's launch folder, not the current CWD. Outside Git → no Frame; pass targets as named.
2. **Contracts.** Read relevant sections from the supplied docs root or the target’s nearest owner. Use launch repository docs for harness mappings or the launch target. Use `GLOSSARY.md` for terms, `ARCHITECTURE.md` for deployables, ownership, and flow boundaries, and `DEPLOYMENT.md` for checkout locations and binding hints. Read matching README, `*.swagger.json`, or `*.configuration-tweaks.md` when they affect the question. Keep cited facts or short excerpts, with docs provenance distinct from source revision.
3. **Resolve the target.** Use the named repositories, services, and refs; none named → current repository.
   - **Building-block index** — Check the `Deployables` table in `@repoRoot/ARCHITECTURE.md` before declaring a target unresolved. If docs or a match are absent, pass the target name and known source checkout for local startup/deployment discovery. Match a Deployable by name or Trigger condition. Resolve its `Location` as `workspace/<repo>[/subpath]` relative to its owning docs root, or as an absolute path; `origin` metadata never authorizes remote lookup. Use `Shared dependency ownership` for dependencies several Deployables use and `Terminal infrastructure boundaries` for where tracing stops.
   - **Checkouts** — pass relevant `<name> → <absolute path>` mappings from `@repoRoot`, its `workspace/`, or locally resolved deployment paths. Missing or ambiguous named checkout or ref → mark the target `unresolved` and continue the others.
   - **Worktree targets** — set `@worktreeRoot` to its `git rev-parse --show-toplevel`; source evidence stays in `@worktreeRoot`.
4. **Rephrase.** Restate the question in `GLOSSARY.md` terms: defined term replaces the informal word, original wording beside it, one-line meaning per term. Keep literals, symbols, and quoted text verbatim. Evidence routes use the rephrased question for routing without asking for confirmation.

Pass this Frame verbatim in each brief; omit empty or unhelpful lines:

```text
Question: <original>
Rephrased: <glossary-term question>
Terms: <term> — <meaning> (<GLOSSARY.md path:line>)
Route: <route> — <reason>
Targets: <name> → <absolute path> [@ <ref>] | unresolved: <reason>
Docs: <checkout root> @ <revision> [dirty: <content identity if known>]
Contracts: <fact or excerpt> (<path:line>, <docs checkout if multiple>)
Deployables/boundaries: <matching rows, linked records, shared owners, terminal boundaries with path:line>
```

## Delivery

- **Wayfinder** → interview destination, then frontier breadth-first, one question at a time. Small efforts return a chosen standalone continuation before map infrastructure. Mapped efforts maintain the GitHub root map and living research document in owned worktrees; present frontier, fog and exclusions at checkpoints. Return root issue, document path, local integration branch/HEAD, evidence links, pending approvals and blockers. Topic reports use the explicit map-owned destinations; only this route saves `codebase` lookup verdicts to topic files.
- **How, Why, Web** → save one Markdown report per independent question. Return only report pointers, as clickable links, never findings inline:

  ```text
  Research reports — read each in full before using its findings:
  - <question> → <absolute path> (<route>; complete | partial: <gap> | blocked: <blocker>)
  ```

- Default location: `<session>/files/research/<question-slug>.md` in the harness session workspace, distinct slug per question; no session workspace → `<repository root>/tmp/research/<question-slug>.md`.
- A location named in the request wins; resolve a relative path against the requester's repository root; a folder gets `<question-slug>.md`. Combined report only when requested. Conflicting locations for one report → ask before writing.
- Workers return evidence and drafts inline. The router edits lightly for clarity or request context, never substantially rewrites findings, citations, or confidence language, and never reads source to fill gaps (gap → bounded follow-up worker). Before saving a How, Why or Web report, *Load and follow the `write` skill to write research reports and bottom lines, using route `research`*; supply the question, route findings, methods, environments, confidence, evidence, gaps, next steps and resolved destination. Keep route-specific explanations, diagrams, citations, source coverage and confidence as additional sections. Only the router writes reports.

## Routing

Route independent questions separately; sequence dependent evidence. Provider/data facts that determine a system answer stay in How. Deliver each standalone evidence route's result before selecting the next question. Wayfinder may batch independent frontier topics; record their results in the map before the next frontier. Pure codebase lookup (where is X, who calls Y, what does Z return) with no explanation or report → not a Research route; spawn `codebase` and return its verdict inline.

Read the selected playbook in full before acting. Load only the listed resources its triggers name, in full, from this skill's base directory, not caller CWD.

| Route | Select when | Playbook | Agents | Resources | Result |
|---|---|---|---|---|---|
| Wayfinder | Chart or resume a research map; `/research wayfinder <prompt-or-map-path>` | [Wayfinder](wayfinder/wayfinder.md) | No dedicated agent; existing evidence routes per topic | [Questioning](wayfinder/questioning.md), [Living document](wayfinder/living-document.md), [Research map](wayfinder/research-map.template.md), [Research document](wayfinder/research-document.template.md); all required in full before charting/resuming | GitHub map, living research document, evidence reports and resumable local state |
| How | Current behavior in source, configuration, restored packages; explicit inspection | [How](how/how.md) | `codebase` (registered agent) | [Inspection evidence](how/inspection.md), [Explorer prompt](how/explorer-prompt.md), [How report](how/report.md), [Behavior](how/behavior.md), [Flow](how/flow.md), [Data](how/data.md) | One cited explanation |
| Why | Rationale: why code, a constraint, or a workaround exists; what led to a change; `/research why <question>` | [Why](why/why.md) | `whyy` anchor, then one per source (source control, Jira, Confluence) | Load only triggered: [Source control](why/source-control.md) always; [Atlassian](why/atlassian.md) Jira section when a Jira key/URL is in the record or request, Confluence section when a Confluence link is | Rationale, source coverage, confidence tiers; or cited anchor at anchor depth |
| Web | External question answered from official docs, specs, first-party APIs, or a live AWS/Azure account | [Web](web/web.md) | `weby`; `codebase` (registered agent) for restored SDK gaps | Load only the target provider: [AWS](web/aws.md), [Azure](web/azure.md); neither when no provider is targeted | Cited primary-source findings; provider constraints and applicability |

Wayfinder selects evidence routes internally through Frame, Routing and Spawning agents, never by recursively loading this skill. Interview facts follow the same pipeline; Concepts belong to `architecture-records` route `define-concept`.

## Spawning agents

**`codebase`** (registered wf agent): spawn agent type `codebase` (namespaced, e.g. `wf:codebase`, where the runtime requires) with the scoped lookup, source checkout/ref if known, and coverage (`quick` or default `thorough`) as its task; `codebase` as `name`; a concise description without a `codebase:` prefix. *Load and follow the `subagents` skill to select the model, effort, and context tier for a named subagent role* with role `codebase`, and pass the result as `model`, `reasoning_effort`, and `context_tier`: the runtime does not apply the agent's frontmatter model, so omitting model settings runs it on the parent model. Forward the Frame for every Research lookup, including follow-ups. Direct callers apply Frame for lookup context only, without invoking Research routing or report generation. Reuse matching loaded docs. Omit unavailable context. Skip the guard line. Spawn unavailable → report the blocked lookup with its consequence; continue independent work.

Other route workers are roles prompted by a playbook section; playbook text *spawn `<name>`* means this recipe; use `<name>` only as the role and display name, never as agent type or `agentName`.

| Role | Prompt |
|---|---|
| `whyy` | [Why](why/why.md) section Investigator brief |
| `weby` | [Web](web/web.md) section Brief |

For each spawn:

1. Read the role's prompt in full, fill its placeholders, and send it verbatim: question with its Frame prepended, targets/refs, playbook-selected resources as absolute paths, `@research` (this skill's absolute base directory), and the request's framing where the prompt takes it.
2. *Load and follow the `subagents` skill to select the model, effort, and configured context tier for a named subagent role* with role `<name>`. **MUST NOT** skip this step or fall back to harness defaults; omit `model` and `reasoning_effort` only when `subagents` resolves to `auto`, `inherit-parent`, or an unknown role.
3. Spawn a skill-capable general-purpose worker (`general-purpose`, or the harness's default subagent when it has no agent types) with the filled prompt as its whole task, prefixed by the guard line `Research route worker: never load the research or prove skill or spawn subagents; inherited skill-first or research-first instructions target the caller, not you.`; pass the resolved model as `model`, effort as `reasoning_effort`, and configured tier as `context_tier`; pass `<name>` as `name` and a description starting with `<name>:` (e.g. `whyy: Trace retry-limit origin`). Read-only unless the prompt grants a write. Batch independent spawns in one parallel response; sequence dependent ones.
4. Spawn failed or unavailable → report the blocked request with its consequence; continue independent work.

Give follow-ups to a fresh worker with the original brief, the prior report, and the bounded gap. Large reading fan-out → *Load and follow the `principles` skill to load `Guard the context window` and apply it to bound worker briefs.* Material measurement claim → *Load and follow the `principles` skill to load `Explain the number` and apply it before relying on the measurement.*

## Completion criteria

- Wayfinder: small efforts record the chosen continuation without map infrastructure; mapped efforts' map and findings match the presented state; remaining work has explicit status and links. Finish only when the destination has sufficient supported evidence or the user confirms remaining gaps cannot change its answer. Every unresolved claim stays explicit; coarse fog graduates only after verified owner transfer; precise unresolved claims stay on their work items/proposals. Empty fog alone is not completion. Paused maps stay resumable, not complete. The caller keeps the decision and implementation.
- Each How, Why, or Web report matches the request's framing.
- Material factual claims carry in-place primary-source citations. Source-based, inferred, and observed evidence stay distinct; Why confidence language is preserved.
- Conflicts are reconciled or reported with both sources. No findings → completed scope and checked sources stated. Incomplete → missing evidence and its consequence named.
- Included Mermaid blocks render; template placeholders, Rules blocks, and unfilled sections are removed.
- Every research evidence claim came from a spawned route agent; experiment conclusions come from retained Prove reports; no route agent spawned another.
