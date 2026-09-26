---
name: experiment
description: Run a minimal throwaway experiment to answer one uncertain technical question by observing actual behavior. Use when asked to test, verify, check, prove, try, or see whether/how something actually behaves and answering requires execution or observation. Covers logic/state, UI/frontend, SDK/API/integration, cloud resources, message brokers, databases, and backend/runtime systems before committing production code.
---

# Experiment

Experiment on the uncertainty, not the feature. Use the smallest executable artifact that exercises the uncertain part for real.

## Workflow

1. State the question, assumption, success/observation criteria, and out-of-scope behavior.
2. Inspect the repository before creating code:
   - repository/agent instructions
   - language, runtime, frameworks, package/task runner
   - test and integration-test projects, fixtures, clients
   - frontend routing/components/styles
   - scripts, containers, Compose, infrastructure tooling
   - AWS/Azure SDKs, CLI usage, IaC and environment conventions
3. Reuse the repository's stack, dependencies, clients, test infrastructure, scripts, and conventions unless the experiment evaluates an alternative.
4. Apply guidance by uncertainty; combine when needed:
   - pure logic, state, transitions, data shape -> [LOGIC.md](LOGIC.md)
   - visual/interaction design -> [UI.md](UI.md)
   - framework/runtime/backend/frontend mechanism -> [RUNTIME.md](RUNTIME.md)
   - real external boundary: SDK, REST, cloud, broker, database, service -> also apply [INTEGRATION.md](INTEGRATION.md)
5. Choose the smallest artifact that answers the question:
   - REST -> curl or PowerShell; script if repeatability is needed
   - AWS/Azure API or resource -> cloud CLI when available
   - SDK semantics -> existing integration-test infrastructure
   - broker/distributed flow -> smallest producer/consumer/app set
   - logic/state -> small console/CLI app; standalone HTML only when shareability helps
   - UI -> existing frontend and route
   - runtime/framework -> minimal app, script, test host, container, or process set
6. Exercise the real boundary/mechanism under test. Stub only irrelevant dependencies.
7. Prefer one-command reproducibility when the experiment has multiple or repeatable steps. Surface the relevant state/result after each meaningful action.
8. Run it and record the answer. A failed assumption is a valid result.
9. Record the observed result and implementation implication. Do not turn the experiment into the production implementation.
10. Clean up experiment code, temporary branches/files, containers, and scratch resources unless explicitly asked to preserve them.

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
