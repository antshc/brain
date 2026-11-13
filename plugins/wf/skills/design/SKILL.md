---
name: design
description: >-
  Design architecture, resolve decisions, and write or publish HLDs, specs or tickets. Use for 'architect this', 'high-level design', 'publish HLD to Confluence', 'grill this', 'write a spec', or 'design review'. Not for PR review → `review`.
---

# Design

One entry point; route to one playbook. Do not load unrelated routes.

| Route | Select for | Playbook |
| --- | --- | --- |
| `architect` | Design code shape across modules, compare candidates, then implement or hand off an accepted sketch. | [Architect](playbooks/architect.md) |
| `sketch` | Explicit request for a usage-first code sketch only, without Arena or implementation. | [Sketch](playbooks/sketch.md) |
| `deep-module` | Deepen an interface, place a seam, or compare module shapes. | [Deep module](playbooks/deep-module.md) |
| `grill` | Challenge a plan, interview domain decisions, or resolve a Wayfinder grilling ticket. | [Grill](playbooks/grill.md) |
| `hld` | Create or update an authoritative high-level feature design from specs and resolved decisions. | [HLD](playbooks/hld.md) |
| `publish-hld` | Publish an HLD to Confluence with research child pages and prototype/sketch attachments on explicit request. | [Publish HLD](playbooks/publish-hld.md) |
| `spec` | Synthesize a spec or PRD from decisions or an accepted sketch. | [Spec](playbooks/spec.md) |
| `tickets` | Break a spec into implementation tickets on explicit request. | [Tickets](playbooks/tickets.md) |
| `wayfinder` | Chart or resume a decision map with a living HLD and automatic evidence work on explicit request. | [Wayfinder](playbooks/wayfinder.md) |
| `review` | Assess a technical design's gaps, risks, and implementation readiness on explicit request. | [Review](playbooks/review.md) |

1. Honor an explicit route from the user or caller. On replies to pending questions or checkpoints, continue the active route. Otherwise infer from clear intent. Ambiguous requests → ask which outcome the user wants and wait.
2. Select `tickets`, `wayfinder`, or `review` only on an explicit user request, including clear natural language relayed by a caller. Ticket publication requires separate approval of the breakdown; Wayfinder automatically runs in-scope factual research and proof; human choices stay interactive. Publication requires an explicit `publish-hld` request; HLD synthesis and Wayfinder completion never select it automatically.
3. Select `sketch` only when the user explicitly requests a sketch without implementation. General code-shape or multi-candidate work selects `architect`. `deep-module` is standalone when explicitly requested and can also be called by Architect. Empirical checks and adversarial review belong to the standalone Prove and Challenge this skills.
4. Select `hld` only for an explicit request to create or update a high-level design or feature design, including `/design hld`. Wayfinder may select it for its living HLD and subsequent updates. A spec or design supplied as input alone does not select it.
5. Read the selected playbook fully before acting and required resources fully before use. For `hld`, load [Design template](templates/design-template.md) and [Decision bullets](references/decision-bullet.md); the playbook owns synthesis and merge checks. Wayfinder loads Grill for interviews and then resumes the map. Continue standalone Grill to Spec only after a requested handoff and closing sweep. Wayfinder synchronizes confirmed outcomes automatically and retains control.

## Conditional resources

Read triggered resources fully before use; resolve from this skill directory.

| Trigger | Resource |
| --- | --- |
| Wayfinder tracker/local integration; Spec issue publication; Tickets publication | [GitHub operations](references/github.md) |
| Wayfinder ticket classification | [Ticket types](references/wayfinder-ticket-types.md) |
| Wayfinder creation/update; HLD evolving draft | [Living document](references/living-document.md) |
| Publish HLD sketch packaging | [Sketch packager](scripts/package_sketch.py); execute with `--help` from this skill directory |
| HLD or Wayfinder material risks | [Risk verification](references/risk-verification.md); select Prove or Challenge this before final synthesis or through the existing Wayfinder queue |
| HLD synthesis, including Wayfinder HLD | [Design template](templates/design-template.md), [Decision bullets](references/decision-bullet.md) |
| Grill session state | [Session ledger](references/track-ledger.md) |
| Grill verification-scope trigger | [Verification](references/tactics-verification.md) |
| Grill external-source trigger | [External source](references/tactics-external-source.md) |
| Grill closing/handoff | [Closing sweep](references/closing-sweep.md) |

Wayfinder additionally reads the full Grill playbook for interviews and the full HLD playbook for document authoring, using the route table above. Spec remains a separate explicitly requested route; Wayfinder does not select it as an output format.

## Principles

*Load and follow the `principles` skill to load indexed engineering principles by name*. Pass task, selected route, phase and explicitly named principles; select `In your own words` for intent. Let the Index select for consumer experience, domain/type shape, seams, boundaries, concurrency and alternatives. Apply before the selected playbook; re-evaluate at phase changes. Fresh candidate workers apply this rule in their own context.

## Architect options and behavior

- Accept `arena-agents=1|2|3`, default `1`; reject other values before Arena. Retain the count across correction re-runs.
- Forward caller-supplied `adversaries` to Challenge this; it owns count validation/defaults.
- `checkpoint` is opt-in, only when explicitly requested; preserve it through caller handoffs. Otherwise Architect implements after review by default. An explicit **design-only handoff** returns the sketch for `design spec` without implementing.
- `architect sketch` routes to `sketch` only, and `architect deep-module` to `deep-module`, for intent compatibility. Prefer the direct `design <route>` spelling.

## Artifact and repository contract

For standalone Architect, Sketch, Deep-module and their evidence calls, use `<repo-root>/tmp/design-<slug>/`, with a kebab-case task slug; never system `/tmp` or a session folder. Grounding, experiments, Arena outputs, findings, and review logs stay under this root; Design selects exact Research destinations under this root and supplies `@outputPath` and `@outputBase`; Research returns inline findings when no save is requested. Design supplies exact Prove/Challenge this report paths and repository base under this root; evidence skills own no Design path policy. Production code, when authorized, goes in the working tree.

```
<artifact-root>/
  task.md
  grounding-*.md
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
- Wayfinder retains accepted sketches and proof evidence under `docs/prototype/<initiative-slug>/`, Research under `docs/research/<initiative-slug>/`; its playbook owns exact destinations and local integration. Standalone temporary roots remain unchanged.
- `hld` owns authoritative feature-design documents in `docs/ongoing/{{initiativeSlug}}.md`; `factory-mode stories` owns story breakdown.
