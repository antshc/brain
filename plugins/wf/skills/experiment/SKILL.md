---
name: experiment
description: >-
  Run a minimal throwaway experiment that answers one uncertain technical question by observing actual behavior. Use for 'run an experiment', 'try it and see', 'how does X actually behave'. Not for broken, failing, or slow code → `diagnosing-bugs`.
---

# Experiment

Experiment on the uncertainty, not the feature. Use the smallest executable artifact that exercises the uncertain part for real.

## Inputs

Callers read this section and Workflow before invoking, then fill these from what they already hold; omitted fields are derived in Workflow. Callers pass facts and limits, never method: Workflow owns option, artifact, playbook, and cleanup. Rationale: forwarded facts skip re-discovery, and one strategy owner avoids callers' stale copies.

- `@question` — one uncertain technical question.
- `[@criteria]` — falsifiable assumption plus observable confirm/refute conditions.
- `[@option]` — `logic | runtime | integration-local | integration-cloud | ui`; omitted → step 5 picks.
- `[@repoFacts]` — facts the caller already discovered: stack, test infra, suites and run commands, cloud account and region, runnable target, prior evidence. Reuse verbatim; never re-discover them.
- `[@limits]` — safety limits, out-of-scope behavior, writable paths.

## Workflow

1. State the question, assumption, success/observation criteria, and out-of-scope behavior from Inputs; fill only what they omit.
2. Docs or code reading can settle it → no experiment. Load `research` skill's Inputs and *run `research` skill to investigate primary sources, codebase, cloud docs, or the web and save cited findings*, passing `@question` verbatim; stop. Experiment only on what observation must settle.
3. Inspect the repository for facts the experiment needs and `@repoFacts` lacks:

   | Fact | `@work` | `@shape` | `@depth` |
   |---|---|---|---|
   | repository/agent instructions, package/task runner, scripts, containers, Compose, IaC | `Exact literal` file name or glob (`AGENTS.md`, `*.csproj`, `package.json`, `docker-compose*.yml`, `*.tf`) | `literal` | `quick` |
   | test and integration-test projects, fixtures, clients for the boundary | `Exact literal` project, package, or client name | `literal` | `quick` |
   | AWS/Azure SDK, CLI usage, profile, environment conventions | `Exact literal` SDK package ID, CLI command, or profile key | `literal` | `quick` |
   | frontend host route or component | `Exact literal` route path or component name | `literal` | `quick` |
   | code under test named in `@question` | `Symbol` `Type.Member` | `symbol` | `medium` |
   | mechanism with unknown names: which module owns it, how a call reaches it | `Names unknown:` | `relationship` | `medium` |

   Load `explore-codebase` skill's **Request** and form one Request per row needed, `@target` = repository as named. Spawn one read-only subagent per independent Request, in parallel, instructing each to *run `explore-codebase` skill for the read-only codebase lookup — multi-repo targets, symbol, flow, and config evidence*; subagents unavailable → run it inline under its read-only contract. Read the files it returns directly. Rationale: a shaped Request routes each lookup straight to rg, LSP, or graphify, and caller facts skip re-discovery entirely. Done when each needed fact has a file:line or `unknown`.
4. Reuse the repository's stack, dependencies, clients, test infrastructure, scripts, and conventions unless the experiment evaluates an alternative.
5. Apply guidance by `@option`, else by uncertainty; combine when needed:
   - `logic`: pure logic, state, transitions, data shape -> [LOGIC.md](LOGIC.md)
   - `ui`: visual/interaction design -> [UI.md](UI.md)
   - `runtime`: framework/runtime/backend/frontend mechanism -> [RUNTIME.md](RUNTIME.md)
   - `integration-local`, `integration-cloud`: real external boundary: SDK, REST, cloud, broker, database, service -> also apply [INTEGRATION.md](INTEGRATION.md)
6. Choose the smallest artifact that answers the question:
   - REST -> curl or PowerShell; script if repeatability is needed
   - AWS/Azure API or resource -> cloud CLI when available
   - SDK semantics -> existing integration-test infrastructure
   - broker/distributed flow -> smallest producer/consumer/app set
   - logic/state -> small console/CLI app; standalone HTML only when shareability helps
   - UI -> existing frontend and route
   - runtime/framework -> minimal app, script, test host, container, or process set
7. Exercise the real boundary/mechanism under test. Stub only irrelevant dependencies.
8. Prefer one-command reproducibility when the experiment has multiple or repeatable steps. Surface the relevant state/result after each meaningful action.
9. Run it and record the answer. A failed assumption is a valid result.
10. Record the observed result and implementation implication. Do not turn the experiment into the production implementation.
11. Clean up experiment code, temporary branches/files, containers, and scratch resources unless explicitly asked to preserve them.

## Result

Report:

- Question
- Method
- Observation
- Conclusion
- Evidence
- Cleanup

## Rules

- One question per experiment.
- Do not experiment when code inspection, documentation, or deterministic reasoning can answer the question confidently.
- Prefer existing dependencies; add only what the question requires.
- No production-grade abstractions, unrelated tests, speculative extensibility, or polish.
- Use in-memory/local/sandbox state unless persistence is the question.
- Never use destructive operations against production resources.
- Mark scratch resources and experiment code as disposable.
- Do not promote experiment code directly to production.
