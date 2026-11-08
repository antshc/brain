# Consolidate GitHub, Git conventions, and worktrees into git-toolkit

**Goal.** Replace the proposed `use-github` skill and the existing `git-conventions` and `worktrees` skills with one model-invoked, tactic-based skill. Callers select only the needed tactic; the skill does not orchestrate feature delivery or assume authority to publish, commit, or delete.

**Baseline.** The earlier [Brain snapshot at dff4393](https://github.com/antshc/brain/tree/dff4393bfe089ed44f4547d603478d811cd60fa0) and [GitHub skill proposal](https://chatgpt.com/library?file_id=libfile_989d274a269c8191b37699402923a3e0&account_id=personal) describe the original GitHub-only migration. Recheck the current `main` before implementation: `git-conventions` and `worktrees` now exist and have live WF, Review, and factory callers.

## Name

**Selected: `git-toolkit`.** One model-invoked tactic router, not an end-to-end workflow. Do not keep compatibility aliases: they would retain extra autodiscoverable skills.

## Constraints

- **MUST** use one discoverable `SKILL.md` with a small tactic router and on-demand references. GitHub access, Git conventions and local worktrees are independent tactic groups, not sequential workflow steps.
- **MUST** keep caller ownership of repository/tracker routing, branch choice, integration, commit/push authorization, publication gates, review ownership, thread closure, worktree lifecycle policy and branch deletion. A formatting tactic returns text; it never executes a Git or GitHub write.
- **MUST** qualify GitHub operations by repository and object. Keep tracker and source routing distinct. Honor the caller's expected state, transport and approval gates. Prefer the GitHub integration for supported, permitted operations, including ChatGPT publication; use authenticated `gh` only where supported and allowed. Missing capabilities stop dependent operations.
- **MUST** read back remote writes and reconcile unknown outcomes before retries. Distinguish confirmed empty, incomplete, failed and partial results.
- **MUST** preserve the existing `worktrees` ownership record and `scripts/worktrees.py` behavior: absolute harness/source separation, pinned commit, clean/unlocked reuse, recoverability, verified removal, no force/reset/prune/recursive deletion and no touching unowned or dirty worktrees.
- **MUST** preserve `git-conventions` contracts: `feat/` or `fix/` branch names without ticket IDs; ordinary conventional commits and WF `ccode(...)` commits; leading initiative marker in PR title/body; concise review prose and terminal hidden agent markers. Keep the `writing-style` dependency only for convention prose that already uses it.
- **MUST** retain caller-specific adapters and policies: Implement Spec's required `GH_TOOL` and checkpoint semantics, Address discussion gates, HITL verbatim approval, Wayfinder body blockers, To Tickets native edges, offline publication and Ralph as a separate migration.
- **MUST NOT** turn this skill into a Git workflow orchestrator, duplicate full command recipes in callers, broaden mutation permissions, or make GitHub publication a side effect of naming/inspection.
- **MUST NOT** refactor the Crew plugin (`plugins/crew/**`), its skills, agents, manifests, documentation, or installer. Leave its existing GitHub operations and skill dependencies unchanged. Crew migration may be proposed separately.

## Proposed structure

```text
plugins/wf/skills/git-toolkit/
  SKILL.md                          # Tactic router; guards, inputs, outputs
  references/
    github/
      issues.md
      pull-requests.md
      reviews.md
      checks.md
      repository.md
    conventions/
      branches.md
      commits.md
      pull-requests.md
      review-comments.md
    worktrees.md                    # Inspect/create/reuse/remove/reconcile + helper contract
  scripts/
    worktrees.py                    # Move existing tested helper without behavioral change
    github_read.py                  # Optional pilot only if justified by callers
```

| Tactic group | Operations | Effect |
| --- | --- | --- |
| **GitHub** | Repository lookup, issues/edges, PRs, review threads/replies, checks | Explicit remote reads/writes, only as authorized by caller |
| **Conventions** | Name branch, draft commit, draft/read PR, draft/finalize review comment | Pure text or metadata; no Git/GitHub writes |
| **Worktrees** | Inspect, create, reuse, remove, reconcile | Local state; mutations only for authorized run-owned worktrees |

The router selects one operation and loads its exact reference. Each tactic reports verified result and relevant completeness/blockers. Keep `github/pull-requests.md` (remote transport) separate from `conventions/pull-requests.md` (format). Merge the old `worktrees/SKILL.md` and `references/helper.md` into the one `references/worktrees.md`; preserve its Python helper. Move the four conventions references verbatim initially, then change paths and check for semantic overlap.

**Skill count.** Relative to the original three-skill target (`use-github`, `git-conventions`, `worktrees`), one discoverable skill replaces three: **net −2**. Relative to today's existing two skills, the migration produces one: **net −1**. Reference and helper files are not discoverable skills.

## Implementation order

1. **Verify discovery.** Confirm WF and Review + WF install paths can discover `git-toolkit`. Review has a separate manifest without a declared WF dependency; document or enforce the prerequisite. Exercise Review-only behavior explicitly. Missing shared capability must surface before remote or local mutation. Do not touch Crew install paths.
2. **Capture behavior and tests.** Recheck current `main`, existing tests, the GitHub migration proposal, `git-conventions` references, `worktrees` Python helper, and all current caller contracts. Record any path-dependent test fixture or script invocation before moving files.
3. **Create the shared tactic router.** Add `git-toolkit/SKILL.md`, five GitHub references, four convention references and `worktrees.md` as above. Standardize target, intent, expected state, authorization, result, and completeness fields without forcing every tactic into a single rigid schema. Keep review reply, inline finding, and PR conversation operations distinct. Worktree operations use separate absolute harness and source paths.
4. **Migrate existing conventions/worktrees callers first.** Redirect branch, commit, PR, review-comment, and worktree references to the new skill; move `scripts/worktrees.py` without changing its JSON/exit/ownership contracts. Keep caller-side fetch, branch setup, integration, publication, run records and editor exclusions. Keep `writing-style` invocation inside conventions tactics. Update Review Address, Code Review, HITL, Implement Spec, factory post-implementation, install guidance and relevant tests.
5. **Migrate straightforward GitHub callers in WF and Review only.** Replace embedded access recipes for repository search, PR context and external sources. Keep local evidence paths and mutation boundaries. Crew retains its current implementation.
6. **Migrate WF backlog callers.** Move reusable issue, artifact, label and relationship transport to GitHub tactics. Keep each caller's record identities and reconciliation keys. Wayfinder retains body blockers; To Tickets retains native dependencies. Offline paths remain local. Run the Init WF label fixture before altering the manifest.
7. **Migrate Review and Implement Spec GitHub transport.** Route remote operations through shared tactics or documented required adapters; preserve local diff/worktree acquisition and existing command/JSON/exit contracts. Address keeps discussion gates, HITL human approval, Code Review marker policy and Implement Spec `GH_TOOL`/draft-only/checkpoints. Do not create duplicate remote writers for one action.
8. **Pilot optional Python GitHub reads.** Only if needed, add read-only thread snapshots and native issue-graph lookup wrapping authenticated `gh`, resolved from the shared skill base. Require explicit repository and object, emit raw IDs/head/edges and completeness as JSON, and wire each shipped command to a real caller. Otherwise defer scripts and keep connector-only runs viable.
9. **Update docs and remove old skills.** Update `ARCHITECTURE.md`, `docs/concepts/structure-resource-access-skill.md`, `README.md`, `plugins/wf/README.md`, installers/manifests, test expectations and relative/absolute skill links. Remove `plugins/wf/skills/git-conventions/` and `plugins/wf/skills/worktrees/` only after migration and validation. Sweep current plugin sources for old names and direct GitHub recipes; classify remaining adapters, installer, caller policy, Ralph follow-up or omissions.

## Affected surfaces

| Area | Files or skills | Preserve |
| --- | --- | --- |
| Shared | `git-toolkit/SKILL.md`, `references/{github,conventions}/*`, `references/worktrees.md`, `scripts/worktrees.py`, optional `scripts/github_read.py` | Tactic boundaries, qualified targets, exact payloads, ownership, recoverability, read-back |
| Existing shared skills | Remove `git-conventions` and `worktrees` after replacing references | No discoverable aliases; full behavior and tests migrate |
| WF evidence | `explore-codebase`, `research/why`, `grill-design/references/tactics-external-source.md` | Local search, pinned evidence, confirmation of external edits |
| WF backlog | `to-spec`, `to-tickets`, `wayfinder`, installer, generated template | Routing labels, blocker semantics, offline mode, label manifest, dispatch approval |
| Review | `code-review`, `hitl`, `test-gaps`, `address`, review references and docs | Comment text/markers, approval gates, discussion and thread ownership |
| Implement Spec | `SKILL.md`, `references/worktrees.md`, planner/publication/sequential/parallel guidance, `scripts/spec_gh.py` | Worktree/commit callers, Codey/Chore isolation, `GH_TOOL`, checkpoints, draft PR and closure evidence |
| Factory/other | `factory-mode/references/post-implementation.md` and other convention/worktree call sites | Commit format and existing workflow authority |
| Docs/install/tests | `ARCHITECTURE.md`, concept, READMEs, plugin prerequisites, skill paths, Python/contract tests | Accurate discovery, counts, paths and behavior |

## Verification

- **Discovery.** Exercise WF-only, Review + WF and Review-only installed setups; simulate an unavailable shared skill. Fail before a mutation when required tactics cannot load. Check old skills are absent from autodiscovery after migration.
- **Convention regression.** Verify `feat/` vs `fix/` slug and omission of IDs; ordinary and `ccode(...)` commit subjects/history filters; PR initiative marker consistency; exact final visible review body, agent marker count and recognition; writing-style selection.
- **Worktree safety.** Run the existing Python helper tests in the new path. Exercise clean create/reuse/remove; dirty, ignored/untracked, locked, unowned, misrouted, stale-HEAD and interrupted cases. Verify no force/delete/reset and no regression in ownership JSON and exit codes. Test working directory changes do not break script resolution.
- **GitHub reads.** Exercise cross-repo targets, pinned search, truncated diffs, paginated issue edges and threads, stale head and denied reads. Missing data must report incompleteness.
- **Remote write recovery.** Simulate lost create/reply results and issue creation with failed parent link; reruns reconcile records and do missing work only. Confirm head changes block stale review writes.
- **Policy regressions.** Offline makes zero GitHub calls; Wayfinder keeps text blockers; To Tickets native edges; HITL approved text unchanged; Address markers/discussion unchanged; Implement Spec `GH_TOOL`, checkpoints and draft PR unchanged. Worktree tactics never auto-commit or auto-push.
- **Repository checks.** Run `python3 .github/scripts/run-python-tests.py --unit-only` after staging tests for Git-based discovery; focused Implement Spec, Init WF, Address, worktrees and conventions suites. Validate skill frontmatter, reference paths, scripts, manifests and discovery. Sweep references to both retired skill names.

**Done when** all in-scope WF, Review and factory GitHub, convention and worktree calls use `git-toolkit` or an explicit required caller adapter; there are no dangling references or duplicate discoverable skills; safety, formatting and publication contracts pass. Crew and Ralph remain unchanged.
