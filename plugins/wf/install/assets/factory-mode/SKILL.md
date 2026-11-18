---
name: factory-mode
description: >-
  Run engineering tasks through a selected playbook with explicit scope and verification.
disable-model-invocation: true
---

# Factory mode

This repo-level skill is installed by the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md). Preserve intentional repo-local edits. When syncing, *Load and follow the `sync-skill` skill to merge upstream changes into the local skill while preserving customizations.*

## Select a route

1. Honor explicit `help` before loading execution dependencies. Use [Help](help.md) for usage or options.
2. Resume an active route when the user answers it. Keep the active checkpoint or HITL prompt until the user responds or redirects the task.
3. Honor an explicit route. Otherwise select a route that clearly matches the request. Select `hitl` only for an explicit request for human-led review. For a Feature or Bug fix request that also asks for human review, run the primary route and perform the HITL handoff at its review phase.
4. If there is no clear match, pass the original request to [Help](help.md) as `help <request>`. Wait for a route choice or clarification.

## Routes

Load [Execution](references/execution.md) and the selected executable playbook together. Apply scope, authorization, and [Principles](https://github.com/antshc/brain/blob/main/plugins/wf/skills/principles/SKILL.md) before execution. Copy the playbook's workflow steps into the todo list before adding task-specific steps. Keep skipped steps with their reasons.

| Route | Select when | Files to load | Skills at the step that calls them |
|---|---|---|---|
| `help` | Explicit help or no clear route | [Help](help.md) | None |
| `bug-fix` | Reproduce, diagnose, and fix a defect | [Bug fix](playbooks/bug-fix.md), [Evidence](references/evidence.md) for diagnosis, [Delegation](references/delegation.md) for workers, [Shipping](references/shipping.md) for branch and PR steps. If review was requested, load [Review](references/review.md). For human review, also load [HITL](playbooks/hitl.md). | [Testing Integrations][testing] for reproduction, [Cloud Scenario][cloud] for cloud-only symptoms, [Research][research] for diagnosis, [Design][design] `architect` before changing a boundary or `deep-module` for a seam decision, [Git][git] and [GitHub][github] for shipping, [Write][write] `bug` for a report. [Review][review] `code` for requested review, [Prove][prove] for runnable findings, and Review `hitl` for human review. |
| `design` | Resolve open design decisions before building | [Design](playbooks/design.md), [Evidence](references/evidence.md) for investigation or proof | [Research][research] for current behavior, [Design][design] `grill` or a user handoff to `wayfinder`, then `sketch`, `spec`, or a user handoff to `hld` when applicable. [Prove][prove] for executable uncertainty. |
| `stories` | Turn requirements into an approved, ordered story list | [Stories](playbooks/stories.md) | [Write][write] `story` for each approved row |
| `feature` | Design, implement, and verify a feature | [Feature](playbooks/feature.md), [Evidence](references/evidence.md) for research and open questions, [Delegation](references/delegation.md) for the checkpoint and workers, [Shipping](references/shipping.md) for code comments and commits. After a complete handoff, load [Post-implementation](references/post-implementation.md). At app verification, load [Verifier](agents/verifier.md) before dispatch. At code review, load [Review](references/review.md). For requested human review, also load [HITL](playbooks/hitl.md). | [Research][research], [Design][design] `architect` and `spec`, [Implement][implement], [Show Me Your Work][trail] Log and Report, [Git][git], [GitHub][github], [Review][review] `code` and `comments`. [Prove][prove], [Challenge This][challenge], and [Testing Integrations][testing] at their triggers. Review `hitl` for requested human review. |
| `hitl` | Run a human-led review of a PR | [HITL](playbooks/hitl.md) and [Review](references/review.md) together | [Review][review] `code` then `hitl`, [GitHub][github] for threads, and [Git][git] and [Prove][prove] for runnable findings |

## Load shared instructions on demand

Resolve bundled files relative to this installed skill. Read each required file in full before its step. If a file is missing, report its path and block the dependent step. For each linked skill, resolve the active installation by name. Load the full skill, selected procedure, and required resources only when called.

- For investigation or executable uncertainty, load [Evidence](references/evidence.md). Load it before treating a technical gap as a user decision.
- For nontrivial work or a worker launch, load [Delegation](references/delegation.md). For a direct worker launch, read it with the [Worker contract](worker.md) and pass the contract's absolute path.
- Before branch preparation, a commit, PR opening, or pre-review checks on code produced by this run, load [Shipping](references/shipping.md). Use [Crew Commit][crew] for Codey work and [Git][git] for ordinary commits.
- Use [Write][write] `sharpen` for a vague task within a selected route and `tighten` when preparing the route's reply. Preserve approval prompts, evidence, and output requirements.

[challenge]: https://github.com/antshc/brain/blob/main/plugins/wf/skills/challenge-this/SKILL.md
[cloud]: https://github.com/antshc/brain/blob/main/skills/engineering/prototype-cloud-scenario/SKILL.md
[crew]: https://github.com/antshc/brain/blob/main/plugins/crew/skills/crew-commit/SKILL.md
[design]: https://github.com/antshc/brain/blob/main/plugins/wf/skills/design/SKILL.md
[git]: https://github.com/antshc/brain/blob/main/plugins/wf/skills/git/SKILL.md
[github]: https://github.com/antshc/brain/blob/main/plugins/wf/skills/github/SKILL.md
[implement]: https://github.com/antshc/brain/blob/main/plugins/wf/skills/implement/SKILL.md
[prove]: https://github.com/antshc/brain/blob/main/plugins/wf/skills/prove/SKILL.md
[research]: https://github.com/antshc/brain/blob/main/plugins/wf/skills/research/SKILL.md
[review]: https://github.com/antshc/brain/blob/main/plugins/wf/skills/review/SKILL.md
[testing]: https://github.com/antshc/brain/blob/main/plugins/wf/install/assets/testing-integrations/SKILL.md
[trail]: https://github.com/antshc/brain/blob/main/plugins/wf/skills/show-me-your-work/SKILL.md
[write]: https://github.com/antshc/brain/blob/main/plugins/wf/skills/write/SKILL.md
