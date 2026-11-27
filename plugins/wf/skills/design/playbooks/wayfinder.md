# Wayfinder

Chart a GitHub decision map and maintain one living HLD throughout discovery. Produce decisions, evidence and the document; implementation requires separate authorization. The root Not yet specified section holds concerns too vague to frame as a topic; child issues own precise questions and risks; the HLD synthesizes supported conclusions. Alternate human decisions and autonomous investigation; helpers always return control here.

## Contents

- Refer by name
- Session and document
- Interview phases
- The Map
- The map body
- Topics
- Topic Types
- Work item approval
- Helper execution
- Prototype approval
- Contract selection
- Research routing
- Fog of war
- Out of scope
- Tracker operations
- Invocation
- Chart the map
- Small effort
- Automatic runs
- Work through the map
- Completion criteria
- Gotchas

## Refer by name

Every map and topic is an issue, so it has a name — its title. In everything the human reads — narration, the map's Decisions-so-far — refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The id and URL don't vanish — a name wraps its link — but they ride inside the name, never stand in for it.

## Session and document

Existing maps resume as mapped efforts: restore the current interview phase, skip initial charting and Small effort, and recover only missing verified document infrastructure. Re-interview changed scope/new human choices only.

1. Before interviews or worktree switches, capture absolute harness root, repository, invocation worktree, dirty state, `@sessionBaseBranch` and its SHA. This is the branch the user started from, not necessarily `main`; leave it unchanged. Persist interview phase/frontier in Grill's session ledger. On resume, use persisted identities. Done when the local base and repository are verified without creating map infrastructure.
2. Run Chart the map through destination interview, separate breadth-first frontier interview and small-effort decision before creating a branch, worktree, HLD seed or issue. Done when the user selected a mapped effort or a standalone continuation.
3. For a mapped effort, use HLD as the only document format; no format question. Resolve detached HEAD, then **Prepare a document worktree** from the captured base. Derive its summary from the confirmed destination; persist branch and ownership outside disposable worktrees. Read the HLD orchestration playbook and Living document resource registered in the router; invoke its Draft document `hld` authoring handoff to seed `docs/ongoing/<initiative-slug>.md` in evolving-draft mode and **Commit the document** before map-topic evidence dispatch. Done when the integration branch, worktree and seed commit are verified.

Wayfinder owns branch prefixes; *Load and follow the `git` skill to run verified Git mechanics for branch naming, creation and worktree lifecycle* using Branches and Worktrees with the selected prefix and summary. Preserve Git's slug normalization, removed initiative/topic IDs, worker ordinals, collision authorization and verified resumes. Explicit caller prefixes override its default feat/fix choice; standalone Research/Prove conventions stay unchanged.

| Work | Prefix |
|---|---|
| Living HLD | `wayfinder/<slug>` |
| Research topic | `research/<slug>` |
| Experiment/verification topic | `prove/<slug>` |
| Contract design Options | `wayfinder/<slug>` |

**Synchronize the document** only after mapped-effort setup; before then persist interview state in the ledger. Synchronize after every research result, Grill session/pause, experiment result/review, Contract design phase, and on resume. Pending approval-gated prototypes update fog/progress only; their design consequences enter the HLD after explicit approval and verified integration. Contract design retains selected-only integration after Choice. Automatically update inside its dedicated worktree without a separate request or confirmation. Read the latest local integration-branch document; apply Living document reconciliation through HLD orchestration and its Draft document `hld update` handoff, then **Commit the document**. Preserve existing diagram approval rules; record a blocked diagram update rather than claiming full readiness. Serialize writes, not whole evidence runs. Record last synchronized topic/result commit and any pending updates on the map. Done when supported consequences appear in all affected sections and the document commit is verified locally.

Research results use `docs/research/<initiative-slug>/`; proof reports, retained evidence and accepted sketches use `docs/prototype/<initiative-slug>/`. Select exact filenames before dispatch; pass the assigned absolute worktree root as output base. Retain accepted sketch packages with rationale, module map and language-native `sketch/` files; standalone temporary roots stay unchanged.

Use owned result worktrees for Prove/Experiment, Deep Module and Code Sketch. Challenge this requires an owned result worktree whenever it changes code or runs tests; read-only inspection and Research may reuse a pinned checkout with isolated outputs. All result worktrees start from a pinned current integration HEAD, not the session base. Independent runs may share that base; dependent runs require prerequisite integration first. Producers never commit or push; Wayfinder owns commit, local merge and cleanup. Keep ownership/state outside disposable worktrees. Preserve runnable proof state through reproduction, user approval and requested review. Prototype approval governs approval-gated payloads at all paths, including explicitly assigned custom destinations; changing a destination does not bypass the gate.

Resume locally: verify refs, ancestry and artifact files before reuse. Missing local state blocks recovery; do not fabricate a remote link or regenerate a guessed result. Legacy maps retain existing PR history untouched; adopt verified content into local integration mode and record the transition without updating, closing or replacing their PRs.

## Interview phases

Wayfinder owns interview phase and breadth-first selection; Grill supplies its existing one-question pacing, fact lookups, ledger/coverage checks, inline records and closing sweep. Read Grill fully as registered in the router. In charting, apply these phase boundaries before its next-question selection or document synchronization:

1. Destination: settle outcome, scope, exclusions and completion boundary only; ask one ready question, wait, and record the answer. User confirmation ends this phase with Grill's closing sweep, then starts the separate frontier interview. Done when the destination is confirmed without requiring downstream decisions to be settled.
2. Frontier: cover major in-scope areas before deepening a single thread. Ask one ready question at a time and wait; recompute dependencies after each answer. Newly unblocked dependents are eligible, but prefer uncovered main areas where dependencies allow. Hold questions awaiting lookups and ask one independent ready question instead. Persist phase, coverage, answers, dependencies and next question in the session ledger. Done when the user confirms sufficient shared understanding of precise questions, coarse fog and dependencies; open downstream decisions remain mapped work.
3. Return: after frontier confirmation and Grill's closing sweep, apply Small effort before branch/worktree, HLD seed or issue creation. Before mapped setup, synchronize interview state only. On existing maps, restore the phase and ask only changed scope/new human choices; document synchronization follows Session and document. Done when the continuation or mapped setup is explicit.

These Wayfinder phase boundaries limit the charting interview, not the overall map's completion criteria. Standalone Grill follows its existing procedure unchanged.

## The Map

The map is a single issue on this repo's GitHub tracker, labelled `wayfinder:map`. Its topics are native sub-issues of the map — see **Tracker operations** and [Wayfinder operations](../references/github.md#wayfinder-operations) for map, child, blocking, and frontier operations.

The map owns fog and a concise decision index. Query child issues for progress; keep detailed commands/artifacts in issue Results and local files. HLD Open Questions belong to users during presentation; agents preserve that section, including blank answers.

### The map body

The whole map at low resolution, loaded once per session. Open topics are not listed — they are open child issues, found by query.

```markdown
## Destination

<what reaching the end of this map looks like — the outcome and decisions
this HLD must settle. One or two lines; every session orients to it
before choosing a topic.>

## Notes

<domain; skills every session should consult; standing preferences for this
effort>

## Document and branches

- Session base: <branch>; starting SHA: <sha>
- Document: HLD; <path>; integration branch: <local branch>; HEAD: <sha>
- Worktree: <absolute path>; ownership record: <path outside worktrees>
- Last synchronized: <result commit>; integrated commit: <sha>; HLD commit: <sha>, or none
- Pending synchronization: <result refs and missing steps or none>
- Pending proposals: <review draft paths/revisions and next action, or none>
- Root-owned verification: <run/status/evidence/next action, or none>

## Decisions so far

<!-- the index — one line per closed topic: enough to judge relevance, then zoom
the link for the detail the topic holds -->

- [<closed topic title>](link) — <one-line gist of the answer>

## Not yet specified

| ID | Unknown / risk and impact | State | Resolve when | Work / next action / owner | Outcome / evidence |
|---|---|---|---|---|---|
| <stable U1> | <in-scope concern too vague to frame as a topic> | <Open / Investigating / Awaiting human / Blocked> | <criterion or missing framing> | <related context; missing framing; next action; owner> | <supported facts, limits and local evidence paths> |

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->
```

### Topics

Each topic is a sub-issue of the map (or of the topic it's narrower than); its issue number is its identity. Its body is the question, sized to one 100K token agent session:

```markdown
## Question

<the decision or investigation this topic resolves>

## Unknowns

<stable unknown/risk IDs, provenance and precise criteria/impact now owned here; no live root fog row required; or whole-HLD discovery scope>

## Work

- Mode: AFK | HITL
- Helper: research | prove | deep-module | sketch | grill | none
- Supporting verification: challenge-this | prove | none
- Scope/inputs: <design, source, prior findings, limits>
- Done when: <deciding evidence or deliverable; Contract design requires user choice>
- Output: <exact caller-owned destinations>

## Blocked by

<!-- One linked topic title per blocker, followed by the finding or decision needed. Empty if none. -->

## Part of

<link to the map>
```

For research topics, add `## Research scope` after `## Question` (see Research routing). After dispatch, persist a `## Result` section with local branch/worktree, pinned integration base SHA, result/integrated/HLD commit SHAs, exact report paths, question/revision/environment identity, actual worker model/effort and pending work. Approval-gated prototype results additionally record review state, exact payload paths/content identity and approval decision/revision; integrated/HLD-result SHAs stay pending until approved integration. Contract design also records candidate phase and user choice. Keep the answer in the resolution comment.

Experiment topics use Prove. Challenge this is supporting verification on the current issue or a root-owned run, never its own tracking issue. Persist run identity, scope, method, worker/model, evidence, pending integration and risk/mitigation criteria on that existing owner; use Risk verification registered in the router.

Each topic carries its tracker label: Research → `wayfinder:research`; Experiment → `wayfinder:experiment`; Decision → `wayfinder:grilling`; Task → `wayfinder:task`; Contract design → `wayfinder:contract-design` (see Topic Types). Preserve these label names.

A session claims a topic by assigning it to itself, first, before any work, so concurrent sessions skip it. That assignee is the claim: an open, unassigned topic is unclaimed.

Record Research and Contract design prerequisites for experiments in `## Blocked by`, including the evidence or choice each experiment needs. Blocking keeps the `## Blocked by` body convention above as its source of truth; unlike implementation topics, Wayfinder decisions do not require native dependency links. A topic is unblocked when every topic named in its `Blocked by` section is closed; the frontier is the open, unblocked, unclaimed children — the edge of the known. An unreadable blocker is not confirmed closed.

The answer isn't part of the body — it's recorded as a resolution comment on close (see Work through the map). Record artifact paths and local SHAs on the issue; they require the local checkout until separately published. Never invent remote URLs for unpushed evidence.

## Topic Types

Use the topic type guide registered in the router when the distinction is unclear.

Every topic is either HITL — human in the loop, worked with a human who speaks for themselves — or AFK, driven by the agent alone. A HITL topic only resolves through that live exchange; the agent never stands in for the human's side of it.

- **Research** (AFK): Gather primary-source evidence a decision depends on. Per Helper execution, *Load and follow the `research` skill to investigate technical questions across source code, docs, packages and external evidence and return cited findings* with Research routing inputs.
- **Experiment** (AFK for factual claims; HITL for human judgment): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to. Material claims follow Risk verification registered in the router; other factual claims, per Helper execution, *Load and follow the `prove` skill to confirm or refute technical claims by executing tests, runnable prototypes, GUI E2E checks, or cloud experiments* with claim, deciding criteria, owned result worktree and exact report path. Name the execution method and deciding observation; source-only findings cannot resolve an Experiment. Retain evidence locally and index paths/SHAs on the owning issue; synthesize only supported conclusions into HLD sections. Use when "does this call/logic behave as expected" is the key question. Verified empirical answers enter Prototype approval before integration and resolution; acceptance of a trade-off, preference, or product choice still requires the user.
- **Decision** (HITL): Conversation. The default case. Always use the Grill playbook to resolve the Wayfinder Decision topic through an interview. Resolving one may surface decisions narrower than the question itself — child-scoped to it rather than independent frontier items; record those as sub-issues of the Decision topic (see Tracker operations) via GitHub's native sub-issue relationship, not a fresh body-text field.
- **Task** (HITL or AFK): Code Sketch preparation or prerequisite manual work that must happen before a decision can be made — nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that does rather than decides — and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Code Sketch results require Prototype approval and integration before resolution. Other Tasks resolve when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later topics depend on.
- **Contract design** (AFK → HITL): Choosing the shape of a contract from radically different designed options. Use instead of Decision when the question introduces a new contract or interface, an abstraction built on inheritance (base class, interface hierarchy, polymorphic substitution), or a significant change to an existing contract (breaking signature, invariants, error modes, ordering, or seam placement). Two phases, never collapsed into one:
  1. **Options (AFK)** — per Helper execution, read the Deep Module playbook registered in the router fully and run it with caller grounding, owned result worktree and exact option root `docs/prototype/<initiative-slug>/<ticket-slug>/deep-module/`. Produce 3+ source sketch packages, each with its own Markdown rationale, plus comparison. For each option, *Load and follow the `doc-diagram` skill to create Mermaid class diagrams* in delta mode for contract type relationships. Validate every package; record candidate paths/revision/worktree and one-line option gists on the topic; release the claim. Retain owned worktree; **do not merge Options**. Done when the user can review all options and the same topic awaits Choice.
  2. **Choice (HITL)** — present option sketches, rationales, diagrams and recommendation through Grill; user chooses an option or agreed hybrid. Run Contract selection before synchronization and closure. Done when only selected artifacts and considered-option notes are integrated and the user decision is recorded.

## Work item approval

**MUST** get user approval before creating the map or any map child or sub-issue and before dispatching Research or other evidence work for it. Applies on chart, follow-ups, sub-issues, changed proposals after every result/answer and on resume.

1. Save the proposed batch before requesting approval: one `map.md` on chart, one unique numbered Markdown file per child/sub-issue (for example `01-blob-read-behavior.md`) under `<document-worktree>/tmp/wayfinder/<initiative-slug>/proposals/<batch-id>/r<revision>/`. Use collision-safe batch IDs; keep drafts untracked and out of document/result commits. Each file contains `Draft — unapproved`, stable proposal key/revision, title, labels, parent, blockers and the full rendered issue body. Preserve Mode, Helper, Question, Unknown IDs and Research scope where applicable. Prototype topics add: Experiment → claim, deciding criteria, report path; Code Sketch → target modules, sketch root; Contract design → contract scope, option count, option root; each → owned worktree and Prototype approval before integration. Use stable proposal keys for unpublished parents/blockers, never invented issue numbers or URLs. Record paths/revisions and pending state in the ownership record outside disposable worktrees. Done when every proposal has a complete readable file.
2. Present one bullet per proposal, map first, with its title linked to the actual Markdown file and a short type/mode summary. Use host-supported clickable file links; ChatGPT uses `[Title](sandbox:/absolute/path/file.md)`. Verify files exist and link targets match; report write/link failures and repair before requesting approval. Ask the user to approve all or selected titles, edit, add, drop or merge. Opening links is not approval. Done when the user answered against the linked revision.
3. Apply edits and rerun the Contract test on changed questions. Write changed proposals into a new revision directory; retain previous revisions and re-present changed titles with fresh links for approval. Keep unchanged approvals tied to their original files; leave unapproved items pending on partial approval. Done when each proposal is approved, pending or dropped with its exact revision recorded.
4. Create only approved topics via **Create a topic** / **Create a sub-issue**, using the approved title, labels and body. Record approved revision/content identity before creation; substitute only verified parent/blocker issue links for proposal keys, recording that mapping. Substantive changes require fresh approval. Uncreated precise proposals stay in retained drafts and Pending proposals with their next action; approval delay or dropping a proposal does not make its question fog. Explicit discard retains an unresolved question/owner in pending state unless the user excludes it; only then move it to Out of scope. Retain pending drafts across pauses, publication failures and reconciliation; on resume verify the same files/content before use, reporting missing or changed drafts instead of assuming approval. Clean only owned drafts after their publication and links are verified or explicit discard; preserve unrelated files and pending proposals. Done when approved tracker writes are verified and remaining drafts retain their next action.

Silence, destination approval or approval of an earlier batch is not work item approval. Reusing an existing open topic unchanged needs no new approval; changing its question or scope does. Root-owned Challenge this runs are not topics. While approval is pending, continue only already-approved independent work.

## Helper execution

Run each helper in the Wayfinder session with its default dispatch. **MUST NOT** wrap a helper in a subagent. Skip Architect.

| Helper | Run | Workers |
|---|---|---|
| Research | *Load and follow the `research` skill to investigate technical questions across source code, docs, packages and external evidence and return cited findings* with Research routing inputs | Research-owned |
| Prove | *Load and follow the `prove` skill to confirm or refute technical claims by executing tests, runnable prototypes, GUI E2E checks, or cloud experiments* | Prove-owned `prover` worker |
| Challenge this | Per Risk verification, *Load and follow the `challenge-this` skill to adversarially test a design and report reproducible counterexamples* | Challenge-this-owned |
| Deep Module | Read the Deep Module playbook registered in the router fully; run it | Design It Twice designers |
| Code Sketch | Read the Sketch playbook registered in the router fully; run it in Wayfinder context | None; wide lookups via the `hunty` agent |
| Grill | Read the Grill playbook registered in the router fully; run it | None; lookups via the `hunty` agent |

Supply question/scope, pinned checkout/revision, unknown IDs, existing owner, prerequisites, limits, exact outputs and cleanup ownership. Run helpers sequentially. Dependent work waits for integrated prerequisites. Record returned artifacts, findings, coverage, actual worker type/model and new unknowns on the issue/root Result. Wayfinder owns commits/integration. Required worker unavailable → record the blocked request on the owner; continue independent work.

Grill asks one question at a time and records the user's actual answer. No agent speaks for the user or chooses subjective trade-offs. Only the user ends Grill; preserve its closing sweep. Done when each run has an accountable owner/result or named blocker.

## Prototype approval

Apply to Prove/Experiment, Code Sketch and Contract design payloads. Research and Challenge this evidence integrate automatically, regardless of report destination. Challenge this requires no approval, including when its verification changes code or runs tests: isolate those actions in an owned result worktree, independently reproduce findings, retain reports/proof patches and restore production-source edits, then Integrate a result and Synchronize the document. Update the owning topic/root run, coarse root fog and supported HLD design conclusions automatically; precise residual risks remain on their owner. Challenge this does not authorize production fixes or human risk acceptance. Supporting Prove runs used solely for Challenge this verification inherit this automatic evidence flow; separately requested prototype work retains the gate. Generation and independent verification remain AFK. Prototype lifecycle: generated → verified → awaiting approval → approved → integrated.

1. Validate the result in its owned worktree. Retain reports, patches, runnable reproduction state and sketch packages there; restore production-source edits before preparing the incoming payload. Persist worktree/branch, pinned base, exact payload inventory/content identity, evidence/limits and review state on the existing issue/root run. Done when the concrete reviewed revision is recoverable without integration.
2. Present the result, limits and exact payload for explicit user approval; release the claim and keep the issue open with status Awaiting human. Contract Options await Choice; follow Contract selection for the selected payload. Keep pending prototype artifacts out of integration commits/merges and their conclusions out of the HLD. Continue independent work; dependent runs requiring integrated artifacts wait. Done when the user can review the retained prototype and its pending step is recorded.
3. Record approval against that payload identity. Passing checks, silence, recommendations, partial feedback and approval of a plan are not prototype approval. An explicit Contract Choice approving the concrete selected package satisfies this gate once; a not-yet-reviewed hybrid requires review. Changes/rejection retain the worktree and exact next action; revisions require fresh approval. Done when approval covers the current payload or the result remains awaiting human input.
4. Verify approval, payload identity and integration drift before Integrate a result; material payload/contract changes require renewed approval. Then synchronize HLD/tracker and resolve only when evidence and completion criteria also pass. Clean owned worktrees only after verified integration, synchronization and all reproduction/review consumers finish. Done when approved artifacts and their consequences are verified locally, or the exact pending step/worktree is retained.

On resume, recover the same pending worktree and approval identity; do not regenerate unchanged results or treat an unclaimed issue as permission to rerun. Missing local state blocks recovery. Approved results resume integration; already merged results resume reconciliation/tracker writes without duplicate merges. Conflicts retain worktrees; reproduce changed mechanisms and renew approval for material payload changes. Preserve legacy integrated evidence without rewriting history.

## Contract selection

1. Read the explicit user choice and retained candidate worktree/revision. An unanswered recommendation is not consent. Materialize a selected hybrid; ask only for unresolved substantive choices. Done when the final contract matches the user's selection.
2. Prepare `deep-module/selected/{rationale.md,module-map.md,sketch/}` with selected contract diagrams and `deep-module/considered-options.md`. Notes summarize other interfaces/seams, trade-offs and actual rejection reasons, distinguishing user choice from agent recommendation. Keep candidate source trees outside the payload. Done when chosen shape and considered alternatives are reviewable.
3. Apply Prototype approval to the final selected payload, reusing explicit Choice approval only when it covers that concrete revision. Use **Integrate a result** only after approval. If candidates were already committed, construct a clean selected-only result from the pinned integration base: *Load and follow the `git` skill to run verified Git mechanics for branch creation, commit and worktree lifecycle*; merging deletions would still bring rejected sources through ancestry. Preserve candidate worktree until verification. Revalidate integration drift; return materially changed choices to the user. Done when incoming diff/ancestry contains selected artifacts and notes only.
4. Synchronize supported HLD conclusions, root fog/decision index and topic Result. Comment verified choice/evidence, close the issue, then clean owned candidate resources after consumers finish. Failure retains exact pending step and worktree. Done when choice, integration and tracker completion are separately confirmed.

## Research routing

Automatically select the relevant scope for factual gaps. Codebase lookups spawn the `hunty` agent; mechanism and inspection questions use How; cloud provider facts use Cloud; external primary-source facts use Web. Historical intent uses Research Why. Missing external checkouts block system evidence; use Web when public documentation suffices.

| Option | Route | Scope |
|---|---|---|
| Web | `web` | Public primary sources, such as specifications and official docs |
| Cloud | `cloud` | Provider, service, and whether live values matter |
| Current system | `system` | Repository or deployable being mapped and inspection axis |
| External system | `system` | Named external repository or deployable and inspection axis. If only public docs suffice, use Web. |

For a system question, choose `Behavior` for one deployable, `Flow` for handoffs across deployables, `Data` for a data boundary, or `focused` for an isolated call or package API. This axis sets the primary lens. The question sets the depth, with an explicit inspection requesting full coverage.

Record one bullet per research part in `## Research scope`: route, target (if known for Web), system axis (for How), and the part's question when the topic spans multiple parts. For Cloud, include the provider, service, and need for live values.

For every research dispatch, write one request holding the topic's Question, its Research scope bullets, content framing, and an exact absolute save path per part under the topic worktree: preserve an explicit topic destination; otherwise `docs/research/<initiative-slug>/<ticket-slug>.md` for one part or `docs/research/<initiative-slug>/<ticket-slug>-<part-slug>.md` for separate parts. Wayfinder owns this convention. For older topics infer and persist scope before dispatch.

## Fog of war

Not yet specified holds only in-scope concerns too vague to frame as a topic. Test sharpness, not answerability: a precise question belongs in a typed topic even when blocked, partial, conflicting or awaiting proof approval. Keep decided work in Decisions so far and excluded work in Out of scope; preserve HLD Open Questions for users.

Assign stable initiative-local IDs; retain consequence, missing framing, next action/owner and evidence pointers. As a concern becomes precise, transfer its ID, provenance, criteria, risk trigger/failure/impact, mitigation and verification limits to its owning topic through Work item approval. Remove the graduated portion only after the approved topic and links are verified, or its exact draft and Pending proposals state are durable. Keep genuinely coarse remainder with predecessor links. Pending approval is a workflow state, not fog.

After each answer/result/resume, choose the cheapest useful next helper: Research for facts, Prove for a claim, Challenge this for blind spots, Deep Module/Code Sketch for shapes, Grill for human choices. A bounded precise research question may clarify a larger coarse area; topic that question and retain only the unspecified remainder in fog. Challenge this stays embedded on an existing owner or root-owned verification run, never its own tracking issue; concrete run status belongs in Result/Root-owned verification, not coarse fog.

Keep inconclusive or unmitigated precise work open on its owner with limits and next action. Reopen the same owning question/ID when new evidence invalidates a result; do not return it to fog merely because it is unresolved. Persist supported outcomes in topic resolution and a Decisions so far pointer. Never repeat unchanged inconclusive runs; change prerequisites, evidence or method. Completion checks include open topics, pending proposals, human choices, root-owned runs, coarse fog and synchronization; empty fog alone is not completion.

## Out of scope

Fog only ever gathers toward the destination. The destination fixes the scope, so work beyond it is out of scope — it isn't fog, and it doesn't belong in Not yet specified. It gets its own Out of scope section on the map: work you've consciously ruled out of this effort. Scope, not sharpness, lands it here.

Out-of-scope work never graduates — the frontier stops at the destination — so it returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

Ruling something out of scope is a scoping act, not a step on the route. When a topic that already exists turns out to sit past the destination — mis-scoped in while charting, or exposed by a resolution — close it (a closed topic is unambiguously off the frontier) and leave one line in the Out of scope section: the gist plus why it's out of scope, linking the closed topic. It stays out of Decisions so far, which records the route actually walked — a scope boundary isn't a step on it.

## Tracker operations

Load [Wayfinder operations](../references/github.md#wayfinder-operations) registered in the router and follow its GitHub operations for this tracker repository. Keep GitHub-specific commands in the reference; do not configure another backlog backend.

- **Create the map**: only after Work item approval. **Create issue** with label `wayfinder:map` and the map body template above.
- **Create a topic**: only after Work item approval. **Create Wayfinder sub-issue** with `parentIssueNumber` = the map, label `wayfinder:<type>`, body = Question + Unknowns + Work + Research scope (research only) + Blocked by + Part of; Result is added on dispatch.
- **Create a sub-issue**: only after Work item approval. **Create Wayfinder sub-issue** with `parentIssueNumber` = the topic it's narrower than, label `wayfinder:<type>`, body = Question + Unknowns + Work + Research scope (research only) + Blocked by + Part of; Result is added on dispatch. Use when a resolution surfaces a decision that's child-scoped to the topic just worked, not a fresh frontier item.
- **Claim a topic**: **Assign issue**.
- **Release a topic**: **Unassign issue**. Use when a session ends without resolving, including prototypes awaiting approval and Contract Options awaiting Choice.
- **Find the frontier**: **List sub-issues** of the map, then of every open child recursively; keep open topics with a `wayfinder:<type>` label, and drop any that's assigned, or whose `Blocked by` section names a still-open topic.
- **Resolve a topic**: **Synchronize the document**, **Comment on issue** with the verified answer, then **Close issue**. Human-choice topics need the recorded user decision; factual questions need sufficient evidence; approval-gated prototype work additionally needs Prototype approval and verified integration.
- **Read the map / a topic**: **Read issue**. **Read a topic's sub-issues**: **List sub-issues**.

**Label not found** (`wayfinder:map`, `wayfinder:research`, `wayfinder:experiment`, `wayfinder:grilling`, `wayfinder:task`, or `wayfinder:contract-design` missing): ask the user to follow the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md) in labels-only mode, then retry.

## Invocation

Supply a loose idea to chart a map, or a map issue number or URL and an optional topic number to resume. Handle one human decision at a time. Use **Automatic runs** for parallel artifact work. When using Grill for a Wayfinder step, resume this playbook after Grill returns.

**Contract test** — apply to every question being classified: does it introduce a new contract, an inheritance-based abstraction, or a significant contract change? Yes → type `contract-design`, not `grilling`.

### Chart the map

1. Capture session identity per Session and document. Use Grill to name the destination: settle outcome, scope, exclusions and completion boundary, then get user confirmation. Ask one question at a time and wait for its answer. Done when the destination is confirmed; this does not approve topics.
2. Start a separate breadth-first frontier interview through Grill. Cover major in-scope areas before deepening one thread; ask exactly one ready question, wait, then recompute dependencies. Identify precise decisions, blocked questions, coarse fog and first useful steps. The interview maps work rather than resolving every downstream decision; user confirmation of sufficient shared understanding ends this phase, with Grill's closing sweep. Done when breadth, dependencies and remaining work are explicit.
3. Apply Small effort before infrastructure creation. If mapped, finish Session and document setup, then propose the map and currently specifiable topics, typing each by the Contract test. Run Work item approval with saved Markdown drafts and clickable bullets; create approved issues, verify native child links, then wire blockers in a second pass. Done when integration state and approved tracker state are verified.
4. Run **Automatic runs** on approved topics without a further dispatch confirmation gate. Done when ready factual work is resolved or blocked and the next human decision is presented.

### Small effort

If the route is clear, no coarse fog remains and the whole journey fits one session, stop before branch/worktree, HLD seed or issue creation. Present the bounded outcome and ask one continuation question: standalone Grill, requested HLD/Spec, or explicitly tracked map. Wait for the choice; no automatic implementation or handoff. Many precise questions or substantial dependencies still warrant a map even with empty fog. Reuse existing deliverable authorization after the chosen continuation. Existing maps resume normally; retain their documents/worktrees rather than collapsing or deleting them.

### Automatic runs

1. Reconcile Not yet specified and existing child issues on initial creation, each result/answer and resume. Reuse sufficient evidence for matching question/scope/revision/dependencies/environment; reuse existing topics or propose precise Research, Experiment, Contract design or Code Sketch Task work through Work item approval. Keep coarse fog without fabricated detail. Done when every actionable gap has approved work, a pending approval or a named blocker.
2. Select Research routing for facts, Prove for a falsifiable condition, Deep Module for contract options, Code Sketch for usage/type shape. Material risks use Risk verification; Challenge this can cover a bounded design or the whole HLD without its own topic. Human preferences/contract choice/risk acceptance remain human. Done when the next observation or required input is explicit.
3. Claim ready open/unclaimed approved issue phases; require blockers closed and prerequisites integrated/accessibly pinned. For root-owned Challenge this persist run identity instead. Use Helper execution. For approval-gated prototypes and for Challenge this code changes or test execution, *Load and follow the `git` skill to run verified Git mechanics for worktree lifecycle* to prepare owned result worktrees; read-only inspection/Research may use a verified pinned checkout with separate outputs. Skip existing runs awaiting approval instead of redispatching them. Done when each eligible run has its scoped environment or precise blocker.
4. Run each helper per Helper execution with question/framing, prior evidence, original harness root, revision/environment/limits, ownership and exact destinations. Research uses Research routing inputs. Prove uses `docs/prototype/<initiative-slug>/<ticket-slug>/report.md`; Challenge this uses `docs/prototype/<initiative-slug>/<owner-or-root-run>/challenge-this/<run>/report.md`. Code Sketch uses `docs/prototype/<initiative-slug>/<ticket-slug>/code-sketch/`; Contract Options use Topic Types. Pass absolute output base and preserve valid explicit destinations. Done when helpers return supported results or explicit gaps.
5. Validate citations, sketch contracts and independent empirical reproductions. Approval-gated prototype outputs: follow Prototype approval, retaining the worktree without integration until approval; Contract Options retain Choice on the same topic. Research and Challenge this outputs: **Integrate a result**, then **Synchronize the document** automatically; update root fog and supported HLD conclusions without an approval pause. Retain proof probes as patches, never production changes. Done when pending approval state or approved local result ancestry/artifacts/HLD commit is verified.
6. Complete factual topics only with deciding evidence and synchronized conclusions; approval-gated prototype topics also require recorded approval and verified integration. Partial/inconclusive work stays open/blocked; experiments needing human judgment stay open. Embedded Challenge this completion does not close its owner or resolve unmitigated risks. Update fog and create/reuse actual follow-up work; continue newly ready independent work. Done when remaining work needs human input, prerequisites or a scope decision.

### Work through the map

1. Read the map and persisted document/base/integration-branch/worktree/commit identities. Verify local state and pending approval identity; resume approved prototype integration, automatic Research/Challenge this integration or pending synchronization before selecting new work. Keep unapproved prototypes awaiting human review. Legacy maps lacking these fields require Session and document setup; resolve the original base before creating branches. Done when the canonical worktree/document/integration branch are recovered, not duplicated.
2. Run Automatic runs for eligible questions without waiting for a queue request. Then choose the named human topic or next human frontier topic; claim it before work. Done when supporting factual gaps are resolved or explicitly blocked.
3. Use Topic Types for the human phase: Grill, Prototype approval, Contract Choice, or experiment judgment. Synchronize confirmed outcomes even on pause; complete Grill's closing sweep before declaring a session resolved. Done when user decisions are recorded or pending.
4. Resolve completed topics, append a context pointer to Decisions so far, and graduate newly precise fog into approved work or durable pending proposals through Fog of war; preserve criteria and blockers on its owner. Re-scope invalidated topics; out-of-scope closures belong in Out of scope, never Decisions so far. Synchronize and rerun Automatic runs for new in-scope factual questions. Done when the next frontier reflects current evidence.

Expect concurrent tracker edits. Re-read before writes and preserve other sessions' contributions.

## Completion criteria

- The HLD reflects supported integrated results and confirmed sessions; precise partial/conflicting questions remain on open topics, pending proposals or root-owned runs; only unframeable concerns remain in root Not yet specified, while HLD Open Questions remain user-owned. Reprocessing the same result creates no duplicate rows, sections, sources, topics or merges.
- Verified evidence is retained locally and indexed by root/child issues; Prove/Experiment and sketch prototypes merge only after explicit approval of their current payload. Challenge this evidence integrates and updates root fog/HLD automatically, with code changes/tests isolated in an owned worktree. Contract design merges selected artifacts only after user choice. HLD contains conclusions without evidence appendices. Report its HEAD, paths, open choices and blocked integration/synchronization.
- No automatic push, PR creation, PR merge/close or merge into the session base. Confluence publishing requires explicit `design publish-hld`; it grants no GitHub publication authority.
- Last, re-read the destination and requested scope; map every obligation to document content, evidence or an explicit remaining blocker. Do not declare the design ready with missing coverage.

## Gotchas

- Resume legacy maps by verified identity. Reconcile legacy root rows and separate registers with existing topics: transfer precise questions/risks to verified owners, preserving IDs, criteria, evidence and history before removing duplicate rows; retain coarse remainder only. Missing/ambiguous owners block affected migration, never justify dropped evidence or duplicate topics; keep Contract design identity and Options/Choice state. Do not rewrite existing candidate history; identify legacy integrated alternatives as superseded.
- Move unambiguously agent-owned discovery rows from legacy HLD Open Questions to their precise owner or coarse root fog before removing them; preserve user presentation rows, and ask when ownership is ambiguous.
- Preserve prior Challenge this history. Pending verification belongs to the current issue/root; reconcile any legacy wrapper before retiring it, never create another wrapper.
- Missing local refs/worktrees block recovery; retain candidates across Choice pauses. Never invent remote artifact links or delete the sole evidence copy. Expect concurrent edits: reread root/issue before writes and preserve others' contributions.
