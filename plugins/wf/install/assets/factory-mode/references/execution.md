# Execution

## Start the task

- Restate the goal and problem in your first message. If the task ships a change, state the smallest change expected to meet it. If evidence rules it out, show the evidence and stop.
- Restate the goal in worker briefs, PR `## Why`, and the final reply. Skip the repeated restatement for a fully specified one-line edit.
- If a request matches a route but is vague or layered, *Load and follow the `write` skill to sharpen the task prompt, using route `sharpen`.*
- If a skill breaks mid-task, fix it in a separate change. Report the blocker and continue independent work.

## Principles

*Load and follow the `principles` skill to apply the principles named by the selected playbook and the matching principles from its index.* Re-evaluate at phase changes. Fresh workers load applicable principles themselves. If a dependency is missing, report it and block the dependent decision. Repository policy and the user's scope, authority, and approval gates govern permitted actions.

## Design preferences

Prefer the smallest change that satisfies the task. Apply YAGNI. Reuse suitable models and utilities. Follow the repository's iDesign layering and implementation patterns. Preserve intentional repo-local overrides.

Before writing code, name the data shape and the structure that organizes it. If code crosses a function boundary, *Load and follow the `design` skill to sketch types, signatures, and module boundaries, using route `architect`.* For a module interface, seam, or testability decision, *Load and follow the `design` skill to compare module boundaries, using route `deep-module`.* Use the Design playbook for unresolved or contested design when the current route does not own the design loop.

## Autonomy

Proceed with reversible local actions within scope. Pause for irreversible or shared writes such as force-push to shared branches, deploys, deletion, merges, or messages to people. When the user asks you to keep going, make covered choices and report defaults for operator decisions within the granted authority. If the evidence supports declining a request, state the reason.

## Reply

Lead with the outcome and its effect for the user and maintainer. Name each principle that shaped a decision and state what it changed. Attach evidence or label the inference or uncertainty. Link verified artifacts from this run and give the full PR URL. Run available checks before handing back work.

*Load and follow the `write` skill to tighten the reply, using route `tighten`.* Preserve the selected playbook's Reply requirements and verbatim evidence.
