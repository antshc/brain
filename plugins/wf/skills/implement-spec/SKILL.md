---
name: implement-spec
description: Implements a GitHub spec or plan through a routed ticket graph; orchestrates sequential or parallel delivery and chore into one draft PR with a post-implementation handoff.
---

# Implement Spec

Orchestrate a routed ticket graph into one integration branch and draft PR. Run steps in order; load each linked reference only when its step is reached, never ahead.

## Inputs

- GitHub spec issue URL `https://github.com/OWNER/REPO/issues/NUMBER`, plan file path, or inline plan/description. Native sub-issues are **tickets**; native blockers form the **ticket graph**.
- Spec routing: `repo:target:<owner/repo>` and `repo:base:<branch>`; use source-root `GLOSSARY.md` vocabulary when present.
- Harness: run from `HARNESS_ROOT` (a git checkout). Either it holds the source repository's primary checkout at `HARNESS_ROOT/workspace/<REPO>` (`origin` = the source repository; `workspace/` git-ignored), or it is itself the source repository's primary checkout (single-repo: `SOURCE_ROOT` = `HARNESS_ROOT`; run and evidence dirs go under git-ignored `HARNESS_ROOT/workspace/`, else beside `HARNESS_ROOT`). Neither → `preflight` exits `2`; report and stop.
- `mode`: `sequential` (default, recommended) | `parallel` (experimental; use only when asked).
- `max-parallel=<positive integer>`: parallel only; default 3. Scheduling always follows the ticket graph.

## GitHub operations

`GH_TOOL` = `python3 <skill base directory>/scripts/spec_gh.py`, resolved as an absolute path before changing into a worktree. Only the orchestrator and planner call it. JSON on stdout; exit `0` ok · `1` GitHub/tool failure · `2` invalid input or unresolved routing · `3` read-back `problems`. Non-zero → report the error, stop dependent work, never claim publication, passing checks, or closure.

| Intent | Command |
|---|---|
| Prerequisites, routing, `INITIATIVE_ID`, `INTEGRATION_BRANCH`, `SOURCE_ROOT`, `RUN_DIR`, `EVIDENCE_ROOT` (no fetch; no `BASE_COMMIT`) | `GH_TOOL preflight --spec REF` |
| Create spec from plan/description | `GH_TOOL spec create --source-repository R --base-branch B --initiative-id I --summary S --body-file F --source-note N` |
| Read spec, tickets, comments, blockers; frontier | `GH_TOOL graph read --spec REF --out RUN_DIR` |
| Recompute effective graph/frontier | `GH_TOOL graph frontier --graph RUN_DIR/graph.json --planner RUN_DIR/planner.json --out RUN_DIR/effective-graph.json --done REF…` |
| Create and link ticket (planner) | `GH_TOOL ticket create --spec REF --title T --body-file F` |
| Blocker edges, edit body (planner) | `GH_TOOL issue block REF --by REF…` · `GH_TOOL issue edit-body REF --body-file F` |
| Ticket evidence comment | `GH_TOOL issue comment REF --body-file F` |
| Close implemented ticket | `GH_TOOL issue close REF --commit SHA --branch B --pr URL` |
| Publish or update draft PR | `GH_TOOL pr publish --source-repository R --base B --head H --title T --initiative-id I --rationale-file F --closes REF… --refs REF…` |
| Split PR diff per file (chore) | `GH_TOOL pr diff-split --pr URL` |
| Read back PR | `GH_TOOL pr read --source-repository R --head H --initiative-id I --expect-closes REF…` |

`REF…` = one or more space-separated values after one flag (`--done A B`); repeating the flag (`--done A --done B`) also works.

- Tracker repository = the spec's. Source repository = exactly one `repo:target:` label; base = exactly one `repo:base:` label; `INITIATIVE_ID` = spec title prefix before the first `:`. Missing or conflicting routing → resolve explicitly before writes (`--source-repository`/`--base-branch` only for a user-confirmed older unlabeled spec).
- Track every issue as `OWNER/REPO#NUMBER` in its owning repository; bare references inherit the containing issue's repository; stop on ambiguity. Tickets may live outside the tracker.
- Empty or 404 reads are failures, never an empty graph. Text relationships only when native sub-issues/blockers are confirmed unavailable; report that mode.
- Run-local map: ticket identity, owner, blockers, status, planner-selected implementer model/effort, integrated commit, validation evidence; the integration worktree/branch once and, in parallel mode, each ticket's. A ticket closed by this run counts as satisfied; dependants need committed, validated blocker implementations on the integration branch. Never use open-issue counts alone.
- Body files live outside the repository; remove only those this run created.

## Implementer model routing

Resolve the newest available, runtime-supported Claude Sonnet model with **high** reasoning and Claude Opus model with **medium** reasoning to exact identifiers before agent launches (currently `claude-sonnet-5.5` and `claude-opus-5.5`). `latest` is a preference, not a model alias; do not invent identifiers. Pass valid candidate pairs to the planner.

Validate this run's planner `tickets[].implementer` pair against supplied candidates before launch; preserve it for ordinary rework. Evidence of capability mismatch → *Targeted replanning*, never silent substitution or changing a running agent. Missing, malformed, or unavailable selection → stop/report.

Evaluate Sonnet/high and Opus/medium defaults on comparable tasks; do not treat them as universal rankings. Save every ticket attempt's actual model/effort, selection/reassignment reason, rework, and validation outcome in `RUN_DIR/model-outcomes.json`; record time/cost only when observed. Reassignment preserves the rework cap.

## Workflow

1. Detect input type, then prepare input:
   → A: Plan file or inline description → load [breakdown.md](./references/breakdown.md); run *Prepare Plan* (ends with `spec create`), then continue as B.
   → B: GitHub spec issue → `GH_TOOL preflight --spec URL` (`HARNESS_ROOT`, `SOURCE_ROOT`, routing, `INITIATIVE_ID`, `INTEGRATION_BRANCH` = `integration_branch`, `RUN_DIR`), then `GH_TOOL graph read`. Existing sub-issues → reuse that graph; launch the planner in `analyze` mode (read-only; **MUST NOT** create tickets). Zero sub-issues → load [breakdown.md](./references/breakdown.md) if not loaded; run *Breakdown Initiative* with planner `breakdown` mode.
   → Unsupported or ambiguous input: ask for valid input; stop.

   Launch planner (initially for `breakdown` or `analyze`; later only per *Targeted replanning*) → [planner.md](./agents/planner.md) subagent from `SOURCE_ROOT`:
   refs `breakdown` only for `breakdown` mode, none for `analyze` · `claude-opus-5.5` high reasoning · rework none.
   Before: fetch validated `BASE_BRANCH`, record `BASE_COMMIT`; resolve available implementer candidates per *Implementer model routing*; create `NOTES_DIR` = `RUN_DIR/notes` outside the repository; `RUN_DIR/spec.json` exists from `graph read`. Done when checkout and base match routing.

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

3. Validate the effective graph: reject `frontier.cycles` (name them) and tickets without scope; resolve `problems` (routing conflicts) and `frontier.needs_resolution` (cancelled, duplicate, external blockers) before writes; `hitl` tickets and their dependants are `deferred`; verify closed blockers' results exist in `BASE_COMMIT`. Record each ticket's identity, owner, status, scope, blockers, and evidence in the run-local map. Show the *Graph report* after Breakdown Initiative and in parallel mode.

4. Explore implementation scope and test seams as needed; save shared notes under `RUN_DIR/notes` and pass pointers. Use the effective graph plus planner footprints, conflicts, and per-ticket model recommendations; planner conflicts without `kind` are `file` only when evidence names a path, otherwise `soft`. Bound every runnable ticket's scope and validate its preferred implementer per *Implementer model routing* before selection.

5. Execute selected mode:
   - Validate `mode` and `MAX_PARALLEL` before creating any branch or worktree.
   - Create the integration branch and worktree per [Integration setup](./references/worktrees.md#integration-setup).
   - Load [publication.md](./references/publication.md) (both modes; ticket publication, read-back, and closure).
   - Load **only** the selected mode reference:
     → C: Sequential → Run [Sequential Implementation](./references/sequential.md#sequential-implementation).
     → D: Parallel → Run [Parallel Implementation](./references/parallel.md#parallel-implementation); isolate tickets per [Ticket worktrees](./references/worktrees.md#ticket-worktrees).

   Launch implementer → [implementer.md](./agents/implementer.md) subagent per ticket in its worktree:
   refs none · validated per-ticket preferred model/effort from *Implementer model routing* · one fresh per ticket; C foreground, settle before next; D background, ≤ `MAX_PARALLEL` in flight · rework same agent and model/effort, ≤2 rounds across any explicit reassignment per *Targeted replanning*.

   Before each initial launch or rework in either mode, **MUST** confirm concrete acceptance outcomes, required producer contracts, and feasible verification from ticket/source evidence. Material requirement/contract gaps or missing verification criteria → block the ticket and dependants in the run-local map, record the exact gap, and withhold launch even if dependency-ready. Resolve evidence gaps through *Targeted replanning*; resolve requirement/contract decisions explicitly. Continue independent eligible work. Leave routine implementation choices to the implementer; handle infrastructure-only gaps per *Implementation focus*. Rationale: dependency-ready does not mean ready to implement.

   | Placeholder | Sequential | Parallel |
   |---|---|---|
   | `{{worktreePath}}` | `WORKTREE_PATH` | `TICKET_WORKTREE(n)` |
   | `{{featureBranch}}` | `INTEGRATION_BRANCH` | `TICKET_BRANCH(n)` |
   | `{{targetBranch}}` | `BASE_BRANCH` | `INTEGRATION_BRANCH` |
   | `{{ticketRef}}` | `OWNER/REPO#NUMBER` | same |
   | `{{ticketFile}}` | `RUN_DIR/tickets/<OWNER>_<REPO>_<NUMBER>.json` | same |
   | `{{commitsFile}}` | `RUN_DIR/commits/<HEAD sha>.txt` | same (integration log) |
   | `{{commitSubjectPrefix}}` | `ccode(<INITIATIVE_ID> <OWNER/REPO#NUMBER>): ` | same |
   | `{{specArtifactsDir}}` | `RUN_DIR/artifacts` | same |

   Verify in the ticket's worktree: `HEAD` = `result.commit`, exactly one commit since `@prevHead`, subject prefix, clean and on its branch, `result.verification` names executed checks and results including skipped infrastructure checks and errors; thin evidence → run cheap confirmations.
   → Evidence invalidates planning assumptions or model capability: run *Targeted replanning* before ordinary rework; preserve original `@prevHead` and work pointers.
   → Other invalid JSON, `failed`, missing evidence, or mismatched commit: rework; recheck after each round.
   → Still invalid after 2 rounds: preserve branch/worktree and report the blocker; stop advancing that ticket.
   Integrate and publish per the mode reference.

6. **Frontier check.** Refresh `graph read`, then run *Effective graph* after each publication and before selection in both modes; use only its recomputed frontier. Check *Targeted replanning* triggers after each result or changed tracker/source evidence. A blocker is satisfied only when integrated in this run or verified in the base. Unfinished tickets but none ready → report each unready ticket and why (open `hitl`, unresolved external dependency); preserve all work and the draft PR; keep the spec open; write *Implementation handoff* with `status: blocked` and partial state before returning, without chore; post-implementation work cannot start. Never force progress or declare completion.

7. Launch chore → [chore.md](./agents/chore.md) subagent in `WORKTREE_PATH`:
   refs `fetch-diff` · `claude-opus-5.5` medium reasoning, fallback `gpt-6.1-sol` medium when rejected · rework none.
   Before: load [fetch-diff.md](./references/fetch-diff.md); split PR diff into `@diffDir`.

   | Placeholder | Value |
   |---|---|
   | `{{featureBranch}}` | `INTEGRATION_BRANCH` |
   | `{{pullRequestUrl}}` | PR URL |
   | `{{worktreePath}}` | `WORKTREE_PATH` |
   | `{{targetBranch}}` | `BASE_BRANCH` |
   | `{{diffDir}}` | `@diffDir` |
   | `{{commitsFile}}` | `RUN_DIR/commits/<HEAD sha>.txt` |
   | `{{commitSubjectPrefix}}` | `chore(<INITIATIVE_ID>): ` |

   Verify: ≤1 commit since `@prevHead`, subject match, clean, checks reported; record actual model/effort or unavailable-model failure.
   After: push; remove `@diffDir`; report out-of-scope findings without acting.
   → No result or failed: record none/failed; continue.
   Done when chore changes are committed (one `chore(<INITIATIVE_ID>): ` commit, or none needed), pushed to `INTEGRATION_BRANCH`, remote head equals `HEAD`, and the worktree is clean.

8. Run *Publication verification* ([publication.md](./references/publication.md)), refresh spec/ticket pointers, and write *Implementation handoff*. Preserve the integration worktree, branch, draft PR, and run/evidence directories; keep the spec open. Done when the handoff matches the read-back remote state. Publication failure or unresolved tickets → `blocked`; never report ready from a PR URL alone.

9. Report per *Output*; check *Completion criteria*. Standalone `ready` result: `implementation complete; verification and review pending`; `blocked` → report partial implementation and blockers. Factory mode owns post-implementation verification, review, final cleanup, and spec closure.

## Effective graph

Persist the completed planner envelope before computing `GH_TOOL graph frontier --graph RUN_DIR/graph.json --planner RUN_DIR/planner.json --out RUN_DIR/effective-graph.json --done REF…` (omit `--done` when none). The tool unions native and inferred blockers, validates spec identity, full ticket coverage, blocker identities and acyclicity, and recomputes readiness and transitive HITL deferral. Keep `graph.json` as the native snapshot; use `effective-graph.json` for scheduling, validation, reports, and handoff. **MUST NOT** replace inferred edges with a later native refresh, even if simpler. Rationale: read-only analysis cannot publish those edges. Missing/stale/invalid planner coverage → stop affected launches and reanalyze; never fall back to native-only readiness.

## Targeted replanning

Reanalyze only evidence-invalidated dependencies, contracts, footprints, verification seams, scope boundaries, or model capability assumptions; routine commits alone do not trigger it. Pause affected launches; let in-flight agents settle, preserve work/reservations, and validate results against updated prerequisites before integration. Save evidence, affected unfinished refs, approved scope, integration tip, prior planner path, and completed/in-flight state under `NOTES_DIR`; launch *Launch planner* in read-only `analyze` mode with `{{analysisContext}}` pointing there and source/base pointers at that tip.

Merge affected recommendations into the full persisted planner envelope; retain unaffected entries and valid inferred edges, and remove inferred edges only with explicit invalidating evidence. Rerun *Effective graph*, conflicts, coverage, model validation, and HITL propagation before resuming. Preserve ticket identities, native blockers, completed work, and approved scope; ticket rewrites, new scope, or unknown external blockers require explicit resolution. A cycle or unresolved gap blocks affected work. Done when every affected unfinished ticket has validated prerequisites and a feasible verification contract.

Reassign a model only with settled-agent evidence, the planner's validated choice/reason, preserved work pointers, and remaining original rework budget. Launch a fresh replacement for that ticket with its preserved state and original `@prevHead`. Never replace a running agent, discard changes to obtain a clean checkout, or restart the rework count.

## Subagent launch contract

**Only this skill launches agents**, including background calls and rework, and controls scheduling, integration, publication, and ticket closure; every launch and rework follows this contract. Agent bodies and references return control here; they never create subagents.

- Resolve `AGENTS_ROOT=<skill base directory>/agents` and `REFERENCES_ROOT=<skill base directory>/references` as absolute paths before changing into a worktree; never from caller CWD.
- Validate the agent body and every manifest file are readable. Missing/unreadable → stop/report exact path.
- Fill every placeholder in the body; attach `referencesRoot`, `referenceManifest`, and the step's `refs` as absolute `requiredReferences`. Pass pointers only per *Pointer handoff*.
- Supply tools, permissions, and model settings at launch, never in agent frontmatter. Agents never gain scheduling, publishing, closure, merging, or cross-ticket authority.

`referenceManifest` lists every `.md` file under `REFERENCES_ROOT`, keyed by its relative path without `.md`: `breakdown` → `REFERENCES_ROOT/breakdown.md`, `fetch-diff` → `REFERENCES_ROOT/fetch-diff.md`.

Launch line legend: `refs` = `requiredReferences` (manifest keys); pass only the listed files, never a whole folder; run style defaults to foreground, one fresh agent; `rework` names who reworks and the round cap.

## Constraints

- **GitHub:** **MUST** perform every GitHub issue, PR, label, and graph operation through `GH_TOOL` per *GitHub operations*, never raw `gh`; load [publication.md](./references/publication.md) at step 5. Missing/unreadable reference or `GH_TOOL` → stop/report.
- **Repository identity:** preserve each issue's `OWNER/REPO#NUMBER`; route issue reads/comments/closures to its owning repository, and Git/implementation/PR operations only to the resolved source repository. Resolve ambiguity before writes; **MUST NOT** infer ownership from checkout, PR repository, or matching issue number.
- **HITL:** re-read labels at selection. Skip `hitl` tickets without implementation, delegation, comments, closure, or closing references. An open skipped ticket never satisfies dependants; only closed tickets with results verified in the integration base do. Reference skipped tickets without closing keywords; keep the spec open while any remain open.
- **One ticket = one subagent:** fresh implementer per ticket; sequential waits for each result, parallel caps concurrency. Ordinary rework uses that ticket's existing agent, at most two rounds; an explicit settled-agent capability reassignment follows *Targeted replanning* within the same total cap. **MUST NOT** implement inline, batch tickets, or reuse agents across tickets. Missing subagents → stop/report.
- **Implementation focus:** at most one quick confirmation of environment/network/Docker/port/registry/external-service failure; use test seams (unit tests, fakes, mocks, in-memory/stubs) and record skipped check/error. Infrastructure-only failures do not block when evidence suffices; code-caused failures do. **MUST NOT** troubleshoot infrastructure during implementation.
- **Draft-only:** PR stays draft; **MUST NOT** merge or mark ready (`gh pr ready`). User controls readiness.
- **Pointer handoff:** subagents load their own task data. Save every spec/ticket/comment/commit-log read a subagent can reuse under `RUN_DIR` (`graph read` writes spec and ticket files); refresh a file before each launch that uses it. Before each worktree agent launch, write `git -C WORKTREE_PATH log --reverse --format='%H %s%n%n%b' BASE_COMMIT..HEAD` (or `None yet.`) to `RUN_DIR/commits/<HEAD sha>.txt` if absent and record `@prevHead`. Pass pointers (paths, `OWNER/REPO#NUMBER` refs, commit ranges); **MUST NOT** inline bodies, comments, or logs into prompts. Missing/unreadable pointer file → agents return `failed` with the path; the orchestrator refreshes it and reworks.
- **Worktree isolation:** **MUST** follow [worktrees.md](./references/worktrees.md) for every worktree create, write, and ticket worktree removal; never reset or discard existing work.

## Graph report

Table of ticket, blocked by (`none` = explicit root), paths, conflicts with kind (`file`/`soft`) and a per-ticket conflict count; then ready frontier, critical path, deferred tickets with reason. Every node listed, including deferred tickets' blocker edges. Then spec artifact count (length of `graph.spec.artifacts`) or `artifacts_note`, and design sketch coverage from the planner notes when a sketch exists.

## Implementation handoff

Write data-only `RUN_DIR/implementation-handoff.json`; pass its absolute path, never internal scripts/references. Use `null` for unavailable scalar data and `[]` for no entries; missing required state makes `status` `blocked`.

| Field | Content |
|---|---|
| `status`, `blockers` | `ready` only after all in-scope tickets and publication checks succeed and chore is verified (including verified no-change); otherwise `blocked` plus reasons. |
| `specRef`, `specUrl`, `sourceRepository`, `trackerRepository`, `prUrl` | Qualified spec identity and URLs; explicit source/tracker `owner/repo`. |
| `initiativeId`, `remote`, `integrationBranch`, `baseBranch`, `baseCommit`, `headCommit` | Validated routing, verified source remote, base SHA, final pushed SHA. |
| `harnessRoot`, `sourceRoot`, `worktreesRoot`, `worktreePath`, `runDir`, `evidenceRoot` | Absolute paths resolved once; roots outside the integration worktree. |
| `specFile`, `graphFile`, `plannerFile`, `modelOutcomesFile`, `commitsFile` | Refreshed absolute data pointers; `graphFile` is `effective-graph.json`, planner envelope and model outcome history are retained; spec/ticket files include title, body, comments; commit log covers `BASE_COMMIT..HEAD`. |
| `tickets` | Every graph ticket: qualified `ref`, `file`, integrated `commit` or null, `status` (`integrated`, `base-verified`, `deferred`, `blocked`), `evidence` pointers, `evidenceCommentId`, read-back `closure` (`completed` or `open`); empty only with an explicit blocker. |
| `chore` | `status` (`verified`, `none-needed`, `failed`), `commits`, actual `model`, `effort`, validation `evidence` pointers (including skipped checks/errors). |
| `publication` | Read-back `verified` boolean, `draft` boolean, `checks` (`passed`, `pending`, `failed`, `absent`), metadata/coverage and posting failures in `problems`. |

```json
{"status":"ready","blockers":[],"specRef":"tracker/repo#1","specUrl":"https://github.com/tracker/repo/issues/1","sourceRepository":"owner/repo","trackerRepository":"tracker/repo","prUrl":"https://github.com/owner/repo/pull/2","initiativeId":"PAY-12","remote":"origin","integrationBranch":"feat/PAY-12","baseBranch":"main","baseCommit":"<base SHA>","headCommit":"<pushed SHA>","harnessRoot":"/harness","sourceRoot":"/harness/workspace/repo","worktreesRoot":"/harness/.worktrees/repo","worktreePath":"/harness/.worktrees/repo/PAY-12","runDir":"/harness/workspace/runs/PAY-12","evidenceRoot":"/harness/workspace/evidence","specFile":"/harness/workspace/runs/PAY-12/spec.json","graphFile":"/harness/workspace/runs/PAY-12/effective-graph.json","plannerFile":"/harness/workspace/runs/PAY-12/planner.json","modelOutcomesFile":"/harness/workspace/runs/PAY-12/model-outcomes.json","commitsFile":"/harness/workspace/runs/PAY-12/commits/<pushed SHA>.txt","tickets":[{"ref":"tracker/repo#3","file":"/harness/workspace/runs/PAY-12/tickets/tracker_repo_3.json","commit":"<ticket SHA>","status":"integrated","evidence":["/harness/workspace/runs/PAY-12/ticket-3.md"],"evidenceCommentId":123,"closure":"completed"}],"chore":{"status":"none-needed","commits":[],"model":"<actual model>","effort":"medium","evidence":["/harness/workspace/runs/PAY-12/chore.md"]},"publication":{"verified":true,"draft":true,"checks":"pending","problems":[]}}
```

Failure: same shape, `status: blocked`, concrete `blockers`, partial values preserved, unavailable values `null`; claim publication/closure only after read-back.

## Output

- Breakdown Initiative or parallel mode → first: *Graph report*.
- Spec URL, created tickets, planner model/effort; PR URL/state.
- Per ticket: chosen/actual implementer model/effort, reassignment reasons, attempts/rework and validation outcomes, integrated commit, evidence, closure or blocker; skipped `hitl` tickets and dependants.
- Chore commits and model/effort; skipped infrastructure checks; preserved worktree status; *Implementation handoff* path and status.
- No runnable tickets: report graph/blockers; never claim implementation.
- Incomplete: name missing evidence, partial GitHub writes, preserved work; distinguish unverified state from read-back success.

## Gotchas

- References are grouped by phase; a cited heading (*X*) resolves only within files already loaded at that step. Load a reference when its step links it, read it to end of file, and continue truncated reads by range; a partial read counts as not loaded.
- A closed issue may be cancelled or duplicate rather than implemented; verify the result exists in the integration base or branch. On resume, a ticket closed by an earlier run is satisfied only if its commit is on the integration branch.
- A ticket commit is not complete until the cumulative integration result passes relevant checks.
- Treat external blockers separately from run-local integrated work; never bypass unresolved external dependencies.

## Completion criteria

- Each integrated ticket has exactly one verified commit from its own implementer, an evidence comment, and read-back `completed` closure in its owning repository. No skipped `hitl` ticket was implemented, commented on, closed, or given a closing reference.
- Source repository/base match routing; PR title prefix and bare first body line equal `INITIATIVE_ID`; every implemented ticket is covered; PR is draft; pending/failed checks are reported accurately.
- Chore result and actual model/effort recorded; valid chore changes committed and pushed. A failed or missing result is a handoff blocker, not “none needed.”
- Handoff pointers readable and refreshed; branch, worktree, and run/evidence directories preserved; spec open and referenced without a closing keyword. No app verifier or code review ran here.
- No reference-loading failure ignored; subagents received pointers, not inlined task data; user work intact.
- Completeness sweep, last: re-read the request; map every spec requirement/ticket to code, tests, docs, configuration, and relevant failure/compatibility evidence. Resolve gaps or report explicit deferrals before declaring completion.
