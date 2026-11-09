# Consolidate Git and GitHub into the `github` skill

Replace WF's `git-conventions` and `worktrees` with one discoverable `github` skill and one Python CLI. Migrate active WF and Factory Mode GitHub recipes. Replace the earlier `git-toolkit` proposal and its optional read-only CLI. Net change **−1 discoverable skill**.

Baseline [Brain main at `11773dd`](https://github.com/antshc/brain/tree/11773dd6e8c0da474c845c9e889b068da7d353de). Keep the existing Crew and Ralph exclusions. Inventory their copies and the legacy AFK module separately.

## Skill structure

```text
plugins/wf/skills/github/
├── SKILL.md
├── tactics/
│   ├── repository.md
│   ├── branches.md
│   ├── commits.md
│   ├── worktrees.md
│   ├── issues.md
│   ├── specs-and-tickets.md
│   ├── pull-requests.md
│   ├── reviews.md
│   └── checks.md
├── references/
│   ├── cli-contract.md
│   ├── transports.md
│   ├── pr-format.md
│   ├── review-comments.md
│   ├── fetch-diff.md
│   └── issue-artifacts.md
└── scripts/
    ├── github.py
    └── github_cli/
        ├── __init__.py
        ├── cli.py
        ├── git.py
        ├── gh.py
        ├── worktrees.py
        ├── issues.py
        ├── specs.py
        ├── pulls.py
        ├── reviews.py
        └── implement_spec.py
```

Resolve `python3 <installed github skill>/scripts/github.py` before changing directory. Use the standard library and existing `git` and `gh` subprocess patterns. `github.py` is the only supported CLI entry point. Put route-specific flags in the tactic and CLI help. Keep shared result and transport contracts in references.

## Progressive disclosure

`SKILL.md` maps requested intent to one tactic. Load a reference only when the selected operation requires it. For example, branch naming loads `branches.md` and returns text. An explicit branch creation request uses the same tactic and runs the CLI. Opening a PR loads `pull-requests.md` and `pr-format.md` only if the caller needs formatted metadata. A task spanning several operations reselects the tactic at each step.

| Tactic | CLI command groups and behavior |
| --- | --- |
| Repository | `repo resolve / read / search` and pinned remote file or commit reads. Identify the source, tracker, checkout and remote explicitly. |
| Branches | `branch inspect / create / fetch / push / delete`. Keep `feat/` and `fix/` names free of ticket IDs, retain worker ordinals, and resume with exact recorded refs. Validate the expected SHA and the destination before writes. |
| Commits | `commit history / create`. Keep conventional subjects and WF `ccode(...)` subjects. Scope history to the caller's pinned range and commits to caller-authorized paths. |
| Worktrees | `worktree inspect / create / reuse / remove / reconcile`. Port the existing helper and ownership record. Require verified checkout identity, a pinned SHA, recoverability and clean, unlocked state where required. |
| Issues | `issue read / list / create / edit-body / assign / unassign / comment / close`, `issue children / link-child / blockers / block`, and `label ensure / verify`. Qualify the issue and retain both API IDs and issue numbers. |
| Specs and tickets | `spec preflight / create`, `ticket create`, `graph read`, `artifact list / get / put`. Reuse issue, label and relationship operations. Load artifact requirements only for artifact work. |
| Pull requests | `pr read / find / publish / diff / diff-split / checkout / comment / upsert-comment`. Preserve draft policy, manual PR text, legacy initiative parsing and plain coverage references. Diff routes retain exact head/base, manifests and output ownership. |
| Reviews | `review discussion / inline / reply / resolve`. Separate inline findings, thread replies and top-level comments. Use one marker reference for visible wording, terminal HTML rules and recognition. |
| Checks | `checks read`. Bind results to the verified PR head and distinguish absent, pending, failed and passed. |

Formatting remains a skill tactic. Apply `writing-style` to the existing commit, PR and review-draft routes. Final comment posting uses the approved body verbatim. The caller decides when to create branches, stage or integrate commits, publish, resolve threads, close issues and clean up. Preserve caller-owned merge, cherry-pick, conflict and approval logic.

## Migration inventory

Paths under `plugins/wf/` are relative to that directory.

| Current source | Move or update |
| --- | --- |
| `skills/git-conventions/SKILL.md` and its four references | Move naming and commit rules to their tactics. Move PR and review formats to their references. Retire the old skill. |
| `skills/worktrees/{SKILL.md,references/helper.md,scripts/worktrees.py}` | Move rules and tested behavior into `worktrees.md` and the CLI. Migrate callers before retiring the skill. Preserve `brain-worktree.json`, the ownership token and changed exclude-file reporting. |
| `skills/implement-spec/scripts/spec_gh.py` | Port preflight, issue/spec/ticket operations, artifacts, graph read, draft PR publication, checks and diff split. Keep `graph frontier` and `run checkpoint` under the same CLI in private `implement_spec.py`. Those commands remain local and Implement Spec-owned. Rebind `GH_TOOL` to the new absolute entry point. Update `SKILL.md`, planner/Chore, breakdown, publication, worktrees, fetch-diff and sequential/parallel references. |
| `skills/design/references/github.md` and Spec, Tickets and Wayfinder playbooks | Replace remote recipes with tactic calls. Keep approved content, publication profiles, label selection and offline output in Design. Keep native blockers for Tickets and body blockers for Wayfinder. Keep `bundle_artifacts.py` in Design for local packaging. Move issue artifact upload, read-back and URL mapping into the shared CLI. |
| `skills/review/scripts/pr_discussion_state.py`, `references/{github-api,posting,fetch-diff,conversation-flows}.md`, and Code, Comments and HITL playbooks | Move snapshot acquisition, parsing, posting and diff mechanisms. Keep Review's approval, anchoring, freshness, thread ownership and resolution decisions in the playbooks. Preserve Code's detached worktree, HITL's authorized interactive checkout and Chore's read-only snapshot handoff as distinct acquisition profiles. |
| `install/{install.md,github.md,copilot-instructions.template.md,scripts/create_labels.py}` | Route baseline label setup through the CLI. Keep the baseline manifest and labels-only entry in the installer. Preserve existing labels and the generated source/tracker remote guard. |
| `agents/codey.agent.md`, `skills/research/why/`, `skills/design/references/tactics-external-source.md` | Update Codey's authorized history/commit usage and route remote evidence lookup or authorized source corrections through `github`. Check Explore Codebase, Architect and other WF callers for GitHub/worktree links. Keep local code search and isolated subagent policy with their owners. |
| `plugins/wf/install/assets/factory-mode/`, `.chatgpt/{dev,feat}.scut.md`, `brain.md`, READMEs and architecture | Migrate direct branch, push, PR, graph, checks, issue closure and comment recipes. Preserve the Factory decision-report marker and verifier verdict comment identity. Document WF as the provider. Keep the GitHub integration as the ChatGPT publication transport. |

**Adjacent inventory.** `tools/src/modules/github/` owns legacy AFK `fetch_issues.py`, `fetch_threads.py`, `pr_discussion_state.py` and transport/domain code. Its 17 nonempty Python files have byte-identical copies in both Ralph `dev/github/` and `fix/github/`. The current WF discussion helper has a different marker-based contract. Keep legacy AFK and Ralph on their existing runtime. Crew's `to-crew` issue instructions and `chorey_diff.py` remain in Crew. Separate GitHub Actions runner definitions and unrelated install downloads from agent-facing repository operations.

## Implementation order

1. **Lock the current contracts.** Capture command arguments, JSON/exit behavior, graph and checkpoint schemas, ownership files, baseline labels and fixture paths. Document differences before sharing code. Design checks duplicate specs and publishes the supplied body. Implement Spec appends its source note and has different existing label setup. Use explicit caller profiles over shared primitives. Preserve exact payloads on read-back.
2. **Build the router and local commands.** Port worktree code first. Share narrow Git primitives for ref verification, history and authorized mutations. Keep the existing branch/commit formats, old recorded refs and owner-token checks. Use explicit checkout and expected SHA for mutations. Avoid force pushes and refuse unsafe worktree cleanup.
3. **Consolidate remote operations.** Reuse one `gh` adapter for REST/GraphQL, paging, verbatim body files and errors. Keep Implement Spec's required CLI backend. For connector-only ChatGPT runs, execute the same tactic through the GitHub integration when it supports the entire operation. The Python CLI does not call the connector. Missing capability blocks dependent work. Record verified IDs and partial progress, reconcile uncertain responses before retrying, and report incomplete reads separately from empty results. Preserve installer label defaults and check issue-artifact capability only on that route.
4. **Switch callers and retire entry points.** Migrate Install/Design, Implement Spec, Review, then Factory/shortcuts. Keep the existing Implement Spec and Review result schemas through cutover, including Review's `stop / skip / proceed` gate. Remove the four old script entry points and two old skills after caller and fixture checks pass. Verify WF discovery and standalone Factory's WF prerequisite before any affected mutation.
5. **Sweep current sources.** Search active tracked instructions and scripts for old skill names, script paths, GitHub API/CLI/MCP recipes and local Git lifecycle recipes. Classify remaining matches as CLI adapter, caller-owned workflow logic, CI/bootstrap, historical documentation or existing scope exclusion. Update the published implementation plan when applying the migration.

## Acceptance checks

- **Discovery and routing.** Installed WF discovers one `github` skill. Each intent loads its selected tactic and runs from an unrelated CWD. Missing capability fails before dependent mutations. Connector-only publication and offline Design still follow their respective routes.
- **Local Git.** Exercise branch collisions, stale refs, normal pushes and pinned `ccode` history. Exercise worktree interruption, wrong repository/token, dirty and locked paths, legacy records and verified removal. Confirm only authorized paths and refs change.
- **Issue and PR writes.** Exercise cross-repo tracker/source routing, duplicate spec detection, paginated graphs, artifact round trips, lost create responses, failed parent links, and idempotent comment upserts. Verify draft PR text and manual edits survive retries. Verify baseline labels are preserved, Wayfinder keeps body blockers, and offline runs make zero remote calls.
- **Review and evidence.** Exercise fork PRs, changed head/base, incomplete comments, exact approved HITL text, marker ownership and resolved-thread read-back. Preserve the current stop on truncated nested comments until complete paging is proven. Verify closure/checkpoint order and that check absence never counts as a pass.
- **Repository checks.** Migrate focused worktree, Implement Spec, Review discussion, Design and installer tests. Add regressions for missing shared behaviors, especially partial writes and the installed entry point. Stage new tests before running `python3 .github/scripts/run-python-tests.py --unit-only`, which uses Git discovery.
