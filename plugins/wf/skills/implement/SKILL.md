---
name: implement
description: >-
  Implement a GitHub spec or plan through a routed ticket graph, delivering tickets sequentially or in parallel into one draft PR with chore cleanup and a handoff. Use for 'implement this spec', 'build plan.md', or delivering a spec's sub-issues end to end.
---

# Implement Spec

Orchestrate a routed ticket graph into one integration branch and a draft PR when changes are needed. Run steps in order; load each linked reference only when its step is reached, never ahead.

## Inputs

- GitHub spec issue URL `https://github.com/OWNER/REPO/issues/NUMBER`, plan file path, or inline plan/description. Native sub-issues are **tickets**; native blockers form the **ticket graph**.
- Spec routing: `repo:target:<owner/repo>` and `repo:base:<branch>`; use source-root `GLOSSARY.md` vocabulary when present.
- Harness: run from `HARNESS_ROOT` (a git checkout). Either it holds the source repository's primary checkout at `HARNESS_ROOT/workspace/<REPO>` (`origin` = the source repository; `workspace/` git-ignored), or it is itself the source repository's primary checkout (single-repo: `SOURCE_ROOT` = `HARNESS_ROOT`; run and evidence dirs go under git-ignored `HARNESS_ROOT/workspace/`, else beside `HARNESS_ROOT`). Neither → `preflight` exits `2`; report and stop.
- `mode`: `sequential` (default, recommended) | `parallel` (experimental; use only when asked).
- `max-parallel=<positive integer>`: parallel only; default 3. Scheduling always follows the ticket graph.
- Optional explicit resume with the absolute prior `RUN_DIR`. Reuse its recorded routing, mode, and base after verification.

## GitHub operations

*Load `github` skill for platform specs, tickets, and issues* using Specs and tickets. *Load `git` skill for branch naming, commit messages, and worktree lifecycle*. Resolve `GH_TOOL` = `python3 <installed github skill directory>/scripts/github.py` and `GIT_TOOL` = `python3 <installed git skill directory>/scripts/git.py` before changing into a worktree. Only the orchestrator and planner call `GH_TOOL`. JSON on stdout; exit `0` ok · `1` tool failure · `2` invalid input/routing · `3` read-back problems. Non-zero → report error and stop dependent work.

| Intent | Command |
|---|---|
| Validate an existing spec or resolved plan; use `--pin-base --integration-branch H` once on a new run to fetch the exact `BASE_COMMIT` | `GH_TOOL spec preflight --spec REF --mode MODE` or `GH_TOOL spec preflight --source-repository R --base-branch B --initiative-id I --mode MODE` |
| Atomically save publication progress | `GH_TOOL run checkpoint --run-dir RUN_DIR --input FILE` |
| Create spec from plan/description | `GH_TOOL spec create --source-repository R --base-branch B --initiative-id I --summary S --body-file F --source-note N` |
| Read spec, tickets, comments, blockers; frontier | `GH_TOOL graph read --spec REF --out RUN_DIR` |
| Recompute effective graph/frontier | `GH_TOOL graph frontier --graph RUN_DIR/graph.json --planner RUN_DIR/planner.json --out RUN_DIR/effective-graph.json --done REF…` |
| Create and link ticket (planner) | `GH_TOOL ticket create --spec REF --title T --body-file F` |
| Blocker edges, edit body (planner) | `GH_TOOL issue block REF --by REF…` · `GH_TOOL issue edit-body REF --body-file F` |
| Ticket evidence comment | `GH_TOOL issue comment REF --body-file F --run-id ID` |
| Close implemented ticket | `GH_TOOL issue close REF --run-id ID --evidence-comment N` |
| Publish or update draft PR | `GH_TOOL pr publish --source-repository R --base B --head H --title T --initiative-id I --rationale-file F --changes-file F --evidence-file F --refs REF…` |
| Split PR diff per file (chore) | `GH_TOOL pr diff-split --pr URL` |
| Read back PR | `GH_TOOL pr read --source-repository R --head H --initiative-id I --expect-refs REF…` |

`REF…` = one or more space-separated values after one flag (`--done A B`); repeating the flag (`--done A --done B`) also works.

- Tracker repository = the spec's. Source repository = exactly one `repo:target:` label; base = exactly one `repo:base:` label; `INITIATIVE_ID` = spec title prefix before the first `:`. Missing or conflicting routing → resolve explicitly before writes (`--source-repository`/`--base-branch` only for a user-confirmed older unlabeled spec).
- Track every issue as `OWNER/REPO#NUMBER` in its owning repository; bare references inherit the containing issue's repository; stop on ambiguity. Tickets may live outside the tracker.
- Empty or 404 reads are failures, never an empty graph. Text relationships only when native sub-issues/blockers are confirmed unavailable; report that mode.
- Run-local map: ticket identity, owner, blockers, status, planner-selected implementer model/effort, integrated commit, validation evidence; the integration worktree/branch once and, in parallel mode, each ticket's. Only verified completion evidence can satisfy a blocker. Keep tracker state separate from Git evidence.
- Body files live outside the repository; remove only those this run created.

## Implementer model routing

Resolve the newest available, runtime-supported Claude Sonnet model with **high** reasoning and Claude Opus model with **medium** reasoning to exact identifiers before agent launches (currently `claude-sonnet-5.5` and `claude-opus-5.5`). `latest` is a preference, not a model alias; do not invent identifiers. Pass valid candidate pairs to the planner.

Validate this run's planner `tickets[].implementer` pair against supplied candidates before launch; preserve it for ordinary rework. Evidence of capability mismatch → *Targeted replanning*, never silent substitution or changing a running agent. Missing, malformed, or unavailable selection → stop/report.

Evaluate Sonnet/high and Opus/medium defaults on comparable tasks; do not treat them as universal rankings. Save every ticket attempt's actual model/effort, selection/reassignment reason, rework, and validation outcome in `RUN_DIR/model-outcomes.json`; record time/cost only when observed. Reassignment preserves the rework cap.

## Workflow

1. Detect input type, then prepare input. Validate `mode` and `MAX_PARALLEL` before creating any branch or worktree or writing to the tracker. Check required runtime capabilities (delegation, planner and implementer model availability, and background execution for parallel) before tracker writes.
   → A: Plan file or inline description → load [breakdown.md](./references/breakdown.md); run *Prepare Plan*. Keep its pinned base and continue as B with its read-back spec.
   → B: GitHub spec issue → `GH_TOOL spec preflight --spec URL --mode MODE` with the supplied worker cap, if any. For a new spec run, *run `git` skill for verified branch naming using Branches* with the work intent and summary from the read-back spec. Verify ref availability in the resolved source repo. Repeat preflight with `--pin-base --integration-branch H` and require matching routing, spec title, and checkout. If A already pinned the base, retain its branch and SHA. Use the returned roots, routing, initiative, and run directory. For explicit resume, use the recorded branch and run path and load [publication.md](./references/publication.md#resume-publication); reconcile the run before any new write or launch. Then `GH_TOOL graph read`. Existing sub-issues → reuse that graph; launch the planner in `analyze` mode (read-only; **MUST NOT** create tickets). Zero sub-issues → load [breakdown.md](./references/breakdown.md) if not loaded; run *Breakdown Initiative* with planner `breakdown` mode.
   → Unsupported or ambiguous input: ask for valid input; stop.

   Launch planner (initially for `breakdown` or `analyze`; later only per *Targeted replanning*) → [planner.md](./agents/planner.md) subagent from `SOURCE_ROOT`:
   refs `breakdown` only for `breakdown` mode, none for `analyze` · `claude-opus-5.5` high reasoning · rework none.
   Before: require the pinned `BASE_COMMIT` (or the reconciled resume baseline) and validated implementer candidates per *Implementer model routing*; create `NOTES_DIR` = `RUN_DIR/notes` outside the repository; `RUN_DIR/spec.json` exists from `graph read`. Done when checkout and base match routing.

   | Placeholder | Value |
   |---|---|
   | `{{operation}}` | `breakdown` for zero sub-issues; `analyze` for existing sub-issues |
   | `{{ghTool}}` | `GH_TOOL` (absolute) |
   | `{{specRef}}` | spec `OWNER/REPO#NUMBER` |
   | `{{specFile}}` | `RUN_DIR/spec.json` |
   | `{{implementationDetails}}` | plan path or `None` |
   | `{{harnessRoot}}` | `HARNESS_ROOT` |
   | `{{sourceRoot}}` | `SOURCE_ROOT` initially; read-only integration worktree for targeted reanalysis |
   | `{{baseCommit}}` | `BASE_COMMIT` initially; recorded integration tip for targeted reanalysis |
   | `{{notesDir}}` | `NOTES_DIR` |
   | `{{specArtifactsDir}}` | `RUN_DIR/artifacts` (spec issue artifacts and `index.json` from `graph read`) |
   | `{{implementerModels}}` | Exact available Sonnet/high and Opus/medium model/effort candidates |
   | `{{analysisContext}}` | `None` initially; absolute evidence/context pointer under `NOTES_DIR` for targeted reanalysis |

   Verify: in `breakdown` mode follow *Breakdown Initiative* publication checks; in `analyze` mode require `created: []` and no ticket writes. For both, require matching `result.specRef`, validate each `tickets[].implementer` against supplied candidates, and save the full completed JSON envelope as `RUN_DIR/planner.json`; retain recommendations in the run-local map. Record actual planner model/effort or unavailable-model failure.
   → `failed`, invalid JSON, missing ticket recommendations, or incomplete GitHub operations: report actual partial state; stop; never claim success.

2. Re-run `GH_TOOL graph read --spec REF --out RUN_DIR` after planner completion: save native graph, spec, tickets, comments, blockers, parents under `RUN_DIR`; retain explicit `OWNER/REPO#NUMBER` identities. Run *Effective graph* before validation or selection.

3. Validate the effective graph: reject cycles (name them) and resolve routing conflicts before implementation writes. Apply *Completion evidence* to closed and resumed tickets and to internal or external blockers. Refresh the effective frontier. Mark unresolved tickets and their affected chains blocked or deferred, record the exact scope or dependency gap, and continue independent eligible work. Record each ticket's identity, owner, status, scope, blockers, and evidence in the run-local map. Show the *Graph report* after Breakdown Initiative and in parallel mode.

4. Explore implementation scope and test seams as needed; save shared notes under `RUN_DIR/notes` and pass pointers. Use the effective graph plus planner footprints, conflicts, and per-ticket model recommendations; planner conflicts without `kind` are `file` only when evidence names a path, otherwise `soft`. Bound every runnable ticket's scope and validate its preferred implementer per *Implementer model routing* before selection.

5. Execute selected mode:
   - Create the integration branch and worktree per [Integration setup](./references/worktrees.md#integration-setup), or reuse the verified resume worktree.
   - Load [publication.md](./references/publication.md) if needed and initialize or reconcile the publication checkpoint before the first worker launch. Both modes use the shared *Ticket publication* procedure.
   - Load **only** the selected mode reference:
     → C: Sequential → Run [Sequential Implementation](./references/sequential.md#sequential-implementation).
     → D: Parallel → Run [Parallel Implementation](./references/parallel.md#parallel-implementation); isolate tickets per [Ticket worktrees](./references/worktrees.md#ticket-worktrees).

   Launch implementer → installed `wf:codey` as a named subagent per ticket in its assigned worktree. If the runtime cannot resolve the named agent, launch `general-purpose` with *Implementer fallback*. A failed or invalid result goes through rework, not fallback. If delegation is unavailable, report the blocker.
   refs none · validated per-ticket preferred model/effort from *Implementer model routing* · one fresh per ticket; C foreground, settle before next; D background, ≤ `MAX_PARALLEL` in flight · rework same agent and model/effort, ≤2 rounds across any explicit reassignment per *Targeted replanning*.

   Before each initial launch or rework in either mode, **MUST** confirm concrete acceptance outcomes, required producer contracts, and feasible verification from ticket/source evidence. Material requirement/contract gaps or missing verification criteria → block the ticket and dependants in the run-local map, record the exact gap, and withhold launch even if dependency-ready. Resolve evidence gaps through *Targeted replanning*; resolve requirement/contract decisions explicitly. Continue independent eligible work. Leave routine implementation choices to the implementer; handle infrastructure-only gaps per *Implementation focus*. Rationale: dependency-ready does not mean ready to implement.

   For either worker, select and validate the workspace, branch or caller-managed rebase state, HEAD, and index. Instruct the worker to enter and verify the absolute assigned worktree before repository work. Set it as the runtime working directory where supported. Ask the worker to implement the assigned ticket and return the workflow ticket JSON result. Capture the integration HEAD at each launch for history and record the worker's starting HEAD and index separately. Keep `@prevHead` as the original ticket start and track the validated ticket base separately if rebased.

   | Handoff field | Sequential | Parallel |
   |---|---|---|
   | `ticketRef` | `OWNER/REPO#NUMBER` | same |
   | `ticketFile` | the ticket’s `file` from the effective graph | same |
   | `baseCommit` | `BASE_COMMIT` | same |
   | `historyTip` | captured integration HEAD | same |
   | `specArtifactsDir` | `RUN_DIR/artifacts` | same |

   Capture `result.gotchas` on every attempt, including failures. Require an array of observed, reusable findings (empty is valid). Attribute findings to the ticket, agent and attempt in the output.

   *Run `git` skill for verified commit messages using Commits* for the WF ticket subject format and body requirements. Explicitly ask the worker to commit in both modes using those instructions. Allow one new local ticket commit if none exists. For rework on an identified unpublished ticket commit, authorize amendment of that exact SHA only. During a caller-managed rebase conflict, request edit-only mode and keep staging and rebase continuation with the orchestrator.

   Validate the actual Git state before accepting the result. In commit mode, require that `result.commit` equals `HEAD`, the branch is as expected, the worktree is clean, and there is exactly one ticket commit directly above its recorded base. Check its subject and inspect its full diff against the ticket and `result.files`. When `result.commit` is null, require a verified no-change result, the starting HEAD and a clean worktree, then apply *Completion evidence*. In edit-only rework, require the original HEAD, branch or rebase state, and index to be intact and inspect the edits. Unexpected Git state or unrelated staged changes → preserve them, block the ticket, and never publish it. If this affects the integration worktree, return a blocked handoff before another launch or push. Apply the *Implementation focus* evidence gate to `result.verification` in every case. Require executed checks and results, including skipped infrastructure checks and errors. Thin evidence → run cheap confirmations before accepting the result.
   → Evidence invalidates planning assumptions or model capability: run *Targeted replanning* before ordinary rework; preserve original `@prevHead` and work pointers.
   → Other invalid JSON, `failed`, missing evidence, or out-of-scope edits: rework; recheck after each round.
   → Still invalid after 2 rounds: preserve branch/worktree and report the blocker; stop advancing that ticket. If the integration worktree contains an unverified commit or unexpected Git state, stop the sequential run before any further launches or pushes. Return a blocked handoff with the preserved state.
   For verified no-change, record the exact checked SHA and criterion-to-check evidence. Use `base-verified` for evidence on `BASE_COMMIT` and `no-change-verified` for evidence on a validated integration tip. Preserve the tracker state and skip commit integration and publication. Integrate verified commits per the mode reference and publish them via *Ticket publication*.

6. **Frontier check.** Refresh `graph read` and recompute *Effective graph* after verified publication or no-change evidence and before selection. Revalidate *Completion evidence* and check *Targeted replanning* triggers when source or tracker evidence changes. If no ticket is eligible and workers remain in flight, wait for a result. If unresolved tickets remain and no worker can make progress, report each exact blocker and write a `blocked` handoff without chore. Preserve work and any draft PR.
   If the graph is nonempty, every in-scope ticket is verified on `BASE_COMMIT`, no unresolved tickets remain, and no changes were needed, write an `already-satisfied` handoff and proceed to Output without chore or PR operations. A zero-ticket graph is incomplete. Only a verified draft PR with integrated changes proceeds to chore.

7. Launch chore → [chore.md](./agents/chore.md) subagent in `WORKTREE_PATH`:
   refs `fetch-diff` · `claude-opus-5.5` medium reasoning, fallback `gpt-6.1-sol` medium when rejected · rework none.
   Before: *run `git` skill for verified commit messages using Commits* for a conventional `chore` subject format. Load [fetch-diff.md](./references/fetch-diff.md); split PR diff into `@diffDir`; record `@prevHead` from the integration worktree. Instruct Chore to enter and verify that worktree before repository work and explicitly authorize one local cleanup commit after verification.

   | Placeholder | Value |
   |---|---|
   | `{{featureBranch}}` | `INTEGRATION_BRANCH` |
   | `{{pullRequestUrl}}` | PR URL |
   | `{{worktreePath}}` | `WORKTREE_PATH` |
   | `{{diffDir}}` | `@diffDir` |
   | `{{baseCommit}}` | `BASE_COMMIT` |
   | `{{historyTip}}` | `@prevHead` |
   | `{{commitSubjectPrefix}}` | `chore: ` |

   Verify: `result.commit` equals `HEAD`, exactly one commit since `@prevHead`, subject match, clean worktree, checks reported. A verified no-change result must report null and leave `HEAD` at `@prevHead`. Record actual model/effort or unavailable-model failure.
   After verified success: checkpoint the chore result and SHA before pushing, or reconcile an already verified chore on resume. Confirm the pushed head, remove `@diffDir` if created, and report out-of-scope findings without acting.
   → Missing, failed, or invalid result: record the chore blocker, preserve the worktree, remove `@diffDir`, and continue to the blocked handoff without pushing.
   Done when chore changes are committed (one `chore: ` commit, or none needed), pushed to `INTEGRATION_BRANCH`, remote head equals `HEAD`, and the worktree is clean.

8. Run *Publication verification* ([publication.md](./references/publication.md)), refresh spec/ticket pointers, and write *Implementation handoff*. Preserve the integration worktree, branch, draft PR, and run/evidence directories; keep the spec open. Done when the handoff matches the read-back remote state. Publication failure or unresolved tickets → `blocked`; never report ready from a PR URL alone.

9. Report per *Output*; check *Completion criteria*. For `ready`, report implementation complete with verification and review pending. For `already-satisfied`, report the pinned SHA and evidence. For `blocked`, report partial implementation and blockers. Factory mode owns post-implementation verification, review, final cleanup, and spec closure.

## Effective graph

Persist the completed planner envelope before computing `GH_TOOL graph frontier --graph RUN_DIR/graph.json --planner RUN_DIR/planner.json --out RUN_DIR/effective-graph.json --done REF…` (omit `--done` when none). The tool unions native and inferred blockers, validates spec identity, full ticket coverage, blocker identities and acyclicity, and recomputes readiness and transitive HITL deferral. Keep `graph.json` as the native snapshot; use `effective-graph.json` for scheduling, validation, reports, and handoff. **MUST NOT** replace inferred edges with a later native refresh, even if simpler. Rationale: read-only analysis cannot publish those edges. Missing/stale/invalid planner coverage → stop affected launches and reanalyze; never fall back to native-only readiness.

## Completion evidence

- Tracker closure alone gives no completion proof. For a ticket with a recorded verified implementation, match the SHA and evidence to the qualified ticket and confirm it is an ancestor of `BASE_COMMIT` or the validated integration tip with `git merge-base --is-ancestor`. Reconcile any pending publication before counting a current-run commit as done. If no reliable implementation SHA exists, prove the required behavior with acceptance checks on the pinned base or validated integration tip. Record the exact checked SHA and evidence pointers.
- Supply only qualified refs with this evidence as `--done`, including verified external blockers. Keep cancelled/duplicate issues and open HITL tickets unresolved until tracker evidence changes. Closed HITL blockers require verified evidence in the base. Track unverified closed tickets without delegating them and continue independent eligible work.
- For parallel no-change results, compare the worker's starting SHA and current validated integration tip. Rerun the affected acceptance checks on the current tip if intervening changes could affect them. If evidence is insufficient or stale, withhold completion and report the exact gap.

## Targeted replanning

Reanalyze only evidence-invalidated dependencies, contracts, footprints, verification seams, scope boundaries, or model capability assumptions; routine commits alone do not trigger it. Pause affected launches; let in-flight agents settle, preserve work/reservations, and validate results against updated prerequisites before integration. Save evidence, affected unfinished refs, approved scope, integration tip, prior planner path, and completed/in-flight state under `NOTES_DIR`; launch *Launch planner* in read-only `analyze` mode with `{{analysisContext}}` pointing there and source/base pointers at that tip.

Merge affected recommendations into the full persisted planner envelope; retain unaffected entries and valid inferred edges, and remove inferred edges only with explicit invalidating evidence. Rerun *Effective graph*, conflicts, coverage, model validation, and HITL propagation before resuming. Preserve ticket identities, native blockers, completed work, and approved scope; ticket rewrites, new scope, or unknown external blockers require explicit resolution. A cycle or unresolved gap blocks affected work. Done when every affected unfinished ticket has validated prerequisites and a feasible verification contract.

Reassign a model only with settled-agent evidence, the planner's validated choice/reason, preserved work pointers, and remaining original rework budget. Launch a fresh replacement for that ticket with its preserved state and original `@prevHead`. Never replace a running agent, discard changes to obtain a clean checkout, or restart the rework count.

## Implementer fallback

For `general-purpose`, give the same assigned worktree, Git range, commit instructions, and validated model/effort. Include this worker contract in the delegation:

- Enter and verify the assigned worktree before repository work. Infer scope and acceptance criteria from the supplied ticket snapshot and comments. Read required references in full and use the artifact index for relevant attachments. Report missing required sources with their path and error. Keep handoff files read-only. Never launch subagents, switch branches, manage worktrees, run a rebase, publish, or interact with GitHub.
- Before edits, *run `git` skill to read commit history* using the Commits tactic on the pinned `baseCommit..historyTip` to read SHAs, subjects, and bodies, oldest first. Keep only subjects matching `^ccode\([^)]*\):` (`ccode(...):`). Empty matches are valid. An unreadable range → return `failed` with the refs and error.
- Implement only this ticket. Use repository conventions and focused risk-based checks, including a failing reproduction before a bug fix and test-first checks for complex logic or a changed public contract. Preserve work and return `failed` with `planning invalidated:` and evidence when acceptance, dependency, scope, or verification assumptions no longer hold.
- For each remaining material integration gap, *run `testing-integrations` skill to pick the minimal seam for a DB or cloud component test or a functional slice*. Pass changed behavior, boundary, gap, and launch workspace. Follow its fastest adequate configuration, narrowest filter, documented test directory within the workspace, and safety gates. If unavailable, use the repository's documented equivalent and safety rules.
- Follow the *Implementation focus* evidence gate. Rerun affected checks on the final tree and report commands, executed counts, outcomes, and risks. Leave edits unstaged and uncommitted in edit-only mode. In commit mode, stop before edits if there are pre-existing staged changes. After verification, stage only ticket-owned changes and make one local commit with the supplied subject and body instructions. Amend only the explicitly authorized unpublished SHA at HEAD, with no active rebase or merge. If fresh verification confirms that commit and no edits are needed, return its SHA without amending. Create no empty commit. Preserve work and report failures. Return exactly one JSON object:

| Field | Content |
|---|---|
| `status` | `completed` when the evidence gate passes, otherwise `failed`. |
| `result.summary` | `completed` only. One-line outcome. |
| `result.files` | `completed` only. Changed paths relative to the assigned workspace. In commit mode, report the paths in the full ticket commit. `[]` for verified no change. |
| `result.commit` | `completed` in commit mode only. Full commit SHA, or `null` for verified no change. Omit in edit-only mode. |
| `result.verification` | `completed` only. Criteria mapped to observed evidence, commands and counts where run, per-check status, and remaining risks. |
| `result.reason` | `failed` only. Blocker or failure with any observed evidence. |
| `result.gotchas` | Both outcomes. Array of observed reusable findings. `[]` when none. |

```json
{"status":"completed","result":{"summary":"<one line>","files":["<changed path relative to launch directory>"],"verification":"<strategy, criterion-to-check evidence, exact commands and counts, outcomes and risks>","gotchas":["<observed reusable finding>"]}}
```

```json
{"status":"failed","result":{"reason":"<why it failed and any observed evidence>","gotchas":[]}}
```

## Subagent launch contract

**Only this skill launches agents**, including background calls and rework, and controls scheduling, integration, publication, and ticket closure; every launch and rework follows this contract. Agent bodies and references return control here; they never create subagents.

- Resolve `AGENTS_ROOT=<skill base directory>/agents` and `REFERENCES_ROOT=<skill base directory>/references` as absolute paths before changing into a worktree; never from caller CWD.
- Validate every manifest file and any local planner or chore body are readable. Missing/unreadable → stop/report exact path. Fill every placeholder in the local bodies. Resolve the named implementer via the runtime, not `AGENTS_ROOT`.
- Attach `referencesRoot`, `referenceManifest`, and the step's `refs` as absolute `requiredReferences` to every launch, including the named implementer and fallback. Pass pointers only per *Pointer handoff*.
- Supply tools, permissions, and model settings at launch, never in agent frontmatter. Agents never gain scheduling, publishing, closure, merging, or cross-ticket authority.
- Apply worker-only runtime restrictions to `wf:codey` and `general-purpose` on every launch and rework where supported. Limit writes to the selected workspace, its Git metadata needed for the authorized local commit, and approved test scratch. Keep handoff files read-only. Allow needed build/test and read-only inspection commands. Allow staging and a local commit only in commit mode, and amendment only when explicitly authorized. Deny other Git mutations, GitHub access, publication, and delegation. If the runtime cannot scope a restriction to the worker, record the missing control and retain the worker instructions and post-run Git-state checks.

`referenceManifest` lists every `.md` file under `REFERENCES_ROOT`, keyed by its relative path without `.md`: `breakdown` → `REFERENCES_ROOT/breakdown.md`, `fetch-diff` → `REFERENCES_ROOT/fetch-diff.md`.

Launch line legend: `refs` = `requiredReferences` (manifest keys); pass only the listed files, never a whole folder; run style defaults to foreground, one fresh agent; `rework` names who reworks and the round cap.

## Constraints

- **GitHub:** **MUST** perform every GitHub issue, PR, label, and graph operation through `GH_TOOL` per *GitHub operations*, never raw `gh`; load [publication.md](./references/publication.md) at step 5. Missing/unreadable reference or `GH_TOOL` → stop/report.
- **Repository identity:** preserve each issue's `OWNER/REPO#NUMBER`; route issue reads/comments/closures to its owning repository, and Git/implementation/PR operations only to the resolved source repository. Resolve ambiguity before writes; **MUST NOT** infer ownership from checkout, PR repository, or matching issue number.
- **HITL:** re-read labels at selection. Skip `hitl` tickets without implementation, delegation, comments, or closure. An open skipped ticket never satisfies dependants; only closed tickets with results verified in the integration base do. Record skipped tickets separately from implemented coverage; keep the spec open while any remain open.
- **One ticket = one subagent:** fresh implementer per ticket; sequential waits for each result, parallel caps concurrency. Ordinary rework uses that ticket's existing agent, at most two rounds; an explicit settled-agent capability reassignment follows *Targeted replanning* within the same total cap. **MUST NOT** implement inline, batch tickets, or reuse agents across tickets. Missing subagents → stop/report.
- **Implementation focus:** `completed` requires passing evidence on the final tree or observed proof of existing behavior for every material requirement. For environment/network/Docker/port/registry/external-service failure, make at most one quick confirmation. Record the unavailable check and error. A substitute check counts only if it passes and exercises the same material risk. An uncovered material requirement or code-caused failure blocks completion. **MUST NOT** troubleshoot infrastructure during implementation.
- **Draft-only:** PR stays draft; **MUST NOT** merge or mark ready (`gh pr ready`). User controls readiness.
- **Pointer handoff:** save reusable spec, ticket, and comment reads under `RUN_DIR` (`graph read` writes spec and ticket files). Refresh files before each launch that uses them. Pass paths, `OWNER/REPO#NUMBER` refs, and pinned Git ranges. Workers read commit history directly from their worktree. **MUST NOT** inline bodies, comments, or logs into prompts. Missing/unreadable input → agents return `failed` with the path or refs and error. The orchestrator restores the required input before rework.
- **Worktree isolation:** **MUST** follow [worktrees.md](./references/worktrees.md) for every worktree create, write, and ticket worktree removal; never reset or discard existing work.

## Graph report

Table of ticket, blocked by (`none` = explicit root), paths, conflicts with kind (`file`/`soft`) and a per-ticket conflict count; then ready frontier, critical path, deferred tickets with reason. Every node listed, including deferred tickets' blocker edges. Then spec artifact count (length of `graph.spec.artifacts`) or `artifacts_note`, and design sketch coverage from the planner notes when a sketch exists.

## Implementation handoff

Write data-only `RUN_DIR/implementation-handoff.json`; pass its absolute path, never internal scripts/references. Use `null` for unavailable scalar data and `[]` for no entries; missing required state makes `status` `blocked`. An `already-satisfied` handoff intentionally has null PR and pushed-head fields, no publication verification, and no chore needed.

| Field | Content |
|---|---|
| `status`, `blockers` | `ready` after integrated changes and verified publication/chore; `already-satisfied` for a verified zero-change run on base; otherwise `blocked` plus reasons. |
| `specRef`, `specUrl`, `sourceRepository`, `trackerRepository`, `prUrl` | Qualified spec identity and URLs; explicit source/tracker `owner/repo`. |
| `initiativeId`, `remote`, `integrationBranch`, `baseBranch`, `baseCommit`, `headCommit` | Validated routing, verified source remote, base SHA, final pushed SHA. |
| `harnessRoot`, `sourceRoot`, `worktreesRoot`, `worktreePath`, `runDir`, `evidenceRoot` | Absolute paths resolved once; roots outside the integration worktree. |
| `specFile`, `graphFile`, `plannerFile`, `modelOutcomesFile` | Refreshed absolute data pointers. `graphFile` is `effective-graph.json`. Keep the planner envelope, model outcomes, and spec/ticket titles, bodies, and comments. |
| `tickets` | Every graph ticket: qualified `ref`, `file`, integrated `commit` or null, `status` (`integrated`, `base-verified`, `no-change-verified`, `deferred`, `blocked`), `verifiedAt` exact evidence SHA or null, `evidence` pointers, `evidenceCommentId`, observed `closure` (`completed`, `open`, or `closed-other`); empty only with an explicit blocker. |
| `chore` | `status` (`verified`, `none-needed`, `failed`), `commits`, actual `model`, `effort`, validation `evidence` pointers (including skipped checks/errors). |
| `publication` | Read-back `verified` boolean, `draft` boolean, `checks` (`passed`, `pending`, `failed`, `absent`), metadata/coverage and posting failures in `problems`. |

```json
{"status":"ready","blockers":[],"specRef":"tracker/repo#1","specUrl":"https://github.com/tracker/repo/issues/1","sourceRepository":"owner/repo","trackerRepository":"tracker/repo","prUrl":"https://github.com/owner/repo/pull/2","initiativeId":"PAY-12","remote":"origin","integrationBranch":"feat/refunds","baseBranch":"main","baseCommit":"<base SHA>","headCommit":"<pushed SHA>","harnessRoot":"/harness","sourceRoot":"/harness/workspace/repo","worktreesRoot":"/harness/.worktrees/repo","worktreePath":"/harness/.worktrees/repo/refunds","runDir":"/harness/workspace/runs/PAY-12","evidenceRoot":"/harness/workspace/evidence","specFile":"/harness/workspace/runs/PAY-12/spec.json","graphFile":"/harness/workspace/runs/PAY-12/effective-graph.json","plannerFile":"/harness/workspace/runs/PAY-12/planner.json","modelOutcomesFile":"/harness/workspace/runs/PAY-12/model-outcomes.json","tickets":[{"ref":"tracker/repo#3","file":"/harness/workspace/runs/PAY-12/tickets/tracker_repo_3.json","commit":"<ticket SHA>","status":"integrated","verifiedAt":"<ticket SHA>","evidence":["/harness/workspace/runs/PAY-12/ticket-3.md"],"evidenceCommentId":123,"closure":"completed"}],"chore":{"status":"none-needed","commits":[],"model":"<actual model>","effort":"medium","evidence":["/harness/workspace/runs/PAY-12/chore.md"]},"publication":{"verified":true,"draft":true,"checks":"pending","problems":[]}}
```

Failure: same shape, `status: blocked`, concrete `blockers`, partial values preserved, unavailable values `null`; claim publication/closure only after read-back.

## Output

- Breakdown Initiative or parallel mode → first: *Graph report*.
- Spec URL, created tickets, planner model/effort; PR URL/state.
- Per ticket: chosen/actual implementer model/effort, reassignment reasons, attempts/rework, validation outcomes and gotchas by agent/attempt, integrated commit, evidence, closure or blocker; skipped `hitl` tickets and dependants.
- Chore commits and model/effort; skipped infrastructure checks; preserved worktree status; *Implementation handoff* path and status.
- No runnable tickets: report graph and blockers or the verified `already-satisfied` outcome.
- Incomplete: name missing evidence, partial GitHub writes, preserved work; distinguish unverified state from read-back success.

## Gotchas

- References are grouped by phase; a cited heading (*X*) resolves only within files already loaded at that step. Load a reference when its step links it, read it to end of file, and continue truncated reads by range; a partial read counts as not loaded.
- A closed issue may be cancelled or duplicate rather than implemented; verify the result exists in the integration base or branch. On resume, apply *Completion evidence* and reconcile the recorded publication before treating prior work as done.
- A ticket commit is not complete until the cumulative integration result passes relevant checks.
- Treat external blockers separately from run-local integrated work; never bypass unresolved external dependencies.

## Completion criteria

- `already-satisfied`: every in-scope ticket has evidence at the pinned base, with no unresolved work. Report the observed tracker state and the evidence pointers.
- For runs with changes, each integrated ticket has exactly one commit backed by its implementer's verified local ticket commit, an evidence comment, and read-back `completed` closure in its owning repository. No skipped `hitl` ticket was implemented, commented on, closed, or counted as implemented coverage.
- For runs with changes, source repository/base match routing; PR title prefix and first body line carry the bracketed `INITIATIVE_ID` under the shared convention; every implemented ticket is covered; PR is draft; pending/failed checks are reported accurately.
- For runs with changes, chore result and actual model/effort recorded; valid chore changes committed and pushed. A failed or missing result is a handoff blocker, not “none needed.”
- Handoff pointers readable and refreshed; existing branch, worktree, and run/evidence directories preserved; spec open and referenced without a closing keyword. No app verifier or code review ran here.
- No reference-loading failure ignored; subagents received pointers, not inlined task data; user work intact.
- Completeness sweep, last: re-read the request; map every spec requirement/ticket to code, tests, docs, configuration, and relevant failure/compatibility evidence. Resolve gaps or report explicit deferrals before declaring completion.
