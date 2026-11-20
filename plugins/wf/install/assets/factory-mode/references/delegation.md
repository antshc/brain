# Delegation

## Throughput checkpoint

For nontrivial work, record four todo items before work starts. Mark an inapplicable item `n/a: {{reason}}`. Update the checkpoint at phase changes.

- **Blocking first steps.** List gates before workers start.
- **Independent workstreams.** Run disjoint work together. Serialize shared writes.
- **Shared mutable state.** Split the target first (**Separate before serializing shared state**). Serialize only where an invariant requires it.
- **Smallest safe decomposition.** If one worker is enough, state why.

Give tightly coupled work to one owner who can delegate after the blockers clear. Dispatch independent artifacts at the parent level.

## Dispatch workers

Keep the playbook in this chat. Delegate independent steps to skill-capable `general-purpose` workers with separate output paths. Use harness model and effort defaults unless the user specifies them.

Before a direct launch, read the [Worker contract](../worker.md) and resolve its absolute path before changing the working directory. Start the kickoff with `Read <absolute worker contract path> in full before task actions.` Pass the path as `workerContractPath`. Include the goal, scope, file paths, data shape, constraints, and success criteria. If the contract is unavailable, report the path and error and block the dependent launch.

Factory mode is the only orchestrator: workers execute, never orchestrate. **MUST** run worker-owning skills in this session, never inside a worker: `research`, `prove`, `challenge-this`, `design`, `review` (`code`, `blast-radius`, `tests-gap`, `hitl`), `implement`, and `subagents` Arena. Brief workers only for work that loads none of them. Pass constraints in their request fields. Let each owner dispatch its workers. When two steps each need `prove`, merge their claims into one batch. Pass the adversary count to Challenge This and let it resolve the `challenge-this reviewers` role. Review returned diffs and evidence before reporting.
