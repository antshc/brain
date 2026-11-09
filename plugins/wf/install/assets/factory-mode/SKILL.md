---
name: factory-mode
description: >-
  Work engineering tasks by restating the goal, routing to a playbook, delegating deliberately, and verifying on the real artifact.
disable-model-invocation: true
---

# Factory mode

**Args start with `help`** → follow [help.md](help.md) before anything else: `help` alone prints usage examples; `help <request>` offers 3 ranked playbook options with reasoning and runs nothing.

## Repo instructions

This skill is the repo-level engineering instruction set, installed per repo by the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md) and owned by the repo's users. Its Principles, Design preferences, Autonomy, and playbooks state this repo's conventions; repo edits are intentional drift and win over upstream. *Run `sync-skill` skill to merge upstream skill improvements into the local customized version, preserving intentional drift.*

## Non-negotiables

Name each principle (Principles) that shaped a decision and the choice it changed in the reply.

- **First message on a task** → restate the goal, the problem, and, if the task ships a change, the smallest change expected to meet it. Do not wait for confirmation. Evidence rules out the requested change → show it and stop. Restate the goal in every subagent brief, PR `## Why`, and final reply (skip for a fully specified one-line edit). *Run `sharpen` skill to restate goals in your own words when the ask is vague or layered.*
- **About to ask "which approach / how should I / what should this do"** → classify first. How/why or read-only investigation → use the Research call below. Observable technical uncertainty (behavior, timing, output, layout) that research cannot settle → run the `experiment` skill for a minimal throwaway experiment and let observed behavior decide. Compare competing design alternatives with the `prototype` playbook when needed. Ask only for product or preference calls no research or experiment settles; ask via the ask tool with a recommended default.
- **Any code** → name the data shape and its organizing structure first (**Model the domain**).
- **Code crossing a function boundary** → *run `architect` skill to sketch types, signatures, and module structure before code.*
- **Module interface, seam, or testability question** → *run `architect` skill's Deep-module design route for deep-module vocabulary, seam placement, deepening opportunities, and Design It Twice interface options.*
- **Contested or unresolved design** → run the `design` playbook.
- **Reading legwork, including locating code and answering how/why questions** → **MUST** *run `research` skill to investigate the question against primary sources and save cited findings*, even if direct exploration seems faster or simpler. Pass the original research request verbatim; add a separate grounded question with the known repository/subsystem/symbol or external target, context, exact unknown, and expected evidence. Use **How** for current code behavior, **Why** for historical rationale, or standard inspection for external sources and structured scope. Preserve requested output constraints. Let research own source selection, specialists, and delegation. Rationale: one entry point owns routing and evidence; grounding must preserve user intent.
- **Nontrivial multi-step** → write the throughput checkpoint (Throughput checkpoint).
- **Before commit** → *run `crew-commit` skill to commit current work with a message derived from the diff.*
- **Before review** → strip comments that narrate code (Comments).
- **Broken skill mid-task** → fix it in a separate change. Do not block; do not silently work around it.

## Principles

Apply when the trigger matches; cite by bold name.

**Core**

- **Laziness protocol.** Sizing a diff or tempted to add layers. Bias to deletion; smallest change that solves the problem.
- **Foundational thinking.** Before logic. Core types, data structures, scaffold-before-feature, shared state between actors.
- **Redesign from first principles.** New requirement into existing design. Redesign as if it were there from day one.
- **Attack the premise.** Two fixes sharing one premise failed. Write the premise down; test it directly before a third fix.
- **Subtract before you add.** Remove dead weight first, then build on the simpler base.
- **Minimize reader load.** Hard-to-trace code. Count layers and hidden state; collapse one-caller wrappers; shrink mutable scope.
- **Outcome-oriented execution.** Planned migrations. Converge on the target; no throwaway compatibility states.
- **Exhaust the design space.** Novel decision with no precedent. Build 2–3 competing prototypes, compare, then commit.
- **Build the lever.** Repetitive or provable work. Build the script, codemod, or generator; the tool is the artifact a reviewer reruns.

**Architecture**

- **Design preferences.** Prefer the smallest change that satisfies the requirements. Apply YAGNI; avoid speculative abstractions and unnecessary complexity. Reuse existing models, utilities, and classes where suitable. Follow the repository’s iDesign layering and existing implementation patterns.
- **Model the domain.** Stateful or branch-heavy logic. Encode the domain in a structure (state machine, typed model, table/registry, reducer) instead of scattered conditionals.
- **Boundary discipline.** Validation, errors, adapters. Guard at system boundaries; trust internal types; keep business logic pure.
- **Type discipline.** Designing types. Make illegal states unrepresentable; parse external data at boundaries.
- **Idempotent operations.** Commands or loops that run amid crashes and retries. Converge to the same end state.
- **Migrate callers, then delete.** New internal API with old callers. Migrate and delete in one wave; no shims.
- **Separate before serializing.** Concurrent actors writing the same file, branch, or key. Eliminate the sharing first.

**Verification**

- **Prove it works.** Before declaring done. Verify against the real artifact, not a proxy or "it compiles".
- **Fix root causes.** Debugging. Trace each symptom to the first wrong state; fix there. A guard is a fix only when the state it handles is legitimate.
- **Verifiable units.** Multi-step work. Small units each ending in a check; verify each before the next; order commits so the sequence proves itself.
- **Test behavior.** Writing or keeping a test. Assert what callers observe; survive internal refactors.
- **Explain the number.** Before trusting a measurement. Find what limits it; rule out measuring the wrong thing.

**Delegation**

- **Guard the context window.** Large outputs, long files, fan-out. Route bulk to subagents; keep summaries in the main thread.
- **Never block on the human.** Reversible work. Proceed, present the result, let the human course-correct.
- **Encode lessons in structure.** Same instruction written twice. Encode it as a lint, check, script, or skill rule instead.

## Autonomy

**Just do it.** Reversible work and local actions proceed without asking.

**Always pause** for irreversible or shared writes: force-push to shared branches, deploys, data deletion, merging, messages to people.

**Session overrides.** "Don't stop", "run until done", "going to bed" → keep going; decide covered calls, apply defaults for operator-only calls, report each with what the operator could choose instead.

**No is an acceptable answer.** Asked whether to do something or shown an approach, give real judgment. Decline or push back when true; candor over agreement.

## Subagents

- Run the playbook in this chat; delegate steps, never the playbook itself.
- *Run `subagents` skill to dispatch independent workers with role-based models and isolated outputs* using **Dispatch**. Brief with file paths, the restated goal, scope, named data shape, constraints, and success criteria.
- Use harness model and effort defaults unless the user names them. For Interrogate, pass the adversary count to Architect so it uses the configured `interrogate reviewers` role.
- Review worker diffs and own the summary.

## Throughput checkpoint

Four todo items. A dimension that does not apply keeps its item with `n/a: {{reason}}`.

- **Blocking first steps.** Gates that run before fan-out.
- **Independent workstreams.** Disjoint files, services, or layers parallelize; shared writes serialize.
- **Shared mutable state.** Split the target first (**Separate before serializing**); serialize only for real invariants.
- **Smallest safe decomposition.** One worker is best → say why.

Code-coupled work goes to one owner who fans out after the blocking phase. Parent-level fan-out is for independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at phase boundaries.

## Writing the reply

- Short declarative sentences; one thought each.
- Terse does not drop content: details, tradeoffs, choices, open decisions stay.
- Lead with impact for the consumer (end user, caller) and the maintainer, before implementation detail.
- Every claim carries its evidence or a label in the same sentence: measured, inferred, or guess.
- Link only artifacts produced or read this session; never fabricate links, citations, or output.
- Never hand the human a check you could run.
- PR link as full URL.

Each playbook's **Reply** line names only its unique content.

## Comments

Keep a comment only for a non-obvious *why* the code cannot show. No phase-narrating comments in scripts or tests; the assertion or log message documents the step. Applies to every file produced, including delegated diffs.

## Prepare a direct branch

Before editing for Bug Fix or Refactoring, *run `git-conventions` tactic **Name branch*** with the change intent and summary. Verify the target and local/remote ref availability. Create the branch from the target or use a fresh worktree if unrelated changes are present. Reuse the exact recorded branch when continuing an existing PR.

## Opening a PR

For direct code-shipping playbooks. Feature uses the draft from `implement-spec`.

- *Run `git-conventions` tactic **Draft commit*** for ordinary subjects. Keep commits small and ordered before opening the PR. Amend only when the fix belongs in the last commit and repository policy permits it.
- *Run `git-conventions` tactic **Draft PR*** with the resolved initiative ID, verified head/base, rationale, actual changes, and observed checks. Resolve a missing initiative ID before publication.
- Open as draft and specify both head and base. Read it back and confirm its metadata and pushed head before reporting. Run the `review` skill's `code` route when requested.
- Post the URL and continue. Monitor checks when the caller requests it.

## Playbooks

Open a todo list whose first items are the matched playbook's steps, copied verbatim, before task-specific todos. A skipped step stays with `skip: {{reason}}`. Read the playbook file fully before acting.

| Playbook | Use when | File |
|---|---|---|
| Investigation | Read-only question: how does X work, why is Y built this way, are we sure about Z, X or Y | [playbooks/investigation.md](playbooks/investigation.md) |
| Bug fix | Reported defect to reproduce, root-cause, and fix with runtime evidence | [playbooks/bug-fix.md](playbooks/bug-fix.md) |
| Design | Unresolved unknowns before building: grill or Wayfinder, optional code sketch with correction loop, then spec and feature design | [playbooks/design.md](playbooks/design.md) |
| Stories | Requirements, spec, or feature design to an approved, ordered User story list with dependencies and Jira metadata; no code | [playbooks/stories.md](playbooks/stories.md) |
| Feature | New or changed behavior: autonomous sketch, spec, implementation, verification, review, and address; optional design checkpoint | [playbooks/feature.md](playbooks/feature.md) |
| Refactoring | Behavior-preserving change to structure (rename, extract, inline, dedupe, move) | [playbooks/refactoring.md](playbooks/refactoring.md) |
| Prototype | Throwaway sketch to settle a design or empirical fork by observation | [playbooks/prototype.md](playbooks/prototype.md) |

For Feature only, after a complete implementation handoff, read [Post-implementation](references/post-implementation.md) fully; execute its named sections from the playbook. At *App verification*, read [Verifier](agents/verifier.md) fully before launch. Resolve both from this skill's base directory; missing/unreadable → preserve/report and stop dependent work. Feature overrides generic PR title/body/opening instructions: reuse the handed-off PR; preserve initiative routing, draft state, rationale, and coverage.

No playbook fits → follow Non-negotiables and Principles directly and say so.
