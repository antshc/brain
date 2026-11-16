# WF work-item terminology migration

## Goal

Use precise leading words for implementation, discovery, tracker mechanics and review follow-ups across WF. Build on the artifact-authoring consolidation in `feat/draft-artifact-routes` at `723ed69edfc7394a0e0c28f156cc512fed83efce`.

Keep `draft-artifact task` as the implementation-artifact route. Rename `design tickets` to `design tasks`. Retain the existing Wayfinder `Task` type.

## Decisions

- Use meaning-specific terms; classify occurrences before editing.
- Add no compatibility aliases, legacy route spellings, old-type translation or fallback behavior.
- Support only `design tasks` after the rename; remove `design tickets` from active executable guidance.
- Rename Wayfinder `Grilling` to `Decision`; keep `Task` unchanged.
- Use `Topic` as the Wayfinder discovery umbrella.
- Keep CLI commands, flags, JSON keys, checkpoint formats, tracker labels and `ccode(...)` history syntax unchanged. These machine contracts are outside this terminology migration; leaving them unchanged adds no compatibility layer.
- Preserve source quotations, external issue titles and historical documents.
- Limit implementation to WF and its installed Factory Mode assets. Exclude `plugins/ralph/`.

## Terminology

| Meaning | Canonical term | Example |
|---|---|---|
| Generic tracked unit across platforms | Work item | Read the work item and its dependencies. |
| Bounded implementation work | Task | Break the spec into implementation tasks. |
| User-facing requirement | Story | Draft one user story. |
| Defect report | Bug | Record reproduction in the bug report. |
| Wayfinder discovery unit | Topic | Resolve the research topic. |
| Human choice | Decision | Present the pending decision. |
| Empirical verification | Experiment | Run the experiment and record the result. |
| GitHub tracker object | Issue | Create a child issue. |
| Jira tracker object | Work item | Update the Jira work item. |
| Deferred review work | Follow-up | An agreed follow-up remains untracked. |
| Historical tracker evidence | Issue or provider-specific work item | Read the linked issue and its comments. |

The same implementation Task can be stored in a GitHub issue or Jira work item. Artifact meaning and tracker representation remain separate.

## Route and resource changes

| Current | Target |
|---|---|
| `design tickets` | `design tasks` |
| `design/playbooks/tickets.md` | `design/playbooks/tasks.md` |
| `design/references/wayfinder-ticket-types.md` | `design/references/wayfinder-topic-types.md` |
| `github/tactics/specs-and-tickets.md` | `github/tactics/specs-and-issues.md` |
| `draft-artifact task` | Unchanged |

Update route selection, argument examples, headings, direct resource disclosure, links and callers together. Remove obsolete resource files; keep no forwarding files.

Rename the standalone decomposition workflow's headings to Task operations and Task labels. Rename the shared gate covering map and child creation to Work item approval. Preserve all existing gate conditions and authority boundaries.

## Wayfinder topic types

| Current type | Target type | Responsibility |
|---|---|---|
| Research | Research | Resolve factual questions through cited evidence. |
| Experiment | Experiment | Check a falsifiable claim through execution. |
| Grilling | Decision | Resolve requirements, preferences or trade-offs with the user. |
| Contract design | Contract design | Compare interface options and obtain a choice. |
| Task | Task | Produce code sketches or complete prerequisite access/data work that unblocks a decision. |

The Wayfinder Task type remains discovery-oriented and excludes implementing the destination feature. Implementation tasks belong to the implementation workflow. Do not introduce Preparation or Prerequisite as replacement type names.

Rename the topic type and its references; keep the `design grill` helper route and its procedure unchanged. Topic classification and helper execution are separate concepts.

Add no automatic translation for old topic-type names. Do not mutate existing remote maps/issues merely to change terminology.

## Skill migration checklist

### Design

- [ ] Update `design/SKILL.md`: canonical `tasks` route, new resource paths, Work item approval heading and references.
- [ ] Rename `design/playbooks/tickets.md` to `tasks.md`; use task breakdown, implementation task, task dependencies and task approval where the scope is implementation.
- [ ] Update `design/references/github.md`: Task operations, Task labels and every affected anchor.
- [ ] Rename `design/references/wayfinder-ticket-types.md` to `wayfinder-topic-types.md`; use the final topic-type table.
- [ ] Update `design/playbooks/wayfinder.md`: topics for discovery, issues for GitHub objects, Work item approval for tracker creation.
- [ ] Update `design/playbooks/sketch.md`, `spec.md`, `hld.md`, `references/living-document.md` and `references/risk-verification.md` according to meaning.
- [ ] Update Design README examples, diagrams and handoffs. Preserve `design grill`, prototype approval, evidence eligibility and publication rules.

### Draft artifact

- [ ] Keep the `task` route, playbook and template names.
- [ ] Use task for implementation-related references in `templates/task-template.md`.
- [ ] Use topics for Wayfinder discovery references and issues for tracker representation in HLD authoring, HLD updates, HLD template and decision bullets.
- [ ] Preserve internal requirements rules, protected source wording and artifact output formats.

### Implement

- [ ] Update `implement/SKILL.md`: task graph, task worker, task commit, task publication and task closure.
- [ ] Update `references/breakdown.md`, `sequential.md`, `parallel.md`, `publication.md` and `worktrees.md`.
- [ ] Update `agents/planner.md` and `agents/chore.md` briefs and prose.
- [ ] Keep graph identities, JSON keys, checkpoint fields, CLI calls, commit recognizers and scheduling behavior unchanged.
- [ ] Keep invoking `draft-artifact task` once per planned implementation task.

### GitHub

- [ ] Rename `tactics/specs-and-tickets.md` to `specs-and-issues.md`; update router links and heading.
- [ ] Use issue for platform reads/writes and native issue relationships.
- [ ] Update `references/wayfinder.md` to distinguish caller-owned topics/work items from GitHub issues; update shared approval references.
- [ ] Update `references/review-comments.md`: follow-up for deferred work, issue/work item for its supplied tracker reference.
- [ ] Preserve existing CLI command names and transport behavior.

### Research

- [ ] Update `research/SKILL.md` and `wayfinder/wayfinder.md`, `questioning.md`, `living-document.md`, and both Wayfinder templates to use topic and issue by meaning.
- [ ] Update references to Design's renamed Work item approval gate.
- [ ] Update Why procedures, investigator/synthesizer prompts and tracker-source guides: issue or provider-specific work item for historical evidence.
- [ ] Preserve Research's research/experiment scope; the terminology change grants no Design execution authority.

### Git

- [ ] Update `git/references/commit-messages.md` and `tactics/commits.md` to use task commit for implementation history.
- [ ] Use work item ID in generic branch naming rules.
- [ ] Preserve commit syntax, history matching, branch slug rules and ownership.

### Review

- [ ] Update `review/playbooks/code.md`, `comments.md`, `references/conversation-flows.md` and `references/initiative-review-guidance.md`.
- [ ] Use follow-up for deferred work; issue/work item for a supplied tracker reference.
- [ ] Preserve source quotations and restrictions on creating follow-up tracking items, posting, waiting and resolving threads.

### Atlassian and diagnosis

- [ ] Update `atlassian/references/address-page-comments.md` to distinguish follow-ups from Jira work items.
- [ ] Inspect Jira duplicate-search wording; retain literal input/search terms when they are data.
- [ ] Update `diagnosing-bugs/references/root-cause-report.md`: work item reference instead of generic ticket ID.
- [ ] Preserve provider schemas and evidence.

### Factory Mode and documentation

- [ ] Update installed Factory Mode feature, design, stories and review playbooks where applicable.
- [ ] Update `agents/verifier.md` and `references/post-implementation.md` to use implementation tasks and task verification.
- [ ] Preserve the distinction between story breakdown and implementation-task breakdown.
- [ ] Update repository/WF READMEs, active examples and diagrams.
- [ ] Update affected contract checks and fixtures for renamed routes, resources, headings and topic types.
- [ ] Search WF agents, installer templates and scripts for additional active prose or resource-path references missed by the initial inventory.

## Implementation sequence

1. Classify each existing occurrence as implementation, discovery, tracker mechanics, review follow-up, machine identifier or protected source text.
2. Rename routes/resources and update every caller, direct resource link and section anchor in one change.
3. Update skill prose, agent briefs, installed workflow assets and active documentation.
4. Update affected checks and fixtures to the canonical names only.
5. Load and follow the repository's `skill-author` Shrink procedure on changed agent-facing instructions. Preserve behavior, literal machine contracts and output formats.
6. Run validation and resolve uncovered obligations before reporting completion.

## Validation

- [ ] `design tasks` resolves to its renamed playbook; `design tickets` has no alias or executable fallback.
- [ ] `draft-artifact task` remains the canonical implementation-artifact author.
- [ ] Wayfinder uses exactly Research, Experiment, Decision, Contract design and Task as its topic types.
- [ ] Wayfinder Task still means sketches/prerequisite work; no Preparation or Prerequisite replacement type is introduced.
- [ ] `design grill` and its existing procedure remain unchanged.
- [ ] Approval conditions, evidence integration, task decomposition, scheduling, publication and closure behavior are preserved.
- [ ] CLI commands, JSON/checkpoint fields, labels and commit matching are unchanged.
- [ ] Markdown lint, local links, skill descriptions, invocation checks and affected Python tests pass.
- [ ] Representative walkthroughs cover spec-to-task breakdown, Wayfinder human decisions, Wayfinder prerequisite Tasks and review follow-ups.
- [ ] Every remaining ticket occurrence is classified as a machine identifier, protected source text, historical document, literal search input or excluded scope.
- [ ] Final completeness sweep maps every requested rename and affected caller to evidence; no stale active paths, anchors or route spellings remain.

## Completion

Report the canonical route/resource changes, affected skills, shrink results, checks performed and any remaining blockers. Publishing this plan does not implement the terminology migration or authorize unrelated changes.
