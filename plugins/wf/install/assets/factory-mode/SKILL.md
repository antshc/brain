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
2. Resume an active route when the user answers it. Keep the active checkpoint or human-review prompt until the user responds or redirects the task.
3. Honor an explicit route. Otherwise select a route that clearly matches the request. Select `review` for a request to review an existing PR. For a Feature or Bug fix request that also asks for human review, run the primary route and perform the Human review handoff at its review phase.
4. If there is no clear match, pass the original request to [Help](help.md) as `help <request>`. Wait for a route choice or clarification.

## Routes

Load [Execution](references/execution.md) and the selected executable playbook together. Apply scope, authorization, and the `principles` skill before execution. Copy the playbook's workflow steps into the todo list before adding task-specific steps. Keep skipped steps with their reasons.

| Route | Select when | Files to load | Skills called at their step |
|---|---|---|---|
| `help` | Explicit help or no clear route | [Help](help.md) | None |
| `bug-fix` | Reproduce, diagnose, and fix a defect | [Bug fix](playbooks/bug-fix.md), [Evidence](references/evidence.md) for diagnosis, [Delegation](references/delegation.md) for workers, [Shipping](references/shipping.md) for branch and PR steps. If review was requested, load [Automated review](references/automated-review.md). For human review, also load [Review](playbooks/review.md) for its Human review handoff. | `testing-integrations` for reproduction, `prototype-cloud-scenario` for cloud-only symptoms, `research` for diagnosis, `design` `architect` before changing a boundary or `deep-module` for a seam decision, `git` and `github` for shipping, `write` `bug` for a report. `review` `code` for requested review, `prove` for runnable findings, and `review` `hitl` for human review. |
| `design` | Resolve open design decisions before building | [Design](playbooks/design.md), [Evidence](references/evidence.md) for investigation or proof | `research` for current behavior, `design` `grill` or a user handoff to `wayfinder`, then `sketch`, `spec`, or a user handoff to `hld` when applicable. `prove` for executable uncertainty. |
| `stories` | Turn requirements into an approved, ordered story list | [Stories](playbooks/stories.md) | `write` `story` for each approved row |
| `feature` | Design, implement, and verify a feature | [Feature](playbooks/feature.md), [Evidence](references/evidence.md) for research and open questions, [Delegation](references/delegation.md) for the checkpoint and workers, [Shipping](references/shipping.md) for code comments and commits. After a complete handoff, load [Post-implementation](references/post-implementation.md). At app verification, load [Verifier](agents/verifier.md) before dispatch. At code review, load [Automated review](references/automated-review.md). For requested human review, also load [Review](playbooks/review.md) for its Human review handoff. | `research`, `design` `architect` and `spec`, `implement`, `show-me-your-work` Log and Report, `git`, `github`, `review` `code` and `comments`. `prove`, `challenge-this`, and `testing-integrations` at their triggers. `review` `hitl` for requested human review. |
| `review` | Review an existing PR: triage, selected code-review axes, blast radius when warranted, proof of every claim, then human-led review | [Review](playbooks/review.md) and [Automated review](references/automated-review.md) together, [Delegation](references/delegation.md) before any worker | `github` for triage and threads, `review` `code` with selected `--axes`, `review` `blast-radius` when warranted, `git` and `prove` for runnable claims, then `review` `hitl` |

## Load shared instructions on demand

Resolve bundled files relative to this installed skill. Read each required file in full before its step. If a file is missing, report its path and block the dependent step. For each named skill, resolve the active installation by name. Load the full skill, selected procedure, and required resources only when called.

- For investigation or executable uncertainty, load [Evidence](references/evidence.md). Load it before treating a technical gap as a user decision.
- For nontrivial work or a worker launch, load [Delegation](references/delegation.md). For a direct worker launch, read it with the [Worker contract](worker.md) and pass the contract's absolute path.
- Before branch preparation, a commit, PR opening, or pre-review checks on code produced by this run, load [Shipping](references/shipping.md). For Codey work, *Load and follow the `crew-commit` skill to commit the worker's changes*; for ordinary commits, *Load and follow the `git` skill to draft and create the commit*.
- For a vague task within a selected route, *Load and follow the `write` skill to sharpen the task prompt, using route `sharpen`*. When preparing the route's reply, *Load and follow the `write` skill to tighten the reply, using route `tighten`*. Preserve approval prompts, evidence, and output requirements.
