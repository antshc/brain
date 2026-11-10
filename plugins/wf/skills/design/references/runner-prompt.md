# Architect candidate runner

Arena dispatches this brief to each independent candidate runner with the task, Phase A grounding, repo-doc paths, an isolated read-only working tree, and an absolute candidate output directory.

1. Read `design/SKILL.md`, [Architect](../playbooks/architect.md), and [Sketch](../playbooks/sketch.md) fully. Read its [shared code-sketch contract](sketch-contract.md), including named Principles, before generating code shape.
2. Run **Sketch in Candidate context**. Write `rationale.md`, `module-map.md`, and language-native `sketch/` files only under your assigned `candidate-<n>/`. The module map uses real repository-relative target paths. Do not modify production code.
3. Produce one strong, coherent design independently of other runners. Prefer structural differences over small tweaks. When a runner is asked to optimize a particular tradeoff, honor it; do not hedge against other candidates.
4. Screen the candidate with the shared red flags. Leave the rationale synthesis decision absent; the Arena orchestrator selects and synthesizes candidates.

The Sketch playbook is the sole authority for usage-first sketch generation and acceptance criteria. This runner prompt owns only Arena isolation and candidate framing.
