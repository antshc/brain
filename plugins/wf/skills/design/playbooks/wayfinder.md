# Wayfinder

Chart a GitHub decision map and maintain one living spec or HLD throughout discovery. Produce decisions, evidence and the document; implementation requires separate authorization. The map schedules questions, tickets hold detailed resolutions, and the document synthesizes current requirements and decisions.

## Contents

- Refer by name
- Session and document
- The Map
- The map body
- Tickets
- Ticket Types
- Research routing
- Fog of war
- Out of scope
- Tracker operations
- Invocation
- Chart the map
- Automatic runs
- Work through the map
- Completion criteria

## Refer by name

Every map and ticket is an issue, so it has a name — its title. In everything the human reads — narration, the map's Decisions-so-far — refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The id and URL don't vanish — a name wraps its link — but they ride inside the name, never stand in for it.

## Session and document

1. Before interviews or worktree switches, capture absolute harness root, repository, invocation worktree, `@sessionBaseBranch` and its SHA. This is the branch the user started from, not necessarily `main`; every PR targets it. Resolve detached HEAD before branch creation. On resume, use the map's persisted base instead of the caller's current branch. Done when the base and remote are verified.
2. Honor explicit spec/HLD selection; otherwise ask which document the user wants. Automatically name/create its branch and dedicated owned worktree using **Prepare a document worktree**. Derive the branch summary from the initial request; keep that recorded name if Grill later refines the document slug. Do this before destination/frontier Grill. Done when ownership and branch are recorded outside disposable worktrees.
3. After destination Grill establishes scope/slug, read the selected Spec or HLD playbook and Living document resource registered in the router. Seed `docs/specs/<initiative-id-or-slug>.md` or `docs/designs/<initiative-slug>.md` in that worktree using repository-document/evolving-draft mode. Use **Publish the document** before evidence dispatch. Done when the seed and its one draft PR exist.

Wayfinder owns branch prefixes; *Load and follow the `git` skill to run verified Git mechanics for branch naming, creation and worktree lifecycle* using Branches and Worktrees with the selected prefix and summary. Preserve Git's slug normalization, removed initiative/ticket IDs, worker ordinals, collision authorization and verified resumes. Explicit caller prefixes override its default feat/fix choice; standalone Research/Prove conventions stay unchanged.

| Work | Prefix |
| --- | --- |
| Living spec/HLD | `wayfinder/<slug>` |
| Research ticket | `research/<slug>` |
| Experiment/verification ticket | `prove/<slug>` |
| Contract design Options | `wayfinder/<slug>` |

**Synchronize the document** after every research result, Grill session/pause, experiment result/review, Contract design phase, and on resume. Automatically update inside its dedicated worktree without a separate request or confirmation. Read the latest remote document; apply Living document reconciliation and the selected author's incremental rules, then **Publish the document**. Preserve existing diagram approval rules; record a blocked diagram update rather than claiming full readiness. Serialize writes, not whole evidence runs. Record last synchronized ticket/result commit and any pending updates on the map. Done when supported consequences appear in all affected sections and the document commit is verified on origin.

## The Map

The map is a single issue on this repo's GitHub tracker, labelled `wayfinder:map`. Its tickets are native sub-issues of the map — see **Tracker operations** and [Wayfinder operations](../references/github.md#wayfinder-operations) for map, child, blocking, and frontier operations.

The map is a scheduling index: gist decisions and link tickets; synthesize their supported consequences into the living document.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are not listed — they are open child issues, found by query.

```markdown
## Destination

<what reaching the end of this map looks like — the spec, decision, or change
this effort is finding its way to. One or two lines; every session orients to it
before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this
effort>

## Document and branches

- Session base: <branch>; starting SHA: <sha>
- Document: <spec or HLD>; <path>; <branch link>; <PR link>
- Worktree: <absolute path>; ownership record: <path outside worktrees>
- Last synchronized: <ticket/result commit or none>
- Pending synchronization: <result refs and missing steps or none>

## Decisions so far

<!-- the index — one line per closed ticket: enough to judge relevance, then zoom
the link for the detail the ticket holds -->

- [<closed ticket title>](link) — <one-line gist of the answer>

## Not yet specified

<!-- see "Fog of war": in-scope fog you can't ticket yet; graduates as the frontier
advances -->

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a sub-issue of the map (or of the ticket it's narrower than); its issue number is its identity. Its body is the question, sized to one 100K token agent session:

```markdown
## Question

<the decision or investigation this ticket resolves>

## Blocked by

<!-- One linked ticket title per blocker, followed by the finding or decision needed. Empty if none. -->

## Part of

<link to the map>
```

For research tickets, add `## Research scope` after `## Question` (see Research routing). After dispatch, persist a `## Result` section with branch link, pinned base SHA, PR link, exact report paths, question/revision/environment identity and pending work. Keep the answer in the resolution comment.

Each ticket carries a `wayfinder:<type>` label — one of `research`, `experiment`, `grilling`, `task`, `contract-design` (see Ticket Types).

A session claims a ticket by assigning it to itself, first, before any work, so concurrent sessions skip it. That assignee is the claim: an open, unassigned ticket is unclaimed.

Record Research and Contract design prerequisites for experiments in `## Blocked by`, including the evidence or choice each experiment needs. Blocking keeps the `## Blocked by` body convention above as its source of truth; unlike implementation tickets, Wayfinder decisions do not require native dependency links. A ticket is unblocked when every ticket named in its `Blocked by` section is closed; the frontier is the open, unblocked, unclaimed children — the edge of the known. An unreadable blocker is not confirmed closed.

The answer isn't part of the body — it's recorded as a resolution comment on close (see Work through the map). Assets created while resolving a ticket are linked from the issue, not pasted in.

## Ticket Types

Use the ticket type guide registered in the router when the distinction is unclear.

Every ticket is either HITL — human in the loop, worked with a human who speaks for themselves — or AFK, driven by the agent alone. A HITL ticket only resolves through that live exchange; the agent never stands in for the human's side of it.

- **Research** (AFK): Gather primary-source evidence a decision depends on. *Load and follow the `research` skill to investigate technical questions across source code, docs, and the web and return cited findings* using the ticket's question and scope (see Research routing).
- **Experiment** (AFK for factual claims; HITL for human judgment): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to: *Load and follow the `prove` skill to confirm or refute one technical claim with reproducible evidence.* Link the published evidence and any explicitly retained prototype. Use when "does this call/logic behave as expected" is the key question. Verified empirical answers resolve automatically; acceptance of a trade-off, preference, or product choice still requires the user.
- **Grilling** (HITL): Conversation. The default case. Always use the Grill playbook to resolve the Wayfinder grilling ticket through an interview. Resolving one may surface decisions narrower than the question itself — child-scoped to it rather than independent frontier items; ticket those as sub-tickets of the grilling ticket (see Tracker operations) via GitHub's native sub-issue relationship, not a fresh body-text field.
- **Task** (HITL or AFK): Manual work that must happen before a decision can be made — nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that does rather than decides — and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later tickets depend on.
- **Contract design** (AFK → HITL): Choosing the shape of a contract from radically different designed options. Use instead of Grilling when the question introduces a new contract or interface, an abstraction built on inheritance (base class, interface hierarchy, polymorphic substitution), or a significant change to an existing contract (breaking signature, invariants, error modes, ordering, or seam placement). Two phases, never collapsed into one:
  1. **Options (AFK)** — when the ticket has no options comment yet. *Load and follow the `design` skill to design architecture by deepening modules and resolving interface decisions; use its `deep-module` route standalone (no sketch, no implementation) to design the deep-module interface with Design It Twice parallel sub-agents, classify dependencies for deepening, and place the seam*, producing 3+ radically different options plus a recommendation. For each option, *Load and follow the `doc-diagram` skill to create a Mermaid class diagram in delta mode to show the Mermaid class diagram of type relationships for contract changes, interfaces, and inheritance*. Write one Markdown options doc where the repo keeps design notes (e.g. `docs/research/<ticket-slug>.md`; match existing convention): per option the interface, delta class diagram, what hides behind the seam, dependency strategy, and trade-offs; then the comparison and recommendation. After **Publish a result** confirms the options on origin, comment the doc link and a one-line gist per option on the ticket (**Comment on ticket**), then **Release a ticket**. The ticket stays open; this phase never resolves it.
  2. **Choice (HITL)** — when the options comment exists. Present each option with its diagram, then the recommendation. The user chooses one option or a hybrid; the agent MUST NOT choose for the user. Resolve with the chosen option, its class diagram, the doc link, and a one-line gist of each rejected option and why.

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

For every research dispatch, pass the ticket's Question as `@question`, Research scope as `@researchScope`, and content framing as `@outputShape`. Wayfinder selects an exact report file per part before dispatch: preserve an explicit ticket destination; otherwise use `docs/research/<ticket-slug>.md` for one part or `docs/research/<ticket-slug>-<part-slug>.md` for separate parts. Pass these as `@outputPath` (a question-to-file mapping for multiple reports), with the ticket worktree's absolute repository root as `@outputBase`. Wayfinder owns this convention; Research never chooses filenames. Reject destination conflicts before writing. For older tickets infer and persist scope before dispatch. For Why pass `@mode=why` instead of a conflicting scope.

## Fog of war

The map is deliberately incomplete: don't chart what you can't yet see. Beyond the live tickets lies the fog of war — the dim view of decisions and investigations you can tell are coming but can't yet pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever's now specifiable into fresh tickets — one at a time, until the way to the destination is clear and no tickets remain.

The map's Not yet specified section is where that dim view is written down: the suspected question, the area to revisit later. It's the undiscovered frontier toward the destination — everything here is in scope, just not sharp enough to ticket. Write as loosely or as fully as the view allows; it doubles as a signpost for collaborators reading where the effort is headed.

Fog or ticket? The test is whether you can state the question precisely now — not whether you can answer it now.

- Ticket when the question is already sharp — even if it's blocked and you can't act on it yet.
- Not yet specified when you can't yet phrase it that sharply. Don't pre-slice the fog into ticket-sized pieces: it's coarser than a ticket, and one patch may graduate into several tickets, or none, once the frontier reaches it.

Not yet specified excludes what's already decided (Decisions so far), what's already a live ticket, and what's out of scope (the next section).

## Out of scope

Fog only ever gathers toward the destination. The destination fixes the scope, so work beyond it is out of scope — it isn't fog, and it doesn't belong in Not yet specified. It gets its own Out of scope section on the map: work you've consciously ruled out of this effort. Scope, not sharpness, lands it here.

Out-of-scope work never graduates — the frontier stops at the destination — so it returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

Ruling something out of scope is a scoping act, not a step on the route. When a ticket that already exists turns out to sit past the destination — mis-scoped in while charting, or exposed by a resolution — close it (a closed ticket is unambiguously off the frontier) and leave one line in the Out of scope section: the gist plus why it's out of scope, linking the closed ticket. It stays out of Decisions so far, which records the route actually walked — a scope boundary isn't a step on it.

## Tracker operations

Load [Wayfinder operations](../references/github.md#wayfinder-operations) registered in the router and follow its GitHub operations for this tracker repository. Keep GitHub-specific commands in the reference; do not configure another backlog backend.

- **Create the map**: **Create ticket** with label `wayfinder:map` and the map body template above.
- **Create a ticket**: **Create Wayfinder sub-ticket** with `parentIssueNumber` = the map, label `wayfinder:<type>`, body = Question + Research scope (research only) + Blocked by + Part of.
- **Create a sub-ticket**: **Create Wayfinder sub-ticket** with `parentIssueNumber` = the ticket it's narrower than, label `wayfinder:<type>`, body = Question + Research scope (research only) + Blocked by + Part of. Use when a resolution surfaces a decision that's child-scoped to the ticket just worked, not a fresh frontier item.
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

1. Complete Session and document setup through branch/worktree creation. Use Grill to name the destination; seed/publish its document and draft PR. Done when the selected document exists before frontier/evidence work.
2. Use Grill breadth-first to chart open decisions and first ready steps. Synchronize confirmed answers and unknowns. Even a one-session effort retains its document/PR; a map is optional only if no tracked questions remain. Done when scope and unresolved questions are explicit.
3. Create the map with Destination, Notes, Document and branches, and fog. Link its branch/PR bidirectionally using **Link branches and PRs**. Create currently specifiable tickets, typing each by the Contract test, then add blockers in a second pass. Done when native child links and dependencies are verified.
4. Run **Automatic runs** without a dispatch confirmation gate. Done when ready factual work is resolved or blocked and the next human decision is presented.

### Automatic runs

1. On initial creation, every result/session and resume, inspect unresolved document questions, fog and tickets. Reuse sufficient evidence for the same question/revision/environment. Create/reuse a precise ticket for each new in-scope factual gap; leave unphraseable fog un-ticketed. Scope expansion needs a user decision. Done when each sharp question has an owner or blocker.
2. Classify factual questions via Research routing; empirical claims use Prove with a falsifiable condition and inferred `logic | runtime | integration-local | integration-cloud | ui` option. Product preferences, contract choices and trade-off acceptance stay human; gather their supporting facts automatically. Done when route and deciding observation/input are explicit.
3. Re-read ready open, unclaimed tickets; claim and dispatch independent Research, Experiment, and Contract design Options runs in parallel via **Prepare a result worktree**. Require every blocker closed and its evidence accessible, even when its PR is unmerged; pass exact branch/SHA/artifact refs. Inaccessible blockers, missing inputs/access/budget, cycles and unavailable required isolation block only dependent work. Observe execution permissions and supplied limits. Done when each eligible ticket runs once or has a named blocker.
4. Resolve the invoked skill's exact name/current description and render its invocation with 3–6 description keywords; read the full body, selected route and required resources before executing in the assigned worktree. Research uses Research routing. Experiment uses Prove with `@question`, falsifiable criteria, prior findings and original harness root in `@repoFacts`, explicit revision/environment/limits, assigned worktree and Wayfinder-owned cleanup. Select exact `@outputPath=docs/research/<ticket-slug>.md` (preserve an explicit destination), worktree root as `@outputBase`; forward to Research fallback. Run only Options for Contract design. Done when the runner returns verified evidence or an explicit gap.
5. Verify sources and Prove's independent reproduction, then **Publish a result** and **Synchronize the document**. Research saves exactly Wayfinder's requested paths; experiments publish method, observations and scoped conclusion (confirmed/refuted/inconclusive), or labeled Research findings. Keep disposable code only if requested; retain runnable state through verification and requested human review. Done when evidence and document commits/PRs are verified and linked.
6. Complete factual answers, including refuted assumptions, resolve the question/ticket and update Decisions so far. Partial/inconclusive results extend the question; do not close it. Human-choice experiments and Contract Options publish facts/options and release the claim, leaving the choice open. On failure release the claim and persist the pending step. Done when ticket status agrees with evidence and human-decision state.
7. Graduate newly precise fog into typed tickets, preserving child-scoped questions under their parent and recording blockers. Re-evaluate dependants after each result; continue automatically until no eligible work remains. Reuse completed/in-flight question+revision+environment identities. Retry only with changed evidence/prerequisites or a bounded new method; unchanged inconclusive results wait. Done when every remaining question needs human input, prerequisites or a scope change.

### Work through the map

1. Read the map and persisted document/base/branch/PR identities. Verify remote state and resume pending publication/synchronization before selecting new work. Legacy maps lacking these fields require Session and document setup; resolve the original base before creating branches. Done when the canonical worktree/document/PR are recovered, not duplicated.
2. Run Automatic runs for eligible questions without waiting for a queue request. Then choose the named human ticket or next human frontier ticket; claim it before work. Done when supporting factual gaps are resolved or explicitly blocked.
3. Use Ticket Types for the human phase: Grill, Contract Choice, or experiment judgment. Synchronize confirmed outcomes even on pause; complete Grill's closing sweep before declaring a session resolved. Done when user decisions are recorded or pending.
4. Resolve completed tickets, append a context pointer to Decisions so far, and graduate fog into typed tickets with blockers. Re-scope invalidated tickets; out-of-scope closures belong in Out of scope, never Decisions so far. Synchronize and rerun Automatic runs for new in-scope factual questions. Done when the next frontier reflects current evidence.

Expect concurrent tracker edits. Re-read before writes and preserve other sessions' contributions.

## Completion criteria

- The selected spec/HLD reflects every consumed result and confirmed session; partial/conflicting questions remain explicit. Reprocessing the same result creates no duplicate rows, sections, sources, tickets or PRs.
- One persistent document PR and separate result PRs target the captured session base; branches/PRs link their owning issues. Report blocked publication/synchronization, open choices and remaining prerequisites.
- Completion of the map or a ticket never merges/closes a PR or enables auto-merge. The user decides each PR's merge/close. A merged/closed PR requires a user-directed continuation, not automatic reopening/replacement.
- Last, re-read the destination and requested scope; map every obligation to document content, evidence or an explicit remaining blocker. Do not declare the design ready with missing coverage.
