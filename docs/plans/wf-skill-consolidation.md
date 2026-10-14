# WF skill consolidation

Status: partially implemented. `track-ledger` is absorbed into `grill-design` as a root-level `track-ledger.md` reference; its standalone skill is removed. The seven architecture record/render skills are absorbed into `record-architecture` with disclosed mode procedures. `to-zdesign` replaces its `doc-decision` call with its own local compact decision reference. Questioning remains unchanged; other consolidation and archive moves remain proposed.

Backlog entry superseded: `manage-backlog` was removed in favor of GitHub references bundled with each consuming skill and label setup owned by `init-wf`. The historical roster/count below describes the original consolidation proposal, not the current plugin.

Reduce 36 active skills to 27. Use progressive disclosure for grouped procedures; archive `to-use-cases`.

## Proposed skill list

| Proposed skill | Existing skills / disclosed procedures |
|---|---|
| `init-wf` | `init-wf` |
| `wayfinder` | `wayfinder` |
| `grill-design` | `grill-design`, `questioning`, `track-ledger` |
| `research` | `research` |
| `bottom-line` | `bottom-line` |
| `define-research` | `define-research` |
| `explore-codebase` | `explore-codebase` |
| `inspect-nuget-source` | `inspect-nuget-source` |
| `inspect-system` | `inspect-system` |
| `experiment` | `experiment` |
| `prototype-cloud-scenario` | `prototype-cloud-scenario` |
| `define-concept` | `define-concept` |
| `record-architecture` | `record-adr`, `record-building-block`, `record-deployment-view`, `record-term`, `doc-concept`, `record-concept`, `doc-decision` |
| `bootstrap-docs` | `bootstrap-docs` |
| `index-docs` | `index-docs` |
| `doc-architecture-diagram` | `doc-architecture-diagram` |
| `doc-behavior-diagram` | `doc-behavior-diagram` |
| `doc-code-diagram` | `doc-code-diagram` |
| `doc-contracts` | `doc-contracts` |
| `normalize-requirements` | `normalize-requirements` |
| `draft-story` | `draft-story` |
| `to-stories` | `to-stories` |
| `draft-bug` | `draft-bug` |
| `to-spec` | `to-spec` |
| `to-zdesign` | `to-zdesign` |
| `to-tickets` | `to-tickets` |
| `manage-backlog` (superseded; removed) | Historical backlog abstraction; now skill-local GitHub references and `init-wf` label setup |

## Proposed archive

| Existing skill | Destination |
|---|---|
| `to-use-cases` | `_backup/to-use-cases/` |

## Triggering and usage

- `grill-design` covers interviews, questioning, and decision forks. Its ledger procedure is now a root-level reference, loaded before ledger access; questioning remains unchanged.
- `record-architecture` covers documenting or recording ADRs, concepts, deployables, deployment topology, glossary terms, and decision bullets. Select the requested record type and load only its procedure and required helpers.
- Explicit modes are `adr`, `building-block`, `deployment-view`, `term`, `concept-body`, `concept-record`, and `decision-bullet`. Honor an explicit mode; route clear natural-language intent; ask for the intended artifact when ambiguous. Render-only modes never persist or index.
- `define-concept` discovers, scopes, and resolves concepts; use `record-architecture` to document and persist settled knowledge. Recording a settled concept must not force another interview.
- Keep `bootstrap-docs` and `index-docs` independently reusable by setup, recording, and inspection workflows.
- Preserve independent triggers for research, findings summaries, NuGet inspection, each diagram family, requirement normalization, and single-story drafting.
- Parent descriptions own discovery; `SKILL.md` owns routing; references own disclosed procedures. MUST load the selected procedure before acting.
- Preserve invocation, approval, evidence, and output contracts. Grouping MUST NOT add interviews, publication, or execution to unrelated modes.
- Replace calls to absorbed skills with the parent skill and exact mode. Exception: `to-zdesign` MUST load its own skill-local `decision-bullet.md` reference before rendering compact slice decisions; do not invoke the parent for this step or access its private resources. Keep each procedure in one place within a skill; the compact-rendering rules are bundled independently in both consumers for skill-local ownership.
- Absorbed procedures lose independent skill triggers and commands; references are not standalone skills.
- Verify representative prompts before implementation is considered complete, especially the broad `record-architecture` entry point.

The `track-ledger` merge was authorized and applied separately. The architecture recording merge and `to-zdesign` local-rendering exception are implemented. Other consolidation and archive moves have not been applied.
