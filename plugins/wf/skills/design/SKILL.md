---
name: design
description: >-
  Design architecture, sketch code, deepen modules, grill decisions, and publish specs or tickets. Use for 'architect this', 'sketch code', 'grill this', 'write a spec'. Not for empirical claim checks → `prove`; adversarial change review → `interrogate`.
---

# Design

One entry point; route to one playbook. Do not load unrelated routes.

| Route | Select for | Playbook |
| --- | --- | --- |
| `architect` | Design code shape across modules, compare candidates, then implement or hand off an accepted sketch. | [Architect](playbooks/architect.md) |
| `sketch` | Explicit request for a usage-first code sketch only, without Arena or implementation. | [Sketch](playbooks/sketch.md) |
| `deep-module` | Deepen an interface, place a seam, or compare module shapes. | [Deep module](playbooks/deep-module.md) |
| `grill` | Challenge a plan, interview domain decisions, or resolve a Wayfinder grilling ticket. | [Grill](playbooks/grill.md) |
| `spec` | Synthesize a spec or PRD from decisions or an accepted sketch. | [Spec](playbooks/spec.md) |
| `tickets` | Break a spec into implementation tickets on explicit request. | [Tickets](playbooks/tickets.md) |
| `wayfinder` | Chart or resume a Wayfinder decision map on explicit request. | [Wayfinder](playbooks/wayfinder.md) |
| `review` | Assess a technical design's gaps, risks, and implementation readiness on explicit request. | [Review](playbooks/review.md) |

1. Honor an explicit route from the user or caller. On replies to pending questions or checkpoints, continue the active route. Otherwise infer from clear intent. Ambiguous requests → ask which outcome the user wants and wait.
2. Select `tickets`, `wayfinder`, or `review` only on an explicit user request, including clear natural language relayed by a caller. Ticket publication requires separate approval of the breakdown; automatic Wayfinder runs have their own confirmation.
3. Select `sketch` only when the user explicitly requests a sketch without implementation. General code-shape or multi-candidate work selects `architect`. `deep-module` is standalone when explicitly requested and can also be called by Architect. Empirical checks and adversarial review belong to the standalone Prove and Interrogate skills.
4. Read only the selected playbook and references it calls for. Wayfinder loads Grill for interviews and then resumes the map. Continue Grill to Spec only after a requested handoff and closing sweep.

## Architect options and behavior

- Accept `arena-agents=1|2|3`, default `1`; reject other values before Arena. Retain the count across correction re-runs.
- Forward caller-supplied `adversaries` to Interrogate; it owns count validation/defaults.
- `checkpoint` is opt-in, only when explicitly requested; preserve it through caller handoffs. Otherwise Architect implements after review by default. An explicit **design-only handoff** returns the sketch for `design spec` without implementing.
- `architect sketch` routes to `sketch` only, and `architect deep-module` to `deep-module`, for intent compatibility. Prefer the direct `design <route>` spelling.

## Artifact and repository contract

For Architect, Sketch, Deep-module and their evidence calls, use `<repo-root>/tmp/design-<slug>/`, with a kebab-case task slug; never system `/tmp` or a session folder. Grounding, experiments, Arena outputs, findings, and review logs stay under this root; Design selects exact Research destinations under this root and supplies `@outputPath` and `@outputBase`; Research returns inline findings when no save is requested. Design supplies exact Prove/Interrogate report paths and repository base under this root; evidence skills own no Design path policy. Production code, when authorized, goes in the working tree.

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
  interrogate.md
  prove/                        # reports and optional patches
  review-log.md
```

- `sketch/` contains language-native source files with `not implemented` bodies, not Markdown with embedded code; `module-map.md` maps them to repo-relative targets. `rationale.md` contains usage, decisions, alternatives, and open questions. The complete `synthesis/` package is the only accepted design handed to Spec; never publish raw candidates.
- Before grounding, read present repository architecture, relevant ADRs, Concepts, and glossary. Preserve their terms and boundaries; document conflicts as open questions and raise them during review. Pass source paths to delegated runners.
- `draft-artifact design` owns authoritative feature-design documents; `factory-mode stories` owns story breakdown.
