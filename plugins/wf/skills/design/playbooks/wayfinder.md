# Wayfinder

Chart a GitHub decision map and maintain one living HLD throughout discovery. Produce decisions, evidence and the document; implementation requires separate authorization. The root Not yet specified section holds unknowns and risks; child issues track concrete work; the HLD synthesizes supported conclusions. Alternate human decisions and autonomous investigation; helpers always return control here.

## Contents

- Refer by name
- Session and document
- The Map
- The map body
- Tickets
- Ticket Types
- Helper dispatch
- Contract selection
- Research routing
- Fog of war
- Out of scope
- Tracker operations
- Invocation
- Chart the map
- Automatic runs
- Work through the map
- Completion criteria
- Gotchas

## Refer by name

Every map and ticket is an issue, so it has a name — its title. In everything the human reads — narration, the map's Decisions-so-far — refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The id and URL don't vanish — a name wraps its link — but they ride inside the name, never stand in for it.

## Session and document

1. Before interviews or worktree switches, capture absolute harness root, repository, invocation worktree, `@sessionBaseBranch` and its SHA. This is the branch the user started from, not necessarily `main`; leave it unchanged. Resolve detached HEAD before branch creation. On resume, use the map's persisted base instead of the caller's current branch. Done when the local base and repository are verified.
2. Use HLD as the only Wayfinder document format; no output-format selection question. Automatically name/create its branch and dedicated owned worktree using **Prepare a document worktree**. Derive the branch summary from the initial request; keep that recorded name if Grill later refines the document slug. Do this before destination/frontier Grill. Done when ownership and branch are recorded outside disposable worktrees.
3. After destination Grill establishes scope/slug, read the HLD playbook and Living document resource registered in the router. Seed `docs/ongoing/<initiative-slug>.md` in that worktree using evolving-draft mode. Use **Commit the document** before evidence dispatch. Done when the seed is committed locally on the integration branch.

Wayfinder owns branch prefixes; *Load and follow the `git` skill to run verified Git mechanics for branch naming, creation and worktree lifecycle* using Branches and Worktrees with the selected prefix and summary. Preserve Git's slug normalization, removed initiative/ticket IDs, worker ordinals, collision authorization and verified resumes. Explicit caller prefixes override its default feat/fix choice; standalone Research/Prove conventions stay unchanged.

| Work | Prefix |
| --- | --- |
| Living HLD | `wayfinder/<slug>` |
| Research ticket | `research/<slug>` |
| Experiment/verification ticket | `prove/<slug>` |
| Contract design Options | `wayfinder/<slug>` |

**Synchronize the document** after every research result, Grill session/pause, experiment result/review, Contract design phase, and on resume. Candidate Options update fog/progress only; their design consequences enter the HLD after user selection and selected-only integration. Automatically update inside its dedicated worktree without a separate request or confirmation. Read the latest local integration-branch document; apply Living document reconciliation and HLD's incremental rules, then **Commit the document**. Preserve existing diagram approval rules; record a blocked diagram update rather than claiming full readiness. Serialize writes, not whole evidence runs. Record last synchronized ticket/result commit and any pending updates on the map. Done when supported consequences appear in all affected sections and the document commit is verified locally.

Research results use `docs/research/<initiative-slug>/`; proof reports, retained evidence and accepted sketches use `docs/prototype/<initiative-slug>/`. Select exact filenames before dispatch; pass the assigned absolute worktree root as output base. Retain accepted sketch packages with rationale, module map and language-native `sketch/` files; standalone temporary roots stay unchanged.

Use owned result worktrees for Deep Module/Code Sketch and mutating proofs; read-only work may reuse a pinned checkout with isolated outputs. All result worktrees start from a pinned current integration HEAD, not the session base. Independent runs may share that base; dependent runs require prerequisite integration first. Producers never commit or push; Wayfinder owns commit, local merge and cleanup. Keep ownership/state outside disposable worktrees. Preserve runnable proof state through reproduction and requested review.

Resume locally: verify refs, ancestry and artifact files before reuse. Missing local state blocks recovery; do not fabricate a remote link or regenerate a guessed result. Legacy maps retain existing PR history untouched; adopt verified content into local integration mode and record the transition without updating, closing or replacing their PRs.

## The Map

The map is a single issue on this repo's GitHub tracker, labelled `wayfinder:map`. Its tickets are native sub-issues of the map — see **Tracker operations** and [Wayfinder operations](../references/github.md#wayfinder-operations) for map, child, blocking, and frontier operations.

The map owns fog and a concise decision index. Query child issues for progress; keep detailed commands/artifacts in issue Results and local files. HLD Open Questions belong to users during presentation; agents preserve that section, including blank answers.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are not listed — they are open child issues, found by query.

```markdown
## Destination

<what reaching the end of this map looks like — the outcome and decisions
this HLD must settle. One or two lines; every session orients to it
before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this
effort>

## Document and branches

- Session base: <branch>; starting SHA: <sha>
- Document: HLD; <path>; integration branch: <local branch>; HEAD: <sha>
- Worktree: <absolute path>; ownership record: <path outside worktrees>
- Last synchronized: <result commit>; integrated commit: <sha>; HLD commit: <sha>, or none
- Pending synchronization: <result refs and missing steps or none>

## Decisions so far

<!-- the index — one line per closed ticket: enough to judge relevance, then zoom
the link for the detail the ticket holds -->

- [<closed ticket title>](link) — <one-line gist of the answer>

## Not yet specified

| ID | Unknown / risk and impact | State | Resolve when | Work / next action / owner | Outcome / evidence |
| --- | --- | --- | --- | --- | --- |
| <stable U1> | <coarse concern or precise question> | <Open / Investigating / Awaiting human / Blocked> | <criterion or missing framing> | <named child links or root-owned run; next action; owner> | <supported facts, limits and local evidence paths> |

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a sub-issue of the map (or of the ticket it's narrower than); its issue number is its identity. Its body is the question, sized to one 100K token agent session:

```markdown
## Question

<the decision or investigation this ticket resolves>

## Unknowns

<root Not yet specified anchor and stable IDs; or whole-HLD discovery scope>

## Work

- Mode: AFK | HITL
- Helper: research | prove | deep-module | sketch | grill | none
- Supporting verification: challenge-this | prove | none
- Scope/inputs: <design, source, prior findings, limits>
- Done when: <deciding evidence or deliverable; Contract design requires user choice>
- Output: <exact caller-owned destinations>

## Blocked by

<!-- One linked ticket title per blocker, followed by the finding or decision needed. Empty if none. -->

## Part of

<link to the map>
```

For research tickets, add `## Research scope` after `## Question` (see Research routing). After dispatch, persist a `## Result` section with local branch/worktree, pinned integration base SHA, result/integrated/HLD commit SHAs, exact report paths, question/revision/environment identity, actual worker model/effort and pending work. Contract design records candidate phase/worktree/revision and user choice; integrated/HLD-result SHAs stay pending until selected-only integration. Keep the answer in the resolution comment.

Experiment tickets use Prove. Challenge this is supporting verification on the current issue or a root-owned run, never its own tracking issue. Persist run identity, scope, method, worker/model, evidence, pending integration and risk/mitigation criteria on that existing owner; use Risk verification registered in the router.

Each ticket carries a `wayfinder:<type>` label — one of `research`, `experiment`, `grilling`, `task`, `contract-design` (see Ticket Types).

A session claims a ticket by assigning it to itself, first, before any work, so concurrent sessions skip it. That assignee is the claim: an open, unassigned ticket is unclaimed.

Record Research and Contract design prerequisites for experiments in `## Blocked by`, including the evidence or choice each experiment needs. Blocking keeps the `## Blocked by` body convention above as its source of truth; unlike implementation tickets, Wayfinder decisions do not require native dependency links. A ticket is unblocked when every ticket named in its `Blocked by` section is closed; the frontier is the open, unblocked, unclaimed children — the edge of the known. An unreadable blocker is not confirmed closed.

The answer isn't part of the body — it's recorded as a resolution comment on close (see Work through the map). Record artifact paths and local SHAs on the issue; they require the local checkout until separately published. Never invent remote URLs for unpushed evidence.

## Ticket Types

Use the ticket type guide registered in the router when the distinction is unclear.

Every ticket is either HITL — human in the loop, worked with a human who speaks for themselves — or AFK, driven by the agent alone. A HITL ticket only resolves through that live exchange; the agent never stands in for the human's side of it.

- **Research** (AFK): Gather primary-source evidence a decision depends on. *Load and follow the `research` skill to investigate technical questions across source code, docs, and the web and return cited findings* using the ticket's question and scope (see Research routing).
- **Experiment** (AFK for factual claims; HITL for human judgment): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to. Material claims use Prove; embedded Challenge this follows Risk verification registered in the router; other factual claims use *Load and follow the `prove` skill to confirm or refute one technical claim with reproducible evidence.* Retain evidence locally and index paths/SHAs on the owning issue; synthesize only supported conclusions into HLD sections. Use when "does this call/logic behave as expected" is the key question. Verified empirical answers resolve automatically; acceptance of a trade-off, preference, or product choice still requires the user.
- **Grilling** (HITL): Conversation. The default case. Always use the Grill playbook to resolve the Wayfinder grilling ticket through an interview. Resolving one may surface decisions narrower than the question itself — child-scoped to it rather than independent frontier items; ticket those as sub-tickets of the grilling ticket (see Tracker operations) via GitHub's native sub-issue relationship, not a fresh body-text field.
- **Task** (HITL or AFK): Code Sketch preparation or prerequisite manual work that must happen before a decision can be made — nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that does rather than decides — and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later tickets depend on.
- **Contract design** (AFK → HITL): Choosing the shape of a contract from radically different designed options. Use instead of Grilling when the question introduces a new contract or interface, an abstraction built on inheritance (base class, interface hierarchy, polymorphic substitution), or a significant change to an existing contract (breaking signature, invariants, error modes, ordering, or seam placement). Two phases, never collapsed into one:
  1. **Options (AFK)** — directly spawn Deep Module through Helper dispatch. *Load and follow the `design` skill to resolve interface decisions* using `deep-module`, caller grounding and exact option root `docs/prototype/<initiative-slug>/<ticket-slug>/deep-module/`. Produce 3+ source sketch packages, each with its own Markdown rationale, plus comparison. For each option, *Load and follow the `doc-diagram` skill to create Mermaid class diagrams* in delta mode for contract type relationships. Validate every package; record candidate paths/revision/worktree and one-line option gists on the ticket; release the claim. Retain owned worktree; **do not merge Options**. Done when the user can review all options and the same ticket awaits Choice.
  2. **Choice (HITL)** — present option sketches, rationales, diagrams and recommendation through Grill; user chooses an option or agreed hybrid. Run Contract selection before synchronization and closure. Done when only selected artifacts and considered-option notes are integrated and the user decision is recorded.

## Helper dispatch

Spawn skill-capable `general-purpose` subagents directly for every helper and nested helper, including Research, Prove, Deep Module, Code Sketch, Challenge this and Grill. Do not invoke the Subagents skill or route Wayfinder work through Architect. Set `@helperDispatch` to this verbatim policy and pass it transitively; it overrides helper defaults for dispatch only, preserving their evidence/verification contracts.

> Spawn a general-purpose subagent directly. Randomly choose Opus or Sol with equal probability, resolve the latest supported model in that family from the host catalog, and set reasoning/thinking to medium. Current repository IDs: `claude-opus-5.5`, `gpt-6.1-sol`; verify availability rather than guessing a version. Pass model and effort separately. If one family is unavailable, use the other at medium and record fallback; if neither family is available or medium effort is unsupported, report the dispatch blocker. Do not load or invoke the Subagents skill. Forward this policy to nested workers.

Record actual model/effort on the existing issue/root run; reuse selection on worker resume. Brief exact skill name/current description with 3–6 distinctive keywords in *Load and follow* form; require full skill body, selected route and required resources before execution. Supply scope, pinned checkout/revision, unknown IDs, existing owner, prerequisites, limits, exact outputs and cleanup ownership. Independent runs may execute concurrently; dependent work waits for integrated prerequisites. Workers return artifacts, findings, coverage and new unknowns; Wayfinder owns commits/integration.

For Research codebase evidence, directly spawn read-only general-purpose workers with Research's Explore/inspection inputs and local-target constraints under this policy; no Hunter dependency. Grill subagents prepare one question at a time; Wayfinder relays it and returns the user's actual answer. No subagent speaks for the user or chooses subjective trade-offs. Only the user ends Grill; preserve its closing sweep. Done when each run has an accountable owner/result or named blocker.

## Contract selection

1. Read the explicit user choice and retained candidate worktree/revision. An unanswered recommendation is not consent. Materialize a selected hybrid; ask only for unresolved substantive choices. Done when the final contract matches the user's selection.
2. Prepare `deep-module/selected/{rationale.md,module-map.md,sketch/}` with selected contract diagrams and `deep-module/considered-options.md`. Notes summarize other interfaces/seams, trade-offs and actual rejection reasons, distinguishing user choice from agent recommendation. Keep candidate source trees outside the payload. Done when chosen shape and considered alternatives are reviewable.
3. Use **Integrate a result** only now. If candidates were already committed, construct a clean selected-only result from the pinned integration base through the Git skill; merging deletions would still bring rejected sources through ancestry. Preserve candidate worktree until verification. Revalidate integration drift; return materially changed choices to the user. Done when incoming diff/ancestry contains selected artifacts and notes only.
4. Synchronize supported HLD conclusions, root fog/decision index and ticket Result. Comment verified choice/evidence, close the issue, then clean owned candidate resources after consumers finish. Failure retains exact pending step and worktree. Done when choice, integration and tracker completion are separately confirmed.

## Research routing

Automatically select the relevant scope for factual gaps. Codebase questions use Research system scope (Explore for pure lookup; How for inspection); cloud provider facts use Cloud; external primary-source facts use Web. Historical intent uses Research Why (`@mode=why`). Missing external checkouts block system evidence; use Web when public documentation suffices.

| Option | Route | Scope |
|---|---|---|
| Web | `web` | Public primary sources, such as specifications and official docs |
| Cloud | `cloud` | Provider, service, and whether live values matter |
| Current system | `system` | Repository or deployable being mapped and inspection axis |
| External system | `system` | Named external repository or deployable and inspection axis. If only public docs suffice, use Web. |

For a system question, choose `Behavior` for one deployable, `Flow` for handoffs across deployables, `Data` for a data boundary, or `focused` for an isolated call or package API. This axis sets the primary lens. The question sets the depth, with an explicit inspection requesting full coverage.

Record one bullet per research part in `## Research scope`: route, target (if known for Web), system axis (for System), and the part's question when the ticket spans multiple parts. For Cloud, include the provider, service, and need for live values.

For every research dispatch, pass the ticket's Question as `@question`, Research scope as `@researchScope`, and content framing as `@outputShape`. Wayfinder selects an exact report file per part before dispatch: preserve an explicit ticket destination; otherwise use `docs/research/<initiative-slug>/<ticket-slug>.md` for one part or `docs/research/<initiative-slug>/<ticket-slug>-<part-slug>.md` for separate parts. Pass these as `@outputPath` (a question-to-file mapping for multiple reports), with the ticket worktree's absolute repository root as `@outputBase`. Wayfinder owns this convention; Research never chooses filenames. Reject destination conflicts before writing. For older tickets infer and persist scope before dispatch. For Why pass `@mode=why` instead of a conflicting scope.

## Fog of war

Not yet specified is the root's single fog-of-war register: store **all unresolved unknowns and risks**, coarse or precise, including those with active child issues. Do not create a separate Unknowns and risks section or copy fog into HLD Open Questions. Child issues track work, not a competing unknown inventory.

Assign stable initiative-local IDs. Keep state, consequence, resolution criterion (or exact missing framing), next action/owner, linked work and supported outcome/limits. Preserve IDs when refining wording; split independent new questions with predecessor links. Risk entries include trigger/failure/impact, mitigation, verification method/result and residual risk through Risk verification. A passing narrow check or no counterexample is not universal safety.

After each answer/result/resume, choose the cheapest useful next helper: Research clarifies facts, Prove tests a claim, Challenge this searches for interacting blind spots, Deep Module/Code Sketch expose shapes, Grill settles human choices. A coarse concern can justify a bounded Research question before the whole area is specified. Create/reuse concrete typed work when frameable; keep the entry in fog until its resolution criterion is met. Challenge this runs within the current owner or root, never a dedicated issue.

Partial, conflicting, blocked or unmitigated risks remain; mark their limitation and next action. When resolved, persist supported outcome, stable ID, linked work and evidence pointer in Decisions so far before removing the active fog entry. Reopen the same ID when new evidence invalidates the outcome. Never repeat unchanged inconclusive runs; retry with changed prerequisites/evidence or a bounded new method. Out-of-scope work belongs in Out of scope and needs an explicit scope decision before investigation.

## Out of scope

Fog only ever gathers toward the destination. The destination fixes the scope, so work beyond it is out of scope — it isn't fog, and it doesn't belong in Not yet specified. It gets its own Out of scope section on the map: work you've consciously ruled out of this effort. Scope, not sharpness, lands it here.

Out-of-scope work never graduates — the frontier stops at the destination — so it returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

Ruling something out of scope is a scoping act, not a step on the route. When a ticket that already exists turns out to sit past the destination — mis-scoped in while charting, or exposed by a resolution — close it (a closed ticket is unambiguously off the frontier) and leave one line in the Out of scope section: the gist plus why it's out of scope, linking the closed ticket. It stays out of Decisions so far, which records the route actually walked — a scope boundary isn't a step on it.

## Tracker operations

Load [Wayfinder operations](../references/github.md#wayfinder-operations) registered in the router and follow its GitHub operations for this tracker repository. Keep GitHub-specific commands in the reference; do not configure another backlog backend.

- **Create the map**: **Create ticket** with label `wayfinder:map` and the map body template above.
- **Create a ticket**: **Create Wayfinder sub-ticket** with `parentIssueNumber` = the map, label `wayfinder:<type>`, body = Question + Unknowns + Work + Research scope (research only) + Blocked by + Part of; Result is added on dispatch.
- **Create a sub-ticket**: **Create Wayfinder sub-ticket** with `parentIssueNumber` = the ticket it's narrower than, label `wayfinder:<type>`, body = Question + Unknowns + Work + Research scope (research only) + Blocked by + Part of; Result is added on dispatch. Use when a resolution surfaces a decision that's child-scoped to the ticket just worked, not a fresh frontier item.
- **Claim a ticket**: **Assign ticket**.
- **Release a ticket**: **Unassign ticket**. Use when a session ends without resolving (contract-design Options phase).
- **Find the frontier**: **List sub-tickets** of the map, then of every open child recursively; keep open tickets with a `wayfinder:<type>` label, and drop any that's assigned, or whose `Blocked by` section names a still-open ticket.
- **Resolve a ticket**: **Synchronize the document**, **Comment on ticket** with the verified answer, then **Close ticket**. Human-choice tickets need the recorded user decision; factual questions need sufficient evidence, not human confirmation.
- **Read the map / a ticket**: **Read ticket**. **Read a ticket's sub-tickets**: **List sub-tickets**.

**Label not found** (`wayfinder:map`, `wayfinder:research`, `wayfinder:experiment`, `wayfinder:grilling`, `wayfinder:task`, or `wayfinder:contract-design` missing): ask the user to follow the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md) in labels-only mode, then retry.

## Invocation

Supply a loose idea to chart a map, or a map issue number or URL and an optional ticket number to resume. Handle one human decision at a time. Use **Automatic runs** for parallel artifact work. When using Grill for a Wayfinder step, resume this playbook after Grill returns.

**Contract test** — apply to every question being ticketed: does it introduce a new contract, an inheritance-based abstraction, or a significant contract change? Yes → type `contract-design`, not `grilling`.

### Chart the map

1. Complete Session and document setup through branch/worktree creation. Use Grill to name the destination; seed and locally commit its HLD. Done when the selected document exists before frontier/evidence work.
2. Use Grill breadth-first to chart open decisions and first ready steps. Synchronize confirmed answers and unknowns. Even a one-session effort retains its document and integration branch; a map is optional only if no tracked questions remain. Done when scope and unresolved questions are explicit.
3. Create the map with Destination, Notes, Document and branches, and fog. Persist local branch, worktree, ownership and commit identities using **Update map or ticket**. Create currently specifiable tickets, typing each by the Contract test, then add blockers in a second pass. Done when native child links and dependencies are verified.
4. Run **Automatic runs** without a dispatch confirmation gate. Done when ready factual work is resolved or blocked and the next human decision is presented.

### Automatic runs

1. Reconcile Not yet specified and existing child issues on initial creation, each result/answer and resume. Reuse sufficient evidence for matching question/scope/revision/dependencies/environment; create/reuse precise Research, Experiment, Contract design or Code Sketch Task work. Keep coarse fog without fabricated detail. Done when every actionable gap has work or a named blocker.
2. Select Research routing for facts, Prove for a falsifiable condition, Deep Module for contract options, Code Sketch for usage/type shape. Material risks use Risk verification; Challenge this can cover a bounded design or the whole HLD without its own ticket. Human preferences/contract choice/risk acceptance remain human. Done when the next observation or required input is explicit.
3. Claim ready open/unclaimed issue phases; require blockers closed and prerequisites integrated/accessibly pinned. For root-owned Challenge this persist run identity instead. Use Helper dispatch; prepare result worktrees via the Git skill for source sketches/mutations or mandatory isolation, otherwise a verified pinned read-only checkout with separate outputs. Done when each eligible run has its scoped environment or precise blocker.
4. Pass `@helperDispatch` to every helper/nested worker, question/framing, prior evidence, original harness root, revision/environment/limits, ownership and exact destinations. Research uses Research routing. Prove uses `docs/prototype/<initiative-slug>/<ticket-slug>/report.md`; Challenge this uses `docs/prototype/<initiative-slug>/<owner-or-root-run>/challenge-this/<run>/report.md`. Code Sketch uses `docs/prototype/<initiative-slug>/<ticket-slug>/code-sketch/`; Contract Options use Ticket Types. Pass absolute output base and preserve valid explicit destinations. Done when helpers return supported results or explicit gaps.
5. Validate citations, sketch contracts and independent empirical reproductions. Contract Options: retain candidates in owned worktree, record review state and release claim, awaiting Choice **without integration**. Other outputs: **Integrate a result**, then **Synchronize the document**; retain proof probes as patches, never production changes. Done when candidate review state or local result ancestry/artifacts/HLD commit is verified.
6. Complete factual tickets only with deciding evidence and synchronized conclusions. Partial/inconclusive work stays open/blocked; experiments needing human judgment stay open. Embedded Challenge this completion does not close its owner or resolve unmitigated risks. Update fog and create/reuse actual follow-up work; continue newly ready independent work. Done when remaining work needs human input, prerequisites or a scope decision.

### Work through the map

1. Read the map and persisted document/base/integration-branch/worktree/commit identities. Verify local state and resume pending integration/synchronization before selecting new work. Legacy maps lacking these fields require Session and document setup; resolve the original base before creating branches. Done when the canonical worktree/document/integration branch are recovered, not duplicated.
2. Run Automatic runs for eligible questions without waiting for a queue request. Then choose the named human ticket or next human frontier ticket; claim it before work. Done when supporting factual gaps are resolved or explicitly blocked.
3. Use Ticket Types for the human phase: Grill, Contract Choice, or experiment judgment. Synchronize confirmed outcomes even on pause; complete Grill's closing sweep before declaring a session resolved. Done when user decisions are recorded or pending.
4. Resolve completed tickets, append a context pointer to Decisions so far, and link newly concrete work to fog entries with blockers; clear only resolved entries. Re-scope invalidated tickets; out-of-scope closures belong in Out of scope, never Decisions so far. Synchronize and rerun Automatic runs for new in-scope factual questions. Done when the next frontier reflects current evidence.

Expect concurrent tracker edits. Re-read before writes and preserve other sessions' contributions.

## Completion criteria

- The HLD reflects supported integrated results and confirmed sessions; partial/conflicting questions remain in root Not yet specified, while HLD Open Questions remain user-owned. Reprocessing the same result creates no duplicate rows, sections, sources, tickets or merges.
- Verified evidence is retained locally and indexed by root/child issues; Contract design merges selected artifacts only after user choice. HLD contains conclusions without evidence appendices. Report its HEAD, paths, open choices and blocked integration/synchronization.
- No automatic push, PR creation, PR merge/close or merge into the session base. Confluence publishing requires explicit `design publish-hld`; it grants no GitHub publication authority.
- Last, re-read the destination and requested scope; map every obligation to document content, evidence or an explicit remaining blocker. Do not declare the design ready with missing coverage.

## Gotchas

- Resume legacy maps by verified identity. Merge any separate unknown/risk register into Not yet specified preserving IDs/evidence/links; keep Contract design identity and Options/Choice state. Do not rewrite existing candidate history; identify legacy integrated alternatives as superseded.
- Move unambiguously agent-owned discovery rows from legacy HLD Open Questions into root fog before removing them; preserve user presentation rows, and ask when ownership is ambiguous.
- Preserve prior Challenge this history. Pending verification belongs to the current issue/root; reconcile any legacy wrapper before retiring it, never create another wrapper.
- Missing local refs/worktrees block recovery; retain candidates across Choice pauses. Never invent remote artifact links or delete the sole evidence copy. Expect concurrent edits: reread root/issue before writes and preserve others' contributions.
