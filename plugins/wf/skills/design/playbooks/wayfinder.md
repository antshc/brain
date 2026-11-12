# Wayfinder

A loose idea has arrived, too big for one agent session, and wrapped in fog: the way from here to the destination isn't visible yet. Wayfinding is about finding that way, not charging at the destination. This playbook charts the way as a shared map on the repo's issue tracker, then works its decision tickets (questions whose resolution is a decision, not slices of a build to execute) one at a time until the route is clear.

The destination varies per effort, and naming it is the first act of charting: it shapes every ticket. It might be a spec to hand off and iterate on, a decision to lock before planning starts, or a change made in place like a data-structure migration. The map is domain-agnostic: engineering work, course content, whatever fits the shape.

## Plan, don't do

Wayfinder is planning by default: each ticket resolves a decision, and the map is done when the way is clear, with nothing left to decide before someone goes and does the thing. The pull to just do the work is usually the signal you've reached the edge of the map and it's time to hand off. An effort can override this in its Notes, carrying execution into the map itself, but absent that, produce decisions, not deliverables.

## Refer by name

Every map and ticket is an issue, so it has a name — its title. In everything the human reads — narration, the map's Decisions-so-far — refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The id and URL don't vanish — a name wraps its link — but they ride inside the name, never stand in for it.

## The Map

The map is a single issue on this repo's GitHub tracker, labelled `wayfinder:map`. Its tickets are native sub-issues of the map — see **Tracker operations** and [Wayfinder operations](../references/github.md#wayfinder-operations) for map, child, blocking, and frontier operations.

The map is an index, not a store. It lists the decisions made and points at the tickets that hold their detail; a decision lives in exactly one place — its ticket — so the map never restates it, only gists it and links.

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

For research tickets, add `## Research scope` after `## Question` (see Research routing).

Each ticket carries a `wayfinder:<type>` label — one of `research`, `experiment`, `grilling`, `task`, `contract-design` (see Ticket Types).

A session claims a ticket by assigning it to itself, first, before any work, so concurrent sessions skip it. That assignee is the claim: an open, unassigned ticket is unclaimed.

Record Research and Contract design prerequisites for experiments in `## Blocked by`, including the evidence or choice each experiment needs. Blocking keeps the `## Blocked by` body convention above as its source of truth; unlike implementation tickets, Wayfinder decisions do not require native dependency links. A ticket is unblocked when every ticket named in its `Blocked by` section is closed; the frontier is the open, unblocked, unclaimed children — the edge of the known. An unreadable blocker is not confirmed closed.

The answer isn't part of the body — it's recorded as a resolution comment on close (see Work through the map). Assets created while resolving a ticket are linked from the issue, not pasted in.

## Ticket Types

Use the [ticket type guide](../references/wayfinder-ticket-types.md) when the distinction is unclear.

Every ticket is either HITL — human in the loop, worked with a human who speaks for themselves — or AFK, driven by the agent alone. A HITL ticket only resolves through that live exchange; the agent never stands in for the human's side of it.

- **Research** (AFK): Gather primary-source evidence a decision depends on. *Load and follow the `research` skill to investigate code, docs, and the web and return cited findings* using the ticket's question and scope (see Research routing).
- **Experiment** (HITL): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to: *Load and follow the `prove` skill to confirm or refute one technical claim with reproducible evidence.* Link the published evidence and any explicitly retained prototype. Use when "does this call/logic behave as expected" is the key question.
- **Grilling** (HITL): Conversation. The default case. Always use the [Grill playbook](./grill.md) to resolve the Wayfinder grilling ticket through an interview. Resolving one may surface decisions narrower than the question itself — child-scoped to it rather than independent frontier items; ticket those as sub-tickets of the grilling ticket (see Tracker operations) via GitHub's native sub-issue relationship, not a fresh body-text field.
- **Task** (HITL or AFK): Manual work that must happen before a decision can be made — nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that does rather than decides — and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later tickets depend on.
- **Contract design** (AFK → HITL): Choosing the shape of a contract from radically different designed options. Use instead of Grilling when the question introduces a new contract or interface, an abstraction built on inheritance (base class, interface hierarchy, polymorphic substitution), or a significant change to an existing contract (breaking signature, invariants, error modes, ordering, or seam placement). Two phases, never collapsed into one:
  1. **Options (AFK)** — when the ticket has no options comment yet. *Load and follow the `design` skill to deepen modules and design interfaces; use its `deep-module` route standalone (no sketch, no implementation) to design the deep-module interface with Design It Twice parallel sub-agents, classify dependencies for deepening, and place the seam*, producing 3+ radically different options plus a recommendation. For each option, *Load and follow the `doc-diagram` skill to use delta mode to draw the Mermaid class diagram of type relationships for contract changes, interfaces, and inheritance*. Write one Markdown options doc where the repo keeps design notes (e.g. `docs/research/<ticket-slug>.md`; match existing convention): per option the interface, delta class diagram, what hides behind the seam, dependency strategy, and trade-offs; then the comparison and recommendation. After **Publish a result** confirms the options on origin, comment the doc link and a one-line gist per option on the ticket (**Comment on ticket**), then **Release a ticket**. The ticket stays open; this phase never resolves it.
  2. **Choice (HITL)** — when the options comment exists. Present each option with its diagram, then the recommendation. The user chooses one option or a hybrid; the agent MUST NOT choose for the user. Resolve with the chosen option, its class diagram, the doc link, and a one-line gist of each rejected option and why.

## Research routing

When mapping the frontier or discovering new evidence gaps, consider all four options. Offer the relevant ones to the user and say what each would verify.

| Option | Route | Scope |
|---|---|---|
| Web | `web` | Public primary sources, such as specifications and official docs |
| Cloud | `cloud` | Provider, service, and whether live values matter |
| Current system | `system` | Repository or deployable being mapped and inspection axis |
| External system | `system` | Named external repository or deployable and inspection axis. If only public docs are available, offer Web. |

For a system question, choose `Behavior` for one deployable, `Flow` for handoffs across deployables, `Data` for a data boundary, or `focused` for an isolated call or package API. This axis sets the primary lens. The question sets the depth, with an explicit inspection requesting full coverage.

Record one bullet per research part in `## Research scope`: route, target (if known for Web), system axis (for System), and the part's question when the ticket spans multiple parts. For Cloud, include the provider, service, and need for live values.

For every research dispatch, pass the ticket's Question as `@question`, Research scope as `@researchScope`, and content framing as `@outputShape`. Wayfinder selects an exact report file per part before dispatch: preserve an explicit ticket destination; otherwise use `docs/research/<ticket-slug>.md` for one part or `docs/research/<ticket-slug>-<part-slug>.md` for separate parts. Pass these as `@outputPath` (a question-to-file mapping for multiple reports), with the ticket worktree's absolute repository root as `@outputBase`. Wayfinder owns this convention; Research never chooses filenames. Reject destination conflicts before writing. Omit `@researchScope` for older tickets without it.

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

Load [Wayfinder operations](../references/github.md#wayfinder-operations) and follow its GitHub operations for this tracker repository. Keep GitHub-specific commands in the reference; do not configure another backlog backend.

- **Create the map**: **Create ticket** with label `wayfinder:map` and the map body template above.
- **Create a ticket**: **Create Wayfinder sub-ticket** with `parentIssueNumber` = the map, label `wayfinder:<type>`, body = Question + Research scope (research only) + Blocked by + Part of.
- **Create a sub-ticket**: **Create Wayfinder sub-ticket** with `parentIssueNumber` = the ticket it's narrower than, label `wayfinder:<type>`, body = Question + Research scope (research only) + Blocked by + Part of. Use when a resolution surfaces a decision that's child-scoped to the ticket just worked, not a fresh frontier item.
- **Claim a ticket**: **Assign ticket**.
- **Release a ticket**: **Unassign ticket**. Use when a session ends without resolving (contract-design Options phase).
- **Find the frontier**: **List sub-tickets** of the map, then of every open child recursively; keep open tickets with a `wayfinder:<type>` label, and drop any that's assigned, or whose `Blocked by` section names a still-open ticket.
- **Resolve a ticket**: **Comment on ticket** with the answer, then **Close ticket**.
- **Read the map / a ticket**: **Read ticket**. **Read a ticket's sub-tickets**: **List sub-tickets**.

**Label not found** (`wayfinder:map`, `wayfinder:research`, `wayfinder:experiment`, `wayfinder:grilling`, `wayfinder:task`, or `wayfinder:contract-design` missing): ask the user to follow the [WF installer](https://github.com/antshc/brain/blob/main/plugins/wf/install/install.md) in labels-only mode, then retry.

## Invocation

Supply a loose idea to chart a map, or a map issue number or URL and an optional ticket number to resume. Handle one human decision at a time. Use **Automatic runs** for parallel artifact work. When using Grill for a Wayfinder step, resume this playbook after Grill returns.

**Contract test** — apply to every question being ticketed: does it introduce a new contract, an inheritance-based abstraction, or a significant contract change? Yes → type `contract-design`, not `grilling`.

### Chart the map

User invokes with a loose idea.

1. Name the destination. Use the [Grill playbook](./grill.md) to resolve the Wayfinder destination, pinning down what this map is finding its way to — the spec, decision, or change. The destination fixes the scope, so it's settled first.
2. Map the frontier. Use the [Grill playbook](./grill.md) again to resolve the Wayfinder frontier, breadth-first this time: fan out across the whole space rather than deep on any one thread, surfacing the open decisions and the first steps takeable now. If this surfaces no fog — the way to the destination is already clear, the whole journey small enough for one session — you don't need a map. Stop and ask the user how they'd like to proceed.
3. Create the map (**Create the map** above): Destination and Notes filled in, Decisions-so-far empty, the fog sketched into Not yet specified.
4. Create the tickets you can specify now (**Create a ticket** above), typing each by the Contract test — then fill in each ticket's `Blocked by` section in a second pass, once every ticket has a number. Everything you can't yet specify stays in the fog — the Not yet specified section.
5. Run **Automatic runs**. Show the created map and tickets and stop at the confirmation gate.

### Automatic runs

1. Capture the absolute harness root, invocation repository, branch, and worktree before switching directories. Use that branch locally and the same branch name on `origin` throughout the run. If HEAD is detached, ask for the target branch.
2. After all GitHub tickets and their `Blocked by` sections are written, show the map and name the ready and waiting Research, Experiment, and Contract design runs. State which prerequisite or human decision each waiting run needs. Wait for explicit confirmation before claiming or dispatching automatic work. If confirmation is absent or declined, leave the tickets queued. Confirmation covers the listed tickets, their dependencies, and publication to the named branch on `origin`. Newly added tickets or material changes to the approved scope require fresh confirmation before dispatch.
3. Re-read the confirmed tickets. Skip published Experiment runs awaiting review and Contract design tickets awaiting Choice. Claim and dispatch independent, open, unclaimed runs in parallel, each in its own temporary branch and worktree based on the invocation branch (see **Prepare a result worktree**). Start dependants only after every blocker is resolved and the named evidence is available. Treat unreadable blockers, missing evidence, and dependency cycles as blocked. Refresh eligibility after each resolution.
4. Resolve the ticket's exact skill name and description before rendering *Load and follow the `skill-name` skill to <task>* with 3–6 description keywords; never emit placeholders literally. Read its full body, selected route and required resources, then execute in its worktree. Keep the ticket question and GitHub references scoped to that ticket. For Research, use **Research routing**. For Experiment, pass Prove the ticket question as `@question`, linked research/design findings as `@repoFacts`, original harness root and the assigned worktree with Wayfinder-owned cleanup. Select an exact `@outputPath=docs/research/<ticket-slug>.md` (preserve an explicit ticket destination) and worktree repository root as `@outputBase`; this also supplies any Research fallback destination. Retain runnable artifacts through verification and requested human review. If a design blocker supplies the chosen design, wait for the recorded user choice. Run only Options automatically for Contract design. Keep Experiment's human review and Contract design's human choice.
5. Verify the result and use **Publish a result**. Research reports are saved to the exact destinations Wayfinder supplied in **Research routing**; Wayfinder publishes those files. Contract design publishes its options and diagrams. Experiment publishes a Markdown record of observations, reproducible method, and evidence, or verified findings if it routes to Research. Include disposable experiment code only if explicitly requested. Publish before linking artifacts. Close a ticket only after its resolution is recorded, including human input where required. For a complete Research ticket, record the resolution and update the map as in **Work through the map**. For Experiment, comment with the published evidence and release the ticket for review. For Contract design, follow the Options phase's comment and release instructions. Leave incomplete work open, release the claim, and report the blocker.

### Work through the map

User invokes with a map (URL or number). A ticket is optional — without one, you pick the next decision, not the user.

1. Load the map — the low-res view, not every ticket body.
2. If the user asks to run the automatic queue, follow **Automatic runs**. When that queue stops, end this invocation. Otherwise choose the named ticket or the first frontier ticket. For Research, Experiment without published evidence, or Contract design Options, use **Automatic runs** scoped to that ticket and its recorded prerequisites, then end this invocation. For human phases, claim the ticket before work.
3. Resolve the human phase using **Ticket Types**. Read related tickets and their published artifacts as needed. Use the [Grill playbook](./grill.md) for grilling. For Contract design Choice, present the published options and record the user's choice. For Experiment review, present the published observations and collect the user's response before resolution.
4. Record the resolution (**Resolve a ticket** above); append a context pointer to the map's Decisions-so-far.
5. Add newly-surfaced tickets, typing each by the Contract test. For each: if it's child-scoped to the ticket just resolved — narrower than that question, not a fresh frontier item — create it as a sub-ticket (**Create a sub-ticket** above, `parentIssueNumber` = the ticket just resolved); otherwise create it as an independent ticket (**Create a ticket** above). Either way, graduate any fog the answer has made specifiable, clearing each graduated patch from Not yet specified so it lives only as its new ticket. If the answer reveals a ticket — this one or another — sits beyond the destination, rule it out of scope rather than resolving it on the route. If the decision invalidates other parts of the map, update or delete those tickets.

When either mode creates newly surfaced tickets, record their dependencies before offering them for confirmation. Expect other sessions to edit the tracker concurrently.
