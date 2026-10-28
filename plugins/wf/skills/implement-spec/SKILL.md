---
name: implement-spec
description: Implements a GitHub spec or plan through a routed ticket graph; orchestrates sequential or parallel delivery, app verification, chore, and independent code review into one draft PR.
disable-model-invocation: true
---

# Implement Spec

Orchestrate a routed ticket graph into one integration branch and draft PR. Run steps in order; load each linked reference only when its step is reached, never ahead.

## Inputs

- GitHub spec issue URL `https://github.com/OWNER/REPO/issues/NUMBER`, plan file path, or inline plan/description. Native sub-issues are **tickets**; native blockers form the **ticket graph**.
- Spec routing: `repo:target:<owner/repo>` and `repo:base:<branch>`; use source-root `GLOSSARY.md` vocabulary when present.
- `mode`: `sequential` (default) | `parallel`.
- `max-parallel=<positive integer>`: parallel only; default 3. Scheduling always follows the ticket graph.

## Workflow

1. Detect input type, load [github_setup.md](./references/github_setup.md) and [breakdown.md](./references/breakdown.md), then prepare input:
   → A: Plan file or inline description → Run *Prepare Plan*.
   → B: GitHub spec issue → Run *Prepare Spec*.
   → Unsupported or ambiguous input: ask for valid input; stop.
   → Handed off to *Breakdown Initiative* → load [github_graph.md](./references/github_graph.md); run *Breakdown Initiative*.

   Launch planner (only from *Breakdown Initiative*) → [planner.md](./agents/planner.md) subagent from `SOURCE_ROOT`:
   refs `breakdown`, `ticket-body-template`, `github_setup` · latest Opus (prefer `claude-opus-5.5`), medium reasoning · rework none.
   Before: fetch validated `BASE_BRANCH`, record `BASE_COMMIT`; resolve `HARNESS_ROOT`; create `RUN_DIR` and `NOTES_DIR` = `RUN_DIR/notes` outside the repository; save spec + comments to `RUN_DIR/spec.json`. Done when checkout and base match routing.

   | Placeholder | Value |
   |---|---|
   | `{{specRef}}` | spec `OWNER/REPO#NUMBER` |
   | `{{specFile}}` | `RUN_DIR/spec.json` |
   | `{{implementationDetails}}` | plan path or `None` |
   | `{{harnessRoot}}` | `HARNESS_ROOT` |
   | `{{sourceRoot}}` | `SOURCE_ROOT` |
   | `{{baseCommit}}` | `BASE_COMMIT` |
   | `{{notesDir}}` | `NOTES_DIR` |

   Verify: per Breakdown Initiative; record actual model/effort or unavailable-model failure.
   → `failed`, invalid JSON, empty `created`, or incomplete GitHub operations: report actual partial state; stop; never claim success.

2. Read the complete ticket graph (spec, tickets, comments, blockers, parents) and save its files per *Read the task graph*; retain explicit `OWNER/REPO#NUMBER` identities.

3. Validate scope, routing, and dependencies per *Graph validation* ([github_graph.md](./references/github_graph.md); load if not loaded).

4. Explore implementation scope and test seams as needed; save shared notes under `RUN_DIR/notes` and pass pointers. Reuse planner evidence (graph, footprints, conflicts) when available; otherwise derive it from the graph and source checkout without a planner. Bound every runnable ticket's scope before selection.

5. Execute selected mode:
   - Validate `mode` and `MAX_PARALLEL` before creating any branch or worktree.
   - Create the integration branch and worktree per [Integration setup](./references/worktrees.md#integration-setup).
   - Load [github_publication.md](./references/github_publication.md) (both modes).
   - Load **only** the selected mode reference:
     → C: Sequential → Run [Sequential Implementation](./references/sequential.md#sequential-implementation).
     → D: Parallel → Run [Parallel Implementation](./references/parallel.md#parallel-implementation); isolate tickets per [Ticket worktrees](./references/worktrees.md#ticket-worktrees).

   Launch implementer → [implementer.md](./agents/implementer.md) subagent per ticket in its worktree:
   refs `github_setup` · one fresh per ticket; C foreground, settle before next; D background, ≤ `MAX_PARALLEL` in flight · rework same agent, ≤2 rounds.

   | Placeholder | Sequential | Parallel |
   |---|---|---|
   | `{{worktreePath}}` | `WORKTREE_PATH` | `TICKET_WORKTREE(n)` |
   | `{{featureBranch}}` | `INTEGRATION_BRANCH` | `TICKET_BRANCH(n)` |
   | `{{targetBranch}}` | `BASE_BRANCH` | `INTEGRATION_BRANCH` |
   | `{{ticketRef}}` | `OWNER/REPO#NUMBER` | same |
   | `{{ticketFile}}` | `RUN_DIR/tickets/<OWNER>_<REPO>_<NUMBER>.json` | same |
   | `{{commitsFile}}` | `RUN_DIR/commits/<HEAD sha>.txt` | same (integration log) |
   | `{{commitSubjectPrefix}}` | `ccode(<INITIATIVE_ID> <OWNER/REPO#NUMBER>): ` | same |

   Verify in the ticket's worktree: `HEAD` = `result.commit`, exactly one commit since `@prevHead`, subject prefix, clean and on its branch, `result.verification` names executed checks and results including skipped infrastructure checks and errors; thin evidence → run cheap confirmations.
   → Invalid JSON, `failed`, missing evidence, or mismatched commit: rework; recheck after each round.
   → Still invalid after 2 rounds: preserve branch/worktree and report the blocker; stop advancing that ticket.
   Integrate and publish per the mode reference.

6. Run *Frontier check*.

7. Launch chore → [chore.md](./agents/chore.md) subagent in `WORKTREE_PATH`:
   refs `fetch-diff` · rework none.
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

   Verify: ≤1 commit since `@prevHead`, subject match, clean, checks reported.
   After: push; remove `@diffDir`; report out-of-scope findings without acting.
   → No result or failed: record none/failed; continue.

8. Launch verifier → [verifier.md](./agents/verifier.md) subagent in `WORKTREE_PATH`:
   refs `github_setup` · rework none (internal: ≤3 verifications, ≤2 fix attempts per finding, one commit per fix).
   Before: load [github_finalize.md](./references/github_finalize.md); detect harness (read-only) in `.github/skills/*/SKILL.md`, `.claude/skills/*/SKILL.md`, `.agents/skills/*/SKILL.md`, keeping skills whose `description` says they launch/drive the app to prove behavior and capture evidence; set `EVIDENCE_DIR` per *Verification evidence*.
   → No harness: record `verification skipped: no verification harness`; no subagent, no comment.
   → Subagents unavailable: record skip reason; never drive the app in the orchestrator.

   | Placeholder | Value |
   |---|---|
   | `{{featureBranch}}` | `INTEGRATION_BRANCH` |
   | `{{pullRequestUrl}}` | PR URL |
   | `{{worktreePath}}` | `WORKTREE_PATH` |
   | `{{targetBranch}}` | `BASE_BRANCH` |
   | `{{evidenceDir}}` | `EVIDENCE_DIR` |
   | `{{verificationSkills}}` | matched `SKILL.md` absolute paths, one per line |
   | `{{specFile}}` | `RUN_DIR/spec.json` |
   | `{{ticketFiles}}` | integrated ticket file paths, one per line |
   | `{{commitsFile}}` | `RUN_DIR/commits/<HEAD sha>.txt` |
   | `{{commitSubjectPrefix}}` | `fix(<INITIATIVE_ID>): ` |

   Verify: `HEAD` = last `result.rounds[].fixCommit` (or `@prevHead`), exactly one `fix(...)` commit per fix round, clean, `result.verification` names executed checks, `EVIDENCE_DIR` holds cited files, valid JSON; proof framework untouched.
   → Missing evidence/invalid JSON, or app fails launch/health: verdict `inconclusive` with error; do not troubleshoot.
   After: push fix commits and update PR coverage per *Pull request lifecycle*; post one spec comment per *Verification evidence*; read back, or record failure with `EVIDENCE_DIR/verdict.md` saved.
   → Final `fail`/`partial`: list unfixed findings with reason and attempts, name unfinished tickets; keep spec open and PR draft; continue.

9. Run *Publication verification* ([github_finalize.md](./references/github_finalize.md); load if not loaded).

10. Run code review → *`code-review` skill for GitHub pull requests, bugs, quality attributes, code smells, and initiative coverage* from `SOURCE_ROOT`:
    inputs PR URL, `SOURCE_ROOT` · foreground; wait until every axis has an outcome.
    Review creates its own fresh detached worktree from `SOURCE_ROOT` without cloning; **MUST NOT** review inside or reuse the integration worktree. Review never fixes code.
    Record: axes, findings, posting results, models/fallbacks, reviewed head.
    → Unavailable: report the blocker; keep spec open.

11. Run [Actualize and cleanup](./references/worktrees.md#actualize-and-cleanup).
    → New commits after review: reviewed head is stale; closure gates keep the spec open.
    → Unresolvable conflict, failed push, or failed removal: preserve and report path/branch; keep spec open; continue to step 12.

12. Finalize per *Closure gates*; report per *Output*; check *Completion criteria*.
    → All closure gates pass: close spec; verify remote state.
    → Otherwise: keep spec open and report findings.

## Subagent launch contract

**Only this `SKILL.md` launches agents**, including background calls and rework, and controls scheduling, integration, publication, and closure; every launch and rework follows this contract. Agent bodies and references return control here; they never create subagents.

- Resolve `AGENTS_ROOT=<skill base directory>/agents` and `REFERENCES_ROOT=<skill base directory>/references` as absolute paths before changing into a worktree; never from caller CWD.
- Validate the agent body and every manifest file are readable. Missing/unreadable → stop/report exact path.
- Fill every placeholder in the body; attach `referencesRoot`, `referenceManifest`, and the step's `refs` as absolute `requiredReferences`. Pass pointers only per *Pointer handoff*.
- Supply tools, permissions, and model settings at launch, never in agent frontmatter. Agents never gain scheduling, publishing, closure, merging, or cross-ticket authority.

`referenceManifest` lists every `.md` file under `REFERENCES_ROOT`, keyed by its relative path without `.md`: `github_setup` → `REFERENCES_ROOT/github_setup.md`, `fetch-diff` → `REFERENCES_ROOT/fetch-diff.md`.

Launch line legend: `refs` = `requiredReferences` (manifest keys); pass only the listed files, never a whole folder; run style defaults to foreground, one fresh agent; `rework` names who reworks and the round cap.

## Constraints

- **GitHub:** **MUST** load [github_setup.md](./references/github_setup.md) before any GitHub action, including step 1 preparation; use its *Prerequisites* `gh` checks and failure handling. Load each other `references/github_*.md` file only at the step that links it. Missing/unreadable reference → stop/report.
- **Repository identity:** preserve each issue's `OWNER/REPO#NUMBER`; route issue reads/comments/closures to its owning repository, and Git/implementation/PR operations only to the resolved source repository. Resolve ambiguity before writes; **MUST NOT** infer ownership from checkout, PR repository, or matching issue number.
- **HITL:** re-read labels at selection. Skip `hitl` tickets without implementation, delegation, comments, closure, or closing references. An open skipped ticket never satisfies dependants; only closed tickets with results verified in the integration base do. Reference skipped tickets without closing keywords; keep the spec open while any remain open.
- **One ticket = one subagent:** fresh implementer per ticket; sequential waits for each result, parallel caps concurrency. Rework uses that ticket's existing agent, at most two rounds. **MUST NOT** implement inline, batch tickets, or reuse agents across tickets. Missing subagents → stop/report; app verification has its own skip policy in step 8.
- **Implementation focus:** at most one quick confirmation of environment/network/Docker/port/registry/external-service failure; use test seams (unit tests, fakes, mocks, in-memory/stubs) and record skipped check/error. Infrastructure-only failures do not block when evidence suffices; code-caused failures do. **MUST NOT** troubleshoot infrastructure during implementation or app verification.
- **Proof framework:** verification fixes change only app code/tests. Check each fix commit against matched verification skill folders, feature maps, journeys, harness scripts/helpers, seed data, and checked cases. A proof-framework change invalidates the fix: undo with `git revert --no-edit`, never reset; record the finding unfixed as a framework gap.
- **Draft-only:** PR stays draft; **MUST NOT** merge or mark ready (`gh pr ready`). User controls readiness.
- **Pointer handoff:** subagents load their own task data. Save every spec/ticket/comment/commit-log read a subagent can reuse under `RUN_DIR` per *Read the task graph*; refresh a file before each launch that uses it. Before each worktree agent launch, write `git -C WORKTREE_PATH log --reverse --format='%H %s%n%n%b' BASE_COMMIT..HEAD` (or `None yet.`) to `RUN_DIR/commits/<HEAD sha>.txt` if absent and record `@prevHead`. Pass pointers (paths, `OWNER/REPO#NUMBER` refs, commit ranges); **MUST NOT** inline bodies, comments, or logs into prompts. Missing/unreadable pointer file → agents holding `github_setup` load the issue from its ref; others return `failed` with the path.
- **Worktree isolation:** **MUST** follow [worktrees.md](./references/worktrees.md) for every worktree create, write, actualize, and removal; never reset or discard existing work.

## Output

- Breakdown Initiative or parallel mode → first: ticket blocker graph/conflicts, critical path, deferred tickets.
- Spec URL, created tickets, planner model/effort; PR URL/state.
- Per ticket: integrated commit, evidence, closure or blocker; skipped `hitl` tickets and dependants.
- Chore commits; verification verdict, checks, fix commits, per-round `EVIDENCE_DIR`, spec comment ID or skip reason.
- Review axes, findings, comment IDs, models/fallbacks; actualize commits/merge result; skipped infrastructure checks; worktree status.
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
- Chore preceded app verification; chore commits verified and pushed. Verification left the proof framework unchanged, preserved evidence outside the worktree, and recorded its verdict or skip; unresolved `fail`/`partial` keeps the spec open.
- Code review ran from `SOURCE_ROOT` in its own detached worktree before actualize; integration worktree actualized, pushed, and removal confirmed, or preserved and reported.
- Spec closed only when every closure gate passes. No reference-loading failure ignored; subagents received pointers, not inlined task data; user work intact.
- Completeness sweep, last: re-read the request; map every spec requirement/ticket to code, tests, docs, configuration, and relevant failure/compatibility evidence. Resolve gaps or report explicit deferrals before declaring completion.
