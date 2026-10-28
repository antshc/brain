---
name: implement-spec
description: Implements a GitHub spec or plan through a routed ticket graph; orchestrates sequential or parallel delivery, app verification, chore, and independent code review into one draft PR.
disable-model-invocation: true
---

# Implement Spec

Prepare inputs, schedule tickets, launch subagents, verify results, publish GitHub state, and finalize. Deliver one integration branch in a run-owned worktree at `<repo-root>/workspace/<repo>.worktrees/<initiative-id>`, with a reviewed **draft** PR covering every implemented ticket.

## Inputs

- GitHub spec issue URL `https://github.com/OWNER/REPO/issues/NUMBER`, or a session `plan.md` path or inline description. Native sub-issues are **tickets**; native blockers form the **ticket graph**.
- Spec routing labels `repo:target:<owner/repo>` and `repo:base:<branch>`; use source-root `GLOSSARY.md` vocabulary when present.
- `[mode]`: `sequential` (default) | `parallel`. Parallel settings: `schedule=waves|graph` (default `waves`), `max-parallel=<positive integer>` (default 3).

## Workflow

1. **Detect input type first.** Plan file or inline description → *Prepare Plan*. GitHub spec issue → *Prepare Spec*. Ambiguous or unsupported input → ask for valid input and stop. After detection, explicitly reject `mode=plan` or other unsupported modes before writes, execution worktrees, or PR creation. Validate parallel settings before side effects. Done when input and supported mode are known.
2. **Prepare input.** Run the selected preparation path below for a routed spec and native ticket graph. Done when the spec, source repository, base branch, and initiative ID are validated and any required Breakdown Initiative has succeeded.
3. **Read and validate the graph.** Read the spec, every ticket, comments, native parents, and blockers. Resolve tracker repository, source repository, and base per the GitHub reference; resolve missing/conflicting routing before writes. Reject cycles and tickets without scope. Mark `hitl` tickets and unsatisfied dependants deferred. Verify closed blockers in `BASE_COMMIT`; explicitly resolve cancelled/duplicate issues and external blockers. Done when the run-local map records each ticket's identity, owner, status, scope, blockers, and evidence.
4. **Explore scope and scheduling.** Explore scope, footprints, and test seams as needed; save shared notes outside the repository and pass pointers. Reuse the planner's conflicts/waves after Breakdown Initiative. For an already-ticketed spec, derive dependency waves, footprints, conflicts, and critical path from the graph and source checkout without a planner. Defer open `hitl` tickets and their dependants; split oversized/conflicting waves. Done when every runnable ticket has bounded scope and conflict-aware scheduling evidence.
5. **Create integration worktree.** Per GitHub reference *Single worktree lifecycle*, fetch the validated base and record `BASE_COMMIT` (reuse Breakdown Initiative's value when set). Derive `INITIATIVE_ID` from the spec title prefix before the first `:`. Done when the run-owned worktree is clean on the new integration branch at `BASE_COMMIT`.
6. **Execute selected mode.** Default or explicit `sequential` → load [sequential.md](./references/sequential.md); `parallel` → load [parallel.md](./references/parallel.md). Follow that reference's scheduling, verification, publication, and rework procedure; every subagent launch returns here through *Subagent launch contract*. Use *Implementer prompt* below. Keep ticket selection, launches, commit verification, pushes, draft PR updates, evidence publication, and integrated-ticket closure in the orchestrator. Done when all runnable tickets are integrated, verified, pushed, and closed or a blocker is explicit.
7. **Check frontier.** Re-read labels and recompute readiness after each publication. If unfinished tickets remain but none are ready, report blockers, preserve all work, keep the spec open and PR draft, and stop before verification, chore, cleanup, review, or finalization. A blocker counts as satisfied only when integrated in this run or verified in the base. Done when no unresolved blocker prevents downstream phases.
8. **Verify the app and fix gaps** after all in-scope tickets are integrated/pushed, before chore. *Load [verifier.md](./agents/verifier.md)*. **Detect** (read-only, in `WORKTREE_PATH`): scan `.github/skills/*/SKILL.md`, `.claude/skills/*/SKILL.md`, `.agents/skills/*/SKILL.md`; keep skills whose frontmatter `description` says they launch/drive the app to prove behavior and capture evidence. None matched → skip: no subagent, no comment, record `verification skipped: no verification harness`. Subagents unavailable → skip and record the reason; never drive the app in the orchestrator. Otherwise run one verify-and-fix subagent:
   1. **Launch.** Set `EVIDENCE_DIR` per the GitHub reference *Verification evidence* and record `@prevHead`. Fill `agents/verifier.md`: `{{featureBranch}}`, `{{pullRequestUrl}}`, `{{worktreePath}}`, `{{targetBranch}}` from *Implementer prompt* using the integration worktree/branch and `BASE_BRANCH`; `{{evidenceDir}}` = `EVIDENCE_DIR`; `{{verificationSkills}}` = matched `SKILL.md` absolute paths, one per line; `{{specJson}}` / `{{ticketsJson}}` = spec and integrated tickets with comments and explicit issue identities; `{{branchCommits}}` = the `{{initiativeCommits}}` log; `{{commitSubjectPrefix}}` = `fix(<initiativeId>): `. Launch a fresh verifier through *Subagent launch contract*. It verifies the app, fixes code-caused failures, and re-verifies, at most 3 verifications and 2 fix attempts per finding (2 fix rounds), one commit per fix, never touching the proof framework; a finding unfixed after 2 attempts is recorded and the run continues; the orchestrator never drives the app or fixes code itself.
   2. **Check.** `HEAD` equals the last `result.rounds[].fixCommit` (or `@prevHead` when none), exactly one commit per fix round since `@prevHead` with the `fix(...)` subject, worktree clean, `result.verification` names executed checks, `EVIDENCE_DIR` holds the files its checks cite, JSON valid. Missing evidence or invalid JSON downgrades the verdict to `inconclusive`; preserve and report a moved head or dirty worktree (step 10 stops on it). An app that cannot launch or fails its health check gives `inconclusive` with the error; do not troubleshoot. When fix commits exist, push and update PR coverage.
   3. **Publish verdict.** Post one comment on the spec per the GitHub reference, covering the final verdict, every round's evidence path, and each fix commit. Done when the comment is read back, the failure to post is recorded with `EVIDENCE_DIR/verdict.md` saved, or the skip is recorded. A final `fail` or `partial` verdict stays unresolved: list each unfixed finding with its reason and attempts in the comment, name the unfinished tickets, keep the PR draft and spec open, and continue to the next phases without stopping.
9. **Chore pass** once verification is settled. *Load [fetch-diff.md](./references/fetch-diff.md)* and split the PR diff into `@diffDir`. Record `@prevHead`. Fill `agents/chore.md`: `{{featureBranch}}`, `{{pullRequestUrl}}`, `{{worktreePath}}`, `{{targetBranch}}` from *Implementer prompt* using the integration worktree/branch and `BASE_BRANCH`; `{{diffDir}}` = `@diffDir`; `{{branchCommits}}` = the `{{initiativeCommits}}` log; `{{commitSubjectPrefix}}` = `chore(<initiativeId>): `. Launch a fresh chore through *Subagent launch contract*. Verify: zero or one commit since `@prevHead`, matching subject when present, worktree clean, checks reported. Push, then remove `@diffDir`. Report its out-of-scope findings; do not act on them. Done when the chore result is verified and pushed or recorded as none/failed.
10. **Publish and remove worktree.** Confirm all implementation/chore work is verified, clean and pushed; read back the draft PR, initiative metadata, ticket coverage and checks. Preserve `SOURCE_ROOT`, PR URL and final head outside the worktree. Change CWD to `SOURCE_ROOT`; remove only the run-owned worktree per the GitHub reference, without force. Verify it is absent from disk and `git worktree list`. If dirty, unpushed, incomplete, or removal fails, preserve/report it and stop before review. Done when the PR exists at the pushed head and implementation worktree removal is confirmed.
11. **Code review.** From `SOURCE_ROOT`, *run `code-review` skill for GitHub pull requests, bugs, quality attributes, code smells, and initiative coverage*, passing the PR URL and `SOURCE_ROOT`. **MUST** run only after step 10; never substitute the former bug-fix pass or reuse the removed implementation worktree. The skill selects models, fetches the PR diff, creates a fresh detached review worktree from `SOURCE_ROOT` without cloning, delegates read-only axes, and posts findings. If unavailable, report the blocker. Done when every axis, finding, posting result, and selection fallback has a recorded outcome.
12. **Finalize.** Recheck PR head, required checks, metadata, coverage, and that the PR is still a draft. Leave the PR as a draft. Close the spec only when every in-scope ticket is integrated/closed, no `hitl` ticket is open, review completed at the current head, initiative verification passed, app verification is not `fail`/`partial`, and no unresolved bug/initiative findings remain. Failed/incomplete/skipped initiative review, posting failures, an unresolved `fail`/`partial` app verdict, or known unresolved earlier bug/initiative concerns keep the spec open. Report quality/smell suggestions separately. Review does not fix code automatically; hand off findings. Keep the branch and PR. Done when remote state is read back or blockers are explicit.

## Prepare Plan

1. Ask for **target repository, target/base branch, and initiative ID**. Validate all three, source checkout/remote identity, and remote branch existence per GitHub reference *Create spec*. **MUST NOT** silently substitute the repository default branch. Done when all answers and routing are verified.
2. Create the spec with the supplied plan/description and `repo:target:<owner/repo>` / `repo:base:<branch>` labels. Read back the created spec, title prefix, and routing. Done when the remote spec matches the validated answers.
3. Run *Breakdown Initiative*. Done when the created/reconciled tickets and native links are read back.

## Prepare Spec

1. Read the spec and native sub-issues, then resolve source repository, base branch, and initiative ID through the GitHub reference. Done when identity and routing are unambiguous.
2. Existing sub-issues → reuse their graph; **MUST NOT** run the planner or create tickets. Zero sub-issues → run *Breakdown Initiative*. Done when the routed spec has a read-back graph.

## Breakdown Initiative

1. Fetch the validated `BASE_BRANCH` and record `BASE_COMMIT`; resolve `HARNESS_ROOT` from the tracker/source workflow and create `NOTES_DIR` outside the repository. Done when the checkout and base match routing and notes have a safe location.
2. Fill [planner.md](./agents/planner.md): `{{breakdown}}` = `true`; `{{specRef}}` = spec `OWNER/REPO#NUMBER`; `{{implementationDetails}}` = plan path or `None`; `{{harnessRoot}}` = `HARNESS_ROOT`; `{{ticketsJson}}` = `[]`; `{{sourceRoot}}` = `SOURCE_ROOT`; `{{baseCommit}}` = `BASE_COMMIT`; `{{maxParallel}}` = `MAX_PARALLEL`; `{{notesDir}}` = `NOTES_DIR`; `{{specJson}}` = spec with comments. Launch a fresh planner through *Subagent launch contract*: latest available Opus (existing preference `claude-opus-5.5`), medium reasoning; record actual model/effort or explicit unavailable-model failure. Done when its JSON result is returned.
3. Require the planner to load [breakdown.md](./references/breakdown.md) and [github.md](./references/github.md), discover/fetch spec artifacts, partition and map relevant pieces to every related ticket, and publish through the embedded online-only, non-interactive procedure. Only the planner writes tickets; never create them inline. No standalone `to-tickets` invocation, availability check, approval question, offline fallback, or new `hitl` label. A relevant inaccessible/uninterpretable artifact stops publication with source and error; no fabricated or silently omitted content. Done when publication, artifact coverage, and native links are verified.
4. On `failed`, invalid JSON, empty `created`, or incomplete GitHub operations, stop/report actual partial state; never claim success. Otherwise re-read the full native graph and validate ticket bodies, artifact mappings, parents, and blockers. Show tickets, waves, conflicts, critical path, and deferred items using the table in [parallel.md](./references/parallel.md), then continue without waiting. Done when the run-local graph matches remote state.

## Constraints

- **GitHub:** **MUST** load [github.md](./references/github.md) before any GitHub action, including reads; use its `gh` prerequisites, procedures, and failure handling. Missing/unreadable reference → stop/report.
- **Repository identity:** preserve each issue's `OWNER/REPO#NUMBER`; route issue reads/comments/closures to its owning repository, and Git/implementation/PR operations only to the resolved source repository. Resolve ambiguity before writes; **MUST NOT** infer ownership from checkout, PR repository, or matching issue number.
- **HITL:** re-read labels at selection. Skip `hitl` tickets without implementation, delegation, comments, closure, or closing references. An open skipped ticket never satisfies dependants; only closed tickets with results verified in the integration base do. Reference skipped tickets without closing keywords; keep the spec open while any remain open.
- **One ticket = one subagent:** fresh implementer per ticket; sequential waits for each result, parallel caps concurrency. Rework uses that ticket's existing agent, at most two rounds. **MUST NOT** implement inline, batch tickets, or reuse agents across tickets. Missing subagents → stop/report; app-verification absence has its explicit skip policy in Workflow step 8.
- **Implementation focus:** at most one quick confirmation of environment/network/Docker/port/registry/external-service failure; use test seams (unit tests, fakes, mocks, in-memory/stubs) and record skipped check/error. Infrastructure-only failures do not block when evidence suffices; code-caused failures do. **MUST NOT** troubleshoot infrastructure during implementation or app verification.
- **Proof framework:** verification fixes change only app code/tests. Check each fix commit against matched verification skill folders, feature maps, journeys, harness scripts/helpers, seed data, and checked cases. A proof-framework change invalidates the fix: undo with `git revert --no-edit`, never reset; record the finding unfixed as a framework gap.
- **Draft-only:** PR remains draft throughout; **MUST NOT** merge or mark ready (`gh pr ready`). User controls readiness.
- **Worktree isolation:** sequential uses one integration branch/worktree for all tickets, fixes, and chore; no per-ticket worktrees. Parallel alone adds isolated run-owned ticket branches/worktrees; integration remains the sole location for serialized cherry-picks, publishing, verification, fixes, and chore. No concurrent writers in one tree, conflicting in-flight tickets, merger subagents, resets, or discarded existing work.

## Subagent launch contract

**Only this `SKILL.md` launches planner, implementer, verifier, and chore agents**, including background calls and rework. Agent bodies and reference procedures return launch requests/control here; they never create subagents. Resolve paths before changing into a source worktree:

- `SKILL_ROOT` = absolute directory containing this skill's `SKILL.md`, independent of caller CWD; `AGENTS_ROOT=SKILL_ROOT/agents`; `REFERENCES_ROOT=SKILL_ROOT/references`.
- Validate selected agent body and all five reference files exist and are readable. Missing/unreadable paths → stop/report exact path; never infer from ticket CWD or inline contents.
- Fill every placeholder in the selected body, then attach `referencesRoot=REFERENCES_ROOT`, `referenceManifest` below, and role-specific `requiredReferences`. Pass issue/worktree/commit/evidence context as pointers rather than duplicated reference contents.

| Manifest key | Absolute path |
| --- | --- |
| `breakdown` | `REFERENCES_ROOT/breakdown.md` |
| `sequential` | `REFERENCES_ROOT/sequential.md` |
| `parallel` | `REFERENCES_ROOT/parallel.md` |
| `github` | `REFERENCES_ROOT/github.md` |
| `fetchDiff` | `REFERENCES_ROOT/fetch-diff.md` |

| Role body | `requiredReferences` keys | Authority |
| --- | --- | --- |
| [planner.md](./agents/planner.md) | `breakdown`, `github` | Breakdown Initiative only; sole ticket writer |
| [implementer.md](./agents/implementer.md) | `github` | One ticket's local implementation/commit |
| [verifier.md](./agents/verifier.md) | `github` | App verification and bounded local fixes |
| [chore.md](./agents/chore.md) | `fetchDiff` | Local behavior-preserving cleanup only |

Expand `requiredReferences` to absolute paths in the launch prompt. Require the agent to open/read each **before taking task actions**, follow only role-relevant instructions, and return `failed` with the exact missing/unreadable path before acting on loading failure. Paths never grant orchestrator-only scheduling, publishing, issue closure, merging, or cross-ticket authority; planner ticket publication is limited to the explicit Breakdown Initiative grant. Supply runtime tools/permissions/model settings here, never agent frontmatter; restrict each role to its listed authority.

## Implementer prompt

Fill [implementer.md](./agents/implementer.md) for each selected ticket; launch through *Subagent launch contract* only.

| Placeholder | Value |
| --- | --- |
| `{{worktreePath}}` | Integration `WORKTREE_PATH` sequentially; isolated ticket worktree in parallel |
| `{{featureBranch}}` | Integration branch sequentially; ticket branch in parallel |
| `{{targetBranch}}` | `BASE_BRANCH` sequentially; integration branch in parallel |
| `{{ticketJson}}` | Issue JSON plus full comments and explicit `OWNER/REPO#NUMBER` |
| `{{initiativeCommits}}` | `git -C WORKTREE_PATH log --reverse --format='%H %s%n%n%b' BASE_COMMIT..HEAD`, or `None yet.`; integration log in parallel |
| `{{commitSubjectPrefix}}` | `ccode(<initiativeId> <OWNER/REPO#NUMBER>): ` |

Record `@prevHead` before launch. Verify completed JSON against actual HEAD, exactly one commit since `@prevHead`, required subject prefix, clean worktree, and executed check evidence. Thin evidence → cheap confirmation; invalid result/failure → same-agent rework, max two rounds, then preserve/report and stop advancement. The selected execution reference owns integration/publication order, not subagent invocation authority.

## Output

Report tickets/waves/conflicts, critical path, and deferred tickets first after Breakdown Initiative or in parallel mode; spec URL and created tickets, planner model/effort; PR URL/state; per-ticket integrated commit, evidence, closure or blocker; skipped `hitl` tickets/dependants; chore commits; verification verdict/checks/fix commits/per-round `EVIDENCE_DIR`/spec comment ID or skip reason; review axes/findings/comment IDs/models/fallbacks; skipped infrastructure checks; worktree status. No runnable tickets → report graph/blockers without claiming implementation. Incomplete → name missing evidence, partial GitHub writes, preserved work; distinguish unverified state from read-back success.

## Completion criteria

- Breakdown Initiative, when needed, used the planner's bundled procedure, read back tickets/native links/artifact mappings without new `hitl` labels, and showed the ticket list before implementation. Existing-ticket specs launched no planner.
- Each integrated ticket has exactly one verified commit from its own implementer, evidence comment, and read-back completed closure in its owning repository. No skipped `hitl` ticket was implemented, commented on, closed, or assigned a closing reference.
- Source repository/base match validated routing; PR title prefix and bare first body line equal `INITIATIVE_ID`, every implemented ticket is covered, and PR remains draft. Pending/failed checks are accurately reported.
- App verification preceded chore, kept proof framework unchanged, preserved evidence outside the worktree, and recorded its verdict/skip; unresolved `fail`/`partial` keeps spec open. Chore commits are verified/pushed, and worktree removal is confirmed before independent review.
- Spec closure satisfies every finalization gate; unresolved review/bug/initiative concerns or posting failures keep it open. No agent path loading failure was ignored.
- Parallel tickets have one serialized cherry-picked commit each, isolated writers, and ticket branches/worktrees removed or reported. Integration worktree is removed or explicitly accounted for; user work remains intact.

## Completeness sweep

Last: re-read the request and map every spec requirement/ticket to code, tests, docs, configuration, and relevant failure/compatibility evidence. Resolve gaps or report explicit deferrals before declaring completion.
