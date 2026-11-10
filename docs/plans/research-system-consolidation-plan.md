# Research System consolidation plan

## Goal

Use How’s answer-first explanation as the shared output for research into current system behavior. Hunter runs the Explore procedure and supplies source evidence. System Inspection extends the explanation with deeper analysis and verification. Research selects the depth automatically and produces one cited Markdown document per system question.

## Responsibilities

| Component | Responsibility |
| --- | --- |
| How | `how/how.md` is the main output template for current-system research. Lead with the direct answer, then explain the mechanism in terms the reader can follow. |
| Hunter / Explore | `plugins/wf/agents/hunter.agent.md` owns and runs the Explore procedure. Hunter accepts `how/explorer-prompt.md` for system evidence work or another caller’s `@work` for a bounded lookup. Pure lookups still return inline. |
| System Inspection | Extends the same explanation with relevant Behavior, Flow, or Data analysis, failure paths, edge cases, and runtime verification or unknowns. |

## Routing and depth

| Request | Depth | Evidence and output |
| --- | --- | --- |
| Narrow system question | Concise | Use Explore for one focused evidence pass. Give the direct answer, explain the deciding behavior, and cite the primary source. |
| Complex system question | Detailed | Extend the explanation with relevant Behavior, Flow, or Data analysis. Include boundaries, failure paths, and edge cases that could change the answer. Split independent evidence work only when useful. |
| Explicit request to inspect or verify a system | Full | Apply the relevant inspection checks across the requested scope. Verify runtime-dependent claims when needed. If verification is blocked, record the unresolved claim, the blocker, and the exact next check. |

An explicit inspection request sets the minimum depth. A supplied `@researchScope` axis sets the primary lens, not the depth. Without an axis, Research selects the lens from the question. Escalate when additional boundaries, consequential failures, or conflicting evidence make the first pass insufficient. For a pure lookup with no requested document, dispatch Hunter and return its verdict inline. An explicit inspection or a requested document takes precedence over that shortcut.

## Implementation

1. **Unify the entry point.** Update `plugins/wf/skills/research/SKILL.md`. Route “how does this work?” and “inspect this system” to the same workflow. Load `how/how.md` for every saved current-system answer. Remove `/research how`, `@mode=how`, and the old How dispatch sequence. Use the explorer prompt for system evidence briefs. Preserve Why and its code-anchor mode, the Explore request contract, and Cloud and Web routing for independent questions.
2. **Preserve How as the output contract.** Repurpose `how/how.md` from a routing procedure into the main output template. Fold the answer-first guidance from `how/explainer-prompt.md` into it, then retire that file. Keep `how/explorer-prompt.md` as the shared brief for delegated system evidence work. The coordinator reconciles conflicting evidence and writes one answer using the How template.
3. **Make the lenses composable.** Keep the Behavior, Flow, and Data references and load only the ones needed. Preserve their proof requirements, such as tracing the real provider and fallback for Behavior, verifying sender, receiver, and binding for Flow, and checking the actual writers, readers, and keys for Data. Keep depth selection and evidence checks in `system/system-inspection.md`. Move the useful axis-template checks into the lens references, then retire the three standalone templates. Each lens adds findings to the How template. A lane decision, persistence detail, or cloud fact that determines the answer belongs in the same document. A separately scoped question can be researched on a later request.
4. **Centralize report rules.** Use the How template’s direct answer and mechanism at every depth. Integrate inspection findings where they explain the mechanism or an outcome. Add sections for relevant failure paths, runtime observations, assumptions, and unknowns as needed. Explain each part of the mechanism once. Cite each material claim where it appears. Distinguish what code permits from what was observed at runtime. Keep diagrams and tables when they add information and render every included Mermaid block. Keep `@outputShape` path and framing, with one document as the system output contract. Preserve the current default filenames for single-axis Flow and Data. Use `docs/research/<slug>.md` for focused or combined work.
5. **Move Explore into Hunter.** Merge `research/explore/explore.md` into `plugins/wf/agents/hunter.agent.md`, then delete the original file. Reconcile overlapping tool rules into one set. Keep repository and deployable resolution, contracts-first reading, shape-based routing, Graphify, GitHub fallback for remote targets, and verdict rules. Hunter loads `research/explore/nuget.md` when a package lookup needs it. Preserve the read-only contract, caller-provided `@work` and `@outputShape`, and the existing `@outputArtifact` exception.
6. **Migrate callers and docs.** Update Blast Radius, Architect grounding, and the Factory Mode feature playbook to request current behavior via default Research. Preserve their requested artifact paths, Why calls, and Blast Radius’s separate proof step. Update Wayfinder’s scope guidance to distinguish axis from depth. Clean up Hunter’s description, Research’s system README and Why introduction, and WF and Architect README references. Update active Explore callers to send the same request directly to Hunter. Cover Define Concept, Record Architecture, Design Grill and Sketch, Architect Sketch, Draft Artifact Bug and TOI, Experiment, Research’s direct lookups and System Inspection, and the AWS and Azure NuGet tactics. Remove Experiment’s inline execution fallback and the generic `explore` agent fallback for this contract. If Hunter is unavailable, report the blocked evidence request and continue independent work. Update `docs/adr/research-explore-is-skill-agnostic.md` and its Architecture index entry to describe agent ownership. Search active paths for stale instructions to load `explore/explore.md` or run the old Explore route in a worker.

## Explorer prompt additions

Keep the assigned angle, components, flow, boundaries, files read, gotchas, open questions, and read-only rules. Add the missing instructions from the existing references.

- **Explore inputs and navigation.** Include the original question, assigned angle, named targets or refs, depth, applicable lens, and evidence return shape. Research passes the filled `how/explorer-prompt.md` verbatim to `hunter` as `@work` in an Explore request. Hunter applies its own Explore procedure to resolve the target, read contracts first, and select tools. The brief specifies the research task and evidence to return.
- **Inspection evidence.** Cite decisive source lines and distinguish as-built code from documented intent and runtime observations. For the selected lens, trace the relevant trigger and outcome, sender/receiver/binding, or readers/writers and storage rules. Include failures and edge cases that affect the answer. Record assumptions, unknowns, and evidence conflicts.
- **Runtime checks and handoff.** When static evidence leaves a material claim open, capture an authorized check and its observed result or report the blocker and exact next check. Return cited findings, files read, and gaps to Research for integration into `how/how.md`. The worker writes no standalone report.

## Research skill layout

```text
research/
├── SKILL.md
├── how/
│   ├── how.md                      Main output template
│   └── explorer-prompt.md          Delegated evidence brief
├── explore/
│   └── nuget.md                    Package lookup reference loaded by Hunter
├── system/
│   ├── README.md
│   ├── system-inspection.md       Depth and verification rules
│   ├── behavior-inspection.md
│   ├── flow-inspection.md
│   └── data-inspection.md
├── cloud/
└── why/
```

The Explore procedure lives in `plugins/wf/agents/hunter.agent.md`.

## Affected paths

| Area | Paths |
| --- | --- |
| Research | `plugins/wf/skills/research/SKILL.md`, `how/`, `explore/explore.md` (remove), `explore/nuget.md`, `system/`, `cloud/aws.md`, `cloud/azure.md`, `why/why.md` |
| Callers | `plugins/wf/skills/review/playbooks/blast-radius.md`, `plugins/wf/skills/architect/design/design.md`, `plugins/wf/skills/design/playbooks/wayfinder.md`, `plugins/wf/install/assets/factory-mode/playbooks/feature.md`, and the active Explore callers listed above |
| Discovery and docs | `plugins/wf/agents/hunter.agent.md`, `plugins/wf/README.md`, `plugins/wf/skills/architect/README.md`, `ARCHITECTURE.md`, `docs/adr/research-explore-is-skill-agnostic.md` |
| Tests | `tests/wf/research/test_contracts.py`, `tests/wf/subagents/test_contracts.py`. Update `tests/wf/research/test_explore_contracts.py` and the existing Explore eval expectations to verify Hunter-owned routing. |

## Acceptance

- A saved question about one function uses `how/how.md` to produce a short explanation with citations from Explore. A pure inline symbol lookup still returns an Explore verdict.
- Hunter handles literal, symbol, relationship, remote GitHub, and NuGet requests under the existing read-only and return contracts. No worker needs to load the deleted `explore/explore.md`. A missing Hunter produces an explicit blocker.
- A delegated system evidence brief uses `how/explorer-prompt.md` and returns source references and gaps without generating a report. A blocked runtime check identifies the claim it would settle.
- A cross-service question that depends on a lane’s retry policy or a storage decision extends the same How structure with cited handoffs and the deciding detail. The report contains one explanation of the mechanism.
- An explicit inspection covers the requested scope. A live-only claim gets runtime evidence or an explicit unknown with a reproducible next check. Runtime verification uses authorized access and a safe target.
- Blast Radius and Architect still receive their requested artifacts. Why code anchor and Wayfinder axis hints still work.
- Active instructions and tests have no stale How invocation or deleted template link. Existing Research, Explore, Subagents, and repository consistency tests pass.

## Rationale

The same answer-first structure works for a small function and a cross-service investigation. Explore gives each explanation a source trail. Inspection adds depth where a boundary, failure path, or runtime observation changes the answer.
