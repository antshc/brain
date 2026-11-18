---
name: design
description: >-
  Design architecture, resolve decisions, and coordinate specs, HLDs and task breakdowns. Use for 'architect this', 'grill this', 'publish HLD to Confluence', or 'design review'. Drafting belongs to `write`; PR review belongs to `review`.
---

# Design

One entry point; route to one playbook. Do not load unrelated routes.

| Route | Select for | Playbook |
|---|---|---|
| `architect` | Design code shape across modules, compare candidates, then implement or hand off an accepted sketch. | [Architect](playbooks/architect.md) |
| `sketch` | Explicit request for a usage-first code sketch only, without Arena or implementation. | [Sketch](playbooks/sketch.md) |
| `deep-module` | Deepen an interface, place a seam, or compare module shapes. | [Deep module](playbooks/deep-module.md) |
| `grill` | Challenge a plan, interview domain decisions, or resolve a Wayfinder Decision topic. | [Grill](playbooks/grill.md) |
| `hld` | Create or update an authoritative high-level feature design from specs and resolved decisions. | [HLD](playbooks/hld.md) |
| `publish-hld` | Publish only the HLD Confluence page on explicit request; evidence remains local. | [Publish HLD](playbooks/publish-hld.md) |
| `spec` | Synthesize a spec or PRD from decisions or an accepted sketch. | [Spec](playbooks/spec.md) |
| `tasks` | Break a spec into implementation tasks on explicit request. | [Tasks](playbooks/tasks.md) |
| `wayfinder` | Chart or resume a decision map with a living HLD and automatic evidence work on explicit request. | [Wayfinder](playbooks/wayfinder.md) |
| `review` | Assess a technical design's gaps, risks, and implementation readiness on explicit request. | [Review](playbooks/review.md) |

1. Honor an explicit route from the user or caller. On replies to pending questions or checkpoints, continue the active route. Otherwise infer from clear intent. Ambiguous requests → ask which outcome the user wants and wait.
2. Select `tasks`, `wayfinder`, or `review` only on an explicit user request, including clear natural language relayed by a caller. Task publication requires separate approval of the breakdown; Wayfinder automatically runs in-scope factual research and proof; human choices stay interactive. Publication requires an explicit `publish-hld` request; HLD synthesis and Wayfinder completion never select it automatically.
3. Select `sketch` for an explicit standalone request or as a Deep Module/Wayfinder helper without implementation. General code-shape or multi-candidate work selects `architect`. `deep-module` generates option sketch packages standalone or for Wayfinder/Architect; Wayfinder retains Prove/Experiment and sketch prototypes in owned result worktrees until explicit user approval; Challenge this verification integrates automatically and updates fog/HLD without approval; Contract Options require user Choice. Empirical checks and adversarial review belong to the standalone Prove and Challenge this skills.
4. Select `hld` only for an explicit request to create or update a high-level design or feature design, including `/design hld`. Wayfinder may select it for its living HLD and subsequent updates. A spec or design supplied as input alone does not select it.
5. Read the selected playbook fully before acting and required resources fully before use. For `hld`, the playbook prepares evidence and invokes `write hld`; Write owns template loading, rendering and merge checks. Wayfinder loads Grill for separate destination and breadth-first frontier interviews, one question at a time, then applies its small-effort decision before map setup. Continue standalone Grill to Spec only after a requested handoff and closing sweep. Wayfinder synchronizes confirmed outcomes automatically and retains control.

## Conditional resources

Read triggered resources fully before use; resolve from this skill directory.

| Trigger | Resource |
|---|---|
| Wayfinder tracker/local integration; Spec issue publication; Task publication | [GitHub operations](references/github.md) |
| Wayfinder topic classification | [Topic types](references/wayfinder-topic-types.md) |
| Wayfinder creation/update; HLD evolving draft | [Living document](references/living-document.md) |
| Explicit standalone sketch packaging outside HLD publication | [Sketch packager](scripts/package_sketch.py); execute with `--help` from this skill directory |
| HLD or Wayfinder material risks | [Risk verification](references/risk-verification.md); select Prove or Challenge this before final synthesis or through the existing Wayfinder queue |
| Sketch, Deep Module options or Architect candidates | [Code-sketch contract](references/sketch-contract.md), [Rationale template](references/rationale.template.md), [Design red flags](references/red-flags.md) |
| Deep Module options | [Deep modules](references/deep-modules.md), [Design It Twice](references/design-it-twice.md) |
| Grill session state | [Session ledger](references/track-ledger.md) |
| Grill verification-scope trigger | [Verification](references/tactics-verification.md) |
| Grill external-source trigger | [External source](references/tactics-external-source.md) |
| Grill closing/handoff | [Closing sweep](references/closing-sweep.md) |

Wayfinder keeps only concerns too vague to frame as a topic in Not yet specified; precise questions/risks belong to typed topics or retained pending proposals; HLD Open Questions are user-owned presentation content. Evidence is local-only: no research/proof/sketch appendices, Confluence subpages or artifact attachments.

Wayfinder additionally reads the full Grill playbook for interviews and, after the mapped-effort decision, the full HLD orchestration playbook for the Write handoff, using the route table above. Spec remains a separate explicitly requested route; Wayfinder does not select it as an output format.

## Work item approval

**MUST NOT** create any tracker issue or offline work-item file (Spec issue, implementation task, Wayfinder map, child, sub-issue, follow-up) before the user explicitly approves that exact proposal. Present title, labels, parent, blockers and rendered body. Prototype topics (Experiment, Code Sketch Task, Contract design) also show the claim and deciding criteria or sketch/contract scope, planned artifact paths, owned worktree and the Prototype approval gate. Silence, partial feedback, corrections, passing checks, and approval of a plan, destination or earlier batch are not approval; a changed proposal needs fresh approval. Selected playbooks own batching and presentation order. Exception: Wayfinder writes temporary, explicitly unapproved Markdown review drafts before approval and presents clickable file links per Work item approval in its playbook. These drafts grant no tracker creation, offline backlog publication or evidence-dispatch authority.

## Principles

*Load and follow the `principles` skill to load `In your own words` plus principles named in the request or matching the task, selected route and phase, and apply them before the selected playbook.* Use `In your own words` for intent; Index matches cover consumer experience, domain/type shape, seams, boundaries, concurrency and alternatives. re-evaluate at phase changes. Fresh candidate workers apply this rule in their own context.

## Architect options and behavior

- Accept explicit `arena-agents=1|2|3` as an Arena request; reject other values before work. Otherwise Architect compares two shapes locally for bounded designs with clear requirements and precedent; new cross-subsystem ownership/state coordination, material unresolved tradeoffs or an unsettled comparison use Arena with one runner by default. Preserve explicit counts through handoffs and correction reruns.
- Forward caller-supplied `adversaries` to Challenge this; it owns count validation/defaults.
- `checkpoint` is opt-in, only when explicitly requested; preserve it through caller handoffs. Otherwise Architect implements after review by default. An explicit **design-only handoff** returns the sketch for `design spec` without implementing.
- `architect sketch` routes to `sketch` only, and `architect deep-module` to `deep-module`, for intent compatibility. Prefer the direct `design <route>` spelling.

## Artifact and repository contract

For standalone Architect, Sketch, Deep-module and their evidence calls, use `<repo-root>/tmp/design-<slug>/`, with a kebab-case task slug; never system `/tmp` or a session folder. Grounding, experiments, Arena outputs, findings, and review logs stay under this root; Design names exact absolute Research destinations under this root in each Research request. Design supplies exact Prove/Challenge this report paths and repository base under this root; evidence skills own no Design path policy. Production code, when authorized, goes in the working tree.

```text
<artifact-root>/
  task.md
  grounding-*.md
  local/candidate-<n>/           # local comparison; preserve on Arena escalation
    rationale.md
    module-map.md
    sketch/
  candidate-<n>/                 # Arena candidates
    rationale.md
    module-map.md
    sketch/                      # real source files
  synthesis/                     # selected package; also standalone Sketch output
    rationale.md
    module-map.md
    sketch/
    synthesis-note.md           # Arena only
  arena-r<k>/                   # optional correction re-runs
  deep-modules/                 # interface options and comparison
  challenge-this.md
  prove/                        # reports and optional patches
  review-log.md
```

- `sketch/` contains language-native source files with `not implemented` bodies, not Markdown with embedded code; `module-map.md` maps them to repo-relative targets. `rationale.md` contains usage, decisions, alternatives, and open questions. The complete `synthesis/` package is the only accepted design handed to Spec; never publish raw candidates.
- Before grounding, read present repository architecture, relevant ADRs, Concepts, and glossary. Preserve their terms and boundaries; document conflicts as open questions and raise them during review. Pass source paths to delegated runners.
- Wayfinder retains accepted sketches and proof evidence under `docs/prototype/<initiative-slug>/`, Research under `docs/research/<initiative-slug>/`; its playbook owns exact destinations, prototype approval and local integration. Prove/Experiment and sketch prototypes require owned worktrees and explicit payload approval before local merge. Challenge this requires no approval: isolate code changes/test execution in an owned worktree, then integrate evidence and update fog/HLD automatically. Standalone temporary roots remain unchanged.
- `hld` coordinates Write authoring of authoritative feature-design documents in `docs/ongoing/{{initiativeSlug}}.md`; `factory-mode stories` owns story breakdown.
