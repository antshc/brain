# Implement the shared GitHub skill

**Goal.** Put GitHub access instructions in one model-invoked skill. Each caller invokes the tactic it needs and supplies its target, required output, and policy.

**Baseline.** [Brain main at dff4393](https://github.com/antshc/brain/tree/dff4393bfe089ed44f4547d603478d811cd60fa0) and the [GitHub skill proposal](https://chatgpt.com/library?file_id=libfile_989d274a269c8191b37699402923a3e0&account_id=personal).

## Constraints

- **MUST** keep `use-github` tactic-based. Load only the references selected by the requested operation.
- **MUST** qualify GitHub operations by repository and object. Keep tracker and source routing distinct. Honor the caller’s authorization, expected state, required transport, and approval gates.
- **MUST** prefer the GitHub integration for supported and permitted operations, including ChatGPT publication. Use authenticated `gh` when the integration lacks the operation and the caller permits CLI access. Stop dependent work if the required capability is unavailable.
- **MUST** read back writes and reconcile unknown outcomes before retrying. Keep confirmed empty, incomplete, failed, and partial results distinguishable.
- **MUST** retain caller policy for issue conventions, review ownership, draft-only publication, offline publishing, and worktrees. Keep Ralph’s migration in a separate follow-up.

## Implementation order

1. **Verify skill discovery.** Confirm installed WF, Review with WF, and Crew with WF can discover and invoke `use-github` by name. Review and Crew have separate manifests with no declared WF dependency. Document and validate WF as a prerequisite for their GitHub operations. Check Review-only and Crew-only behavior as well. If the supported install paths cannot reliably supply WF, resolve packaging before removing local recipes from those plugins. A missing skill must surface before any affected remote action.
2. **Add the shared skill.** Create `plugins/wf/skills/use-github/SKILL.md` and its five references from the proposal. Add stable tactic inputs and outputs. For writes, carry the exact payload, target, and applicable expected SHA or state. For reads, carry qualified IDs and completeness. Keep separate operations for review replies, inline comments, and PR conversation comments.
3. **Migrate straightforward callers.** Replace embedded GitHub access recipes for repo search, PR context, external sources, and explicit Crew issue inputs. Retain the local evidence paths and mutation boundaries.
4. **Migrate WF backlog callers.** Move reusable issue, artifact, label, and relationship instructions to the shared skill. Keep each caller’s record identity and reconciliation keys. Wayfinder keeps body-based blockers, and To Tickets uses native dependency edges. Keep explicit offline paths entirely local. Run the existing Init WF label fixture before altering how its manifest is supplied.
5. **Migrate Review and Implement Spec.** Replace remote transport instructions with shared invocations, including final snapshot checks. Keep local diff/worktree acquisition in callers. Address retains its mandatory discussion gate, and Implement Spec retains `GH_TOOL` as the required backend. Record these as caller-selected adapters. Leave their local command paths, JSON and exit contracts, and caller-specific scripts in place for this migration.
6. **Pilot the optional Python CLI.** Start with a read-only review-thread snapshot and native issue graph lookup, wrapping authenticated `gh`. Resolve the script from the shared skill base. Require an explicit repo and issue or PR number. Return raw IDs, observed head or edge data, and completeness as JSON. Reuse acquisition code where packaging permits without crossing skill directories. Wire the pilot to at least one migrated caller per command before shipping. If existing mandatory helpers cover all actual consumers, defer the extra command. Keep transport errors explicit and preserve the integration path for connector-only runs.
7. **Finish docs and run the coverage sweep.** Update `ARCHITECTURE.md`, `docs/concepts/structure-resource-access-skill.md`, `README.md`, and `plugins/wf/README.md`. Explain the new GitHub-native ownership rule and installation requirement. Scan current plugin sources for direct GitHub commands and API instructions. Classify each remaining occurrence as an approved adapter, caller policy, separate Ralph migration, tool installer, or an omission to fix.

## Affected surfaces

| Area | Files or skills | Preserve |
| --- | --- | --- |
| Shared | `use-github/SKILL.md`, `references/{issues,pull-requests,reviews,checks,repository}.md`, optional `scripts/github_read.py` | Qualified targets, complete pagination, exact payloads, read-back |
| WF evidence | `explore-codebase`, `research/why`, `grill-design/references/tactics-external-source.md` | Local search, commit-pinned evidence, explicit confirmation of external edits |
| Crew | `to-crew/SKILL.md` and install guidance | Only an explicit issue input authorizes issue handling. Agent verdict determines the operation |
| WF backlog | `to-spec`, `to-tickets`, `wayfinder`, WF installer, generated instructions template | Routing labels, native versus body-based blockers, offline behavior, baseline label manifest, Wayfinder dispatch approval |
| Review | `code-review`, `hitl`, `test-gaps`, `address` and their GitHub references | Code Review markers, HITL verbatim approved body, Test Gaps read-only, Address origin and reply rules |
| Implement Spec | `SKILL.md`, planner and publication guidance, `scripts/spec_gh.py` contract | Planner/orchestrator permissions, Codey/Chore isolation, qualified ticket routing, resumable checkpoints, draft-only PR, closure evidence |

## Verification

- **Discovery.** Exercise WF-only, Review + WF, and Crew + WF installed setups. Simulate an unavailable shared skill. Confirm failures precede remote writes.
- **Read integrity.** Exercise cross-repo targets, pinned search results, truncated diffs, multi-page issue edges and nested thread comments, stale PR head, and a denied API read. Confirm required missing data returns an incomplete result.
- **Write recovery.** Simulate lost create and reply responses and a successful issue create with a failed parent link. Confirm reruns reconcile existing records and perform only missing work. Confirm changed head blocks stale review writes and read-back confirms the exact thread or object.
- **Policy regressions.** Check offline paths make zero GitHub calls, Wayfinder keeps text blockers, To Tickets creates native edges, HITL preserves exact approved text, Address preserves marker behavior, and Implement Spec keeps `GH_TOOL`, checkpoints, and draft status.
- **Repository checks.** Run `python3 .github/scripts/run-python-tests.py --unit-only` after staging new tests so the Git-based discovery includes them. Run the focused Implement Spec, Init WF, and Address suites. Add fixtures only for newly shared behavior or missing regression coverage. Validate frontmatter, reference paths, and discoverability from installed plugins.

**Done when** each in-scope GitHub operation routes through the shared skill or a documented caller adapter, callers pass the above checks, and Ralph’s follow-up remains independently reviewable.
